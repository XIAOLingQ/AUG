import json
dir = 'total.json'
# 打开并读取 total.json 文件
with open(dir, 'r', encoding='utf-8') as file:
    data = json.load(file)

# 为每个对象添加 ID，并修改 'system' 和 'input' 字段
for index, item in enumerate(data):
    item['id'] = index + 1  # 从1开始编号
    item['system'] = "需求建模使用plantuml格式"  # 修改 'system' 字段
    item['input'] = "需求分析，需求建模，plantuml格式画uml图，uml建模"

    # 如果 'history' 字段不存在，则添加
    if 'history' not in item:
        item['history'] = []  # 添加一个空列表作为 history 字段

# 将修改后的数据写回 total.json 文件
with open(dir, 'w', encoding='utf-8') as file:
    json.dump(data, file, ensure_ascii=False, indent=4)

print("ID、system 和 history 字段已成功添加和修改！")
