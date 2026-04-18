

import pandas as pd
import numpy as np

from xgboost import XGBClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score


# ===============================
# Step 1: Load Data
# ===============================
df = pd.read_csv("mining_data.csv")

# 必须包含字段：
# mine_id, year, production, ndvi_mean, backscatter_db, mining_area, label


# ===============================
# Step 2: Feature Engineering
# ===============================
df = df.sort_values(['mine_id', 'year'])

# ---- Production ----
df['prod_norm'] = df.groupby('year')['production'].transform(
    lambda x: (x - x.min()) / (x.max() - x.min())
)
df['prod_change'] = df.groupby('mine_id')['production'].pct_change().fillna(0)

# ---- Human activity ----
df['area_change'] = df.groupby('mine_id')['mining_area'].diff().fillna(0)

# ---- Surface change (SAR) ----
df['backscatter_change'] = df.groupby('mine_id')['backscatter_db'].diff().fillna(0)

# ---- Ecological condition ----
df['ndvi_change'] = df.groupby('mine_id')['ndvi_mean'].diff().fillna(0)


# ===============================
# Step 3: Prepare Training Data
# ===============================
features = [
    'prod_norm',
    'prod_change',
    'area_change',
    'backscatter_change',
    'ndvi_mean',
    'ndvi_change'
]

# 标签编码
le = LabelEncoder()
df['label_encoded'] = le.fit_transform(df['label'])

X = df[features]
y = df['label_encoded']

# 划分训练测试集
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)


# ===============================
# Step 4: Train XGBoost Model
# ===============================
model = XGBClassifier(
    n_estimators=300,
    max_depth=5,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    eval_metric='mlogloss',
    random_state=42
)

model.fit(X_train, y_train)


# ===============================
# Step 5: Model Evaluation
# ===============================
y_pred = model.predict(X_test)

print("Accuracy:", accuracy_score(y_test, y_pred))
print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=le.classes_))


# ===============================
# Step 6: Predict All Samples
# ===============================
df['pred'] = model.predict(X)
df['pred_label'] = le.inverse_transform(df['pred'])

# 保存结果
df.to_csv("mining_classification_result.csv", index=False)

print("\nClassification finished. Results saved.")

