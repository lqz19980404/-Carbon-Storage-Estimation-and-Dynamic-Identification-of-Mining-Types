import os
import numpy as np
import rasterio
import torch
import torch.nn as nn
import torch.nn.functional as F
from tqdm import tqdm

# =============================
# 基础配置
# =============================
YEARS = list(range(2015, 2021))  # 2015–2020

VAR_NAMES = ["agb", "rhu", "ndvi"]

TIFF_PARAMS = {
    "agb": {"vmin": 0, "vmax": 450},
    "rhu": {"vmin": 0, "vmax": 100},
    "ndvi": {"vmin": 0, "vmax": 9000},
}

PATCH_SIZE = (9, 9)
TARGET_MIN = 0
TARGET_MAX = 2000

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

MODEL_PATH = r"D:\论文3碳储量数据\sy\2010spatial normalization\npy9\xl\best_stt_model.pth"
OUTPUT_NPY = r"D:\论文3碳储量数据\sy\2010spatial normalization\npy9\stt_pred.npy"

BASE_PATH = r"D:\论文3碳储量数据\sy\2010spatial normalization"

# =============================
# 数据读取函数
# =============================
def read_tiff(path):
    with rasterio.open(path) as src:
        return src.read(1)

def filter_values(img, vmin, vmax):
    img = img.copy()
    img[(img < vmin) | (img > vmax)] = 0
    return img

def normalize(img, new_min=0, new_max=2000):
    old_min, old_max = img.min(), img.max()
    if old_max == old_min:
        return np.zeros_like(img)
    return (img - old_min) / (old_max - old_min) * (new_max - new_min) + new_min


# =============================
# 构建 2015–2020 时空数据
# =============================
def load_st_data():
    data = []

    for year in YEARS:
        yearly = []

        for var in VAR_NAMES:
            path = os.path.join(BASE_PATH, f"{var}{year}.tif")

            img = read_tiff(path)

            params = TIFF_PARAMS[var]
            img = filter_values(img, params["vmin"], params["vmax"])
            img = normalize(img, TARGET_MIN, TARGET_MAX)

            yearly.append(img)

        # [C, H, W]
        yearly = np.stack(yearly, axis=0)
        data.append(yearly)

    # [T, C, H, W]
    return np.stack(data, axis=0)


# =============================
# STT模型
# =============================
class STTModel(nn.Module):
    def __init__(self, in_channels=3, embed_dim=64, num_heads=4, depth=3):
        super().__init__()

        # 空间编码（CNN）
        self.spatial = nn.Conv2d(in_channels, embed_dim, 3, padding=1)

        # 时间Transformer
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=embed_dim,
            nhead=num_heads,
            batch_first=True
        )
        self.temporal = nn.TransformerEncoder(encoder_layer, num_layers=depth)

        # 输出层
        self.fc = nn.Sequential(
            nn.Linear(embed_dim, 32),
            nn.ReLU(),
            nn.Linear(32, 1)
        )

    def forward(self, x):
        # x: [B, T, C, H, W]
        B, T, C, H, W = x.shape

        x = x.view(B * T, C, H, W)

        # 空间特征
        x = self.spatial(x)  # [B*T, D, H, W]
        x = F.adaptive_avg_pool2d(x, 1).view(B, T, -1)  # [B, T, D]

        # 时间建模
        x = self.temporal(x)  # [B, T, D]

        # 时间聚合
        x = x.mean(dim=1)  # [B, D]

        return self.fc(x)


# =============================
# patch生成（时空版本）
# =============================
def generate_stt_patches(data, row_idx, patch_size=(9,9), target_cols=None):
    # data: [T, C, H, W]
    T, C, H, W = data.shape
    ph, pw = patch_size

    max_cols = target_cols if target_cols else W

    pad_rows = max(0, ph - (H - row_idx))
    pad_cols = max(0, max_cols - W)

    data_pad = np.pad(data, ((0,0),(0,0),(0,pad_rows),(0,pad_cols)))

    patches = []

    for j in range(0, data_pad.shape[3] - pw + 1):
        patch = data_pad[:, :, row_idx:row_idx+ph, j:j+pw]
        patches.append(patch)

    return np.array(patches, dtype=np.float32)


# =============================
# 推理函数
# =============================
def predict_stt(model, output_path):

    data = load_st_data()  # [T, C, H, W]

    T, C, H, W = data.shape
    results = []

    print(f"Total rows: {H}")

    for row_idx in tqdm(range(H), desc="Processing rows"):

        X_row = generate_stt_patches(data, row_idx, PATCH_SIZE)

        # [N, T, C, H, W]
        X_tensor = torch.tensor(X_row, dtype=torch.float32).to(DEVICE)

        with torch.no_grad():
            pred = model(X_tensor).cpu().numpy()

        results.append(pred)

        del X_tensor, X_row, pred
        torch.cuda.empty_cache()

    results = np.concatenate(results, axis=0)
    np.save(output_path, results)

    print("保存完成:", output_path)


# =============================
# 主程序
# =============================
if __name__ == "__main__":

    model = STTModel(in_channels=3).to(DEVICE)

    model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
    model.eval()

    predict_stt(model, OUTPUT_NPY)