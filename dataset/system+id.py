import json
import random

# 打开并读取 total.json 文件
dir = './total_3.json'
with open(dir, 'r', encoding='utf-8') as file:
    data = json.load(file)

s = ''

# 准备一些随机的评价语句
evaluation_statements = [
    "请对生成的图进行评价。",
    "请根据生成的图给出您的意见。",
    "对生成的图进行详细的评价。",
    "请对图的质量做出评价。",
    "根据图的内容，请进行打分。",
    "请检查图，并给出相关的评价。",
    "请对该图进行全面的评估。",
    "根据评估标准，请对图进行评分。",
    "请对生成的图表做出评价。",
    "请对这张图的质量和正确性进行评价。"
]

# 为每个对象添加 ID，并修改 'system' 和 'input' 字段
for index, item in enumerate(data):
    item["id"] = index + 1  # 从1开始编号
    item['system'] = "你是AUG需求助手，你的任务是协助开发者进行需求建模"  # 修改 'system' 字段

    # 随机选择一条评价语句
    item['input'] = random.choice(evaluation_statements)

    # 修改 'instruction' 字段
    item['instruction'] = "评分标准：• Completeness (完整性): 图表涵盖了所有需求的内容，并且具有足够的细节以便与潜在的利益相关者进行沟通。 • Correctness (正确性): 图表指定的行为与需求一致且连贯。 • Adherence to the standard (遵循标准): 图表在语法上是正确的（即，它可以被 PlanText6 解释），在语义上也是合理的（即，使用了适当的结构）。 • Degree of understandability (可理解度): 鉴于需求的复杂性，图表足够清晰，并且没有包含冗余内容。 • Terminological alignment (术语对齐): 生成的图表中使用的术语与需求中的术语一致。 根据用户提供的需求用户故事文档，生成相应的uml图，并根据提供的评估标准对生成的图进行评分。"

    # 如果 'history' 字段不存在，则添加
    if 'history' not in item:
        item['history'] = []  # 添加一个空列表作为 history 字段

# 将修改后的数据写回 total.json 文件
with open(dir, 'w', encoding='utf-8') as file:
    json.dump(data, file, ensure_ascii=False, indent=4)

print("ID、system、input 和 history 字段已成功添加和修改！")
