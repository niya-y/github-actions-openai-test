"use client"

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { background, firstPrimary, secondPrimary } from '../colors'
import { apiGet, apiPost } from '@/utils/api'
import ErrorAlert from '@/components/ErrorAlert'
import type { MatchingResponse, CaregiverMatch } from '@/types/api'

export default function CaregiverResultList() {
  const router = useRouter()
  const [matches, setMatches] = useState<CaregiverMatch[]>([])
  const [totalCount, setTotalCount] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)
  const [flippedCards, setFlippedCards] = useState<{ [key: string]: boolean }>({})

  useEffect(() => {
    const fetchMatchingResults = async () => {
      // 먼저 세션 스토리지에서 매칭 결과 확인
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
          console.error('세션 스토리지 파싱 오류:', e)
        }
      }

      // API에서 직접 조회 - 실제 백엔드 엔드포인트 사용
      try {
        const response = await apiGet<any>(
          `/api/matching/results-enhanced`
        )

        // 백엔드 응답이 배열인 경우 처리
        if (Array.isArray(response)) {
          const caregiverMatches = response.map((result: any) => ({
            matching_id: result.matching_id,
            caregiver_id: result.caregiver_id,
            caregiver_name: result.caregiver_name || 'Unknown',
            grade: result.grade || '요양보호사',
            match_score: result.match_score || 0,
            experience_years: result.experience_years || 0,
            specialties: result.specialties || [],
            hourly_rate: result.hourly_rate || 0,
            avg_rating: result.avg_rating || 0,
            profile_image_url: result.profile_image_url || ''
          }))

          // 응답이 배열이면 그대로 사용 (비어있어도 상관없음)
          setMatches(caregiverMatches)
          setTotalCount(caregiverMatches.length)
        } else {
          // 응답 형식이 배열이 아니면 에러로 취급
          console.error('예상하지 못한 응답 형식:', response)
          setMatches([])
          setTotalCount(0)
        }
      } catch (err) {
        console.error('매칭 결과 조회 실패:', err)
        // 에러 시 빈 배열 표시 (실제 데이터가 없음을 명확히)
        setMatches([])
        setTotalCount(0)
      }

      setLoading(false)
    }

    fetchMatchingResults()
  }, [])

  const handleSelectCaregiver = async (caregiver: CaregiverMatch) => {
    try {
      // 1. 백엔드에 매칭 선택 API 호출 (status를 'selected'로 변경)
      if (caregiver.matching_id) {
        const response = await apiPost<any>(
          `/api/matching/${caregiver.matching_id}/select`,
          {}
        )
        console.log('[Caregiver Result List] Caregiver selected:', response)
      }

      // 2. sessionStorage에 저장
      sessionStorage.setItem('selectedCaregiver', JSON.stringify(caregiver))
      if (caregiver.matching_id) {
        sessionStorage.setItem('matching_id', caregiver.matching_id.toString())
      }

      // 3. 페이지 이동
      router.push('/mypage-mycaregiver')
    } catch (err) {
      console.error('[Caregiver Result List] Failed to select caregiver:', err)
      // 에러가 나도 계속 진행 (sessionStorage 저장은 됨)
      sessionStorage.setItem('selectedCaregiver', JSON.stringify(caregiver))
      if (caregiver.matching_id) {
        sessionStorage.setItem('matching_id', caregiver.matching_id.toString())
      }
      router.push('/mypage-mycaregiver')
    }
  }

  const handleCardClick = (id: string) => {
    setFlippedCards(prev => ({
      ...prev,
      [id]: !prev[id]
    }))
  }

  const getAvatarEmoji = (name: string) => {
    // 이름에 따라 다른 아바타 표시
    if (name.includes('미숙') || name.includes('은영')) return '👩‍⚕️'
    return '👨‍⚕️'
  }

  const getGradeStars = (grade: string) => {
    // 등급에 따른 별 개수 (A=3, B=2, C=1)
    if (grade === 'A') return '⭐⭐⭐'
    if (grade === 'B') return '⭐⭐'
    if (grade === 'C') return '⭐'
    return '⭐'
  }

  const styles = {
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
      background: 'transparent',
      marginBottom: '15px',
      perspective: '1000px',
      height: '400px', // 고정 높이 필요
      cursor: 'pointer'
    },
    cardInner: (isFlipped: boolean) => ({
      position: 'relative' as const,
      width: '100%',
      height: '100%',
      textAlign: 'left' as const,
      transition: 'transform 0.6s',
      transformStyle: 'preserve-3d' as const,
      transform: isFlipped ? 'rotateY(180deg)' : 'rotateY(0deg)',
    }),
    cardFront: {
      position: 'absolute' as const,
      width: '100%',
      height: '100%',
      backfaceVisibility: 'hidden' as const,
      background: 'white',
      borderRadius: '15px',
      padding: '20px',
      boxShadow: '0 2px 8px rgba(0,0,0,0.05)',
      display: 'flex',
      flexDirection: 'column' as const
    },
    cardBack: {
      position: 'absolute' as const,
      width: '100%',
      height: '100%',
      backfaceVisibility: 'hidden' as const,
      background: 'white',
      borderRadius: '15px',
      padding: '20px',
      boxShadow: '0 2px 8px rgba(0,0,0,0.05)',
      transform: 'rotateY(180deg)',
      display: 'flex',
      flexDirection: 'column' as const,
      overflowY: 'auto' as const
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
    ratingCount: {
      color: '#999'
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
      <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', background: background }}>
        <div style={styles.navBar}>
          <button style={styles.backBtn} onClick={() => router.push('/caregiver-finder')}>‹</button>
          <div style={styles.navTitle}>추천 간병인</div>
          <button style={styles.filterBtn}>⚙️</button>
        </div>
        <div style={styles.loadingContainer}>
          매칭 결과를 불러오는 중...
        </div>
      </div>
    )
  }

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', background: background }}>
      <ErrorAlert error={error} onClose={() => setError(null)} />

      <div style={styles.navBar}>
        <button style={styles.backBtn} onClick={() => router.push('/caregiver-finder')}>‹</button>
        <div style={styles.navTitle}>추천 간병인</div>
        <button style={styles.filterBtn}>⚙️</button>
      </div>

      <div style={styles.header}>
        <h2 style={styles.h2}>환자분에게 적합한 간병인</h2>
        <p style={styles.p}>{totalCount}명의 전문가를 찾았습니다</p>
      </div>

      <div style={styles.content}>
        {matches.length === 0 ? (
          <div style={styles.loadingContainer}>
            매칭된 간병인이 없습니다.
          </div>
        ) : (
          matches.map((caregiver, index) => {
            const id = caregiver.matching_id?.toString() || index.toString()
            const isFlipped = flippedCards[id] || false

            return (
              <div key={id} style={styles.caregiverCard} onClick={() => handleCardClick(id)}>
                <div style={styles.cardInner(isFlipped)}>
                  {/* 앞면 */}
                  <div style={styles.cardFront}>
                    <div style={styles.caregiverHeader}>
                      <div style={styles.caregiverAvatar}>
                        {caregiver.profile_image_url ? (
                          <img
                            src={caregiver.profile_image_url}
                            alt={caregiver.caregiver_name}
                            style={{ width: '100%', height: '100%', borderRadius: '50%', objectFit: 'cover' }}
                          />
                        ) : (
                          getAvatarEmoji(caregiver.caregiver_name)
                        )}
                      </div>
                      <div style={styles.caregiverInfo}>
                        <div style={styles.nameRating}>
                          <span style={styles.caregiverName}>{caregiver.caregiver_name}</span>
                        </div>
                        <div style={styles.rating}>
                          <span style={styles.star}>⭐</span>
                          <span>{caregiver.avg_rating}</span>
                        </div>
                        <div style={{ marginTop: '8px' }}>
                          <span style={{ fontSize: '14px' }}>{getGradeStars(caregiver.grade)}</span>
                        </div>
                        <div style={styles.experience}>경력 {caregiver.experience_years}년</div>
                      </div>
                    </div>

                    <div style={styles.caregiverBody}>
                      <div style={styles.specialtyTags}>
                        {caregiver.specialties?.map((specialty, i) => (
                          <span key={i} style={styles.specialtyTag}>{specialty}</span>
                        ))}
                      </div>
                      <div style={styles.matchInfo}>
                        <div style={styles.matchIcon}>✨</div>
                        <div style={styles.matchText}>
                          <div style={styles.matchScore}>{caregiver.match_score}% 매칭</div>
                          <div style={styles.matchDetail}>▼ 매칭 근거 보기</div>
                        </div>
                      </div>
                    </div>

                    <div style={{ marginTop: 'auto' }}>
                      <div style={styles.caregiverFooter}>
                        <div style={styles.rate}>{caregiver.hourly_rate.toLocaleString()}원/시간</div>
                        <button
                          style={styles.actionBtn}
                          onClick={(e) => {
                            e.stopPropagation()
                            handleCardClick(id)
                          }}
                        >
                          상세 보기
                        </button>
                        <button
                          style={{ ...styles.actionBtn, ...styles.actionBtnPrimary }}
                          onClick={(e) => {
                            e.stopPropagation()
                            handleSelectCaregiver(caregiver)
                          }}
                        >
                          선택
                        </button>
                      </div>
                    </div>
                  </div>

                  {/* 뒷면 (상세 정보) */}
                  <div style={styles.cardBack}>
                    <h3 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '15px' }}>상세 프로필</h3>
                    <div style={{ marginBottom: '10px' }}>
                      <div style={{ fontSize: '14px', color: '#666', marginBottom: '5px' }}>자기소개</div>
                      <div style={{ fontSize: '15px', lineHeight: 1.6 }}>
                        안녕하세요, {caregiver.caregiver_name}입니다.
                        {caregiver.experience_years}년의 경력으로 환자분을 가족처럼 돌보겠습니다.
                      </div>
                    </div>
                    <div style={{ marginBottom: '10px' }}>
                      <div style={{ fontSize: '14px', color: '#666', marginBottom: '5px' }}>전문 분야</div>
                      <div style={styles.specialtyTags}>
                        {caregiver.specialties?.map((specialty, i) => (
                          <span key={i} style={styles.specialtyTag}>{specialty}</span>
                        ))}
                      </div>
                    </div>
                    <div style={{ marginTop: 'auto' }}>
                      <button
                        style={{ ...styles.actionBtn, width: '100%' }}
                        onClick={(e) => {
                          e.stopPropagation()
                          handleCardClick(id)
                        }}
                      >
                        돌아가기
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            )
          })
        )}
      </div>

      <div style={styles.bottomSection}>
        <button style={styles.showMoreBtn}>더 많은 간병인 보기</button>
        <button style={styles.skipBtn} onClick={() => router.push('/care-plans-create-1')}>
          간병인 없이 진행하기
        </button>
      </div>
    </div>
  )
}
