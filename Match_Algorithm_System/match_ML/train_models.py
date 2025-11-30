"""
Multiple ML Models Training and ONNX Conversion
여러 머신러닝 모델 학습 및 성능 비교
"""

import numpy as np
import pandas as pd
import json
import shutil
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from xgboost import XGBRegressor
import onnx
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType
import onnxmltools
from onnxmltools.convert import convert_xgboost as convert_xgb_to_onnx
import onnxruntime as rt


# 경로 설정
BASE_DIR = Path("/Users/sangwon/Project/Sesac_class/bluedonulab-01/match_ML")
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
BEST_MODEL_DIR = BASE_DIR / "best_model"


def load_data():
    """학습 데이터 로드"""
    df = pd.read_csv(DATA_DIR / "training_data.csv")

    # Feature columns - 개선된 Feature 사용
    feature_cols = [
        # 기본 차이값 (가장 중요)
        'empathy_diff', 'patience_diff', 'activity_diff', 'independence_diff',
        # 통계적 Feature
        'max_diff', 'avg_diff',
        # 비선형 Feature
        'empathy_diff_sq', 'patience_diff_sq',
        # 상호작용 Feature
        'empathy_patience_interaction',
        # 원본 값도 포함 (추가 정보)
        'patient_empathy', 'patient_patience',
        'caregiver_empathy', 'caregiver_patience'
    ]

    X = df[feature_cols].values
    y = df['satisfaction_score'].values

    return train_test_split(X, y, test_size=0.2, random_state=42), feature_cols


def evaluate_model(y_true, y_pred, model_name):
    """모델 성능 평가"""
    mse = mean_squared_error(y_true, y_pred)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)

    # 0-100 범위에서의 정확도 (±5점 이내를 정확하다고 판단)
    accuracy_5 = np.mean(np.abs(y_true - y_pred) <= 5) * 100
    accuracy_10 = np.mean(np.abs(y_true - y_pred) <= 10) * 100

    return {
        'model_name': model_name,
        'rmse': round(rmse, 2),
        'mae': round(mae, 2),
        'r2_score': round(r2, 4),
        'accuracy_within_5': round(accuracy_5, 2),
        'accuracy_within_10': round(accuracy_10, 2)
    }


def convert_to_onnx(model, model_name, X_sample, feature_cols):
    """모델을 ONNX 포맷으로 변환"""
    onnx_path = MODELS_DIR / f"{model_name}.onnx"

    try:
        if isinstance(model, XGBRegressor):
            # XGBoost → ONNX (onnxmltools 사용)
            print(f"  🔧 XGBoost 전용 ONNX 변환 프로세스 시작...")

            # 1. Booster 객체 가져오기
            booster = model.get_booster()

            # 2. 입력 타입 정의
            n_features = X_sample.shape[1]
            initial_type = [('float_input', FloatTensorType([None, n_features]))]

            # 3. XGBoost 전용 변환 함수 사용 (올바른 API)
            onnx_model = convert_xgb_to_onnx(
                booster,
                name='XGBoostModel',
                initial_types=initial_type,
                target_opset=12
            )

        else:
            # Sklearn 모델 → ONNX
            initial_type = [('float_input', FloatTensorType([None, X_sample.shape[1]]))]
            onnx_model = convert_sklearn(
                model,
                initial_types=initial_type,
                target_opset=12
            )

        # ONNX 모델 저장
        onnx.save_model(onnx_model, str(onnx_path))

        # ONNX 모델 검증
        onnx_model_check = onnx.load(str(onnx_path))
        onnx.checker.check_model(onnx_model_check)

        print(f"  ✅ ONNX 변환 성공: {onnx_path.name}")
        return True

    except Exception as e:
        print(f"  ❌ ONNX 변환 실패 ({model_name}): {e}")
        import traceback
        traceback.print_exc()
        return False


