from pyspark.sql import SparkSession
import os
'''
提高运行速度
,增大executor内存、core数，合理设置spark.executor.memory、spark.executor.cores和spark.driver.memory。
G1 GC适用于大内存堆,启用G1垃圾回收器
-XX:+ParallelRefProcEnabled：启用并行引用处理，提高效率
配置G1
增加shuffle分区，避免单个分区过大
在 Spark 配置中指定本地库路径
'''
def get_spark_session(app_name="RecommenderApp"):
    return SparkSession.builder \
        .appName(app_name) \
        .config("spark.hadoop.fs.defaultFS", "hdfs://localhost:9000") \
        .config("spark.executor.memory", "8g") \
        .config("spark.executor.cores", "4") \
        .config("spark.driver.memory", "4g") \
        .config("spark.executor.extraJavaOptions",
            "-XX:+UseG1GC -XX:InitiatingHeapOccupancyPercent=35 -XX:+ParallelRefProcEnabled") \
        .config("spark.driver.extraJavaOptions",
                "-XX:+UseG1GC -XX:InitiatingHeapOccupancyPercent=35 -XX:+ParallelRefProcEnabled") \
        .config("spark.sql.shuffle.partitions", "500") \
        .config("spark.eventLog.gcMetrics.youngGenerationGarbageCollectors", "G1 Young Generation") \
        .config("spark.eventLog.gcMetrics.oldGenerationGarbageCollectors", "G1 Old Generation") \
        .config("spark.executor.extraJavaOptions", f"-Djava.library.path={os.environ['HADOOP_HOME']}/lib/native") \
        .config("spark.driver.extraJavaOptions", f"-Djava.library.path={os.environ['HADOOP_HOME']}/lib/native") \
        .getOrCreate()