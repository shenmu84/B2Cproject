import json

from django.http import JsonResponse
from django_redis import get_redis_connection
from pyspark import StorageLevel

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
    df = spark.read.json("hdfs:///output/cleaned_reviews")
    return df


#已经测试成功了，这个生成的推荐结果是
'''
{"recommendations": [{"asin": "B009SZFHP6",
 "title": "\u63a8\u8350\u5546\u54c1 FHP6", 
"image": "https://images-na.ssl-images-amazon.com/images/P/B009SZFHP6.jpg",
"url": "https://www.amazon.com/dp/B009SZFHP6"}
之后有十个}
'''
import requests
from PIL import Image
from io import BytesIO
#选出有效图片
def check_image_exists(url):
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            image = Image.open(BytesIO(response.content))
            # 可根据需要调整判定条件，比如尺寸过小认为是无效图
            if image.width < 50 or image.height < 50:
                return False
            return True
        return False
    except Exception:
        return False


def recommend(request):
    #id=30
    userID = request.user.id
    redis_cli = get_redis_connection('recommend')
    redis_key = f"user:{userID}:recommendations"
    data = redis_cli.get(redis_key)
    if data:
        asin_list = json.loads(data)
    else:
        asin_list=get_recommendations_for_user(userID)
    data = []
    for asin in asin_list:
        title = "test"  # 你可以替换成真正的标题逻辑
        data.append({
            'asin': asin,
            'title': title,
            'image':  f"https://images-na.ssl-images-amazon.com/images/P/{asin}.jpg",
            'url': f"https://www.amazon.com/dp/{asin}",
        })
    return JsonResponse({'recommendations': data})

#爬虫爬取标题名字
import requests
from bs4 import BeautifulSoup
from django.http import JsonResponse
from django_redis import get_redis_connection
import json
import time
import random


# ---------- 安全爬虫函数 ----------
def get_title_by_asin(asin):
    url = f"https://www.amazon.com/dp/{asin}"
    headers = {
        "User-Agent": random.choice([
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
        ]),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate",
        "Referer": "https://www.amazon.com/",
        "Connection": "keep-alive",
    }

    try:
        time.sleep(random.uniform(1.5, 3.0))
        response = requests.get(url, headers=headers, timeout=10)
        print(f"抓取 {asin} 状态码：{response.status_code}")
        print(response.text[:500])  # 打印前500字符内容看看是不是有验证码或跳转

        if response.status_code != 200:
            return f"推荐商品 {asin[-4:]}"

        soup = BeautifulSoup(response.text, 'html.parser')
        meta_title = soup.find('meta', attrs={'name': 'title'})
        if meta_title:
            return meta_title.get('content', f"推荐商品 {asin[-4:]}")

        title_tag = soup.find('h1', id='title')
        if title_tag:
            font_tag = title_tag.find('font')
            if font_tag:
                return font_tag.get_text(strip=True)
            return title_tag.get_text(strip=True)
        return f"推荐商品 {asin[-4:]}"
    except Exception as e:
        print(f"抓取 {asin} 标题失败: {e}")
        return f"推荐商品 {asin[-4:]}"


def get_recommendations_for_user(user_id):
    from pyspark.sql.functions import col
    df = getJsonData()
    # 提取有用列并清洗数据
    ratings = df.select("reviewerID", "asin", "overall") \
                .dropna() \
                .filter(col("overall") > 0).persist(StorageLevel.MEMORY_AND_DISK)


    #把 reviewerID 和 asin 映射成了整数型的 userIndex 和 itemIndex：
    #因为 ALS 模型要求输入是 整数型 的用户 ID 和商品 ID，为了节省内存并提高效率
    '''StringIndexer是分布式进行的，不会集中在单机处理；相比 Window + dense_rank 全局排序，占用资源少得多。'''
    # # 创建一个窗口，按照 reviewerID 排序
    # user_window = Window.partitionBy().orderBy("reviewerID")
    # item_window = Window.partitionBy().orderBy("asin")
    # # 通过 dense_rank() 给每个 reviewerID 编一个唯一的整数，从1开始，减1后从0开始
    # ratings = ratings.withColumn("userIndex", dense_rank().over(user_window) - 1)
    # ratings = ratings.withColumn("itemIndex", dense_rank().over(item_window) - 1)

    from pyspark.ml.feature import StringIndexer

    user_indexer = StringIndexer(inputCol="reviewerID", outputCol="userIndex")
    item_indexer = StringIndexer(inputCol="asin", outputCol="itemIndex")

    ratings = user_indexer.fit(ratings).transform(ratings)
    ratings = item_indexer.fit(ratings).transform(ratings)
    # 对 DataFrame 持久化缓存
    ratings.persist(StorageLevel.MEMORY_AND_DISK)
    # 提前保存一个“映射表”，记录 userIndex 和原始 reviewerID 的对应关系，itemIndex 和 asin 的对应关系
    # 先做映射表持久化
    user_mapping = ratings.select("reviewerID", "userIndex").distinct().persist(StorageLevel.MEMORY_AND_DISK)
    item_mapping = ratings.select("asin", "itemIndex").distinct().persist(StorageLevel.MEMORY_AND_DISK)


    #  构建 ALS 所需格式
    als_data = ratings.select(
        col("userIndex").cast("int"),
        col("itemIndex").cast("int"),
        col("overall").cast("float")
    ).persist(StorageLevel.MEMORY_AND_DISK)

    # 拆分训练与测试数据
    train_data, test_data = als_data.randomSplit([0.8, 0.2], seed=123)

    # 构建 ALS 模型
    als = ALS(
        userCol="userIndex",
        itemCol="itemIndex",
        ratingCol="overall",
        rank=8,#隐向量维度，越大越准但计算量更大
        maxIter=5,#迭代次数，越多越准确但也越慢
        regParam=0.2,
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
        20
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
    #选择5个有对应图片的asgin
    valid_asins = []
    for asin in asin_list:
        url = f"https://images-na.ssl-images-amazon.com/images/P/{asin}.jpg"
        if check_image_exists(url):
            valid_asins.append(asin)
            if len(valid_asins) == 5:
                break
    # 存入 Redis：key 为用户 ID，值为 JSON 列表
    redis_cli = get_redis_connection('recommend')
    redis_key = f"user:{user_id}:recommendations"
    #将 Python 列表序列化成字符串，Redis 只能存字符串
    redis_cli.setex(redis_key, 60, json.dumps(valid_asins))  # 设置1个星期过期3600*24*7
    return valid_asins

