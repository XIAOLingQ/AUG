import json

# 加载数据集，指定编码为 utf-8
with open('2.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 遍历数据集并提取指令、输入和输出
for item in data:
    instruction = item['instruction']
    input_text = item['input']
    output_text = item['output']
    his = item['history']

    # 打印或处理数据
    print(f"Instruction: {instruction}")
    print(f"Input: {input_text}")
    print(f"Output: {output_text}")
    print(f"History: {his}")
    print("----")
