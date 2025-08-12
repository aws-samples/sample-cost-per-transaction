import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrame
from pyspark.sql import functions as F
from pyspark.sql.types import *
from pyspark.sql.window import Window

# Initialize Glue context
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)

# Get job parameters
args = getResolvedOptions(sys.argv, ['JOB_NAME', 'source_bucket', 'target_bucket', 'database_name'])
job.init(args['JOB_NAME'], args)

# Source and target paths
source_path = f"s3://{args['source_bucket']}/tco_tbm/"
target_path = f"s3://{args['target_bucket']}/analytics/"
database_name = args['database_name']

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

# Create marketing channel performance analysis
marketing_performance = spark.sql("""
    WITH search_counts AS (
        SELECT 
            marketing_channel,
            COUNT(*) as search_count,
            COUNT(DISTINCT user_id) as unique_searchers
        FROM hotel_searches
        GROUP BY marketing_channel
    ),
    booking_counts AS (
        SELECT 
            marketing_channel,
            COUNT(*) as booking_count,
            COUNT(DISTINCT user_id) as unique_bookers,
            SUM(amount) as total_revenue
        FROM hotel_bookings
        GROUP BY marketing_channel
    )
    SELECT 
        COALESCE(s.marketing_channel, b.marketing_channel) as marketing_channel,
        COALESCE(s.search_count, 0) as search_count,
        COALESCE(s.unique_searchers, 0) as unique_searchers,
        COALESCE(b.booking_count, 0) as booking_count,
        COALESCE(b.unique_bookers, 0) as unique_bookers,
        COALESCE(b.total_revenue, 0) as total_revenue,
        CASE 
            WHEN s.search_count > 0 THEN COALESCE(b.booking_count, 0) / s.search_count 
            ELSE 0 
        END as conversion_rate
    FROM search_counts s
    FULL OUTER JOIN booking_counts b ON s.marketing_channel = b.marketing_channel
    ORDER BY total_revenue DESC
""")

# Create city popularity analysis
city_popularity = spark.sql("""
    SELECT 
        city,
        COUNT(*) as search_count,
        COUNT(DISTINCT user_id) as unique_searchers
    FROM hotel_searches
    WHERE city IS NOT NULL
    GROUP BY city
    ORDER BY search_count DESC
""")

# Create booking patterns by device type
device_patterns = spark.sql("""
    SELECT 
        device_type,
        COUNT(*) as booking_count,
        AVG(amount) as avg_booking_value,
        SUM(amount) as total_revenue
    FROM hotel_bookings
    WHERE device_type IS NOT NULL
    GROUP BY device_type
    ORDER BY total_revenue DESC
""")

# Create user booking frequency analysis
user_frequency = spark.sql("""
    SELECT 
        user_id,
        COUNT(*) as booking_count,
        SUM(amount) as total_spent,
        MIN(check_in) as first_booking,
        MAX(check_in) as last_booking
    FROM hotel_bookings
    WHERE user_id IS NOT NULL
    GROUP BY user_id
    ORDER BY booking_count DESC
""")

# Create hotel popularity analysis
hotel_popularity = spark.sql("""
    SELECT 
        hotel_id,
        hotel_name,
        COUNT(*) as booking_count,
        SUM(amount) as total_revenue,
        AVG(amount) as avg_booking_value
    FROM hotel_bookings
    WHERE hotel_id IS NOT NULL
    GROUP BY hotel_id, hotel_name
    ORDER BY booking_count DESC
""")

# Convert to DynamicFrames
marketing_performance_df = DynamicFrame.fromDF(marketing_performance, glueContext, "marketing_performance")
city_popularity_df = DynamicFrame.fromDF(city_popularity, glueContext, "city_popularity")
device_patterns_df = DynamicFrame.fromDF(device_patterns, glueContext, "device_patterns")
user_frequency_df = DynamicFrame.fromDF(user_frequency, glueContext, "user_frequency")
hotel_popularity_df = DynamicFrame.fromDF(hotel_popularity, glueContext, "hotel_popularity")

# Write to S3 in Parquet format
glueContext.write_dynamic_frame.from_options(
    frame=marketing_performance_df,
    connection_type="s3",
    connection_options={"path": f"{target_path}marketing_performance"},
    format="parquet"
)

glueContext.write_dynamic_frame.from_options(
    frame=city_popularity_df,
    connection_type="s3",
    connection_options={"path": f"{target_path}city_popularity"},
    format="parquet"
)

glueContext.write_dynamic_frame.from_options(
    frame=device_patterns_df,
    connection_type="s3",
    connection_options={"path": f"{target_path}device_patterns"},
    format="parquet"
)

glueContext.write_dynamic_frame.from_options(
    frame=user_frequency_df,
    connection_type="s3",
    connection_options={"path": f"{target_path}user_frequency"},
    format="parquet"
)

glueContext.write_dynamic_frame.from_options(
    frame=hotel_popularity_df,
    connection_type="s3",
    connection_options={"path": f"{target_path}hotel_popularity"},
    format="parquet"
)

# Create tables in the Glue Data Catalog
for table_name in ["marketing_performance", "city_popularity", "device_patterns", "user_frequency", "hotel_popularity"]:
    glueContext.create_dynamic_frame.from_catalog(
        database=database_name,
        table_name=table_name
    )

job.commit()