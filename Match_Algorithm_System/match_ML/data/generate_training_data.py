"""
Training Data Generator for ML Matching Model
시뮬레이션 데이터 생성 (실제 만족도 데이터가 없는 경우)
"""

import numpy as np
import pandas as pd

np.random.seed(42)

def generate_training_data(n_samples=1000):
    """
    환자-간병인 매칭 만족도 학습 데이터 생성

    Args:
        n_samples: 생성할 샘플 수

    Returns:
        DataFrame with columns:
        - patient_empathy, patient_activity, patient_patience, patient_independence
        - caregiver_empathy, caregiver_activity_support, caregiver_patience, caregiver_independence_support
        - satisfaction_score (0-100)
    """

    data = []

    for _ in range(n_samples):
        # 환자 성향 (0-100)
        patient = {
            'empathy': np.random.uniform(0, 100),
            'activity': np.random.uniform(0, 100),
            'patience': np.random.uniform(0, 100),
            'independence': np.random.uniform(0, 100)
        }

        # 간병인 스타일 (0-100)
        caregiver = {
            'empathy': np.random.uniform(0, 100),
            'activity_support': np.random.uniform(0, 100),
            'patience': np.random.uniform(0, 100),
            'independence_support': np.random.uniform(0, 100)
        }

        # 만족도 계산 (실제 패턴을 반영)
        # 핵심: 성향 차이가 작을수록 만족도 높음
        empathy_diff = abs(patient['empathy'] - caregiver['empathy'])
        activity_diff = abs(patient['activity'] - caregiver['activity_support'])
        patience_diff = abs(patient['patience'] - caregiver['patience'])
        independence_diff = abs(patient['independence'] - caregiver['independence_support'])

        # 각 축별 유사도 (차이가 작을수록 100에 가까움)
        empathy_sim = 100 - empathy_diff
        activity_sim = 100 - activity_diff
        patience_sim = 100 - patience_diff
        independence_sim = 100 - independence_diff

        # 평균 유사도
        avg_similarity = np.mean([empathy_sim, activity_sim, patience_sim, independence_sim])

        # 비선형 효과 추가 (큰 차이는 더욱 불만족스러움)
        max_diff = max(empathy_diff, activity_diff, patience_diff, independence_diff)
        penalty = 0
        if max_diff > 50:
            penalty = (max_diff - 50) * 0.5  # 한 축이라도 차이가 크면 큰 페널티

        # 기본 만족도
        base_satisfaction = avg_similarity - penalty

        # 현실적인 노이즈 추가 (±10점)
        noise = np.random.normal(0, 10)
        satisfaction = np.clip(base_satisfaction + noise, 0, 100)

        data.append({
            'patient_empathy': patient['empathy'],
            'patient_activity': patient['activity'],
            'patient_patience': patient['patience'],
            'patient_independence': patient['independence'],
            'caregiver_empathy': caregiver['empathy'],
            'caregiver_activity_support': caregiver['activity_support'],
            'caregiver_patience': caregiver['patience'],
            'caregiver_independence_support': caregiver['independence_support'],
            'empathy_diff': empathy_diff,
            'activity_diff': activity_diff,
            'patience_diff': patience_diff,
            'independence_diff': independence_diff,
            'satisfaction_score': satisfaction
        })

    df = pd.DataFrame(data)
    return df


if __name__ == "__main__":
    # 1000개 샘플 생성
    df = generate_training_data(1000)

    # CSV 저장
    output_path = "/Users/sangwon/Project/Sesac_class/bluedonulab-01/match_ML/data/training_data.csv"
    df.to_csv(output_path, index=False)

    print(f"✅ 학습 데이터 생성 완료: {len(df)}개 샘플")
    print(f"📁 저장 위치: {output_path}")
    print(f"\n📊 데이터 통계:")
    print(df.describe())
    print(f"\n🎯 만족도 분포:")
    print(f"  - 평균: {df['satisfaction_score'].mean():.1f}")
    print(f"  - 최소: {df['satisfaction_score'].min():.1f}")
    print(f"  - 최대: {df['satisfaction_score'].max():.1f}")
