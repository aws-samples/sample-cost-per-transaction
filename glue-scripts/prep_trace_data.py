import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrame
from pyspark.sql import functions as F
from pyspark.sql.types import *

# Initialize Glue context
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)

# Get job parameters
args = getResolvedOptions(sys.argv, ['JOB_NAME', 'source_bucket', 'target_bucket', 'database_name'])
job.init(args['JOB_NAME'], args)

# Source and target paths
source_path = f"s3://{args['source_bucket']}/xray-data/"
target_path = f"s3://{args['target_bucket']}/tco_tbm/"
database_name = args['database_name']

# Read X-Ray trace data from S3
xray_data = glueContext.create_dynamic_frame.from_options(
    connection_type="s3",
    connection_options={"paths": [source_path], "recurse": True},
    format="json"
)

# Convert to Spark DataFrame for easier processing
xray_df = xray_data.toDF()

# Flatten the nested structure
def process_traces(df):
    # Explode segments array
    segments_df = df.select(
        "traceId",
        "duration",
        F.explode("segments").alias("segment")
    )
    
    # Extract fields from segment
    flattened_df = segments_df.select(
        "traceId",
        "duration",
        F.col("segment.name").alias("segment_name"),
        F.col("segment.startTime").alias("start_time"),
        F.col("segment.endTime").alias("end_time"),
        F.col("segment.origin").alias("origin"),
        F.col("segment.aws").alias("aws_data"),
        F.col("segment.annotations").alias("annotations"),
        F.col("segment.metadata").alias("metadata")
    )
    
    # Extract annotations
    annotations_df = flattened_df.select(
        "traceId",
        "segment_name",
        F.col("annotations.user_id").alias("user_id"),
        F.col("annotations.hotel_id").alias("hotel_id"),
        F.col("annotations.hotel_name").alias("hotel_name"),
        F.col("annotations.city").alias("city"),
        F.col("annotations.check_in").alias("check_in"),
        F.col("annotations.check_out").alias("check_out"),
        F.col("annotations.guests").alias("guests"),
        F.col("annotations.rooms").alias("rooms"),
        F.col("annotations.marketing_channel").alias("marketing_channel"),
        F.col("annotations.device_type").alias("device_type"),
        F.col("annotations.payment_method").alias("payment_method"),
        F.col("annotations.amount").alias("amount"),
        F.col("annotations.currency").alias("currency"),
        F.col("annotations.confirmation_number").alias("confirmation_number"),
        F.col("annotations.results_count").alias("results_count"),
        F.col("annotations.operation").alias("operation"),
        F.col("annotations.table").alias("table"),
        F.col("annotations.function_name").alias("function_name"),
        F.col("annotations.email_type").alias("email_type"),
        F.col("annotations.recipient").alias("recipient"),
        F.col("annotations.function").alias("function"),
        F.col("annotations.loyalty_level").alias("loyalty_level")
    )
    
    return annotations_df

# Process the traces
processed_df = process_traces(xray_df)

# Create a view for SQL queries
processed_df.createOrReplaceTempView("traces")

# Extract hotel search data
hotel_searches = spark.sql("""
    SELECT 
        traceId,
        user_id,
        city,
        check_in,
        check_out,
        guests,
        rooms,
        marketing_channel,
        device_type,
        results_count,
        segment_name
    FROM traces
    WHERE segment_name = 'API Gateway - Hotel Search'
    AND user_id IS NOT NULL
""")

# Extract hotel booking data
hotel_bookings = spark.sql("""
    SELECT 
        traceId,
        user_id,
        hotel_id,
        hotel_name,
        check_in,
        check_out,
        guests,
        rooms,
        marketing_channel,
        device_type,
        payment_method,
        amount,
        currency,
        confirmation_number,
        segment_name
    FROM traces
    WHERE segment_name = 'API Gateway - Hotel Booking'
    AND user_id IS NOT NULL
    AND hotel_id IS NOT NULL
""")

# Convert back to DynamicFrames
searches_dynamic_frame = DynamicFrame.fromDF(hotel_searches, glueContext, "searches")
bookings_dynamic_frame = DynamicFrame.fromDF(hotel_bookings, glueContext, "bookings")

# Write to S3 in Parquet format
glueContext.write_dynamic_frame.from_options(
    frame=searches_dynamic_frame,
    connection_type="s3",
    connection_options={"path": f"{target_path}hotel_searches", "partitionKeys": ["marketing_channel"]},
    format="parquet"
)

glueContext.write_dynamic_frame.from_options(
    frame=bookings_dynamic_frame,
    connection_type="s3",
    connection_options={"path": f"{target_path}hotel_bookings", "partitionKeys": ["marketing_channel"]},
    format="parquet"
)

# Create tables in the Glue Data Catalog
glueContext.create_dynamic_frame.from_catalog(
    database=database_name,
    table_name="hotel_searches"
)

glueContext.create_dynamic_frame.from_catalog(
    database=database_name,
    table_name="hotel_bookings"
)

job.commit()