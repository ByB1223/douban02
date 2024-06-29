import csv

# 读取数据文件并转换为列表
data = []
with open('d5', 'r', encoding='utf-8') as file:
    for line in file:
        # 假设字段之间使用空格分隔
        fields = line.strip().split('\t')  # 使用制表符分隔
        data.append(fields)

# 将数据写入CSV文件
with open('d5.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    # 写入表头
    writer.writerow(['国家', '数量'])
    # 写入数据
    writer.writerows(data)
print("CSV文件已生成。")
