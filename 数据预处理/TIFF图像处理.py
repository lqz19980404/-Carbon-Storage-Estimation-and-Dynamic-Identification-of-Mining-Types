import os
import numpy as np
import rasterio
import pandas as pd


# 将图像中的空值替换为0，并打印空值的数量
def replace_nans_with_zero(tiff_path, output_path):
    with rasterio.open(tiff_path) as src:
        # 读取图像数据
        image = src.read(1)  # 读取单波段数据

        # 获取当前图像的nodata值
        nodata_value = src.nodata

        # 如果图像中有nodata值，统计原始图像中的nodata数量
        original_nan_count = np.isnan(image).sum()

        if nodata_value is not None:
            # 将nodata值替换为0
            image[image == nodata_value] = 0
            print(f"图像中的 nodata 值 {nodata_value} 已替换为 0")

        # 替换空值（NaN）为 0
        image[np.isnan(image)] = 0

        # 统计修改后的 NaN 数量（应该为0）
        modified_nan_count = np.isnan(image).sum()

        # 打印原始和修改后的空值数量
        print(f"文件: {os.path.basename(tiff_path)}")
        print(f"  原始空值数量: {original_nan_count}")
        print(f"  修改后空值数量: {modified_nan_count}")

        # 获取原始文件的元数据
        metadata = src.meta

        # 如果nodata值为负数，通常是 float 类型，修改数据类型为浮动型（float32 或 float64）
        if nodata_value is not None:
            metadata.update(dtype=rasterio.float32)  # 使用浮动型保存
        else:
            metadata.update(dtype=rasterio.uint8)  # 其他情况下保存为 uint8

        # 保存修改后的图像
        with rasterio.open(output_path, 'w', **metadata) as dst:
            dst.write(image, 1)

        print(f"已处理并保存: {output_path}\n")

    # 计算并返回文件的最小值和最大值
    min_value = np.min(image)
    max_value = np.max(image)

    return min_value, max_value


# 批量处理文件夹中的 TIFF 文件并统计最值
def process_tiff_folder(input_folder, output_folder, summary_file):
    # 获取文件夹内所有的 TIFF 文件
    tiff_files = [f for f in os.listdir(input_folder) if f.endswith('.tif')]

    # 用于存储每个文件的最小值和最大值
    summary_data = []

    # 处理每个 TIFF 文件
    for tiff_file in tiff_files:
        input_tiff_path = os.path.join(input_folder, tiff_file)
        output_tiff_path = os.path.join(output_folder, tiff_file)

        # 确保输出文件夹存在
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # 调用替换空值的函数
        min_value, max_value = replace_nans_with_zero(input_tiff_path, output_tiff_path)

        # 将文件的最小值和最大值存储在 summary_data 中
        summary_data.append([tiff_file, min_value, max_value])

    # 将汇总数据保存为 CSV 文件
    df = pd.DataFrame(summary_data, columns=['FileName', 'MinValue', 'MaxValue'])
    df.to_csv(summary_file, index=False)

    print(f"汇总信息已保存为 CSV 文件: {summary_file}")
    print("所有TIFF文件处理完成！")


# 输入输出文件夹路径
input_folder = r"G:\xlunwen\sy\3.impact_data\TIF3"  # 输入文件夹路径
output_folder = r"G:\xlunwen\sy\3.impact_data\TIF4"  # 输出文件夹路径
summary_file = r"G:\xlunwen\sy\3.impact_data\TIF4/summary.csv"  # 保存汇总信息的 CSV 文件路径

# 处理文件夹中的所有 TIFF 文件并统计最值
process_tiff_folder(input_folder, output_folder, summary_file)
