'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { background, firstPrimary } from '../colors'
import Image from 'next/image'

export default function Screen8Loading() {
  const router = useRouter()

  useEffect(() => {
    const timer = setTimeout(() => {
      router.push('/caregiver-result-2')
    }, 3000)

    return () => clearTimeout(timer)
  }, [router])

  const styles = {
    container: {
      minHeight: '100vh',
      background: background,
      display: 'flex',
      flexDirection: 'column' as const,
      justifyContent: 'center',
      alignItems: 'center',
      padding: '40px',
      color: 'black'
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
    stepMessage: {
      opacity: 0,
      animation: 'fadeInOut 8s infinite'
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
      fontWeight: 700
    },
    progressBarContainer: {
      width: '100%',
      maxWidth: '300px',
      marginTop: '40px'
    },
    progressBar: {
      width: '100%',
      height: '6px',
      background: 'rgba(255, 255, 255, 0.3)',
      borderRadius: '3px',
      overflow: 'hidden'
    },
    progressFill: {
      height: '100%',
      background: firstPrimary,
      borderRadius: '3px',
      width: '0%',
      animation: 'fillProgress 3s ease-out forwards'
    },
    progressText: {
      textAlign: 'center' as const,
      marginTop: '10px',
      fontSize: '14px',
      opacity: 0.9
    }
  }

  return (
    <>
      <style>
        {`
          @keyframes spin {
            to { transform: rotate(360deg); }
          }
          @keyframes pulse {
            0%, 100% { transform: scale(1); opacity: 1; }
            50% { transform: scale(1.1); opacity: 0.8; }
          }
          @keyframes rotate {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
          }
          @keyframes fadeInOut {
            0%, 20% { opacity: 0; transform: translateY(10px); }
            25%, 45% { opacity: 1; transform: translateY(0); }
            50%, 100% { opacity: 0; transform: translateY(-10px); }
          }
          @keyframes fillProgress {
            0% { width: 0%; }
            100% { width: 100%; }
          }
        `}
      </style>
      <div style={styles.container}>
          <div style={styles.loaderContainer}>
            <div style={styles.loadingRing}></div>
            <div style={styles.loader}>
              <Image src="/assets/logo.png" alt="Logo" width={64} height={64} style={styles.loaderIcon} />
            </div>
          </div>

          <div style={styles.messageContainer}>
            <h2 style={styles.mainMessage}>AI가 케어 플랜을 생성하고 있어요</h2>

            <div style={styles.stepMessages}>
              <div style={{...styles.stepMessage, animationDelay: '0s'}}>
                후보가 너무 많아요...
              </div>
              <div style={{...styles.stepMessage, animationDelay: '1s'}}>
                최고의 파트너를 찾았어요...
              </div>
            </div>
          </div>

          <div style={styles.infoCards}>
            <div style={styles.infoCard}>
              <div style={styles.infoIcon}>📋</div>
              <div style={styles.infoTitle}>분석 중</div>
              <div style={styles.infoValue}>42개</div>
            </div>
            <div style={styles.infoCard}>
              <div style={styles.infoIcon}>🏥</div>
              <div style={styles.infoTitle}>참고 자료</div>
              <div style={styles.infoValue}>15건</div>
            </div>
          </div>

          <div style={styles.progressBarContainer}>
            <div style={styles.progressBar}>
              <div style={styles.progressFill}></div>
            </div>
            <div style={styles.progressText}>곧 완료됩니다...</div>
          </div>
      </div>
    </>
  )
}
