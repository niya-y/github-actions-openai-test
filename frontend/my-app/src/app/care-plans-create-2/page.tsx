"use client"

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { background, firstPrimary } from '../colors'
import { apiGet } from '@/utils/api'
import ErrorAlert from '@/components/ErrorAlert'
import type { CarePlansResponse, Schedule, MealPlan } from '@/types/api'

export default function Screen9Schedule() {
  const router = useRouter()
  const [activeTab, setActiveTab] = useState<'weekly' | 'monthly'>('weekly')
  const [schedules, setSchedules] = useState<Schedule[]>([])
  const [mealPlans, setMealPlans] = useState<MealPlan[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  // 기본 활동 데이터 (API에서 데이터가 없을 경우 사용)
  const defaultActivities = [
    { time: '07:00', title: '기상 도움', assignee: '👨‍⚕️ 간병인 김미숙' },
    { time: '07:30', title: '아침 식사 준비', assignee: '👩 딸 박지은' },
    { time: '08:00', title: '약 복용 확인', assignee: '👨‍⚕️ 간병인 김미숙', note: '⚠️ 아스피린 100mg, 메트포민 500mg' },
    { time: '09:00', title: '가벼운 스트레칭', assignee: '👨‍⚕️ 간병인 김미숙' },
    { time: '10:00', title: '산책 (날씨 좋을 시)', assignee: '👩 딸 박지은' },
    { time: '12:00', title: '점심 식사 준비', assignee: '👨‍⚕️ 간병인 김미숙' }
  ]

  useEffect(() => {
    fetchCarePlans()
  }, [activeTab])

  const fetchCarePlans = async () => {
    const patientId = sessionStorage.getItem('patient_id')
    if (!patientId) {
      setLoading(false)
      return
    }

    setLoading(true)
    setError(null)

    try {
      const response = await apiGet<CarePlansResponse>(
        `/api/patients/${patientId}/care-plans?type=${activeTab}`
      )

      if (response.schedules && response.schedules.length > 0) {
        setSchedules(response.schedules)
      }
      if (response.meal_plans && response.meal_plans.length > 0) {
        setMealPlans(response.meal_plans)
      }
    } catch (err) {
      console.error('케어 플랜 조회 실패:', err)
      // 에러 시에도 기본 데이터 표시
    } finally {
      setLoading(false)
    }
  }

  // 스케줄을 활동 형식으로 변환
  const getActivities = () => {
    if (schedules.length > 0) {
      return schedules.map(schedule => ({
        time: schedule.start_time.slice(0, 5), // HH:MM 형식
        title: schedule.title,
        assignee: `👨‍⚕️ ${schedule.category}`,
        note: schedule.is_completed ? '✅ 완료' : undefined
      }))
    }
    return defaultActivities
  }

  const styles = {
    container: {
      minHeight: '100vh',
      background: background,
      display: 'flex',
      flexDirection: 'column' as const
    },
    header: {
      background: background,
      color: 'black',
      padding: '20px'
    },
    headerBox: {
      background: 'white',
      borderRadius: '12px',
      padding: '20px',
      margin: '10px'
    },
    h1: {
      fontSize: '24px',
      marginBottom: '5px'
    },
    p: {
      fontSize: '14px',
      opacity: 0.9
    },
    summaryCard: {
      background: 'rgba(255,255,255,0.2)',
      borderRadius: '12px',
      padding: '15px',
      marginTop: '15px',
      display: 'flex',
      justifyContent: 'space-around'
    },
    summaryItem: {
      textAlign: 'center' as const
    },
    summaryNumber: {
      fontSize: '24px',
      fontWeight: 'bold'
    },
    summaryLabel: {
      fontSize: '11px',
      marginTop: '3px',
      opacity: 0.9
    },
    content: {
      flex: 1,
      overflowY: 'auto' as const,
      padding: '20px'
    },
    tabBar: {
      display: 'flex',
      gap: '10px',
      marginBottom: '20px'
    },
    tab: {
      flex: 1,
      padding: '10px',
      background: '#f0f0f0',
      borderRadius: '8px',
      textAlign: 'center' as const,
      fontSize: '14px',
      cursor: 'pointer',
      border: 'none',
      fontWeight: 500
    },
    tabActive: {
      background: firstPrimary,
      color: 'white'
    },
    daySchedule: {
      background: 'white',
      borderRadius: '12px',
      padding: '15px',
      marginBottom: '15px',
      boxShadow: '0 2px 8px rgba(0,0,0,0.05)'
    },
    dayHeader: {
      fontWeight: 'bold',
      color: '#333',
      marginBottom: '15px',
      paddingBottom: '10px',
      borderBottom: '2px solid #f0f0f0'
    },
    activity: {
      display: 'flex',
      gap: '12px',
      marginBottom: '12px',
      padding: '12px',
      background: '#fafafa',
      borderRadius: '8px',
      borderLeft: `3px solid ${firstPrimary}`
    },
    activityTime: {
      fontWeight: 'bold',
      color: firstPrimary,
      fontSize: '14px',
      minWidth: '45px'
    },
    activityContent: {
      flex: 1
    },
    activityTitle: {
      fontWeight: 600,
      color: '#333',
      marginBottom: '4px'
    },
    activityAssignee: {
      fontSize: '13px',
      color: '#666',
      marginBottom: '4px'
    },
    activityNote: {
      fontSize: '12px',
      color: '#999',
      display: 'flex',
      alignItems: 'center',
      gap: '4px'
    },
    reviewCard: {
      background: 'white',
      borderRadius: '15px',
      padding: '20px',
      color: 'black',
      marginTop: '20px',
      boxShadow: '0 4px 15px rgba(245, 87, 108, 0.3)'
    },
    reviewCardH3: {
      fontSize: '18px',
      marginBottom: '10px'
    },
    reviewCardP: {
      fontSize: '14px',
      lineHeight: 1.6,
      marginBottom: '15px',
      opacity: 0.95
    },
    reviewButtons: {
      display: 'flex',
      gap: '10px'
    },
    btn: {
      flex: 1,
      padding: '12px',
      borderRadius: '8px',
      border: 'none',
      fontWeight: 600,
      cursor: 'pointer',
      fontSize: '14px'
    },
    btnOutline: {
      background: '#f0f0f0',
      color: 'black',
      border: '1px solid rgba(255,255,255,0.4)'
    },
    btnPrimary: {
      background: firstPrimary,
      color: 'white',
    },
    bottomBar: {
      padding: '15px 20px',
      background: background,
      borderTop: '1px solid #f0f0f0',
      display: 'flex',
      gap: '10px'
    },
    btnSecondary: {
      background: '#f0f0f0',
      color: '#333'
    },
    btnAction: {
      background: firstPrimary,
      color: 'white'
    },
    loadingContainer: {
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      padding: '40px',
      fontSize: '14px',
      color: '#666'
    }
  }

  const activities = getActivities()

  return (
    <div style={styles.container}>
      <ErrorAlert error={error} onClose={() => setError(null)} />

      <div style={styles.header}>
        <div style={styles.headerBox}>
          <h1 style={styles.h1}>케어 플랜</h1>
          <p style={styles.p}>AI가 생성한 {activeTab === 'weekly' ? '7일' : '30일'} 간병 일정입니다</p>

          <div style={styles.summaryCard}>
            <div style={styles.summaryItem}>
              <div style={styles.summaryNumber}>{schedules.length > 0 ? schedules.length : 42}개</div>
              <div style={styles.summaryLabel}>총 활동</div>
            </div>
            <div style={styles.summaryItem}>
              <div style={styles.summaryNumber}>4명</div>
              <div style={styles.summaryLabel}>참여 인원</div>
            </div>
            <div style={styles.summaryItem}>
              <div style={styles.summaryNumber}>6시간</div>
              <div style={styles.summaryLabel}>일일 평균</div>
            </div>
          </div>
        </div>
      </div>

      <div style={styles.content}>
        <div style={styles.tabBar}>
          <button
            style={{ ...styles.tab, ...(activeTab === 'weekly' ? styles.tabActive : {}) }}
            onClick={() => setActiveTab('weekly')}
          >
            주간
          </button>
          <button
            style={{ ...styles.tab, ...(activeTab === 'monthly' ? styles.tabActive : {}) }}
            onClick={() => setActiveTab('monthly')}
          >
            월간
          </button>
        </div>

        {loading ? (
          <div style={styles.loadingContainer}>
            케어 플랜을 불러오는 중...
          </div>
        ) : (
          <div style={styles.daySchedule}>
            <div style={styles.dayHeader}>{activeTab === 'weekly' ? '월요일' : '이번 달'} 일정</div>

            {activities.map((activity, index) => (
              <div key={index} style={styles.activity}>
                <div style={styles.activityTime}>{activity.time}</div>
                <div style={styles.activityContent}>
                  <div style={styles.activityTitle}>{activity.title}</div>
                  <div style={styles.activityAssignee}>{activity.assignee}</div>
                  {activity.note && (
                    <div style={styles.activityNote}>{activity.note}</div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* 식단 계획 표시 */}
        {mealPlans.length > 0 && (
          <div style={styles.daySchedule}>
            <div style={styles.dayHeader}>식단 계획</div>
            {mealPlans.map((meal, index) => (
              <div key={index} style={styles.activity}>
                <div style={styles.activityTime}>{meal.meal_type}</div>
                <div style={styles.activityContent}>
                  <div style={styles.activityTitle}>{meal.menu_name}</div>
                  <div style={styles.activityAssignee}>
                    칼로리: {meal.nutrition_info.calories}kcal
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        <div style={styles.reviewCard}>
          <h3 style={styles.reviewCardH3}>전문가 의견을 들어보세요</h3>
          <p style={styles.reviewCardP}>간병인님께 이 일정에 대한 검토를 요청하시겠어요?</p>
          <p style={{ ...styles.reviewCardP, fontSize: '13px', opacity: 0.9 }}>
            전문가의 현장 경험이 더해지면 더 실용적인 케어 플랜이 됩니다.
          </p>
          <div style={styles.reviewButtons}>
            <button style={{ ...styles.btn, ...styles.btnOutline }}>나중에</button>
            <button
              style={{ ...styles.btn, ...styles.btnPrimary }}
              onClick={() => router.push('/care-plans-create-3')}
            >
              리뷰 요청하기
            </button>
          </div>
        </div>
      </div>

      <div style={styles.bottomBar}>
        <button style={{ ...styles.btn, ...styles.btnSecondary }}>일정 수정</button>
        <button
          style={{ ...styles.btn, ...styles.btnAction }}
          onClick={() => router.push('/mypage-dashboard')}
        >
          이대로 시작
        </button>
      </div>
    </div>
  )
}
