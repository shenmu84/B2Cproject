#!/usr/bin/env python3
import sys
import gzip
import json
def safe_parse(line):
    try:
        return json.loads(line)
    except Exception:
        return None
for line in sys.stdin:
    data = safe_parse(line)
    if not data:
        continue
    asin = data.get("asin")
    reviewerID = data.get("reviewerID")
    overall = data.get("overall")
    if asin and reviewerID and overall is not None:
        # 作为key去重用
        key = f"{asin}\t{reviewerID}"
        value = overall
        print(f"{key}\t{value}")
