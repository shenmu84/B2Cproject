from pyspark.sql import SparkSession

def get_spark_session(app_name="RecommenderApp"):
    return SparkSession.builder \
        .appName(app_name) \
        .config("spark.hadoop.fs.defaultFS", "hdfs://localhost:9000") \
        .getOrCreate()