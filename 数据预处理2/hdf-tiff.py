import os
from osgeo import gdal
import rioxarray

# =========================
# 1️⃣ 输入与输出路径
# =========================
input_hdf = r"G:\ndvi\MOD13.hdf"  # 修改为你的 HDF 文件路径
output_tif = r"G:\ndvi\cl\MOD13_NDVI.tif"

print(f"文件存在: {os.path.exists(input_hdf)}")
os.makedirs(os.path.dirname(output_tif), exist_ok=True)

# =========================
# 2️⃣ 使用 GDAL 列出 HDF 子数据集
# =========================
hdf_ds = gdal.Open(input_hdf)
subdatasets = hdf_ds.GetSubDatasets()

print("\n=== HDF 文件子数据集（SDS）列表 ===")
for idx, (sds_name, desc) in enumerate(subdatasets):
    print(f"{idx+1}. Name: {sds_name}")
    print(f"   Description: {desc}")

# =========================
# 3️⃣ 找到 NDVI SDS（名字包含 'NDVI'）
# =========================
ndvi_sds_name = None
for sds_name, desc in subdatasets:
    if "NDVI" in sds_name.upper():
        ndvi_sds_name = sds_name
        break

if ndvi_sds_name is None:
    raise ValueError("⚠️ 未找到 NDVI SDS，请检查文件")

print(f"\n✅ 检测到 NDVI SDS: {ndvi_sds_name}")

# =========================
# 4️⃣ 用 rioxarray 打开 NDVI SDS
# =========================
ndvi = rioxarray.open_rasterio(ndvi_sds_name)

# 如果存在时间维度，仅取第一个时间片
if "time" in ndvi.dims:
    print(f"🕒 数据包含时间维度，共 {len(ndvi['time'])} 个时间点")
    ndvi = ndvi.isel(time=0)
    print("→ 已选择第一个时间片导出")

# =========================
# 5️⃣ 添加投影信息（MODIS原始投影可用 EPSG:4326 近似地理坐标）
# =========================
ndvi = ndvi.rio.write_crs("EPSG:4326", inplace=True)

# =========================
# 6️⃣ 导出为 GeoTIFF
# =========================
ndvi.rio.to_raster(output_tif)
print(f"\n🎉 已成功导出 GeoTIFF: {output_tif}")
