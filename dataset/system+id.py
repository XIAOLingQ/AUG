# 构建 evaluation_statements 列表，包含用户指定的评价语句以及一些额外的语句
import json
import random

evaluation_statements = [
    "我会根据五大标准进行打分：",
    "根据五大标准我进行如下分析：",
    "好的，我根据评价PlantUML的五大标准进行打分：",
    "结合五大标准，我对生成的UML图进行如下评价：",
    "我会使用五大标准为此需求进行评分：",
    "根据模型设计的完整性、清晰度、可维护性、扩展性和一致性进行打分：",
    "接下来，我根据五大标准对该UML图进行细致分析：",
    "按照五大评价标准进行评估，具体分析如下：",
    "我将根据五大标准逐一进行评价，评分如下：",
    "基于五大评价标准，我给出的分析结果如下："
]

# 打开并读取 total_3.json 文件
dir = './total_3.json'
with open(dir, 'r', encoding='utf-8') as file:
    data = json.load(file)

# 为每个对象添加 ID，并修改 'system' 和 'input' 字段
for index, item in enumerate(data):
    item["id"] = index + 1  # 从1开始编号
    # item['system'] = "你是AUG需求助手，你的任务是协助开发者进行需求建模;结合生成的UML图进行打分"  # 修改 'system' 字段

    # # 在 'input' 字段前随机添加评价语句
    # item['output'] = random.choice(evaluation_statements) + item['output']

    # # 如果 'history' 字段不存在，则添加空列表
    # if 'history' not in item:
    #     item['history'] = []

# 将修改后的数据写回 total_3.json 文件
with open(dir, 'w', encoding='utf-8') as file:
    json.dump(data, file, ensure_ascii=False, indent=4)

# 操作完成
"Modification complete. Data has been written back to the file."
