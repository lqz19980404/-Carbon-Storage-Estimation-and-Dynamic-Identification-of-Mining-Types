import os
import rasterio
import numpy as np
import pandas as pd
from rasterio.warp import calculate_default_transform, reproject, Resampling
from rasterio import Affine
from rasterio.transform import from_origin

# 设置输入和输出路径
input_dir = r'G:\xlunwen\sy\3.impact_data\TIF2'  # 替换为输入目录路径
reference_tif = r'E:\xlwsy\impact2\cropped_evp2010.tif'  # 替换为参考 tif 文件路径
output_dir = r'G:\xlunwen\sy\3.impact_data\TIF3'  # 替换为输出目录路径
output_csv = r'G:\xlunwen\sy\3.impact_data\TIF3/summary.csv'  # 替换为保存汇总信息的 CSV 文件路径

# 读取参考 tiff 文件
with rasterio.open(reference_tif) as src_ref:
    ref_crs = src_ref.crs  # 获取参考投影
    ref_transform = src_ref.transform  # 获取参考的仿射变换
    ref_width = src_ref.width
    ref_height = src_ref.height
    ref_res = src_ref.res[0]  # 获取参考栅格分辨率

# 设置目标栅格分辨率为 3000 米
target_resolution = 3000  # 目标空间分辨率，单位为米

# 获取输入目录中的所有 TIFF 文件
tif_files = [f for f in os.listdir(input_dir) if f.endswith('.tif')]
tif_files.sort()  # 可以根据需要对文件排序

# 获取文件总数
total_files = len(tif_files)

# 用于存储新栅格的最小值和最大值的列表
summary_data = []

# 打印待处理的总文件数
print(f"总共需要处理 {total_files} 个 TIFF 文件")

# 遍历所有 tiff 文件
for i, tif_file in enumerate(tif_files, 1):
    input_tif_path = os.path.join(input_dir, tif_file)
    output_tif_path = os.path.join(output_dir, tif_file)

    with rasterio.open(input_tif_path) as src:
        # 计算参考投影和目标投影之间的变换
        transform, width, height = calculate_default_transform(
            src.crs, ref_crs, src.width, src.height, *src.bounds, resolution=(target_resolution, target_resolution)
        )

        # 创建输出的 tiff 文件
        with rasterio.open(output_tif_path, 'w', driver='GTiff', count=1, dtype='float32',
                           width=width, height=height, crs=ref_crs, transform=transform) as dst:
            # 重新投影并调整分辨率，同时确保输出与参考栅格对齐
            reproject(
                source=rasterio.band(src, 1),
                destination=rasterio.band(dst, 1),
                src_transform=src.transform,
                src_crs=src.crs,
                dst_transform=transform,
                dst_crs=ref_crs,
                resampling=Resampling.nearest  # 使用最近邻插值法进行重采样
            )

        # 计算新栅格的最小值和最大值
        with rasterio.open(output_tif_path) as new_tif:
            data = new_tif.read(1)  # 读取第一个波段
            min_value = np.min(data)
            max_value = np.max(data)

            # 将结果保存到 summary_data 中
            summary_data.append([tif_file, min_value, max_value])

    # 打印当前处理的文件进度
    print(f"已处理 {i}/{total_files} 个文件: {tif_file}")

# 将汇总数据保存到 CSV 文件
df = pd.DataFrame(summary_data, columns=['FileName', 'MinValue', 'MaxValue'])
df.to_csv(output_csv, index=False)

# 打印汇总保存完毕的提示
print(f"汇总信息已保存为 CSV 文件: {output_csv}")
