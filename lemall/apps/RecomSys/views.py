from django.http import JsonResponse
from apps.RecomSys.spark_utils import get_spark_session
'''
原始数据 → 清洗 → 用户/商品映射 → ALS建模 → 训练 → 预测 → RMSE评估

训练好的模型
    ↓
model.recommendForAllUsers(N)  ➜  获取每个用户的 Top-N 推荐列表
    ↓
可选：用映射表还原为原始用户 ID 和商品 ID

'''

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, dense_rank,explode
from pyspark.sql.window import Window
from pyspark.ml.recommendation import ALS
from pyspark.ml.evaluation import RegressionEvaluator
# 调用你的推荐流程
def getJsonData():
    spark = get_spark_session()
    df = spark.read.json("hdfs:///amazon/output/cleaned_reviews.json.gz")
    return df


#已经测试成功了，这个生成的推荐结果是
'''
{"recommendations": [{"asin": "B009SZFHP6",
 "title": "\u63a8\u8350\u5546\u54c1 FHP6", 
"image": "https://images-na.ssl-images-amazon.com/images/P/B009SZFHP6.jpg",
"url": "https://www.amazon.com/dp/B009SZFHP6"}
之后有十个}
'''
def recommend(request):
    #id=30
    userID = request.user.id

    asin_list=get_recommendations_for_user(userID)
    data=[]
    for asin in asin_list[:10]:
        data.append({
            'asin': asin,
            'title': f"推荐商品 {asin[-4:]}",  # 可以从文件或数据库中取标题
            'image': f"https://images-na.ssl-images-amazon.com/images/P/{asin}.jpg",  # 图片链接格式
            'url': f"https://www.amazon.com/dp/{asin}",
        })
    return JsonResponse({'recommendations': data})

def get_recommendations_for_user(user_id):
    from pyspark.sql.functions import col
    df = getJsonData()
    # 提取有用列并清洗数据
    ratings = df.select("reviewerID", "asin", "overall") \
                .dropna() \
                .filter(col("overall") > 0)


    #把 reviewerID 和 asin 映射成了整数型的 userIndex 和 itemIndex：
    #因为 ALS 模型要求输入是 整数型 的用户 ID 和商品 ID，为了节省内存并提高效率
    # 创建一个窗口，按照 reviewerID 排序
    user_window = Window.partitionBy().orderBy("reviewerID")
    item_window = Window.partitionBy().orderBy("asin")
    # 通过 dense_rank() 给每个 reviewerID 编一个唯一的整数，从1开始，减1后从0开始
    ratings = ratings.withColumn("userIndex", dense_rank().over(user_window) - 1)
    ratings = ratings.withColumn("itemIndex", dense_rank().over(item_window) - 1)

    # 提前保存一个“映射表”，记录 userIndex 和原始 reviewerID 的对应关系，itemIndex 和 asin 的对应关系
    user_mapping = ratings.select("reviewerID", "userIndex").distinct()
    item_mapping = ratings.select("asin", "itemIndex").distinct()

    #  构建 ALS 所需格式
    als_data = ratings.select(
        col("userIndex").cast("int"),
        col("itemIndex").cast("int"),
        col("overall").cast("float")
    ).cache()

    # 拆分训练与测试数据
    train_data, test_data = als_data.randomSplit([0.8, 0.2], seed=123)

    # 构建 ALS 模型
    als = ALS(
        userCol="userIndex",
        itemCol="itemIndex",
        ratingCol="overall",
        rank=10,
        maxIter=10,
        regParam=0.1,
        coldStartStrategy="drop"
    )
    #用你提供的训练数据，让 ALS 模型学习“用户-商品”的评分规律，训练出一个可以进行推荐和预测的模型
    model = als.fit(train_data)
    # 预测与评估
    predictions = model.transform(test_data)

    evaluator = RegressionEvaluator(metricName="rmse", labelCol="overall", predictionCol="prediction")
    rmse = evaluator.evaluate(predictions)
    #RMSE 是 Root Mean Squared Error（均方根误差） 的缩写，是一种常用来衡量预测值与真实值之间差异的指标
    print(f"RMSE = {rmse}")
    #RMSE = 2.123718513970498
    # 已经训练好的模型: model

    #推荐给指定用户
    top_n_for_user = model.recommendForUserSubset(
        als_data.select("userIndex").distinct().filter(col("userIndex") == user_id),
        10
    )

    # 展开数组
    recommendation = top_n_for_user.select(
        col("userIndex"),
        explode("recommendations").alias("rec")
    ).select(
        col("userIndex"),
        col("rec.itemIndex").alias("itemIndex"),
        col("rec.rating")
    )
    recommendation_with_asin = recommendation.join(item_mapping, on="itemIndex", how="left")

    asin_list = [row['asin'] for row in recommendation_with_asin.select("asin").collect()]
    return asin_list

