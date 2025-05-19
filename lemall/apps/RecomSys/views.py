from django.http import JsonResponse
from pyspark.sql.functions import col
import json
from apps.RecomSys.spark_utils import get_spark_session
#fileName="hdfs:///amazon/AMAZON_FASHION_5.json.gz"
fileName="hdfs:///amazon/All_Beauty_5.json.gz"
'''
css复制编辑[ HDFS 上的 JSON.GZ 文件 ]
        ↓（PySpark 读取）
[ Spark ALS 模型训练与推荐 ]
        ↓（结果：user_id -> product_ids）
[ Django 后端 API ]
        ↓
[ 前端页面展示推荐内容 ]
'''

#读取 HDFS 上 gzip 的 JSON 文件
def getJsonData():
    spark = get_spark_session()

    # 直接读取 gzip 压缩文件
    df = spark.read.json(fileName)

    #显示前十行数据
   # df.show(10, truncate=False)
    return df
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lit
from pyspark.sql.types import IntegerType
#商品画像
def create_item_profile(df):
    import pandas as pd

    # 这里只保留 asin 不为空的记录
    items =  df.filter(col("asin").isNotNull())
    #只保留 asin, style, summary 三列
    items = items[['asin', 'style', 'summary']]

    # 拼接 style 和 summary 作为商品描述
    items['desc'] = items.withColumn(
    "desc",
    concat_ws(" ", coalesce(items["style"], lit("")), coalesce(items["summary"], lit("")))
)
    # 最终只保留 asin 和 desc
    items = items[['asin', 'desc']]
    items = items.drop_duplicates(subset=['asin'])

    items = items.sort_values('asin').reset_index(drop=True)
        #用 sklearn 的 TfidfVectorizer 提取文本特征，生成商品画像
    from sklearn.feature_extraction.text import TfidfVectorizer

    v = TfidfVectorizer(stop_words="english", max_features=100, ngram_range=(1,3), sublinear_tf=True)

    x = v.fit_transform(items['desc'])
    #item_profile 是每个商品对应的 tf-idf 特征向量
    #（矩阵行数=商品数量，列数=特征数量）
    item_profile = x.todense()  # 得到稠密矩阵形式的商品画像特征
    print("商品数量:", items.shape[0])
    print("画像矩阵维度:", item_profile.shape)
    return item_profile
#生成用户画像
def create_user_item_matrix(df):
    #  选择用户ID和商品ID两列
    user_item_df = df.select("reviewerID", "asin").distinct()

    #  给所有交互赋值1，表示用户访问/购买过该商品
    user_item_df = user_item_df.withColumn("rating", lit(1).cast(IntegerType()))

    # 构造用户-商品评分矩阵（稀疏格式）
    # 这里我们只生成DataFrame形式的稀疏矩阵（长格式）， Spark 推荐系统中ALS 算法需要。

    #  将用户和商品编码为数值索引
    #，方便后续用Spark MLlib算法（如ALS协同过滤）直接用数字索引。
    from pyspark.ml.feature import StringIndexer

    user_indexer = StringIndexer(inputCol="reviewerID", outputCol="userIndex").fit(user_item_df)
    item_indexer = StringIndexer(inputCol="asin", outputCol="itemIndex").fit(user_item_df)

    user_item_df = user_indexer.transform(user_item_df)
    user_item_df = item_indexer.transform(user_item_df)

    #返回用户-商品评分长格式表，包含数值索引和rating列
    return user_item_df.select("userIndex", "itemIndex", "rating")
def PersonalizedRecom(request):
    #获取目录，循环输出文件名
    dir="hdfs:///amazon/"

    #获取文件
    df=getJsonData()
    #处理数据
        #生成用户画像
    matrix_df = create_user_item_matrix(df)
    #显示结果
    #matrix_df.show(10, truncate=False)
    #结果是userIndex|itemIndex|rating|二维数组
    
    #生成商品画像
    item_profile = create_item_profile(df)

    #用 ALS 模型生成推荐结果
    #   1. 生成推荐引擎模型。
    #   2. 推荐排名前 N 的推荐
    #推荐结果保存为 JSON/CSV
    return JsonResponse({'msg':'ok'})
