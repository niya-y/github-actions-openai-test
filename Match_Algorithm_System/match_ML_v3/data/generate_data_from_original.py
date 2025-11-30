"""
V3 모델: 원본 데이터 기반 학습 데이터 생성
Residents.csv + staff.csv를 활용하여 실제 매칭 시뮬레이션
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta

np.random.seed(42)

# 경로 설정
BASE_DIR = Path("/Users/sangwon/Project/Sesac_class/bluedonulab-01")
PROJECT_ROOT = BASE_DIR
DATA_OUTPUT_DIR = BASE_DIR / "match_ML_v3" / "data"

print("=" * 70)
print("📊 V3 모델: 원본 데이터 기반 학습 데이터 생성")
print("=" * 70)

# 1. 원본 데이터 로드
print("\n📖 1단계: 원본 데이터 로드...")

try:
    residents_df = pd.read_csv(PROJECT_ROOT / "Residents.csv")
    print(f"  ✅ Residents.csv 로드: {len(residents_df)}명")
    print(f"     Columns: {list(residents_df.columns)}")
except Exception as e:
    print(f"  ❌ 오류: {e}")
    residents_df = None

try:
    staff_df = pd.read_csv(PROJECT_ROOT / "staff.csv")
    print(f"  ✅ staff.csv 로드: {len(staff_df)}명")
    print(f"     Columns: {list(staff_df.columns)}")
except Exception as e:
    print(f"  ❌ 오류: {e}")
    staff_df = None

# 2. 데이터 전처리
print("\n🔧 2단계: 데이터 전처리...")

# Residents 데이터 정제
residents_df = residents_df.dropna(subset=['ResidentID'])
residents_df['ResidentID'] = residents_df['ResidentID'].astype(int)

# Date of Birth를 나이로 변환
residents_df['Date of Birth'] = pd.to_datetime(residents_df['Date of Birth'], errors='coerce')
residents_df['Age'] = (datetime.now() - residents_df['Date of Birth']).dt.days // 365

# Care Level을 수치로 변환
care_level_map = {'Low': 1, 'Moderate': 2, 'High': 3}
residents_df['Care Level Numeric'] = residents_df['Care Level'].map(care_level_map)

print(f"  ✅ Residents 전처리 완료")
print(f"     - 나이 범위: {residents_df['Age'].min()}-{residents_df['Age'].max()}")
print(f"     - Care Level 분포: {residents_df['Care Level'].value_counts().to_dict()}")

# Staff 데이터 정제
staff_df = staff_df.dropna(subset=['StaffID'])
staff_df['StaffID'] = staff_df['StaffID'].astype(int)

# Date of Birth를 경력으로 변환
staff_df['Date of Birth'] = pd.to_datetime(staff_df['Date of Birth'], errors='coerce')
staff_df['Age'] = (datetime.now() - staff_df['Date of Birth']).dt.days // 365

# Employment Date를 경력 년수로 변환
staff_df['Employment Date'] = pd.to_datetime(staff_df['Employment Date'], errors='coerce')
staff_df['Experience Years'] = (datetime.now() - staff_df['Employment Date']).dt.days // 365

# Job Title을 전문성 수준으로 매핑
expertise_map = {
    'Nurse': 3,
    'Doctor': 3,
    'Caregiver': 2,
    'Therapist': 2,
    'Administrator': 1
}
staff_df['Expertise Level'] = staff_df['Job Title'].map(expertise_map).fillna(1)

print(f"  ✅ Staff 전처리 완료")
print(f"     - 나이 범위: {staff_df['Age'].min()}-{staff_df['Age'].max()}")
print(f"     - 경력 범위: {staff_df['Experience Years'].min()}-{staff_df['Experience Years'].max()}")
print(f"     - 직종 분포: {staff_df['Job Title'].value_counts().to_dict()}")

# 3. 매칭 조합 생성
print("\n⚙️ 3단계: 환자-간병인 매칭 조합 생성...")

# 샘플링 (전체 1000×1000은 너무 많으니 현실적인 수로)
sample_residents = residents_df.sample(n=min(100, len(residents_df)), random_state=42)
sample_staff = staff_df.sample(n=min(100, len(staff_df)), random_state=42)

print(f"  - 샘플 환자: {len(sample_residents)}명")
print(f"  - 샘플 간병인: {len(sample_staff)}명")
print(f"  - 가능한 조합: {len(sample_residents) * len(sample_staff)}개")

# 모든 조합 생성 (샘플 사용)
print(f"  - 실제 사용할 샘플: 10,000개 (무작위 선택)")

data = []

# 더 많은 다양한 조합을 만들기 위해 반복
num_samples = 10000

for _ in range(num_samples):
    # 무작위 환자와 간병인 선택
    resident = sample_residents.sample(1).iloc[0]
    staff = sample_staff.sample(1).iloc[0]

    # ========== 환자 특성 추출 ==========
    resident_age = resident['Age']
    resident_care_level = resident['Care Level Numeric']
    resident_gender = 1 if resident['Gender'] == 'Male' else 0

    # 환자 성향 점수 계산 (나이 기반)
    # - 고령(75+): 인내심 필요 (높음), 활동성 낮음, 공감도 중간
    if resident_age >= 75:
        resident_empathy = np.random.normal(60, 15)
        resident_activity = np.random.normal(40, 15)
        resident_patience = np.random.normal(70, 15)
        resident_independence = np.random.normal(40, 15)
    elif resident_age >= 60:
        resident_empathy = np.random.normal(65, 15)
        resident_activity = np.random.normal(50, 15)
        resident_patience = np.random.normal(65, 15)
        resident_independence = np.random.normal(50, 15)
    else:
        resident_empathy = np.random.normal(70, 15)
        resident_activity = np.random.normal(65, 15)
        resident_patience = np.random.normal(60, 15)
        resident_independence = np.random.normal(65, 15)

    # Care Level에 따른 조정
    # High: 더 전문적인 간병인 필요 (스트레스 높음)
    stress_multiplier = 1 + (resident_care_level - 1) * 0.2
    resident_patience *= (1 + 0.2 * stress_multiplier)

    resident_empathy = np.clip(resident_empathy, 0, 100)
    resident_activity = np.clip(resident_activity, 0, 100)
    resident_patience = np.clip(resident_patience, 0, 100)
    resident_independence = np.clip(resident_independence, 0, 100)

    # ========== 간병인 특성 추출 ==========
    staff_age = staff['Age']
    staff_expertise = staff['Expertise Level']
    staff_experience = staff['Experience Years']
    staff_gender = 1 if staff['Gender'] == 'Male' else 0

    # 간병인 성향 점수 계산 (경력과 직종 기반)
    # - 경력 많을수록: 공감도 높음, 인내심 높음
    # - 전문성 높을수록: 독립성 지원 능력 높음
    base_empathy = 50 + (staff_experience * 0.5)  # 경력에 따라 증가
    base_patience = 50 + (staff_experience * 0.4)
    base_activity_support = 60
    base_independence_support = 50 + (staff_expertise * 10)

    caregiver_empathy = np.clip(np.random.normal(base_empathy, 10), 0, 100)
    caregiver_patience = np.clip(np.random.normal(base_patience, 10), 0, 100)
    caregiver_activity_support = np.clip(np.random.normal(base_activity_support, 15), 0, 100)
    caregiver_independence_support = np.clip(np.random.normal(base_independence_support, 10), 0, 100)

    # ========== 만족도 계산 (V2와 동일한 로직) ==========

    # 차이값 계산
    empathy_diff = abs(resident_empathy - caregiver_empathy)
    activity_diff = abs(resident_activity - caregiver_activity_support)
    patience_diff = abs(resident_patience - caregiver_patience)
    independence_diff = abs(resident_independence - caregiver_independence_support)

    # 비선형 페널티
    def penalty_function(diff):
        if diff < 20:
            return diff
        elif diff < 40:
            return 20 + (diff - 20) * 1.5
        else:
            return 50 + (diff - 40) * 2.0

    empathy_penalty = penalty_function(empathy_diff)
    activity_penalty = penalty_function(activity_diff)
    patience_penalty = penalty_function(patience_diff)
    independence_penalty = penalty_function(independence_diff)

    # 축별 가중치 적용
    weighted_satisfaction = (
        (100 - empathy_penalty) * 0.40 +
        (100 - patience_penalty) * 0.30 +
        (100 - activity_penalty) * 0.20 +
        (100 - independence_penalty) * 0.10
    )

    # 상호작용 효과
    empathy_score = 100 - empathy_penalty
    if empathy_score < 50:
        weighted_satisfaction -= 10
    elif empathy_score > 80:
        weighted_satisfaction += 5

    # 실제 경력과 Care Level의 호환성 추가
    # 복잡한 환자(High)는 경험 많은 간병인이 필요
    expertise_bonus = 0
    if resident_care_level == 3 and staff_expertise >= 2:  # High Care + 전문가
        expertise_bonus = 5
    elif resident_care_level == 3 and staff_expertise < 2:  # High Care + 비전문가
        expertise_bonus = -10

    weighted_satisfaction += expertise_bonus

    # 노이즈 추가
    noise = np.random.normal(0, 5)
    satisfaction = np.clip(weighted_satisfaction + noise, 0, 100)

    # 데이터 저장
    data.append({
        # 환자 정보
        'resident_id': resident['ResidentID'],
        'resident_age': resident_age,
        'resident_care_level': resident_care_level,
        'resident_gender': resident_gender,
        'resident_empathy': resident_empathy,
        'resident_activity': resident_activity,
        'resident_patience': resident_patience,
        'resident_independence': resident_independence,

        # 간병인 정보
        'staff_id': staff['StaffID'],
        'staff_age': staff_age,
        'staff_expertise': staff_expertise,
        'staff_experience': staff_experience,
        'staff_gender': staff_gender,
        'caregiver_empathy': caregiver_empathy,
        'caregiver_activity_support': caregiver_activity_support,
        'caregiver_patience': caregiver_patience,
        'caregiver_independence_support': caregiver_independence_support,

        # 차이값
        'empathy_diff': empathy_diff,
        'activity_diff': activity_diff,
        'patience_diff': patience_diff,
        'independence_diff': independence_diff,
        'max_diff': max(empathy_diff, activity_diff, patience_diff, independence_diff),
        'avg_diff': np.mean([empathy_diff, activity_diff, patience_diff, independence_diff]),

        # 비선형 Feature
        'empathy_diff_sq': empathy_diff ** 2,
        'patience_diff_sq': patience_diff ** 2,
        'empathy_patience_interaction': empathy_diff * patience_diff,

        # 타겟
        'satisfaction_score': satisfaction
    })

df = pd.DataFrame(data)

# 4. CSV로 저장
print("\n💾 4단계: 학습 데이터 저장...")

output_path = DATA_OUTPUT_DIR / "training_data_v3.csv"
df.to_csv(output_path, index=False)

print(f"  ✅ 저장 완료: {output_path}")
print(f"     - 샘플 수: {len(df)}")
print(f"     - Feature 개수: {len(df.columns) - 1}")

# 5. 통계 출력
print("\n📊 5단계: 데이터 통계...")

print(f"\n환자 정보:")
print(f"  - 나이 범위: {df['resident_age'].min():.0f}-{df['resident_age'].max():.0f}")
print(f"  - Care Level 분포:")
for level, count in df['resident_care_level'].value_counts().sort_index().items():
    print(f"    Level {int(level)}: {count}개 ({count/len(df)*100:.1f}%)")

print(f"\n간병인 정보:")
print(f"  - 나이 범위: {df['staff_age'].min():.0f}-{df['staff_age'].max():.0f}")
print(f"  - 경력 범위: {df['staff_experience'].min():.0f}-{df['staff_experience'].max():.0f}년")
print(f"  - 전문성 분포:")
for level, count in df['staff_expertise'].value_counts().sort_index().items():
    print(f"    Level {int(level)}: {count}개 ({count/len(df)*100:.1f}%)")

print(f"\n매칭 만족도:")
print(f"  - 평균: {df['satisfaction_score'].mean():.1f}점")
print(f"  - 표준편차: {df['satisfaction_score'].std():.1f}점")
print(f"  - 최소: {df['satisfaction_score'].min():.1f}점")
print(f"  - 최대: {df['satisfaction_score'].max():.1f}점")

print(f"\n주요 상관관계:")
correlations = df[[
    'empathy_diff', 'patience_diff', 'activity_diff', 'independence_diff',
    'max_diff', 'avg_diff', 'satisfaction_score'
]].corr()['satisfaction_score'].sort_values()

for feature, corr in correlations.items():
    if feature != 'satisfaction_score':
        print(f"  - {feature}: {corr:.3f}")

print("\n" + "=" * 70)
print("✅ V3 학습 데이터 생성 완료!")
print("=" * 70)
