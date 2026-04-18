# -*- coding: utf-8 -*-
import arcpy
import os

# 设置工作环境
arcpy.env.overwriteOutput = True

# 输入参数
input_folder = r"E:\LW3\jg2"  # 输入TIF文件夹路径
mask_file = r"E:\LW3\guo.shp"  # 掩膜文件路径（矢量或栅格）
output_folder = r"E:\LW3\cjjg"  # 输出文件夹路径
target_tif = r'E:\LW3\NDVI2020.tif'  # 对齐目标TIFF文件路径

# 检查输入路径
if not os.path.exists(input_folder):
    raise RuntimeError("输入文件夹不存在: {}".format(input_folder))
if not os.path.exists(target_tif):
    raise RuntimeError("目标栅格文件不存在: {}".format(target_tif))
if not os.path.exists(mask_file):
    raise RuntimeError("掩膜文件不存在: {}".format(mask_file))

# 创建输出文件夹
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# 临时文件夹（存放中间重采样文件）
temp_folder = os.path.join(output_folder, "temp")
if not os.path.exists(temp_folder):
    os.makedirs(temp_folder)

# 检查并启用 Spatial Analyst 扩展
if arcpy.CheckExtension("Spatial") == "Available":
    arcpy.CheckOutExtension("Spatial")
else:
    raise RuntimeError("Spatial Analyst 扩展不可用！")

# 获取目标栅格的空间参考和分辨率
target_raster = arcpy.Raster(target_tif)
target_sr = target_raster.spatialReference
target_cell_size = target_raster.meanCellWidth

# 遍历输入文件夹中的所有 TIF 文件
for file_name in os.listdir(input_folder):
    if file_name.lower().endswith(".tif") or file_name.lower().endswith(".tiff"):
        input_tif_path = os.path.join(input_folder, file_name)
        output_tif_path = os.path.join(output_folder, "cropped_" + file_name)
        temp_raster_path = os.path.join(temp_folder, "aligned_" + file_name)

        try:
            print("正在处理: {}".format(file_name))

            # 重采样到目标分辨率（硬盘临时文件）
            arcpy.Resample_management(
                in_raster=input_tif_path,
                out_raster=temp_raster_path,
                cell_size=target_cell_size,
                resampling_type="NEAREST"
            )
            aligned_raster = arcpy.Raster(temp_raster_path)

            # 执行掩膜裁剪
            cropped_raster = arcpy.sa.ExtractByMask(aligned_raster, mask_file)

            # 保存裁剪后的栅格
            cropped_raster.save(output_tif_path)
            print("成功裁剪并保存: {}".format(output_tif_path))

            # 删除临时重采样文件
            arcpy.Delete_management(temp_raster_path)

        except Exception as e:
            print("处理 {} 时出错: {}".format(file_name, e))

# 释放 Spatial Analyst 扩展
arcpy.CheckInExtension("Spatial")

print("所有文件处理完成！")
