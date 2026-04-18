import os
import glob
import numpy as np
import xarray as xr
import rioxarray as rxr
from tqdm import tqdm

# ===============================
# 路径配置（⚠️已加统一规范）
# ===============================
input_folder = r"E:\LW3\cjjg"
output_folder = r"E:\LW3\上传"

# 创建输出目录
os.makedirs(output_folder, exist_ok=True)

# ===============================
# 获取 TIFF 文件
# ===============================
tif_files = glob.glob(os.path.join(input_folder, "*.tif")) + \
            glob.glob(os.path.join(input_folder, "*.tiff"))

print(f"共找到 {len(tif_files)} 个 TIFF 文件，开始转换...\n")

# ===============================
# 批量转换
# ===============================
for tif_path in tqdm(tif_files, desc="转换进度"):

    try:
        print(f"\n▶ 正在处理: {tif_path}")

        # 读取 TIFF
        da = rxr.open_rasterio(tif_path)

        # 如果是多波段，只保留第1波段
        if "band" in da.dims:
            da = da.squeeze("band", drop=True)

        # 数据类型优化
        da = da.astype(np.float32)

        # 转为 Dataset
        ds = da.to_dataset(name="variable")

        # 输出文件名
        filename = os.path.basename(tif_path)
        out_name = os.path.splitext(filename)[0] + ".nc"
        out_path = os.path.join(output_folder, out_name)

        print(f"   输出路径: {out_path}")

        # ===============================
        # NetCDF 压缩设置
        # ===============================
        encoding = {
            "variable": {
                "zlib": True,
                "complevel": 4,
                "dtype": "float32"
            }
        }

        # ===============================
        # 写入 NetCDF（关键修复）
        # ===============================
        ds.to_netcdf(
            out_path,
            encoding=encoding,
            engine="netcdf4"
        )

        # ===============================
        # ✔ 强制验证是否生成
        # ===============================
        if os.path.exists(out_path):
            size_mb = os.path.getsize(out_path) / 1024 / 1024
            print(f"✔ 成功生成: {out_name} ({size_mb:.2f} MB)")
        else:
            raise RuntimeError(f"❌ 文件未生成: {out_path}")

    except Exception as e:
        print(f"\n❌ 处理失败: {tif_path}")
        print("错误信息:", e)

print("\n🎉 所有文件处理完成！")