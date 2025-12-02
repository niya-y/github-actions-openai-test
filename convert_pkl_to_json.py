"""
PKL 모델을 JSON 형식으로 변환
새 알고리즘 (neulbomcare-matching 2) → 현재 프로젝트 통합
"""

import joblib
from xgboost import XGBRegressor
from pathlib import Path
import json
import shutil

# 경로 설정
SOURCE_DIR = Path("/Users/sangwon/Project/Sesac_class/neulbom-merge/neulbomcare-matching 2")
TARGET_DIR = Path("/Users/sangwon/Project/Sesac_class/neulbom-merge/neulbomcare-test03/backend/models")

# 모델 디렉토리 생성
TARGET_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 60)
print("🔄 PKL 모델 → JSON 변환")
print("=" * 60)

# 1. PKL 모델 로드
print("\n1️⃣ PKL 모델 로드 중...")
pkl_path = SOURCE_DIR / "models" / "xgboost_regressor.pkl"

if not pkl_path.exists():
    print(f"❌ PKL 파일을 찾을 수 없습니다: {pkl_path}")
    exit(1)

model = joblib.load(pkl_path)
print(f"✅ 모델 로드 완료: {pkl_path}")
print(f"   - 모델 타입: {type(model).__name__}")

# 2. JSON 형식으로 저장
print("\n2️⃣ JSON 형식으로 변환 중...")
json_path = TARGET_DIR / "xgboost_v2.json"
model.save_model(str(json_path))
print(f"✅ JSON 저장 완료: {json_path}")

# 파일 크기 확인
file_size = json_path.stat().st_size / 1024  # KB
print(f"   - 파일 크기: {file_size:.1f} KB")

# 3. 특성 컬럼 정보 복사
print("\n3️⃣ 특성 컬럼 정보 복사 중...")
feature_source = SOURCE_DIR / "models" / "feature_columns.json"
feature_target = TARGET_DIR / "feature_columns_v2.json"

if feature_source.exists():
    shutil.copy2(feature_source, feature_target)
    print(f"✅ 특성 정보 복사 완료: {feature_target}")
    
    # 특성 컬럼 확인
    with open(feature_target, 'r') as f:
        features = json.load(f)
    print(f"   - 특성 개수: {len(features)}개")
    print(f"   - 특성 목록:")
    for i, feat in enumerate(features, 1):
        print(f"     {i}. {feat}")
else:
    print(f"⚠️  특성 파일을 찾을 수 없습니다: {feature_source}")

# 4. 학습 결과 정보 복사
print("\n4️⃣ 학습 결과 정보 복사 중...")
results_source = SOURCE_DIR / "models" / "training_results.json"
results_target = TARGET_DIR / "training_results_v2.json"

if results_source.exists():
    shutil.copy2(results_source, results_target)
    print(f"✅ 학습 결과 복사 완료: {results_target}")
    
    # 성능 지표 확인
    with open(results_target, 'r') as f:
        results = json.load(f)
    
    if 'regression' in results and 'xgboost_regressor' in results['regression']:
        metrics = results['regression']['xgboost_regressor']
        print(f"\n📊 모델 성능 지표:")
        print(f"   - R² Score: {metrics.get('R2', 'N/A'):.4f}")
        print(f"   - RMSE: {metrics.get('RMSE', 'N/A'):.2f}")
        print(f"   - MAE: {metrics.get('MAE', 'N/A'):.2f}")
else:
    print(f"⚠️  학습 결과 파일을 찾을 수 없습니다: {results_source}")

# 5. 기존 모델 백업
print("\n5️⃣ 기존 모델 백업 중...")
old_model_path = TARGET_DIR.parent.parent / "Match_Algorithm_System" / "match_ML_v3" / "models" / "xgboost.json"

if old_model_path.exists():
    backup_path = TARGET_DIR / "xgboost_v1_backup.json"
    shutil.copy2(old_model_path, backup_path)
    print(f"✅ 기존 모델 백업 완료: {backup_path}")
else:
    print(f"⚠️  기존 모델을 찾을 수 없습니다: {old_model_path}")

# 6. 최종 확인
print("\n" + "=" * 60)
print("✅ 변환 완료!")
print("=" * 60)
print(f"\n📁 생성된 파일:")
print(f"   1. {json_path}")
print(f"   2. {feature_target}")
print(f"   3. {results_target}")
print(f"\n🎯 다음 단계:")
print(f"   1. feature_engineering.py 복사")
print(f"   2. xgboost_matching_service.py 업데이트")
print(f"   3. 테스트 실행")
print()
