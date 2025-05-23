#!/usr/bin/env python3
import sys

seen = set()
for line in sys.stdin:
    try:
        key, value = line.strip().split("\t", 1)
        if key not in seen:
            print(value)         # 输出原始 JSON
            seen.add(key)        # 标记这个评论已处理
    except:
        continue
