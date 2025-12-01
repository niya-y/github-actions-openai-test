"use client"

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { background, firstPrimary, secondPrimary } from '../colors'
import { apiGet } from '@/utils/api'
import ErrorAlert from '@/components/ErrorAlert'
import type { MatchingResponse, CaregiverMatch } from '@/types/api'

export default function MatchingPage() {
  const router = useRouter()
  const [matches, setMatches] = useState<CaregiverMatch[]>([])
  const [totalCount, setTotalCount] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  // Default caregiver data (fallback when API returns no data)
  const defaultCaregivers: CaregiverMatch[] = [
    {
      matching_id: 1,
      caregiver_id: 1,
      caregiver_name: '김미숙',
      grade: '요양보호사 1급',
      match_score: 92,
      experience_years: 8,
      specialties: ['치매 케어', '당뇨 관리', '고혈압 관리'],
      hourly_rate: 25000,
      avg_rating: 4.9,
      profile_image_url: ''
    },
    {
      matching_id: 2,
      caregiver_id: 2,
      caregiver_name: '이정호',
      grade: '요양보호사 1급',
      match_score: 88,
      experience_years: 6,
      specialties: ['치매 케어', '재활 운동'],
      hourly_rate: 23000,
      avg_rating: 4.8,
      profile_image_url: ''
    },
    {
      matching_id: 3,
      caregiver_id: 3,
      caregiver_name: '박은영',
      grade: '요양보호사 1급',
      match_score: 85,
      experience_years: 12,
      specialties: ['당뇨 관리', '식사 케어', '투약 관리'],
      hourly_rate: 27000,
      avg_rating: 4.7,
      profile_image_url: ''
    }
  ]

  useEffect(() => {
    const fetchMatches = async () => {
      // Check session storage for matching results first
      const storedResults = sessionStorage.getItem('matching_results')
      if (storedResults) {
        try {
          const parsed: MatchingResponse = JSON.parse(storedResults)
          if (parsed.matches && parsed.matches.length > 0) {
            setMatches(parsed.matches)
            setTotalCount(parsed.total_count)
            setLoading(false)
            return
          }
        } catch (e) {
          console.error('Session storage parsing error:', e)
        }
      }

      // Fetch from API
      const patientId = sessionStorage.getItem('selected_patient_id')
      if (patientId) {
        try {
          const response = await apiGet<MatchingResponse>(
            `/api/patients/${patientId}/matching-results?status=recommended`
          )

          if (response.matches && response.matches.length > 0) {
            setMatches(response.matches)
            setTotalCount(response.total_count)
          } else {
            // Use default data if API returns empty
            setMatches(defaultCaregivers)
            setTotalCount(defaultCaregivers.length)
          }
        } catch (err) {
          console.error('Failed to fetch matching results:', err)
          // Use default data on error
          setMatches(defaultCaregivers)
          setTotalCount(defaultCaregivers.length)
        }
      } else {
        // No patient_id, use default data
        setMatches(defaultCaregivers)
        setTotalCount(defaultCaregivers.length)
      }

      setLoading(false)
    }

    fetchMatches()
  }, [])

  const handleSelectCaregiver = (caregiver: CaregiverMatch) => {
    sessionStorage.setItem('selectedCaregiver', JSON.stringify(caregiver))
    sessionStorage.setItem('matching_id', caregiver.matching_id.toString())
    router.push('/care-plans-create-1')
  }

  const getAvatarEmoji = (name: string) => {
    if (name.includes('미숙') || name.includes('은영')) return '👩‍⚕️'
    return '👨‍⚕️'
  }

  const styles = {
    container: {
      minHeight: '100vh',
      display: 'flex',
      flexDirection: 'column' as const,
      background: background
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
    filterBtn: {
      fontSize: '20px',
      cursor: 'pointer',
      color: firstPrimary,
      background: 'none',
      border: 'none'
    },
    header: {
      padding: '20px',
      background: background,
      borderBottom: '1px solid #f0f0f0'
    },
    h2: {
      fontSize: '22px',
      color: '#333',
      marginBottom: '5px'
    },
    p: {
      fontSize: '14px',
      color: '#666'
    },
    content: {
      flex: 1,
      overflowY: 'auto' as const,
      padding: '15px',
      background: background
    },
    caregiverCard: {
      background: 'white',
      borderRadius: '15px',
      padding: '20px',
      marginBottom: '15px',
      boxShadow: '0 2px 8px rgba(0,0,0,0.05)'
    },
    caregiverHeader: {
      display: 'flex',
      gap: '15px',
      marginBottom: '15px',
      paddingBottom: '15px',
      borderBottom: '1px solid #f0f0f0'
    },
    caregiverAvatar: {
      width: '70px',
      height: '70px',
      borderRadius: '35px',
      background: background,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      fontSize: '36px',
      flexShrink: 0
    },
    caregiverInfo: {
      flex: 1
    },
    nameRating: {
      display: 'flex',
      alignItems: 'center',
      gap: '8px',
      marginBottom: '5px'
    },
    caregiverName: {
      fontSize: '18px',
      fontWeight: 600,
      color: '#333'
    },
    rating: {
      display: 'flex',
      alignItems: 'center',
      gap: '4px',
      fontSize: '14px'
    },
    star: {
      color: secondPrimary
    },
    certificationBadge: {
      display: 'inline-block',
      padding: '4px 10px',
      background: '#dbeafe',
      color: '#1e40af',
      borderRadius: '12px',
      fontSize: '12px',
      fontWeight: 600,
      marginRight: '6px'
    },
    experience: {
      fontSize: '13px',
      color: '#666',
      marginTop: '5px'
    },
    caregiverBody: {
      marginBottom: '15px'
    },
    specialtyTags: {
      display: 'flex',
      flexWrap: 'wrap' as const,
      gap: '6px',
      marginBottom: '12px'
    },
    specialtyTag: {
      padding: '6px 12px',
      background: '#f0f4ff',
      color: firstPrimary,
      borderRadius: '12px',
      fontSize: '12px'
    },
    matchInfo: {
      background: '#fce7f3',
      border: `1px solid ${secondPrimary}`,
      padding: '12px',
      borderRadius: '10px',
      display: 'flex',
      alignItems: 'center',
      gap: '10px'
    },
    matchIcon: {
      fontSize: '24px'
    },
    matchText: {
      flex: 1
    },
    matchScore: {
      fontSize: '18px',
      fontWeight: 700,
      color: secondPrimary
    },
    matchDetail: {
      fontSize: '11px',
      color: secondPrimary,
      cursor: 'pointer'
    },
    caregiverFooter: {
      display: 'flex',
      gap: '10px'
    },
    rate: {
      fontSize: '16px',
      fontWeight: 700,
      color: firstPrimary,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '0 10px'
    },
    actionBtn: {
      flex: 1,
      padding: '12px',
      borderRadius: '10px',
      border: '1px solid #e0e0e0',
      background: 'white',
      fontSize: '14px',
      fontWeight: 600,
      cursor: 'pointer',
      color: '#333'
    },
    actionBtnPrimary: {
      background: firstPrimary,
      color: 'white',
      borderColor: firstPrimary
    },
    bottomSection: {
      padding: '15px 20px',
      background: background,
      borderTop: '1px solid #f0f0f0'
    },
    showMoreBtn: {
      width: '100%',
      padding: '12px',
      background: '#f9fafb',
      color: firstPrimary,
      border: '1px solid #e0e0e0',
      borderRadius: '10px',
      fontSize: '14px',
      fontWeight: 600,
      cursor: 'pointer',
      marginBottom: '10px'
    },
    skipBtn: {
      width: '100%',
      padding: '12px',
      background: 'white',
      color: '#999',
      border: 'none',
      fontSize: '14px',
      cursor: 'pointer'
    },
    loadingContainer: {
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      height: '200px',
      fontSize: '16px',
      color: '#666'
    }
  }

  if (loading) {
    return (
      <div style={styles.container}>
        <div style={styles.navBar}>
          <button style={styles.backBtn} onClick={() => router.push('/caregiver-finder')}>‹</button>
          <div style={styles.navTitle}>AI 추천 간병인</div>
          <button style={styles.filterBtn}>⚙️</button>
        </div>
        <div style={styles.loadingContainer}>
          로딩 중...
        </div>
      </div>
    )
  }

  return (
    <div style={styles.container}>
      <ErrorAlert error={error} onClose={() => setError(null)} />

      <div style={styles.navBar}>
        <button style={styles.backBtn} onClick={() => router.push('/caregiver-finder')}>‹</button>
        <div style={styles.navTitle}>AI 추천 간병인</div>
        <button style={styles.filterBtn}>⚙️</button>
      </div>

      <div style={styles.header}>
        <h2 style={styles.h2}>AI 추천 간병인 ({totalCount}명)</h2>
        <p style={styles.p}>환자 상태에 맞는 최적의 간병인을 추천해드립니다</p>
      </div>

      <div style={styles.content}>
        {matches.length === 0 ? (
          <div style={styles.loadingContainer}>
            매칭 결과가 없습니다.
          </div>
        ) : (
          matches.map((match) => (
            <div key={match.matching_id} style={styles.caregiverCard}>
              <div style={styles.caregiverHeader}>
                <div style={styles.caregiverAvatar}>
                  {match.profile_image_url ? (
                    <img
                      src={match.profile_image_url}
                      alt={match.caregiver_name}
                      style={{ width: '100%', height: '100%', borderRadius: '50%', objectFit: 'cover' }}
                    />
                  ) : (
                    getAvatarEmoji(match.caregiver_name)
                  )}
                </div>
                <div style={styles.caregiverInfo}>
                  <div style={styles.nameRating}>
                    <span style={styles.caregiverName}>{match.caregiver_name}</span>
                  </div>
                  <div style={styles.rating}>
                    <span style={styles.star}>⭐</span>
                    <span>{match.avg_rating}/5.0</span>
                  </div>
                  <div style={{ marginTop: '8px' }}>
                    <span style={styles.certificationBadge}>{match.grade}</span>
                  </div>
                  <div style={styles.experience}>경력 {match.experience_years}년</div>
                </div>
              </div>

              <div style={styles.caregiverBody}>
                <div style={styles.specialtyTags}>
                  {match.specialties.map((specialty, i) => (
                    <span key={i} style={styles.specialtyTag}>{specialty}</span>
                  ))}
                </div>
                <div style={styles.matchInfo}>
                  <div style={styles.matchIcon}>✨</div>
                  <div style={styles.matchText}>
                    <div style={styles.matchScore}>{match.match_score}% 매칭</div>
                    <div style={styles.matchDetail}>▼ 매칭 근거 보기</div>
                  </div>
                </div>
              </div>

              <div style={styles.caregiverFooter}>
                <div style={styles.rate}>{match.hourly_rate.toLocaleString()}원/시간</div>
                <button style={styles.actionBtn}>프로필 보기</button>
                <button
                  style={{ ...styles.actionBtn, ...styles.actionBtnPrimary }}
                  onClick={() => handleSelectCaregiver(match)}
                >
                  선택하기
                </button>
              </div>
            </div>
          ))
        )}
      </div>

      <div style={styles.bottomSection}>
        <button style={styles.showMoreBtn}>더 많은 간병인 보기</button>
        <button style={styles.skipBtn} onClick={() => router.push('/care-plans-create-1')}>
          나중에 결정하기
        </button>
      </div>
    </div>
  )
}
