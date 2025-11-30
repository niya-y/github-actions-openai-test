'use client'

import { useRouter } from 'next/navigation'
import { background, firstPrimary, secondPrimary } from '@/app/colors'

interface Mypage3Props {
  onNavigate?: (route: string) => void
}

export default function Mypage3({ onNavigate }: Mypage3Props) {
  const router = useRouter()

  const styles = {
    container: {
      background: background,
      display: 'flex',
      flexDirection: 'column' as const,
      minHeight: 'calc(100vh - 64px - 80px)',
      paddingBottom: '100px'
    },
    statusBar: {
      height: '44px',
      background: 'white',
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      padding: '0 20px',
      fontSize: '12px'
    },
    header: {
      background: background,
      padding: '20px',
      borderBottom: '1px solid #f0f0f0'
    },
    date: {
      fontSize: '14px',
      color: 'black',
      marginBottom: '5px'
    },
    patientInfo: {
      display: 'flex',
      alignItems: 'center',
      gap: '12px',
      marginBottom: '15px'
    },
    patientAvatar: {
      width: '50px',
      height: '50px',
      borderRadius: '25px',
      background: background,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      color: 'white',
      fontSize: '20px'
    },
    patientDetails: {},
    patientDetailsH2: {
      fontSize: '18px',
      marginBottom: '3px'
    },
    statusBadge: {
      display: 'inline-block',
      padding: '4px 10px',
      background: '#d1fae5',
      color: '#065f46',
      borderRadius: '12px',
      fontSize: '12px',
      fontWeight: 600
    },
    content: {
      flex: 1,
      overflowY: 'auto' as const,
      padding: '15px'
    },
    progressCard: {
      background: 'white',
      borderRadius: '15px',
      padding: '20px',
      marginBottom: '15px',
      boxShadow: '0 2px 8px rgba(0,0,0,0.05)'
    },
    progressCardH3: {
      fontSize: '16px',
      marginBottom: '15px',
      color: 'black'
    },
    progressBar: {
      width: '100%',
      height: '10px',
      background: '#e5e7eb',
      borderRadius: '5px',
      overflow: 'hidden',
      marginBottom: '12px'
    },
    progressFill: {
      height: '100%',
      background: `linear-gradient(90deg, ${firstPrimary} 0%, ${secondPrimary} 100%)`,
      width: '65%',
      borderRadius: '5px'
    },
    progressStats: {
      display: 'flex',
      justifyContent: 'space-between',
      fontSize: '13px',
      color: 'black',
      marginBottom: '15px'
    },
    nextActivity: {
      background: '#f3f4f6',
      padding: '12px',
      borderRadius: '8px',
      display: 'flex',
      alignItems: 'center',
      gap: '10px'
    },
    nextActivityIcon: {
      fontSize: '24px'
    },
    nextActivityInfo: {
      flex: 1
    },
    nextActivityTime: {
      fontSize: '12px',
      color: 'black'
    },
    nextActivityTitle: {
      fontWeight: 600,
      color: 'black',
      marginTop: '2px'
    },
    warningCard: {
      background: '#fce7f3',
      borderLeft: `4px solid ${secondPrimary}`,
      borderRadius: '12px',
      padding: '15px',
      marginBottom: '15px'
    },
    warningCardH4: {
      fontSize: '14px',
      marginBottom: '8px',
      color: secondPrimary,
      display: 'flex',
      alignItems: 'center',
      gap: '5px'
    },
    warningContent: {
      fontSize: '13px',
      color: 'black',
      lineHeight: 1.5,
      marginBottom: '10px'
    },
    warningButtons: {
      display: 'flex',
      gap: '8px'
    },
    warningBtn: {
      padding: '8px 12px',
      borderRadius: '6px',
      border: 'none',
      fontSize: '12px',
      cursor: 'pointer',
      fontWeight: 600
    },
    btnDetail: {
      background: secondPrimary,
      color: 'white'
    },
    btnContact: {
      background: 'white',
      color: secondPrimary,
      border: `1px solid ${secondPrimary}`
    },
    feedCard: {
      background: 'white',
      borderRadius: '15px',
      padding: '20px',
      marginBottom: '15px',
      boxShadow: '0 2px 8px rgba(0,0,0,0.05)'
    },
    feedCardH3: {
      fontSize: '16px',
      marginBottom: '15px',
      color: 'black'
    },
    feedItem: {
      padding: '12px',
      background: '#f9fafb',
      borderRadius: '8px',
      marginBottom: '10px',
      borderLeft: `3px solid ${secondPrimary}`
    },
    feedTime: {
      fontSize: '12px',
      color: 'black',
      marginBottom: '5px'
    },
    feedContent: {
      fontSize: '14px',
      color: 'black',
      lineHeight: 1.5
    },
    feedMeta: {
      fontSize: '13px',
      color: 'black',
      marginTop: '5px'
    },
    quickActions: {
      display: 'grid',
      gridTemplateColumns: 'repeat(2, 1fr)',
      gap: '10px',
      marginBottom: '20px'
    },
    actionBtn: {
      background: 'white',
      padding: '15px',
      borderRadius: '12px',
      border: 'none',
      cursor: 'pointer',
      display: 'flex',
      flexDirection: 'column' as const,
      alignItems: 'center',
      gap: '8px',
      boxShadow: '0 2px 8px rgba(0,0,0,0.05)'
    },
    actionIcon: {
      fontSize: '28px'
    },
    actionLabel: {
      fontSize: '13px',
      fontWeight: 600,
      color: 'black'
    },
    bottomNav: {
      display: 'flex',
      background: background,
      borderTop: '1px solid #f0f0f0',
      padding: '10px 0'
    },
    navItem: {
      flex: 1,
      textAlign: 'center' as const,
      padding: '5px',
      cursor: 'pointer',
      border: 'none',
      background: 'none',
      color: '#999'
    },
    navItemActive: {
      color: firstPrimary
    },
    navIcon: {
      fontSize: '24px',
      marginBottom: '3px'
    },
    navLabel: {
      fontSize: '11px'
    }
  }

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <div style={styles.date}>2025년 11월 12일 화요일</div>
        <div style={styles.patientInfo}>
          <div style={styles.patientAvatar}>👵</div>
          <div style={styles.patientDetails}>
            <h2 style={styles.patientDetailsH2}>김영희 어머니</h2>
            <span style={styles.statusBadge}>양호 😊</span>
          </div>
        </div>
      </div>

      <div style={styles.content}>
        <div style={styles.progressCard}>
          <h3 style={styles.progressCardH3}>📊 오늘의 진행 상황</h3>
          <div style={styles.progressBar}>
            <div style={styles.progressFill}></div>
          </div>
          <div style={styles.progressStats}>
            <span>완료: 13개</span>
            <span>진행 중: 2개</span>
            <span>예정: 5개</span>
          </div>
          <div style={styles.nextActivity}>
            <div style={styles.nextActivityIcon}>🎯</div>
            <div style={styles.nextActivityInfo}>
              <div style={styles.nextActivityTime}>다음 활동</div>
              <div style={styles.nextActivityTitle}>15:00 말벗/여가활동 - 아들 이준호</div>
            </div>
          </div>
        </div>

        <div style={styles.warningCard}>
          <h4 style={styles.warningCardH4}>⚠️ 확인 필요</h4>
          <div style={styles.warningContent}>
            혈압이 평소보다 약간 높습니다<br />
            (정상: 120/80, 현재: 135/82)
          </div>
          <div style={styles.warningButtons}>
            <button style={{...styles.warningBtn, ...styles.btnDetail}}>상세 보기</button>
            <button style={{...styles.warningBtn, ...styles.btnContact}}>간병인에게 문의</button>
          </div>
        </div>

        <div style={styles.feedCard}>
          <h3 style={styles.feedCardH3}>🔔 실시간 업데이트</h3>

          <div style={styles.feedItem}>
            <div style={styles.feedTime}>14:32 ✅ 낮잠/휴식 완료</div>
            <div style={styles.feedContent}>
              간병인: "1시간 30분 푹 주무셨어요"
            </div>
          </div>

          <div style={styles.feedItem}>
            <div style={styles.feedTime}>12:15 ✅ 점심 식사 완료</div>
            <div style={styles.feedContent}>
              간병인: "식사량 80% 완료"
            </div>
            <div style={styles.feedMeta}>📸 사진 1장</div>
          </div>

          <div style={styles.feedItem}>
            <div style={styles.feedTime}>08:05 ✅ 약 복용 완료</div>
            <div style={styles.feedContent}>
              간병인: "모든 약 복용 확인"
            </div>
            <div style={styles.feedMeta}>⚠️ 혈압: 135/82 (약간 높음)</div>
          </div>
        </div>

        <div style={styles.quickActions}>
          <button style={styles.actionBtn} onClick={() => router.push('/checklist')}>
            <div style={styles.actionIcon}>📋</div>
            <div style={styles.actionLabel}>전체 일정</div>
          </button>
          <button style={styles.actionBtn} onClick={() => router.push('/messages')}>
            <div style={styles.actionIcon}>💬</div>
            <div style={styles.actionLabel}>간병인과 대화</div>
          </button>
          <button style={styles.actionBtn} onClick={() => router.push('/report')}>
            <div style={styles.actionIcon}>📊</div>
            <div style={styles.actionLabel}>주간 리포트</div>
          </button>
          <button style={styles.actionBtn}>
            <div style={styles.actionIcon}>⚙️</div>
            <div style={styles.actionLabel}>일정 조정</div>
          </button>
        </div>
      </div>

      <div style={styles.bottomNav}>
        <button style={{...styles.navItem, ...styles.navItemActive}}>
          <div style={styles.navIcon}>🏠</div>
          <div style={styles.navLabel}>홈</div>
        </button>
        <button style={styles.navItem} onClick={() => router.push('/checklist')}>
          <div style={styles.navIcon}>📅</div>
          <div style={styles.navLabel}>일정</div>
        </button>
        <button style={styles.navItem} onClick={() => router.push('/messages')}>
          <div style={styles.navIcon}>💬</div>
          <div style={styles.navLabel}>메시지</div>
        </button>
        <button style={styles.navItem}>
          <div style={styles.navIcon}>👤</div>
          <div style={styles.navLabel}>프로필</div>
        </button>
      </div>
    </div>
  )
}
