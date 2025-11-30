"use client"

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { background, firstPrimary } from '../colors'
import { apiPost } from '@/utils/api'
import ErrorAlert from '@/components/ErrorAlert'
import type { ReviewCreateRequest, ReviewResponse } from '@/types/api'

export default function Screen10CaregiverReview() {
  const router = useRouter()
  const [selectedFeedback, setSelectedFeedback] = useState('adjustment')
  const [selectedReason, setSelectedReason] = useState('order')
  const [suggestion, setSuggestion] = useState('약 복용은 식사 후 30분 뒤에 하는 것이 더 좋습니다. 메트포민은 공복에 먹으면 속이 불편할 수 있습니다.')
  const [alternativeTime, setAlternativeTime] = useState('08:30')
  const [overallFeedback, setOverallFeedback] = useState('전반적으로 잘 구성되었으나, 오전에 활동이 너무 집중되어 있습니다. 환자분이 쉽게 피로해하실 수 있으니 휴식 시간을 더 확보하시는 것을 추천드립니다.')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<Error | null>(null)

  // 피드백을 점수로 변환
  const feedbackToRating = (feedback: string): number => {
    switch (feedback) {
      case 'appropriate': return 5
      case 'adjustment': return 4
      case 'suggestion': return 3
      case 'inappropriate': return 1
      default: return 3
    }
  }

  const handleSubmit = async () => {
    const matchingId = sessionStorage.getItem('matching_id')
    if (!matchingId) {
      alert('매칭 정보를 찾을 수 없습니다.')
      router.push('/caregiver-result-list')
      return
    }

    setLoading(true)
    setError(null)

    try {
      const rating = feedbackToRating(selectedFeedback)
      const comment = `[${selectedReason}] ${suggestion}\n\n전체 의견: ${overallFeedback}`

      const payload: ReviewCreateRequest = {
        rating: rating,
        comment: comment
      }

      const response = await apiPost<ReviewResponse>(
        `/api/matching/${matchingId}/reviews`,
        payload
      )

      console.log('리뷰 등록 성공:', response)

      // 리뷰 ID를 세션 스토리지에 저장
      sessionStorage.setItem('review_id', response.review_id.toString())

      router.push('/care-plans-create-4')
    } catch (err) {
      console.error('리뷰 등록 실패:', err)
      setError(err as Error)
    } finally {
      setLoading(false)
    }
  }

  const styles = {
    container: {
      minHeight: '100vh',
      background: background,
      display: 'flex',
      flexDirection: 'column' as const
    },
    navBar: {
      display: 'flex',
      alignItems: 'center',
      padding: '15px 20px',
      borderBottom: '1px solid #f0f0f0',
      background: 'white'
    },
    backBtn: {
      fontSize: '20px',
      cursor: 'pointer',
      color: 'black',
      background: 'none',
      border: 'none'
    },
    navTitle: {
      flex: 1,
      textAlign: 'center' as const,
      fontWeight: 600,
      fontSize: '17px',
      color: 'black'
    },
    patientCard: {
      background: 'white',
      color: 'black',
      padding: '20px',
      margin: '15px',
      borderRadius: '15px'
    },
    patientCardH3: {
      fontSize: '18px',
      marginBottom: '8px'
    },
    patientCardP: {
      fontSize: '13px',
      opacity: 0.9
    },
    content: {
      flex: 1,
      overflowY: 'auto' as const,
      padding: '0 15px 20px'
    },
    activityReview: {
      background: 'white',
      borderRadius: '12px',
      padding: '15px',
      marginBottom: '15px',
      border: '1px solid #e0e0e0'
    },
    activityHeader: {
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      marginBottom: '12px',
      paddingBottom: '12px',
      borderBottom: '1px solid #f0f0f0'
    },
    activityTimeTitle: {
      fontWeight: 600,
      color: 'black'
    },
    activityDetails: {
      fontSize: '13px',
      color: 'black',
      marginBottom: '12px'
    },
    feedbackOptions: {
      display: 'grid',
      gridTemplateColumns: 'repeat(2, 1fr)',
      gap: '8px',
      marginBottom: '12px'
    },
    feedbackBtn: {
      padding: '10px',
      borderRadius: '8px',
      border: '2px solid #e0e0e0',
      background: 'white',
      fontSize: '13px',
      cursor: 'pointer',
      display: 'flex',
      alignItems: 'center',
      gap: '5px',
      transition: 'all 0.2s',
      color: 'black'
    },
    feedbackBtnSelected: {
      background: firstPrimary,
      color: 'white',
      borderColor: firstPrimary
    },
    feedbackDetail: {
      marginTop: '12px',
      padding: '12px',
      background: '#f9f9f9',
      borderRadius: '8px'
    },
    feedbackDetailH4: {
      fontSize: '13px',
      marginBottom: '8px',
      color: 'black'
    },
    reasonOptions: {
      display: 'flex',
      flexDirection: 'column' as const,
      gap: '8px',
      marginBottom: '12px'
    },
    reasonOption: {
      display: 'flex',
      alignItems: 'center',
      gap: '8px',
      fontSize: '13px',
      color: 'black'
    },
    reasonRadio: {
      accentColor: firstPrimary
    },
    textarea: {
      width: '100%',
      padding: '10px',
      border: '1px solid #e0e0e0',
      borderRadius: '8px',
      fontSize: '13px',
      fontFamily: 'inherit',
      resize: 'vertical' as const,
      minHeight: '60px',
      boxSizing: 'border-box' as const,
      color: 'black'
    },
    timeSuggest: {
      display: 'flex',
      alignItems: 'center',
      gap: '10px',
      marginTop: '8px'
    },
    timeInput: {
      padding: '8px',
      border: '1px solid #e0e0e0',
      borderRadius: '6px',
      fontSize: '14px',
      color: 'black'
    },
    overallFeedback: {
      background: 'white',
      borderRadius: '12px',
      padding: '15px',
      marginBottom: '15px',
      border: `2px solid ${firstPrimary}`
    },
    overallFeedbackH3: {
      fontSize: '16px',
      marginBottom: '12px',
      color: 'black'
    },
    badge: {
      display: 'inline-block',
      padding: '4px 8px',
      background: '#fef3c7',
      color: '#92400e',
      borderRadius: '4px',
      fontSize: '11px',
      fontWeight: 600
    },
    bottomBar: {
      padding: '15px 20px',
      background: background,
      borderTop: '1px solid #f0f0f0',
      display: 'flex',
      gap: '10px'
    },
    btn: {
      flex: 1,
      padding: '15px',
      borderRadius: '8px',
      border: 'none',
      fontWeight: 600,
      cursor: 'pointer',
      fontSize: '15px'
    },
    btnSecondary: {
      background: '#f0f0f0',
      color: 'black'
    },
    btnPrimary: {
      background: firstPrimary,
      color: 'white'
    },
    btnDisabled: {
      opacity: 0.5,
      cursor: 'not-allowed'
    }
  }

  return (
    <div style={styles.container}>
      <ErrorAlert error={error} onClose={() => setError(null)} />

      <div style={styles.navBar}>
        <button style={styles.backBtn} onClick={() => router.push('/care-plans-create-2')}>‹</button>
        <div style={styles.navTitle}>케어 플랜 검토</div>
        <div style={{ width: '20px' }}></div>
      </div>

      <div style={styles.patientCard}>
        <h3 style={styles.patientCardH3}>케어 플랜 리뷰</h3>
        <p style={styles.patientCardP}>케어 플랜에 대한 의견을 남겨주세요</p>
      </div>

      <div style={styles.content}>
        <div style={styles.activityReview}>
          <div style={styles.activityHeader}>
            <div style={styles.activityTimeTitle}>08:00 약 복용 확인</div>
          </div>
          <div style={styles.activityDetails}>
            아스피린 100mg, 메트포민 500mg
          </div>

          <div style={styles.feedbackOptions}>
            <button
              style={{
                ...styles.feedbackBtn,
                ...(selectedFeedback === 'appropriate' ? styles.feedbackBtnSelected : {})
              }}
              onClick={() => setSelectedFeedback('appropriate')}
            >
              적절함
            </button>
            <button
              style={{
                ...styles.feedbackBtn,
                ...(selectedFeedback === 'adjustment' ? styles.feedbackBtnSelected : {})
              }}
              onClick={() => setSelectedFeedback('adjustment')}
            >
              조정 필요
            </button>
            <button
              style={{
                ...styles.feedbackBtn,
                ...(selectedFeedback === 'inappropriate' ? styles.feedbackBtnSelected : {})
              }}
              onClick={() => setSelectedFeedback('inappropriate')}
            >
              부적절함
            </button>
            <button
              style={{
                ...styles.feedbackBtn,
                ...(selectedFeedback === 'suggestion' ? styles.feedbackBtnSelected : {})
              }}
              onClick={() => setSelectedFeedback('suggestion')}
            >
              제안 있음
            </button>
          </div>

          {selectedFeedback !== 'appropriate' && (
            <div style={styles.feedbackDetail}>
              <h4 style={styles.feedbackDetailH4}>이유 선택</h4>
              <div style={styles.reasonOptions}>
                <label style={styles.reasonOption}>
                  <input
                    type="radio"
                    name="reason"
                    style={styles.reasonRadio}
                    checked={selectedReason === 'time'}
                    onChange={() => setSelectedReason('time')}
                  />
                  <span>시간이 부족함</span>
                </label>
                <label style={styles.reasonOption}>
                  <input
                    type="radio"
                    name="reason"
                    style={styles.reasonRadio}
                    checked={selectedReason === 'condition'}
                    onChange={() => setSelectedReason('condition')}
                  />
                  <span>환자 상태에 맞지 않음</span>
                </label>
                <label style={styles.reasonOption}>
                  <input
                    type="radio"
                    name="reason"
                    style={styles.reasonRadio}
                    checked={selectedReason === 'order'}
                    onChange={() => setSelectedReason('order')}
                  />
                  <span>순서가 적절하지 않음</span>
                </label>
                <label style={styles.reasonOption}>
                  <input
                    type="radio"
                    name="reason"
                    style={styles.reasonRadio}
                    checked={selectedReason === 'safety'}
                    onChange={() => setSelectedReason('safety')}
                  />
                  <span>안전상 문제</span>
                </label>
              </div>

              <h4 style={{ ...styles.feedbackDetailH4, marginTop: '12px' }}>제안사항</h4>
              <textarea
                style={styles.textarea}
                placeholder="상세한 의견을 작성해주세요..."
                value={suggestion}
                onChange={(e) => setSuggestion(e.target.value)}
              />

              <h4 style={{ ...styles.feedbackDetailH4, marginTop: '12px' }}>대안 시간 제안</h4>
              <div style={styles.timeSuggest}>
                <input
                  type="time"
                  style={styles.timeInput}
                  value={alternativeTime}
                  onChange={(e) => setAlternativeTime(e.target.value)}
                />
                <span style={{ fontSize: '13px', color: 'black' }}>(식사 30분 후)</span>
              </div>
            </div>
          )}
        </div>

        <div style={styles.activityReview}>
          <div style={styles.activityHeader}>
            <div style={styles.activityTimeTitle}>10:00 산책</div>
            <span style={styles.badge}>검토 대기</span>
          </div>
          <div style={styles.activityDetails}>
            날씨 좋을 시 20분 산책
          </div>

          <div style={styles.feedbackOptions}>
            <button style={styles.feedbackBtn}>적절함</button>
            <button style={styles.feedbackBtn}>조정 필요</button>
            <button style={styles.feedbackBtn}>부적절함</button>
            <button style={styles.feedbackBtn}>제안 있음</button>
          </div>
        </div>

        <div style={styles.overallFeedback}>
          <h3 style={styles.overallFeedbackH3}>전체 일정에 대한 종합 의견</h3>
          <textarea
            style={{ ...styles.textarea, minHeight: '100px' }}
            placeholder="전반적인 의견을 작성해주세요..."
            value={overallFeedback}
            onChange={(e) => setOverallFeedback(e.target.value)}
          />
        </div>
      </div>

      <div style={styles.bottomBar}>
        <button style={{ ...styles.btn, ...styles.btnSecondary }}>임시 저장</button>
        <button
          style={{
            ...styles.btn,
            ...styles.btnPrimary,
            ...(loading ? styles.btnDisabled : {})
          }}
          onClick={handleSubmit}
          disabled={loading}
        >
          {loading ? '저장 중...' : '검토 완료'}
        </button>
      </div>
    </div>
  )
}
