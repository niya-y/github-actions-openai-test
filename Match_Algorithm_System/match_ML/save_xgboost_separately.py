"""
XGBoost 모델을 여러 형식으로 저장 (ONNX 대신)
Azure에서 사용 가능한 형식들
"""

import pickle
import json
from pathlib import Path
import numpy as np
import pandas as pd
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split

# 경로 설정
BASE_DIR = Path("/Users/sangwon/Project/Sesac_class/bluedonulab-01/match_ML")
DATA_DIR = BASE_DIR / "data"
BEST_MODEL_DIR = BASE_DIR / "best_model"

# 데이터 로드
df = pd.read_csv(DATA_DIR / "training_data.csv")

feature_cols = [
    'empathy_diff', 'patience_diff', 'activity_diff', 'independence_diff',
    'max_diff', 'avg_diff',
    'empathy_diff_sq', 'patience_diff_sq',
    'empathy_patience_interaction',
    'patient_empathy', 'patient_patience',
    'caregiver_empathy', 'caregiver_patience'
]

X = df[feature_cols].values
y = df['satisfaction_score'].values
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# XGBoost 모델 학습
print("🔧 XGBoost 모델 재학습 중...")
model = XGBRegressor(
    n_estimators=200,
    max_depth=6,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42
)
model.fit(X_train, y_train)

# 성능 확인
y_pred = model.predict(X_test)
from sklearn.metrics import r2_score
r2 = r2_score(y_test, y_pred)
print(f"✅ R² Score: {r2:.4f}")

# 여러 형식으로 저장

# 1. Pickle 형식 (가장 안정적, Python에서 로드 가능)
pickle_path = BEST_MODEL_DIR / "xgboost_model.pkl"
with open(pickle_path, 'wb') as f:
    pickle.dump(model, f)
print(f"✅ Pickle 저장: {pickle_path}")

# 2. XGBoost JSON 형식 (크로스 플랫폼, Azure 가능)
json_path = BEST_MODEL_DIR / "xgboost_model.json"
model.save_model(str(json_path))
print(f"✅ XGBoost JSON 저장: {json_path}")

# 3. UBJ (Universal Binary JSON) 형식
ubj_path = BEST_MODEL_DIR / "xgboost_model.ubj"
model.save_model(str(ubj_path))
print(f"✅ UBJ 저장: {ubj_path}")

# 4. Feature 정보 저장
features_info = {
    'feature_names': feature_cols,
    'n_features': len(feature_cols),
    'model_type': 'XGBRegressor',
    'performance': {
        'r2_score': float(r2),
        'best_params': model.get_params()
    }
}

features_path = BEST_MODEL_DIR / "xgboost_features.json"
with open(features_path, 'w') as f:
    json.dump(features_info, f, indent=2)
print(f"✅ Feature 정보 저장: {features_path}")

# 테스트 코드
print("\n🧪 로드 테스트:")

# Pickle 로드 테스트
with open(pickle_path, 'rb') as f:
    loaded_model = pickle.load(f)
test_pred = loaded_model.predict(X_test[:5])
print(f"  - Pickle 모델 예측: {test_pred[:3]}")

# JSON 로드 테스트
loaded_model_json = XGBRegressor()
loaded_model_json.load_model(str(json_path))
test_pred_json = loaded_model_json.predict(X_test[:5])
print(f"  - JSON 모델 예측: {test_pred_json[:3]}")

print("\n✅ 모든 형식 저장 완료!")
print(f"📁 저장 위치: {BEST_MODEL_DIR}")
