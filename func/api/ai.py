import json

# result 变量包含实际的换行符
result = '''{"title": "2024 欧洲杯，狂欢盛宴
，赢享期待","article": "
**2024 欧洲杯，足球盛宴，万众期待**"}'''

result = result.replace('\n', '\\n')
# 将字符串解析为字典

data = json.loads(result)
print(data)

print(json.dumps(data, indent=4, ensure_ascii=False))
