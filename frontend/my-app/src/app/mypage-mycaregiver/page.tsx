'use client'

import { useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'
import { background, firstPrimary, secondPrimary } from '@/app/colors'

interface Caregiver {
  caregiver_id?: number
  caregiver_name?: string
  name?: string
  age?: number
  rating?: number
  avg_rating?: number
  reviews?: number
  certification?: string
  job_title?: string
  experience?: string
  experience_years?: number
  specialties?: string[]
  intro?: string
  matchScore?: number
  match_score?: number
  rate?: number
  hourly_rate?: number
  avatar?: string
  profile_image_url?: string
}

export default function MyMatchingConfirmedPage() {
  const router = useRouter()
  const [caregiver, setCaregiver] = useState<Caregiver | null>(null)
  const [showBanner, setShowBanner] = useState(true)

  useEffect(() => {
    // Retrieve selected caregiver from session storage
    const stored = sessionStorage.getItem('selectedCaregiver')
    if (stored) {
      setCaregiver(JSON.parse(stored))
    }

    // Auto-hide banner after 5 seconds
    const timer = setTimeout(() => {
      setShowBanner(false)
    }, 5000)

    return () => clearTimeout(timer)
  }, [])

  const styles = {
    container: {
      minHeight: 'calc(100vh - 64px - 80px)',
      background: background,
      display: 'flex',
      flexDirection: 'column' as const,
      paddingBottom: '100px'
    },
    navBar: {
      display: 'flex',
      alignItems: 'center',
      padding: '15px 20px',
      borderBottom: '1px solid #f0f0f0'
    },
    backBtn: {
      fontSize: '20px',
      cursor: 'pointer',
      color: firstPrimary,
      background: 'none',
      border: 'none'
    },
    navTitle: {
      flex: 1,
      textAlign: 'center' as const,
      fontWeight: 600,
      fontSize: '17px'
    },
    content: {
      flex: 1,
      overflowY: 'auto' as const,
      padding: '20px'
    },
    matchedBanner: {
      position: 'fixed' as const,
      top: '64px',
      left: '50%',
      transform: 'translateX(-50%)',
      width: 'calc(100% - 20px)',
      maxWidth: '320px',
      background: '#d1fae5',
      border: `1px solid #10b981`,
      borderRadius: '8px',
      padding: '12px 15px',
      textAlign: 'center' as const,
      zIndex: 1000,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      gap: '10px',
      boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
      margin: '8px auto 0',
      animation: 'slideDown 0.5s ease-out forwards'
    },
    bannerCloseBtn: {
      background: 'none',
      border: 'none',
      fontSize: '18px',
      cursor: 'pointer',
      color: '#065f46',
      padding: '0',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      flexShrink: 0
    },
    bannerContent: {
      flex: 1,
      display: 'flex',
      flexDirection: 'column' as const,
      alignItems: 'center',
      gap: '4px'
    },
    matchedIcon: {
      fontSize: '28px'
    },
    matchedTitle: {
      fontSize: '14px',
      fontWeight: 700,
      color: '#065f46'
    },
    matchedDesc: {
      fontSize: '12px',
      color: '#047857'
    },
    caregiverCard: {
      background: 'white',
      borderRadius: '15px',
      padding: '20px',
      boxShadow: '0 2px 8px rgba(0,0,0,0.05)',
      marginBottom: '20px'
    },
    caregiverHeader: {
      display: 'flex',
      gap: '15px',
      marginBottom: '15px',
      paddingBottom: '15px',
      borderBottom: '1px solid #f0f0f0'
    },
    caregiverAvatar: {
      width: '80px',
      height: '80px',
      borderRadius: '40px',
      background: '#f0f4ff',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      fontSize: '40px',
      flexShrink: 0
    },
    caregiverInfo: {
      flex: 1,
      display: 'flex',
      flexDirection: 'column' as const,
      justifyContent: 'center'
    },
    caregiverName: {
      fontSize: '20px',
      fontWeight: 700,
      color: '#333',
      marginBottom: '4px'
    },
    caregiverMeta: {
      display: 'flex',
      alignItems: 'center',
      gap: '8px',
      marginBottom: '8px',
      fontSize: '14px'
    },
    rating: {
      color: secondPrimary,
      fontWeight: 600
    },
    certBadge: {
      display: 'inline-block',
      padding: '4px 10px',
      background: '#dbeafe',
      color: '#1e40af',
      borderRadius: '12px',
      fontSize: '12px',
      fontWeight: 600
    },
    experienceText: {
      fontSize: '13px',
      color: '#666'
    },
    caregiverBody: {
      marginBottom: '15px'
    },
    intro: {
      fontSize: '14px',
      color: '#555',
      lineHeight: 1.6,
      marginBottom: '12px',
      fontStyle: 'italic'
    },
    specialties: {
      display: 'flex',
      flexWrap: 'wrap' as const,
      gap: '8px'
    },
    specialtyTag: {
      padding: '6px 12px',
      background: '#f0f4ff',
      color: firstPrimary,
      borderRadius: '12px',
      fontSize: '12px'
    },
    matchScore: {
      background: '#fce7f3',
      border: `1px solid ${secondPrimary}`,
      padding: '15px',
      borderRadius: '10px',
      textAlign: 'center' as const,
      marginTop: '15px'
    },
    matchScoreValue: {
      fontSize: '28px',
      fontWeight: 700,
      color: secondPrimary,
      marginBottom: '4px'
    },
    matchScoreLabel: {
      fontSize: '13px',
      color: secondPrimary
    },
    rateInfo: {
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      background: '#f9fafb',
      padding: '12px 15px',
      borderRadius: '10px',
      marginTop: '12px'
    },
    rateLabel: {
      fontSize: '13px',
      color: '#666'
    },
    rateValue: {
      fontSize: '16px',
      fontWeight: 700,
      color: firstPrimary
    },
    actionSection: {
      marginBottom: '20px'
    },
    sectionTitle: {
      fontSize: '16px',
      fontWeight: 600,
      color: '#333',
      marginBottom: '12px'
    },
    actionButtons: {
      display: 'flex',
      flexDirection: 'column' as const,
      gap: '10px'
    },
    actionBtn: {
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      gap: '10px',
      padding: '15px',
      borderRadius: '12px',
      border: 'none',
      fontSize: '15px',
      fontWeight: 600,
      cursor: 'pointer',
      transition: 'all 0.3s'
    },
    actionBtnPrimary: {
      background: firstPrimary,
      color: 'white'
    },
    actionBtnSecondary: {
      background: 'white',
      color: firstPrimary,
      border: `2px solid ${firstPrimary}`
    },
    infoCard: {
      background: 'white',
      borderRadius: '12px',
      padding: '16px',
      marginTop: '15px',
      fontSize: '13px',
      color: '#666',
      lineHeight: 1.6,
      boxShadow: '0 2px 4px rgba(0,0,0,0.05)'
    },
    infoCardTitle: {
      fontWeight: 600,
      color: '#333',
      marginBottom: '8px'
    },
    infoBullet: {
      marginBottom: '6px'
    }
  }

  return (
    <>
      <style>
        {`
          @keyframes slideDown {
            from {
              opacity: 0;
              transform: translateX(-50%) translateY(-20px);
            }
            to {
              opacity: 1;
              transform: translateX(-50%) translateY(0);
            }
          }
        `}
      </style>
      <div style={styles.container}>
        <div style={styles.navBar}>
        <button style={styles.backBtn} onClick={() => router.back()}>←</button>
        <div style={styles.navTitle}>매칭 확인</div>
        <div style={{width: '20px'}}></div>
      </div>

      <div style={styles.content}>
        {/* Matched Banner - Toast Notification */}
        {showBanner && (
          <div style={styles.matchedBanner}>
            <div style={styles.bannerContent}>
              <div style={styles.matchedIcon}>✅</div>
              <div style={styles.matchedTitle}>매칭되었습니다!</div>
              <div style={styles.matchedDesc}>간병인과의 관계가 시작되었습니다</div>
            </div>
            <button
              style={styles.bannerCloseBtn}
              onClick={() => setShowBanner(false)}
            >
              ✕
            </button>
          </div>
        )}

        {/* Add padding to content when banner is shown */}
        <div style={{paddingTop: showBanner ? '140px' : '0'}}></div>

        {/* Caregiver Card */}
        {caregiver && (
          <div style={styles.caregiverCard}>
            <div style={styles.caregiverHeader}>
              <div style={styles.caregiverAvatar}>{caregiver.avatar || caregiver.profile_image_url || '👨‍⚕️'}</div>
              <div style={styles.caregiverInfo}>
                <div style={styles.caregiverName}>{caregiver.name || caregiver.caregiver_name}</div>
                <div style={styles.caregiverMeta}>
                  <span style={styles.rating}>⭐ {caregiver.rating || caregiver.avg_rating || 4.5}</span>
                  <span style={{color: '#999'}}>({caregiver.reviews || 0}건)</span>
                </div>
                <span style={styles.certBadge}>{caregiver.certification || caregiver.job_title || '요양보호사'}</span>
                <div style={styles.experienceText}>{caregiver.experience || `경력 ${caregiver.experience_years || 0}년`}</div>
              </div>
            </div>

            <div style={styles.caregiverBody}>
              <div style={styles.intro}>&ldquo;{caregiver.intro || '친절하고 성실한 간병을 제공하겠습니다.'}&rdquo;</div>
              <div style={styles.specialties}>
                {(caregiver.specialties && caregiver.specialties.length > 0) ? (
                  caregiver.specialties.map((specialty, i) => (
                    <span key={i} style={styles.specialtyTag}>{specialty}</span>
                  ))
                ) : (
                  <span style={styles.specialtyTag}>기본 돌봄</span>
                )}
              </div>
            </div>

            <div style={styles.matchScore}>
              <div style={styles.matchScoreValue}>{caregiver.matchScore || caregiver.match_score || 0}%</div>
              <div style={styles.matchScoreLabel}>매칭 일치도</div>
            </div>

            <div style={styles.rateInfo}>
              <span style={styles.rateLabel}>시간당 요금</span>
              <span style={styles.rateValue}>
                {(caregiver.rate || caregiver.hourly_rate || 0) > 0
                  ? `${(caregiver.rate || caregiver.hourly_rate).toLocaleString()}원`
                  : '문의'}
              </span>
            </div>
          </div>
        )}

        {/* Action Section */}
        <div style={styles.actionSection}>
          <div style={styles.sectionTitle}>다음 단계</div>
          <div style={styles.actionButtons}>
            <button
              style={{...styles.actionBtn, ...styles.actionBtnPrimary}}
              onClick={() => router.push('/care-plans-create-1')}
            >
              <span>📅</span>
              AI 맞춤 케어 일정 만들기
            </button>
            <button
              style={{...styles.actionBtn, ...styles.actionBtnSecondary}}
              onClick={() => router.push('/mypage')}
            >
              <span>💬</span>
              간병인과 채팅하기
            </button>
          </div>
        </div>

        {/* Info Card */}
        <div style={styles.infoCard}>
          <div style={styles.infoCardTitle}>📋 매칭 후 절차</div>
          <div style={styles.infoBullet}>1️⃣ 간병인과 채팅으로 세부사항 조율</div>
          <div style={styles.infoBullet}>2️⃣ AI가 추천하는 케어 플랜 검토</div>
          <div style={styles.infoBullet}>3️⃣ 케어 시작 날짜 확정</div>
          <div style={styles.infoBullet}>4️⃣ 케어 진행 상황 모니터링</div>
        </div>
      </div>
    </div>
    </>
  )
}
