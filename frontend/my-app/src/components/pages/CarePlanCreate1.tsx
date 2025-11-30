'use client'

import { useEffect } from 'react'
import { background, firstPrimary } from '@/app/colors'

interface CarePlanCreate1Props {
  onNext: () => void
  initialData?: any
}

export default function CarePlanCreate1({ onNext, initialData = {} }: CarePlanCreate1Props) {
  useEffect(() => {
    const timer = setTimeout(() => {
      onNext()
    }, 3000)

    return () => clearTimeout(timer)
  }, [onNext])

  // initialData에서 carePlan 정보 추출
  const carePlan = initialData?.carePlan
  const summary = carePlan?.summary || {}
  const totalActivities = summary?.total_activities || 42
  const participants = summary?.participants || 4
  const dailyHours = summary?.daily_hours || 6

  const styles = {
    container: {
      background: background,
      display: 'flex',
      flexDirection: 'column' as const,
      justifyContent: 'center',
      alignItems: 'center',
      padding: '40px',
      color: 'black',
      minHeight: 'calc(100vh - 64px - 80px)',
      paddingBottom: '100px'
    },
    loaderContainer: {
      marginBottom: '50px',
      position: 'relative' as const
    },
    loadingRing: {
      position: 'absolute' as const,
      width: '140px',
      height: '140px',
      border: '4px solid rgba(255, 255, 255, 0.3)',
      borderTopColor: firstPrimary,
      borderRadius: '50%',
      animation: 'spin 1.5s linear infinite',
      top: '-10px',
      left: '-10px'
    },
    loader: {
      width: '120px',
      height: '120px',
      borderRadius: '60px',
      background: 'rgba(255, 255, 255, 0.2)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      position: 'relative' as const,
      animation: 'pulse 2s infinite'
    },
    loaderIcon: {
      width: '64px',
      height: '64px'
    },
    messageContainer: {
      textAlign: 'center' as const,
      maxWidth: '300px'
    },
    mainMessage: {
      fontSize: '24px',
      fontWeight: 600,
      marginBottom: '20px'
    },
    stepMessages: {
      fontSize: '16px',
      lineHeight: 1.8,
      opacity: 0.95
    },
    infoCards: {
      display: 'flex',
      gap: '15px',
      marginTop: '50px',
      width: '100%',
      maxWidth: '320px'
    },
    infoCard: {
      flex: 1,
      background: 'rgba(255, 255, 255, 0.15)',
      backdropFilter: 'blur(10px)',
      padding: '20px 15px',
      borderRadius: '15px',
      textAlign: 'center' as const
    },
    infoIcon: {
      fontSize: '32px',
      marginBottom: '10px'
    },
    infoTitle: {
      fontSize: '13px',
      opacity: 0.9,
      marginBottom: '5px'
    },
    infoValue: {
      fontSize: '20px',
      fontWeight: 'bold'
    }
  }

  return (
    <div style={styles.container}>
      <style>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
        @keyframes pulse {
          0%, 100% { opacity: 0.5; }
          50% { opacity: 1; }
        }
      `}</style>

      <div style={styles.loaderContainer}>
        <div style={styles.loadingRing}></div>
        <div style={styles.loader}>
          <div style={styles.loaderIcon}>🤖</div>
        </div>
      </div>

      <div style={styles.messageContainer}>
        <div style={styles.mainMessage}>AI가 케어 플랜을 생성하고 있어요</div>
        <div style={styles.stepMessages}>
          <div>환자분의 건강 상태를 분석 중...</div>
          <div>최적의 케어 활동을 추천 중...</div>
          <div>케어기버 배정 중...</div>
        </div>
      </div>

      <div style={styles.infoCards}>
        <div style={styles.infoCard}>
          <div style={styles.infoIcon}>⏱️</div>
          <div style={styles.infoTitle}>일일 소요시간</div>
          <div style={styles.infoValue}>{dailyHours}시간</div>
        </div>
        <div style={styles.infoCard}>
          <div style={styles.infoIcon}>📋</div>
          <div style={styles.infoTitle}>활동 수</div>
          <div style={styles.infoValue}>{totalActivities}개</div>
        </div>
        <div style={styles.infoCard}>
          <div style={styles.infoIcon}>👥</div>
          <div style={styles.infoTitle}>참여자</div>
          <div style={styles.infoValue}>{participants}명</div>
        </div>
      </div>
    </div>
  )
}
