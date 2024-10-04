import json

# 打开并读取1.json文件
with open('2.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# 为每个对象添加ID，并修改'system'字段
for index, item in enumerate(data):
    item['id'] = index + 1  # 从1开始编号
    item['system'] = "需求建模使用plantuml格式"  # 修改'system'字段
    item['input'] = "需求分析，需求建模，plantuml格式画uml图，uml建模"


# 将修改后的数据写回1.json文件
with open('2.json', 'w', encoding='utf-8') as file:
    json.dump(data, file, ensure_ascii=False, indent=4)

print("ID和system字段已成功添加和修改！")
