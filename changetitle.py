import json
import os
import re

paths = [path for path in os.walk('./out')][0][2]
results = []

for path in paths:
    title = re.findall(r'^out_\d{14}(.*)', path)[0]
    result = {}
    with open('./out/' + path, 'r', encoding='utf-8') as f:
        per = f.read()
        raw = json.loads(per)
        result[title] = raw['测试']
        results.append(result)

with open('all_results.json', 'w+', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False)
