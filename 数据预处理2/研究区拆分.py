# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import arcpy
import os

# ================================
# 输入与输出路径
# ================================
input_shp = r"G:\论文3矿产资源与碳储量\数据收集\sy\Export_Output_3.shp"
output_folder = r"G:\论文3矿产资源与碳储量\数据收集\sy\shp"

# ================================
# 创建输出文件夹
# ================================
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# ================================
# 获取要素总数
# ================================
count_result = arcpy.GetCount_management(input_shp)
total_count = int(count_result.getOutput(0))
print(u"总要素数: {}".format(total_count))

# ================================
# 设定拆分份数
# ================================
split_num = 20
features_per_part = total_count / split_num
remainder = total_count % split_num
print(u"平均每份约 {} 个要素".format(features_per_part))

# ================================
# 读取所有要素
# ================================
with arcpy.da.SearchCursor(input_shp, ["OID@", "SHAPE@"]) as cursor:
    features = [row for row in cursor]

# ================================
# 自动识别 FID / OBJECTID 字段
# ================================
try:
    oid_field = arcpy.Describe(input_shp).OIDFieldName
    if oid_field is None or oid_field == "":
        oid_field = "FID"
except:
    oid_field = "FID"

print(u"主键字段为: {}".format(oid_field))

# ================================
# 拆分并保存
# ================================
start = 0
for i in range(split_num):
    end = start + features_per_part
    if i < remainder:  # 分配余数
        end += 1

    part_features = features[start:end]
    start = end

    if len(part_features) == 0:
        continue

    out_name = "split_{}.shp".format(i + 1)
    out_path_folder = output_folder
    out_path = os.path.join(output_folder, out_name)

    print(u"正在创建第 {}/{} 个文件: {}".format(i + 1, split_num, out_path))

    # ✅ 创建空 shapefile
    arcpy.CreateFeatureclass_management(
        out_path_folder,
        out_name,
        arcpy.Describe(input_shp).shapeType,
        spatial_reference=arcpy.Describe(input_shp).spatialReference
    )

    # 获取原字段（排除系统字段）
    fields = [f.name for f in arcpy.ListFields(input_shp) if f.type not in ("OID", "Geometry")]

    # 添加字段
    for f in fields:
        field = arcpy.ListFields(input_shp, f)[0]
        arcpy.AddField_management(out_path, field.name, field.type, field.precision,
                                  field.scale, field.length, field.aliasName,
                                  field.isNullable, field.required, field.domain)

    # 插入数据
    with arcpy.da.InsertCursor(out_path, fields + ["SHAPE@"]) as icursor:
        for row in part_features:
            fid, shape = row
            where_clause = "{} = {}".format(oid_field, fid)
            cursor = arcpy.da.SearchCursor(input_shp, fields, where_clause)
            vals = cursor.next()
            icursor.insertRow(list(vals) + [shape])
            del cursor

print(u"✅ 拆分完成！共生成 {} 个文件，输出路径：{}".format(split_num, output_folder))
