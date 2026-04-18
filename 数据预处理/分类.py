# -*- coding: utf-8 -*-
import os
import shutil

# 输入文件夹路径（包含 TIFF 文件）
input_folder = r"G:\xlunwen\sy\3.impact_data\tiff7"  # 替换为你的输入文件夹路径

# 输出文件夹路径（保存分类后的 TIFF 文件）
output_folder = r"G:\xlunwen\sy\3.impact_data\tiff8"  # 替换为你的输出文件夹路径

# 检查输出文件夹是否存在，不存在则创建
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# 获取输入文件夹中的所有文件
files = [f for f in os.listdir(input_folder) if f.endswith('.tif')]

# 打印找到的文件数量
print(f"找到 {len(files)} 个 TIFF 文件")

# 遍历每个文件
for file_name in files:
    # 提取文件名的最后四位数字
    file_suffix = file_name[-8:-4]  # 假设文件名格式类似于 "example_2020.tif"

    # 如果最后四位不是数字，跳过该文件
    if not file_suffix.isdigit():
        print(f"跳过文件：{file_name}，原因：最后四位不是数字")
        continue

    # 根据文件名后四位创建分类文件夹
    category_folder = os.path.join(output_folder, file_suffix)
    if not os.path.exists(category_folder):
        os.makedirs(category_folder)

    # 移动文件到对应的分类文件夹
    source_path = os.path.join(input_folder, file_name)
    destination_path = os.path.join(category_folder, file_name)

    shutil.move(source_path, destination_path)
    print(f"已将文件 {file_name} 移动到 {category_folder}")

print("文件分类完成！")
