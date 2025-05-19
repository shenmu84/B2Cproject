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

#生成用户-商品评分矩阵
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
def recom(df,user_profile, item_profile):
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
        #生成用户画像
    matrix_df = create_user_item_matrix(df)
    #显示结果
    #matrix_df.show(10, truncate=False)
    #结果是userIndex|itemIndex|rating|二维数组
    
    #生成商品画像
    item_profile = create_item_profile(df)
#TODO 没检察
    #用 ALS 模型生成推荐结果
    #   1. 生成推荐引擎模型。
    #   2. 推荐排名前 N 的推荐
    #推荐结果保存为 JSON/CSV
    return JsonResponse({'msg':'ok'})
