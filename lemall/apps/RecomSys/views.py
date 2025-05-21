from django.http import JsonResponse
from pyspark.sql.functions import col
import json
import pandas as pd
from pyspark.sql import functions as F
from pyspark.sql.functions import lit, col, when
from numpy import dot, linalg
import numpy as np
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lit
from pyspark.sql.types import IntegerType
from apps.RecomSys.spark_utils import get_spark_session
#fileName="hdfs:///amazon/AMAZON_FASHION_5.json.gz"
fileName="hdfs:///amazon/Kindle_Store_5.json.gz"
'''
css复制编辑[ HDFS 上的 JSON.GZ 文件 ]
        ↓（PySpark 读取）
[ Spark ALS 模型训练与推荐 ]
        ↓
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


#PySpark构建稠密用户-商品二值矩阵代码（行用户，列商品,0/1有无购买)
from pyspark.sql.functions import col, when, lower, lit
from functools import reduce

def create_user_item_matrix(df):
    # 1. 过滤出有评分的记录
    user_item_df = df.select("reviewerID", "asin", "overall", "verified", "reviewText", "vote")
    # 2. 转换 vote 为数值
    user_item_df = user_item_df.withColumn("vote", col("vote").cast("int")).fillna(0, ["vote"])
    # 3. 评论内容中是否包含正向词
    positive_words = ["great", "excellent", "amazing", "love", "good", "perfect", "awesome"]
    contains_positive = reduce(lambda acc, word: acc | lower(col("reviewText")).contains(word),
                               positive_words[1:],
                               lower(col("reviewText")).contains(positive_words[0]))
    user_item_df = user_item_df.withColumn("has_positive_words", when(contains_positive, 1.0).otherwise(0.0))
    # 4. 已验证购买：True -> 1.0，False -> 0.8
    user_item_df = user_item_df.withColumn(
        "verified_weight", when(col("verified") == True, 1.0).otherwise(0.8)
    )
    # 5. vote 加权（越多人觉得评论有帮助越可信）
    user_item_df = user_item_df.withColumn("vote_weight", when(col("vote") > 0, 1 + col("vote") / 10).otherwise(1.0))
    # 6. 综合喜爱程度评分（
    user_item_df = user_item_df.withColumn(
        "preference_score",
        col("overall") * col("verified_weight") * (1 + 0.2 * col("has_positive_words")) * col("vote_weight")
    )
    # 7. 最终评分表：只保留有实际交互记录的 user-item 对
    user_item_matrix = user_item_df.groupBy("reviewerID").pivot("asin").agg(F.first("preference_score"))

    return user_item_matrix

from pyspark.sql.functions import col, coalesce, lit, concat_ws

#创建商品画像
def create_item_profile(df):
    # 只保留 asin 不为空的记录，选取需要的列
    items = df.filter(col("asin").isNotNull()).select("asin", "style", "summary")

    # style 结构体字段名，带冒号的字段名用反引号括起来
    fields = ["Color:", "Design:", "Flavor:", "Scent Name:", "Size:", "Style Name:"]

    # 处理 style 中字段，防止null
    style_fields = [coalesce(col(f"style.{field}"), lit('')) for field in fields]

    # 拼接 style 字段字符串
    style_str = concat_ws(" ", *style_fields)

    # 处理 summary 空值
    summary_str = coalesce(col("summary"), lit(''))

    # 新增 desc 列，拼接 style + summary
    items = items.withColumn("desc", concat_ws(" ", style_str, summary_str))

    # 去重和排序
    items = items.dropDuplicates(["asin"]).orderBy("asin")

    # 转成 Pandas DataFrame 用于 sklearn 处理
    items_pd = items.select("asin", "desc").toPandas()
    #sklearn 的 TfidfVectorizer 只能在本地运行，且要求数据是 Pandas 或类似结构，不能直接用 Spark DataFrame。
    # sklearn TfidfVectorizer 提取文本特征
    from sklearn.feature_extraction.text import TfidfVectorizer

    v = TfidfVectorizer(stop_words="english", max_features=100, ngram_range=(1, 3), sublinear_tf=True)
    x = v.fit_transform(items_pd['desc'])

    item_profile = x.todense()
    # 测试
    # print("商品数量:", items_pd.shape[0])
    # print("画像矩阵维度:", item_profile.shape)
    return item_profile

#创建用户画像
def create_user_profile(df,user_item_matrix,item_profile):
    #  把 Spark DataFrame 转成 pandas，再转 numpy 矩阵
    user_item_pd = user_item_matrix.toPandas().fillna(0).set_index('reviewerID')  # 以 reviewerID 为索引
    ratmat = user_item_pd.values  # numpy ndarray

    # 计算用户画像（user_profile）
    #    先点乘，再做归一化（L2范数）
    user_profile = dot(ratmat, item_profile) / (
                linalg.norm(ratmat, axis=1)[:, None] * linalg.norm(item_profile, axis=0)[None, :])

    # 处理归一化分母可能为0的情况
    user_profile = np.nan_to_num(user_profile)
    #  返回用户画像矩阵
    print("用户画像矩阵 shape:", user_profile.shape)
    return user_profile

def recom(df,user_profile, item_profile,k=10):
        #计算用户画像与商品画像之间的余弦相似度
        #用 user_profile（U × F） 与 item_profile.T（F × I）相乘得到一个用户对所有商品的评分预测矩阵（U × I）：
        # item_profile 是 (I × F)，转置后为 (F × I)
        sim_matrix = dot(user_profile, item_profile.T)  # 得到 (U × I) 预测矩阵
        # 如果数据稀疏且大，避免直接计算所有用户-商品对的评分也可以采用分批计算
        sim_matrix = np.nan_to_num(sim_matrix)
        print("相似度矩阵 shape:", sim_matrix.shape)
        #Top-K 推荐（每位用户只推荐前 K 个商品）
        binary_pred = np.zeros_like(sim_matrix)
        for i in range(sim_matrix.shape[0]):
            top_k_idx = np.argsort(sim_matrix[i])[-k:]  # 取分数最高的 k 个商品索引
            binary_pred[i, top_k_idx] = 1
        return binary_pred


def PersonalizedRecom(request):
    #获取目录，循环输出文件名
    dir="hdfs:///amazon/"

    #获取文件
    df=getJsonData()
    #处理数据
        #生成用户-商品矩阵
    user_item_matrix = create_user_item_matrix(df)
    print("用户商品矩阵")
    print(type(user_item_matrix))
    user_item_matrix.show(10)
    #显示结果
    #matrix_df.show(10, truncate=False)
    #结果是userIndex|itemIndex|rating|二维数组

    #生成商品画像
    item_profile = create_item_profile(df)
    # print("生成商品画像")
    # print(pd.DataFrame(item_profile).head(4))

    #生成用户画像
    user_profile=create_user_profile(df,user_item_matrix,item_profile)
    print("生成用户画像")
    print(pd.DataFrame(user_profile).head(10))
#TODO 没检察
    #用 ALS 模型生成推荐结果
    #   1. 生成推荐引擎模型。
    binary_pred=recom(df,user_profile,item_profile)
    print(binary_pred.head(10))
    #   2. 推荐排名前 N 的推荐
    #推荐结果保存为 JSON/CSV
    return JsonResponse({'msg':'ok'})
