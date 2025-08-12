import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrame
from pyspark.sql import functions as F
from pyspark.sql.types import *
import datetime

# Initialize Glue context
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)

# Get job parameters
args = getResolvedOptions(sys.argv, ['JOB_NAME', 'source_bucket', 'target_bucket', 'database_name', 'redshift_connection'])
job.init(args['JOB_NAME'], args)

# Source and target paths
source_path = f"s3://{args['source_bucket']}/tco_tbm/"
target_path = f"s3://{args['target_bucket']}/redshift_data/"
database_name = args['database_name']
redshift_connection = args['redshift_connection']

# Read processed data from S3
hotel_searches = glueContext.create_dynamic_frame.from_options(
    connection_type="s3",
    connection_options={"paths": [f"{source_path}hotel_searches"], "recurse": True},
    format="parquet"
).toDF()

hotel_bookings = glueContext.create_dynamic_frame.from_options(
    connection_type="s3",
    connection_options={"paths": [f"{source_path}hotel_bookings"], "recurse": True},
    format="parquet"
).toDF()

# Register as temp views for SQL
hotel_searches.createOrReplaceTempView("hotel_searches")
hotel_bookings.createOrReplaceTempView("hotel_bookings")

# Create date dimension
def create_date_dimension(start_date, end_date):
    # Generate a list of dates
    date_list = []
    current_date = start_date
    while current_date <= end_date:
        date_list.append(current_date)
        current_date += datetime.timedelta(days=1)
    
    # Create DataFrame
    date_df = spark.createDataFrame([(date,) for date in date_list], ["date"])
    
    # Add date attributes
    date_df = date_df.withColumn("date_id", F.date_format("date", "yyyyMMdd").cast("int"))
    date_df = date_df.withColumn("year", F.year("date"))
    date_df = date_df.withColumn("month", F.month("date"))
    date_df = date_df.withColumn("day", F.dayofmonth("date"))
    date_df = date_df.withColumn("quarter", F.quarter("date"))
    date_df = date_df.withColumn("day_of_week", F.dayofweek("date"))
    date_df = date_df.withColumn("day_name", F.date_format("date", "EEEE"))
    date_df = date_df.withColumn("month_name", F.date_format("date", "MMMM"))
    date_df = date_df.withColumn("is_weekend", F.when(F.col("day_of_week").isin([1, 7]), True).otherwise(False))
    
    return date_df

# Create hotel dimension
hotel_dimension = spark.sql("""
    SELECT DISTINCT
        hotel_id,
        hotel_name
    FROM hotel_bookings
    WHERE hotel_id IS NOT NULL
""")

# Create user dimension
user_dimension = spark.sql("""
    SELECT DISTINCT
        user_id
    FROM hotel_bookings
    WHERE user_id IS NOT NULL
    
    UNION
    
    SELECT DISTINCT
        user_id
    FROM hotel_searches
    WHERE user_id IS NOT NULL
""")

# Create marketing channel dimension
marketing_dimension = spark.sql("""
    SELECT DISTINCT
        marketing_channel
    FROM hotel_bookings
    WHERE marketing_channel IS NOT NULL
    
    UNION
    
    SELECT DISTINCT
        marketing_channel
    FROM hotel_searches
    WHERE marketing_channel IS NOT NULL
""")

# Create city dimension
city_dimension = spark.sql("""
    SELECT DISTINCT
        city
    FROM hotel_searches
    WHERE city IS NOT NULL
""")

# Create device dimension
device_dimension = spark.sql("""
    SELECT DISTINCT
        device_type
    FROM hotel_bookings
    WHERE device_type IS NOT NULL
    
    UNION
    
    SELECT DISTINCT
        device_type
    FROM hotel_searches
    WHERE device_type IS NOT NULL
""")

# Create booking fact table
booking_fact = spark.sql("""
    SELECT
        b.traceId,
        b.user_id,
        b.hotel_id,
        b.marketing_channel,
        b.device_type,
        b.check_in,
        b.check_out,
        b.guests,
        b.rooms,
        b.amount as booking_amount,
        b.confirmation_number
    FROM hotel_bookings b
""")

# Create search fact table
search_fact = spark.sql("""
    SELECT
        s.traceId,
        s.user_id,
        s.city,
        s.marketing_channel,
        s.device_type,
        s.check_in,
        s.check_out,
        s.guests,
        s.rooms,
        s.results_count
    FROM hotel_searches s
""")

