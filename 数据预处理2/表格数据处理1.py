import os
import pandas as pd

folder = r"G:\论文3矿产资源与碳储量\数据收集\bg\td"
files = [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith('.xlsx')]

if not files:
    raise FileNotFoundError(f"文件夹 {folder} 中没有找到 .xlsx 文件。")

merged_df = None

for file in files:
    df = pd.read_excel(file)
    filename = os.path.splitext(os.path.basename(file))[0]

    # 给除了 OBJECTID 的列加前缀（使用文件名）
    df = df.rename(columns={col: f"{filename}_{col}" for col in df.columns if col != "OBJECTID"})

    if merged_df is None:
        merged_df = df
    else:
        merged_df = pd.merge(merged_df, df, on="OBJECTID", how="outer")

output_file = os.path.join(folder, "merged_td.xlsx")
merged_df.to_excel(output_file, index=False)
print(f"✅ 合并完成！结果保存在：{output_file}")
