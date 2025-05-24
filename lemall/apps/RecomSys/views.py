import json
from random import random

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
def get_info_from_asin(asin):
    redis_cli = get_redis_connection('recommend')
    redis_key=f"asin:{asin}"
    #如果有直接拿
    info_json = redis_cli.get(redis_key)
    if info_json:
        info = json.loads(info_json)
    #没有再向亚马逊拿
    else:
        title = get_title_by_asin_selenium(asin)
        if "推荐商品" in title:
            # 抓取失败，返回基础信息但不缓存
            return {
                'asin': asin,
                'title': title,
                'image': f"https://images-na.ssl-images-amazon.com/images/P/{asin}.jpg",
                'url': f"https://www.amazon.com/dp/{asin}",
            }
        else:
            info={
                'asin': asin,
                'title': title,
                'image': f"https://images-na.ssl-images-amazon.com/images/P/{asin}.jpg",
                'url': f"https://www.amazon.com/dp/{asin}",
            }
            #存入redis
            # 存入 Redis，设置缓存时间（例如 24 小时）
            redis_cli.setex(redis_key, 3600*24*14, json.dumps(info))
    return info
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
        #从redis中直接找
        data.append(get_info_from_asin(asin))
    return JsonResponse({'recommendations': data})

#爬虫爬取标题名字
import requests
from django.http import JsonResponse
from django_redis import get_redis_connection
import json
from selenium import webdriver

from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time

def get_title_by_asin_selenium(asin):
    url = f"https://www.amazon.com/dp/{asin}"

    # 配置 Chrome options
    options = Options()

    # 更真实的 user-agent
    user_agent = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36")
    options.add_argument(f'user-agent={user_agent}')

    # 更接近真实用户行为
    options.add_argument('--start-maximized')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--disable-infobars')
    options.add_argument('--disable-extensions')
    options.add_argument('--no-sandbox')
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)

    # 重要：禁用自动化特征
    options.add_argument('--disable-dev-shm-usage')
    # 指定 chromedriver 路径（如果不在 PATH 中）
    service = Service("/home/B2Cproject/lemall/apps/RecomSys/chromedriver-linux64")

    import undetected_chromedriver as uc
    #模拟真实 Headers
    options = uc.ChromeOptions()
    options.add_argument(f'user-agent={user_agent}')
    # 其他参数同上...

    driver = uc.Chrome(options=options)

    try:
        print(f"访问 {url}")
        driver.get(url)

        time.sleep(random.uniform(3, 5))

        # 检查是否遇到验证码
        if "captcha" in driver.page_source.lower():
            print("⚠️ 检测到验证码页面，终止抓取")
            return f"推荐商品 {asin[-4:]}"

        # 获取标题
        try:
            title_element = driver.find_element(By.ID, "productTitle")
            title = title_element.text.strip()
            return title
        except NoSuchElementException:
            print("❌ 未找到商品标题元素")
            return f"推荐商品 {asin[-4:]}"
    except TimeoutException:
        print("请求超时")
        return f"推荐商品 {asin[-4:]}"
    except Exception as e:
        print(f"抓取出错：{e}")
        return f"推荐商品 {asin[-4:]}"
    finally:
        driver.quit()


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
    redis_cli.setex(redis_key, 3600*24*14, json.dumps(valid_asins))  # 设置1个星期过期3600*24*7
    return valid_asins