# Create date dimension
# Get min and max dates from data
min_date_row = spark.sql("""
    SELECT MIN(LEAST(
        MIN(TO_DATE(check_in, 'yyyy-MM-dd')), 
        MIN(TO_DATE(check_out, 'yyyy-MM-dd'))
    )) as min_date
    FROM (
        SELECT check_in, check_out FROM hotel_bookings
        UNION ALL
        SELECT check_in, check_out FROM hotel_searches
    )
""").collect()[0]

max_date_row = spark.sql("""
    SELECT MAX(GREATEST(
        MAX(TO_DATE(check_in, 'yyyy-MM-dd')), 
        MAX(TO_DATE(check_out, 'yyyy-MM-dd'))
    )) as max_date
    FROM (
        SELECT check_in, check_out FROM hotel_bookings
        UNION ALL
        SELECT check_in, check_out FROM hotel_searches
    )
""").collect()[0]

min_date = min_date_row["min_date"]
max_date = max_date_row["max_date"]

# Add buffer of 30 days on each side
min_date = min_date - datetime.timedelta(days=30)
max_date = max_date + datetime.timedelta(days=30)

# Create date dimension
date_dimension = create_date_dimension(min_date, max_date)

# Convert to DynamicFrames
hotel_dim_df = DynamicFrame.fromDF(hotel_dimension, glueContext, "hotel_dimension")
user_dim_df = DynamicFrame.fromDF(user_dimension, glueContext, "user_dimension")
marketing_dim_df = DynamicFrame.fromDF(marketing_dimension, glueContext, "marketing_dimension")
city_dim_df = DynamicFrame.fromDF(city_dimension, glueContext, "city_dimension")
device_dim_df = DynamicFrame.fromDF(device_dimension, glueContext, "device_dimension")
date_dim_df = DynamicFrame.fromDF(date_dimension, glueContext, "date_dimension")
booking_fact_df = DynamicFrame.fromDF(booking_fact, glueContext, "booking_fact")
search_fact_df = DynamicFrame.fromDF(search_fact, glueContext, "search_fact")

# Write to S3 in Parquet format for Redshift Spectrum
glueContext.write_dynamic_frame.from_options(
    frame=hotel_dim_df,
    connection_type="s3",
    connection_options={"path": f"{target_path}hotel_dimension"},
    format="parquet"
)

glueContext.write_dynamic_frame.from_options(
    frame=user_dim_df,
    connection_type="s3",
    connection_options={"path": f"{target_path}user_dimension"},
    format="parquet"
)

glueContext.write_dynamic_frame.from_options(
    frame=marketing_dim_df,
    connection_type="s3",
    connection_options={"path": f"{target_path}marketing_dimension"},
    format="parquet"
)

glueContext.write_dynamic_frame.from_options(
    frame=city_dim_df,
    connection_type="s3",
    connection_options={"path": f"{target_path}city_dimension"},
    format="parquet"
)

glueContext.write_dynamic_frame.from_options(
    frame=device_dim_df,
    connection_type="s3",
    connection_options={"path": f"{target_path}device_dimension"},
    format="parquet"
)

glueContext.write_dynamic_frame.from_options(
    frame=date_dim_df,
    connection_type="s3",
    connection_options={"path": f"{target_path}date_dimension"},
    format="parquet"
)

glueContext.write_dynamic_frame.from_options(
    frame=booking_fact_df,
    connection_type="s3",
    connection_options={"path": f"{target_path}booking_fact"},
    format="parquet"
)

glueContext.write_dynamic_frame.from_options(
    frame=search_fact_df,
    connection_type="s3",
    connection_options={"path": f"{target_path}search_fact"},
    format="parquet"
)

# Write directly to Redshift tables
for table_name, dynamic_frame in [
    ("hotel_dimension", hotel_dim_df),
    ("user_dimension", user_dim_df),
    ("marketing_dimension", marketing_dim_df),
    ("city_dimension", city_dim_df),
    ("device_dimension", device_dim_df),
    ("date_dimension", date_dim_df),
    ("booking_fact", booking_fact_df),
    ("search_fact", search_fact_df)
]:
    glueContext.write_dynamic_frame.from_jdbc_conf(
        frame=dynamic_frame,
        catalog_connection=redshift_connection,
        connection_options={
            "dbtable": f"public.{table_name}",
            "database": "tco_tbm_db"
        },
        redshift_tmp_dir=f"s3://{args['target_bucket']}/temp/"
    )

job.commit()