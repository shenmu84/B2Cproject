#!/usr/bin/env python3
import sys, json

for line in sys.stdin:
    try:
        record = json.loads(line)
        asin = record.get("asin")                       # 商品ID
        reviewerID = record.get("reviewerID")           # 评论者ID
        reviewText = record.get("reviewText")           # 评论内容
        overall = record.get("overall")                 # 打分
        unixTime = record.get("unixReviewTime")         # 时间戳

        # 如果字段完整
        if asin and reviewerID and reviewText and overall and unixTime:
            key = f"{reviewerID}_{asin}_{unixTime}"     # 构造唯一键
            print(f"{key}\t{json.dumps(record)}")        # 输出 key 和原始 JSON 数据
    except:
        continue
