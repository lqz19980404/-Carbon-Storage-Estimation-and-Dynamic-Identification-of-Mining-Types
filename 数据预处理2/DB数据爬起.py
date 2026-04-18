import ee
import pandas as pd
import math
import os

# =========================..0
# 配置参数0.
# =========0.......................................................================
PROJECT_ID = "ee-qingzhoulu528"  # ✅ 替换为你有权限的项目ID
START_YEAR = 2016
END_YEAR = 2017
SHAPEFILE_ASSET = 'projects/ee-qingzhoulu528/assets/split_6'  # 你的 shapefile GEE 路径
ORBIT_PASS = 'ASCENDING'
POLARIZATION = 'VV'
SCALE = 100
N_BATCH = 10  # 分批处理数量
OUTPUT_DIR = r"E:\GEE\6"
os.makedirs(OUTPUT_DIR, exist_ok=True)  # 确保输出目录存在

# =========================
# 初始化 Earth Engine
# =========================
try:
    ee.Initialize(project=PROJECT_ID)
except ee.EEException:
    print("Earth Engine 未登录，正在启动认证...")
    ee.Authenticate()
    ee.Initialize(project=PROJECT_ID)

print("✅ Earth Engine 初始化成功")

# =========================
# 读取 shapefile
# =========================
study_area = ee.FeatureCollection(SHAPEFILE_ASSET)

# =========================
# Sentinel-1 数据集
# =========================
s1 = (
    ee.ImageCollection('COPERNICUS/S1_GRD')
    .filterBounds(study_area)
    .filter(ee.Filter.eq('instrumentMode', 'IW'))
    .filter(ee.Filter.eq('orbitProperties_pass', ORBIT_PASS))
    .filter(ee.Filter.eq('resolution_meters', 10))
    .select(POLARIZATION)
)

# =========================
# 按年份循环计算
# =========================
feature_count = study_area.size().getInfo()
batch_size = math.ceil(feature_count / N_BATCH)

for year in range(START_YEAR, END_YEAR + 1):
    print(f"\n===== Year: {year} =====")

    start_date = ee.Date.fromYMD(year, 1, 1)
    end_date = ee.Date.fromYMD(year, 12, 31)

    # 添加 db 波段
    s1_year = s1.filterDate(start_date, end_date).map(
        lambda img: img.addBands(img.select(0).log10().multiply(10).rename('db'))
    )

    # 中位数影像
    median_db = s1_year.select('db').median()

    # 分批处理
    for i in range(N_BATCH):
        start = i * batch_size
        end = min(start + batch_size, feature_count)

        batch_fc = ee.FeatureCollection(study_area.toList(feature_count).slice(start, end)) \
            .map(lambda f: f.set('year', year))

        # 计算平均 db
        mean_db_batch = median_db.reduceRegions(
            collection=batch_fc,
            reducer=ee.Reducer.mean(),
            scale=SCALE,
            tileScale=4
        )

        # 转换为 Python 可用列表
        features = mean_db_batch.getInfo()["features"]
        batch_results = []
        for f in features:
            props = f["properties"]
            batch_results.append({
                "OBJECTID": props.get("OBJECTID"),
                "Shape_Area": props.get("Shape_Area"),
                "mean": props.get("mean", -999),
                "year": year
            })

        # 每批次保存 CSV
        batch_csv = os.path.join(OUTPUT_DIR, f"sy3_y{year}_batch{i+1}.csv")
        df = pd.DataFrame(batch_results)
        df.to_csv(batch_csv, index=False, encoding="utf-8-sig")

        # 打印进度和前10行数据
        print(f"Batch {i + 1}/{N_BATCH} processed, features: {len(features)}")
        print(f"Preview of batch CSV:\n{df.head(10)}")