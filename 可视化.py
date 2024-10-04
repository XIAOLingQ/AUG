import pandas as pd
import matplotlib.pyplot as plt

# 读取数据文件
file_path = '数据汇总表.xlsx'
data = pd.read_excel(file_path)

# 删除汇总行，并重命名列
data_filtered = data[data['Unnamed: 0'] != '汇总']
data_filtered.columns = ['姓名', '有效', '无效', '汇总']

# 使用英文名称替换中文名称
name_mapping = {
    '朱诗雨': 'Zhu Shiyu',
    '袁瑛凯': 'Yuan Yingkai',
    '陈億': 'Chen Yi',
    '张一淼': 'Zhang Yimiao'
}
data_filtered['姓名'] = data_filtered['姓名'].replace(name_mapping)

# 绘制堆叠柱状图
plt.figure(figsize=(10, 6))
plt.bar(data_filtered['姓名'], data_filtered['有效'], label='有效工作量', color='b')
plt.bar(data_filtered['姓名'], data_filtered['无效'], bottom=data_filtered['有效'], label='无效工作量', color='r')

# 设置英文标签和标题
plt.xlabel('Name')
plt.ylabel('Workload')
plt.title('Effective and Ineffective Workload Distribution')
plt.xticks(rotation=45)
plt.legend()

# 显示图表
plt.tight_layout()
plt.show()
