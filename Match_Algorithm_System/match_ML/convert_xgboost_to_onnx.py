"""
XGBoost 모델을 ONNX로 변환 (XGBoost 2.x 버전 사용)
"""

import numpy as np
import pandas as pd
from pathlib import Path
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score
import onnx
from onnxmltools.convert import convert_xgboost
from onnxmltools.convert.common.data_types import FloatTensorType
import onnxruntime as rt

# 경로 설정
BASE_DIR = Path("/Users/sangwon/Project/Sesac_class/bluedonulab-01/match_ML")
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
BEST_MODEL_DIR = BASE_DIR / "best_model"

print("=" * 60)
print("🔄 XGBoost → ONNX 변환 (XGBoost 2.x)")
print("=" * 60)

# 1. 데이터 로드
print("\n📊 1단계: 데이터 로드")
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

print(f"  - 학습 데이터: {len(X_train)}개")
print(f"  - Feature 개수: {len(feature_cols)}개")

# 2. XGBoost 모델 학습
print("\n🔧 2단계: XGBoost 2.x 모델 학습")
model = XGBRegressor(
    n_estimators=200,
    max_depth=6,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    tree_method='hist'  # 안정성을 위해
)

model.fit(X_train, y_train)

# 성능 확인
y_pred = model.predict(X_test)
r2 = r2_score(y_test, y_pred)
print(f"  ✅ R² Score: {r2:.4f}")

# 3. ONNX 변환 시도 (여러 방법)
print("\n🔄 3단계: ONNX 변환 시도")

# 방법 1: onnxmltools 사용
print("\n  방법 1: onnxmltools 직접 변환...")
try:
    # Booster 객체 추출
    booster = model.get_booster()

    # 초기 타입 정의
    n_features = len(feature_cols)
    initial_type = [('float_input', FloatTensorType([None, n_features]))]

    # ONNX 변환
    onnx_model = convert_xgboost(
        booster,
        name='XGBoostRegressor',
        initial_types=initial_type,
        target_opset=12
    )

    # 저장
    onnx_path = MODELS_DIR / "xgboost.onnx"
    onnx.save_model(onnx_model, str(onnx_path))

    # 검증
    onnx.checker.check_model(onnx_model)

    print(f"    ✅ 변환 성공: {onnx_path}")

    # ONNX Runtime 테스트
    print("\n  🧪 ONNX 모델 테스트...")
    sess = rt.InferenceSession(str(onnx_path))

    # 입력/출력 확인
    input_name = sess.get_inputs()[0].name
    output_name = sess.get_outputs()[0].name

    print(f"    - 입력 이름: {input_name}")
    print(f"    - 출력 이름: {output_name}")

    # 예측 테스트
    X_test_sample = X_test[:5].astype(np.float32)

    # XGBoost 예측
    xgb_pred = model.predict(X_test_sample)

    # ONNX 예측
    onnx_pred = sess.run([output_name], {input_name: X_test_sample})[0]

    # 비교
    print(f"\n    예측 비교:")
    print(f"    - XGBoost: {xgb_pred[:3]}")
    print(f"    - ONNX:    {onnx_pred.flatten()[:3]}")

    # 차이 확인
    max_diff = np.max(np.abs(xgb_pred - onnx_pred.flatten()))
    print(f"    - 최대 차이: {max_diff:.6f}")

    if max_diff < 0.01:
        print(f"    ✅ 예측 일치! (오차 < 0.01)")

        # best_model 폴더에 복사
        best_onnx_path = BEST_MODEL_DIR / "xgboost.onnx"
        onnx.save_model(onnx_model, str(best_onnx_path))
        print(f"\n✅ 베스트 모델 저장: {best_onnx_path}")

        # 모델 정보 업데이트
        import json
        model_info = {
            'model_name': 'xgboost',
            'format': 'ONNX',
            'r2_score': float(r2),
            'xgboost_version': '2.1.4',
            'onnx_opset': 12,
            'feature_names': feature_cols,
            'n_features': len(feature_cols),
            'input_name': input_name,
            'output_name': output_name,
            'note': 'Converted successfully with XGBoost 2.x + onnxmltools'
        }

        info_path = BEST_MODEL_DIR / "xgboost_onnx_info.json"
        with open(info_path, 'w') as f:
            json.dump(model_info, f, indent=2)
        print(f"✅ 모델 정보 저장: {info_path}")

        print("\n" + "=" * 60)
        print("🎉 XGBoost ONNX 변환 성공!")
        print("=" * 60)
        print(f"\n📁 ONNX 파일 위치:")
        print(f"  - {onnx_path}")
        print(f"  - {best_onnx_path}")

    else:
        print(f"    ⚠️  예측 차이가 큼 (>{0.01})")

except Exception as e:
    print(f"    ❌ 방법 1 실패: {e}")
    import traceback
    traceback.print_exc()

    # 방법 2: sklearn wrapper 사용
    print("\n  방법 2: sklearn wrapper 시도...")
    try:
        from skl2onnx import convert_sklearn
        from skl2onnx.common.data_types import FloatTensorType

        initial_type = [('float_input', FloatTensorType([None, len(feature_cols)]))]

        onnx_model = convert_sklearn(
            model,
            initial_types=initial_type,
            target_opset=12
        )

        onnx_path = MODELS_DIR / "xgboost.onnx"
        onnx.save_model(onnx_model, str(onnx_path))

        print(f"    ✅ 방법 2 성공: {onnx_path}")

    except Exception as e2:
        print(f"    ❌ 방법 2도 실패: {e2}")
        print("\n⚠️  ONNX 변환 실패 - JSON/PKL 형식 사용 권장")
