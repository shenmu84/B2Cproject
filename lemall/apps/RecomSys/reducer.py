#!/usr/bin/env python3
import sys
import json
prev_key = None
for line in sys.stdin:
    parts = line.strip().split('\t')
    if len(parts) != 3:
        continue
    key = f"{parts[0]}\t{parts[1]}"
    overall = parts[2]
    if key != prev_key:
        asin, reviewerID = parts[0], parts[1]
        print(json.dumps({
            "asin": asin,
            "reviewerID": reviewerID,
            "overall": float(overall)
        }))
        prev_key = key
