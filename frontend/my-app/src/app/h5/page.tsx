'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { background, firstPrimary, secondPrimary } from '../colors'

export default function Screen15Report() {
  const router = useRouter()

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
    shareBtn: {
      fontSize: '20px',
      cursor: 'pointer',
      color: firstPrimary,
      background: 'none',
      border: 'none'
    },
    reportHeader: {
      background: background,
      color: 'black',
      padding: '20px'
    },
    reportDate: {
      fontSize: '14px',
      opacity: 0.9,
      marginBottom: '5px'
    },
    reportTitle: {
      fontSize: '20px',
      fontWeight: 600,
      marginBottom: '10px'
    },
    caregiverInfo: {
      display: 'flex',
      alignItems: 'center',
      gap: '10px',
      fontSize: '13px',
      opacity: 0.95
    },
    content: {
      flex: 1,
      overflowY: 'auto' as const,
      padding: '20px'
    },
    summarySection: {
      background: 'white',
      borderRadius: '12px',
      padding: '15px',
      marginBottom: '15px',
      boxShadow: '0 2px 8px rgba(0,0,0,0.05)'
    },
    summarySectionH3: {
      fontSize: '15px',
      fontWeight: 600,
      color: '#333',
      marginBottom: '10px'
    },
    summaryContent: {
      fontSize: '14px',
      lineHeight: 1.7,
      color: '#555'
    },
    activityList: {
      listStyle: 'none',
      marginTop: '8px'
    },
    activityListItem: {
      padding: '8px 0',
      borderBottom: '1px solid #f0f0f0',
      fontSize: '13px',
      color: '#555'
    },
    dataSection: {
      background: 'white',
      borderRadius: '12px',
      padding: '15px',
      marginBottom: '15px',
      boxShadow: '0 2px 8px rgba(0,0,0,0.05)'
    },
    dataSectionH3: {
      fontSize: '15px',
      fontWeight: 600,
      color: '#333',
      marginBottom: '15px'
    },
    dataRow: {
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      padding: '12px',
      background: '#f9fafb',
      borderRadius: '8px',
      marginBottom: '10px'
    },
    dataLabel: {
      fontSize: '14px',
      color: '#666'
    },
    dataValue: {
      fontSize: '15px',
      fontWeight: 600,
      color: '#333'
    },
    dataWarning: {
      color: secondPrimary
    },
    dataGood: {
      color: secondPrimary
    },
    mealBar: {
      height: '10px',
      background: '#e5e7eb',
      borderRadius: '5px',
      overflow: 'hidden',
      marginTop: '5px'
    },
    mealFill: {
      height: '100%',
      background: firstPrimary,
      borderRadius: '5px'
    },
    photoGallery: {
      background: 'white',
      borderRadius: '12px',
      padding: '15px',
      marginBottom: '15px',
      boxShadow: '0 2px 8px rgba(0,0,0,0.05)'
    },
    photoGalleryH3: {
      fontSize: '15px',
      fontWeight: 600,
      color: '#333',
      marginBottom: '12px'
    },
    photoGrid: {
      display: 'grid',
      gridTemplateColumns: 'repeat(3, 1fr)',
      gap: '8px'
    },
    photoItem: {
      aspectRatio: '1',
      background: 'linear-gradient(135deg, #e0e7ff 0%, #f3e8ff 100%)',
      borderRadius: '8px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      fontSize: '24px'
    },
    actionButtons: {
      display: 'grid',
      gridTemplateColumns: 'repeat(3, 1fr)',
      gap: '10px',
      marginTop: '20px'
    },
    actionBtn: {
      padding: '12px',
      borderRadius: '8px',
      border: 'none',
      cursor: 'pointer',
      display: 'flex',
      flexDirection: 'column' as const,
      alignItems: 'center',
      gap: '5px',
      background: 'white',
      boxShadow: '0 2px 8px rgba(0,0,0,0.05)'
    },
    actionIcon: {
      fontSize: '24px'
    },
    actionLabel: {
      fontSize: '12px',
      color: '#666',
      fontWeight: 500
    },
    bottomBar: {
      padding: '15px 20px',
      background: background,
      borderTop: '1px solid #f0f0f0'
    },
    bottomBtn: {
      width: '100%',
      padding: '15px',
      borderRadius: '10px',
      border: 'none',
      background: firstPrimary,
      color: 'white',
      fontWeight: 600,
      fontSize: '15px',
      cursor: 'pointer',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      gap: '8px'
    }
  }

  return (
    <div style={{
      minHeight: '100vh',
      background: background,
      display: 'flex',
      flexDirection: 'column'
    }}>
      <div style={styles.navBar}>
        <button style={styles.backBtn} onClick={() => router.push('/dashboard')}>‹</button>
        <div style={styles.navTitle}>오늘의 케어 보고서</div>
        <button style={styles.shareBtn}>↗</button>
      </div>

      <div style={styles.reportHeader}>
        <div style={styles.reportDate}>2025년 11월 12일</div>
        <div style={styles.reportTitle}>김영희 어머니 케어 보고서</div>
        <div style={styles.caregiverInfo}>
          <span>👨‍⚕️</span>
          <span>작성자: 간병인 김미숙</span>
        </div>
      </div>

      <div style={styles.content}>
        <div style={styles.summarySection}>
          <h3 style={styles.summarySectionH3}>전반적인 상태</h3>
          <div style={styles.summaryContent}>
            오늘 김영희 어머니는 전반적으로 양호한 상태를 보이셨습니다. 식사량이 평소보다 약간 적었으나 (80%), 특별한 문제는 없었습니다.
          </div>
        </div>

        <div style={styles.summarySection}>
          <h3 style={styles.summarySectionH3}>주요 활동</h3>
          <ul style={styles.activityList}>
            <li style={styles.activityListItem}>✅ 아침 산책: 20분 완료 (날씨 좋음)</li>
            <li style={styles.activityListItem}>✅ 약물 복용: 모두 정상 복용</li>
            <li style={styles.activityListItem}>✅ 혈압 측정: 135/82 (약간 높음)</li>
            <li style={styles.activityListItem}>✅ 인지 활동: 옛날 사진 보며 대화</li>
            <li style={{...styles.activityListItem, borderBottom: 'none'}}>✅ 오후 휴식: 1시간 30분 숙면</li>
          </ul>
        </div>

        <div style={styles.dataSection}>
          <h3 style={styles.dataSectionH3}>📊 오늘의 데이터</h3>

          <div style={styles.dataRow}>
            <div>
              <div style={styles.dataLabel}>혈압 (오전)</div>
              <div style={{...styles.dataValue, ...styles.dataWarning}}>135/82 ⚠️</div>
            </div>
            <div>
              <div style={styles.dataLabel}>혈압 (오후)</div>
              <div style={{...styles.dataValue, ...styles.dataGood}}>125/78 ✅</div>
            </div>
          </div>

          <div style={{marginBottom: '15px'}}>
            <div style={{...styles.dataLabel, marginBottom: '8px'}}>식사량</div>
            <div style={{display: 'flex', gap: '10px', fontSize: '13px'}}>
              <div style={{flex: 1}}>
                <div style={{marginBottom: '5px', color: '#666'}}>아침: 90%</div>
                <div style={styles.mealBar}>
                  <div style={{...styles.mealFill, width: '90%'}}></div>
                </div>
              </div>
              <div style={{flex: 1}}>
                <div style={{marginBottom: '5px', color: '#666'}}>점심: 80%</div>
                <div style={styles.mealBar}>
                  <div style={{...styles.mealFill, width: '80%'}}></div>
                </div>
              </div>
              <div style={{flex: 1}}>
                <div style={{marginBottom: '5px', color: '#666'}}>저녁: 95%</div>
                <div style={styles.mealBar}>
                  <div style={{...styles.mealFill, width: '95%'}}></div>
                </div>
              </div>
            </div>
          </div>

          <div style={styles.dataRow}>
            <div style={styles.dataLabel}>활동 완료율</div>
            <div>
              <div style={{...styles.dataValue, ...styles.dataGood}}>95% ⭐</div>
              <div style={{fontSize: '12px', color: '#666', marginTop: '4px'}}>19/20</div>
            </div>
          </div>
        </div>

        <div style={styles.summarySection}>
          <h3 style={styles.summarySectionH3}>특이사항</h3>
          <div style={styles.summaryContent}>
            • 손주 이야기에 밝은 표정 보임<br />
            • 오후에 약간의 피로감 호소<br />
            • 저녁 혈압은 정상 범위로 회복
          </div>
        </div>

        <div style={styles.photoGallery}>
          <h3 style={styles.photoGalleryH3}>오늘의 주요 순간</h3>
          <div style={styles.photoGrid}>
            <div style={styles.photoItem}>🍚</div>
            <div style={styles.photoItem}>🚶</div>
            <div style={styles.photoItem}>📖</div>
          </div>
        </div>

        <div style={styles.summarySection}>
          <h3 style={styles.summarySectionH3}>내일 권장사항</h3>
          <div style={styles.summaryContent}>
            • 수분 섭취 독려 (오늘 섭취량 부족)<br />
            • 오후 휴식 시간 10분 연장 고려<br />
            • 혈압 체크 지속 필요
          </div>
        </div>

        <div style={styles.actionButtons}>
          <button style={styles.actionBtn}>
            <div style={styles.actionIcon}>👍</div>
            <div style={styles.actionLabel}>감사합니다</div>
          </button>
          <button style={styles.actionBtn}>
            <div style={styles.actionIcon}>💬</div>
            <div style={styles.actionLabel}>질문하기</div>
          </button>
          <button style={styles.actionBtn}>
            <div style={styles.actionIcon}>📌</div>
            <div style={styles.actionLabel}>중요 표시</div>
          </button>
        </div>
      </div>

      <div style={styles.bottomBar}>
        <button style={styles.bottomBtn}>
          <span>📤</span>
          <span>가족에게 공유하기</span>
        </button>
      </div>
    </div>
  )
}