def train_all_models():
    """모든 모델 학습 및 평가"""
    print("=" * 60)
    print("🤖 머신러닝 모델 학습 시작")
    print("=" * 60)

    # 데이터 로드
    (X_train, X_test, y_train, y_test), feature_cols = load_data()
    print(f"\n📊 데이터 로드 완료:")
    print(f"  - 학습 데이터: {len(X_train)}개")
    print(f"  - 테스트 데이터: {len(X_test)}개")
    print(f"  - Feature 개수: {X_train.shape[1]}개")

    # 모델 정의 - 하이퍼파라미터 튜닝으로 성능 개선
    models = {
        'linear_regression': LinearRegression(),
        'random_forest': RandomForestRegressor(
            n_estimators=200,        # 100 → 200
            max_depth=15,            # 10 → 15
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42
        ),
        'xgboost': XGBRegressor(
            n_estimators=200,        # 100 → 200
            max_depth=6,             # 5 → 6
            learning_rate=0.05,      # 0.1 → 0.05 (더 느리지만 정확)
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42
        ),
        'svm': SVR(
            kernel='rbf',
            C=100,
            gamma='scale',           # 'auto' → 'scale'
            epsilon=0.1
        ),
        'neural_network': MLPRegressor(
            hidden_layer_sizes=(128, 64, 32),  # (64, 32) → (128, 64, 32)
            max_iter=1000,                      # 500 → 1000
            learning_rate_init=0.001,
            random_state=42,
            early_stopping=True
        )
    }

    results = []

    # 각 모델 학습
    for model_name, model in models.items():
        print(f"\n{'='*60}")
        print(f"🔧 {model_name.upper()} 학습 중...")
        print(f"{'='*60}")

        # 학습
        model.fit(X_train, y_train)

        # 예측
        y_pred = model.predict(X_test)

        # 평가
        metrics = evaluate_model(y_test, y_pred, model_name)
        results.append(metrics)

        print(f"\n📈 성능 지표:")
        print(f"  - RMSE: {metrics['rmse']:.2f}")
        print(f"  - MAE: {metrics['mae']:.2f}")
        print(f"  - R² Score: {metrics['r2_score']:.4f}")
        print(f"  - ±5점 이내 정확도: {metrics['accuracy_within_5']:.2f}%")
        print(f"  - ±10점 이내 정확도: {metrics['accuracy_within_10']:.2f}%")

        # ONNX 변환
        print(f"\n🔄 ONNX 변환 중...")
        convert_to_onnx(model, model_name, X_train, feature_cols)

    return results, feature_cols


def find_best_model(results):
    """최고 성능 모델 선정 (R² 기준)"""
    best_model = max(results, key=lambda x: x['r2_score'])
    return best_model


def copy_best_model(best_model_name):
    """최고 모델을 best_model 폴더에 복사"""
    src = MODELS_DIR / f"{best_model_name}.onnx"
    dst = BEST_MODEL_DIR / "best_model.onnx"

    if not src.exists():
        print(f"\n⚠️  경고: {src}가 존재하지 않습니다. ONNX 변환 실패했을 수 있습니다.")
        return

    shutil.copy2(src, dst)
    print(f"\n✅ 최고 모델 복사 완료:")
    print(f"  - 원본: {src}")
    print(f"  - 복사본: {dst}")


def save_results(results, best_model, feature_cols):
    """결과 저장"""
    # 전체 비교 결과
    comparison = {
        'models': results,
        'best_model': best_model,
        'feature_columns': feature_cols,
        'timestamp': pd.Timestamp.now().isoformat()
    }

    comparison_path = BASE_DIR / "model_comparison.json"
    with open(comparison_path, 'w', encoding='utf-8') as f:
        json.dump(comparison, f, indent=2, ensure_ascii=False)

    print(f"\n💾 비교 결과 저장: {comparison_path}")

    # 베스트 모델 정보
    best_info = {
        'model_name': best_model['model_name'],
        'metrics': best_model,
        'feature_columns': feature_cols,
        'onnx_path': 'best_model.onnx',
        'timestamp': pd.Timestamp.now().isoformat()
    }

    best_info_path = BEST_MODEL_DIR / "model_info.json"
    with open(best_info_path, 'w', encoding='utf-8') as f:
        json.dump(best_info, f, indent=2, ensure_ascii=False)

    print(f"💾 베스트 모델 정보 저장: {best_info_path}")


def print_summary(results, best_model):
    """최종 요약 출력"""
    print("\n" + "=" * 60)
    print("📊 최종 모델 비교 결과")
    print("=" * 60)

    # 테이블 형식으로 출력
    df_results = pd.DataFrame(results)
    df_results = df_results.sort_values('r2_score', ascending=False)

    print("\n" + df_results.to_string(index=False))

    print("\n" + "=" * 60)
    print(f"🏆 최고 성능 모델: {best_model['model_name'].upper()}")
    print("=" * 60)
    print(f"  - R² Score: {best_model['r2_score']:.4f}")
    print(f"  - RMSE: {best_model['rmse']:.2f}점")
    print(f"  - ±10점 이내 정확도: {best_model['accuracy_within_10']:.2f}%")
    print("=" * 60)


if __name__ == "__main__":
    # 모든 모델 학습
    results, feature_cols = train_all_models()

    # 최고 모델 선정
    best_model = find_best_model(results)

    # 최고 모델 복사
    copy_best_model(best_model['model_name'])

    # 결과 저장
    save_results(results, best_model, feature_cols)

    # 요약 출력
    print_summary(results, best_model)

    print("\n✅ 모든 작업 완료!")
    print(f"📁 ONNX 모델 저장 위치: {MODELS_DIR}")
    print(f"🏆 베스트 모델 위치: {BEST_MODEL_DIR}")
