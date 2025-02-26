from pyspark.sql import SparkSession
from pyspark.sql.functions import col
spark = SparkSession.builder.appName("ADHDScreenTimeETL").getOrCreate()

# Read from S3
df = spark.read.csv("s3://rakesh-adhd-bucket/adhd_screen_time.csv", header=True, inferSchema=True)

# Transform 1: Aggregate by app and month
df = df.withColumn("month", col("date").substr(1, 7))  # Extract YYYY-MM
agg_df = df.groupBy("app", "month").agg(
    {"screen_time_min": "sum", "adhd_score": "avg"}
).withColumnRenamed("sum(screen_time_min)", "total_screen_time").withColumnRenamed("avg(adhd_score)", "avg_adhd_score")

# Transform 2: Clean data (e.g., remove outliers > 600 min)
clean_df = df.filter(col("screen_time_min") <= 600)

# Write to S3
agg_df.write.parquet("s3://rakesh-accounting-bucket/processed/agg_data/")
clean_df.write.csv("s3://rakesh-accounting-bucket/processed/clean_data/")
spark.stop()