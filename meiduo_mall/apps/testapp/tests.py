from django.test import TestCase

# Create your tests here.

import pandas as pd
import gzip
import json

def parse(path):
    g = gzip.open(path, 'rb')
    for l in g:
        yield json.loads(l)

def getDF(path):
    i = 0
    df = {}
    for d in parse(path):
        df[i] = d
        i += 1
    return pd.DataFrame.from_dict(df, orient='index')

# df = getDF('/home/B2Cproject/meiduo_mall/static/ALiECS/Appliances_5.json.gz')
# print(df)
first_line = next(parse('/home/B2Cproject/meiduo_mall/static/ALiECS/Home_and_Kitchen_5.json.gz'))
print("第一行数据:", first_line)

# 打印第一行数据的所有字段名
print("字段名（标题）:", list(first_line.keys()))