import xarray as xr
import rioxarray
import os
import os


# === 1. 输入与输出路径 ===
input_nc = r"G:\ndvi\2010_0106.nc4"
output_tif = r"G:\ndvi\cl\2010_0106.tif"
print(os.path.exists(input_nc))

print("🔍 正在读取 NetCDF 文件...")
ds = xr.open_dataset(input_nc)

# === 2. 打印基本信息 ===
print("\n=== 🗂 数据集总体信息 ===")
print(ds)

print("\n=== 📏 维度信息 ===")
for dim, size in ds.dims.items():
    print(f"  - {dim}: {size}")

print("\n=== 📊 数据变量 ===")
for var in ds.data_vars:
    print(f"  - {var} → {ds[var].attrs.get('long_name', '无描述')}")

print("\n=== 🌍 坐标变量（前5个值） ===")
for coord in ds.coords:
    try:
        print(f"  - {coord}: {ds[coord].values[:5]}")
    except Exception:
        print(f"  - {coord}: (非数值坐标)")

# === 3. 自动识别 NDVI 变量 ===
ndvi_var = None
for var in ds.data_vars:
    if "ndvi" in var.lower():
        ndvi_var = var
        break

if ndvi_var is None:
    ndvi_var = list(ds.data_vars.keys())[0]
    print(f"\n⚠️ 未找到明显名为 NDVI 的变量，默认使用第一个变量: {ndvi_var}")
else:
    print(f"\n✅ 检测到 NDVI 变量: {ndvi_var}")

ndvi = ds[ndvi_var]

# === 4. 若存在时间维度，仅导出第一个时间片 ===
if "time" in ndvi.dims:
    print(f"\n🕒 数据包含时间维度，共 {len(ndvi['time'])} 个时间点。")
    print("前5个时间点：", ndvi["time"].values[:5])
    ndvi = ndvi.isel(time=0)
    print("→ 已选择第一个时间片导出。")

# === 5. 添加投影信息（假设为 WGS84，经纬度坐标） ===
ndvi = ndvi.rio.write_crs("EPSG:4326", inplace=True)

# === 6. 导出为 GeoTIFF ===
os.makedirs(os.path.dirname(output_tif), exist_ok=True)
ndvi.rio.to_raster(output_tif)

print(f"\n🎉 已成功导出为 GeoTIFF 文件：{output_tif}")
