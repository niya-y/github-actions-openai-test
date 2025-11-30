'use client'
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { background, firstPrimary } from '../colors'

export default function Screen16Messages() {
  const router = useRouter()
  const [activeTab, setActiveTab] = useState('chat')
  const [message, setMessage] = useState('')

  const styles = {
    container: {
      width: '100%',
      height: '100vh',
      background: background,
      display: 'flex',
      flexDirection: 'column' as const,
      overflow: 'hidden'
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
      borderTop: 'none',
      borderRight: 'none',
      borderBottom: 'none',
      borderLeft: 'none'
    },
    navTitle: {
      flex: 1,
      textAlign: 'center' as const,
      fontWeight: 600,
      fontSize: '17px',
      color: 'black'
    },
    tabBar: {
      display: 'flex',
      background: background,
      borderBottom: '1px solid #f0f0f0'
    },
    tab: {
      flex: 1,
      padding: '12px',
      textAlign: 'center' as const,
      cursor: 'pointer',
      fontSize: '14px',
      color: 'black',
      borderTop: 'none',
      borderLeft: 'none',
      borderRight: 'none',
      borderBottom: '2px solid transparent',
      background: background
    },
    tabActive: {
      color: firstPrimary,
      borderBottomColor: firstPrimary,
      fontWeight: 600
    },
    content: {
      flex: 1,
      overflowY: 'auto' as const,
      background: background,
    },
    messagesContainer: {
      padding: '15px',
      display: 'flex',
      flexDirection: 'column' as const,
      gap: '12px',
      background: background
    },
    contextBanner: {
      background: '#e0e7ff',
      padding: '10px 12px',
      borderRadius: '8px',
      textAlign: 'center' as const,
      fontSize: '12px',
      color: 'black',
      borderLeft: `3px solid ${firstPrimary}`
    },
    message: {
      display: 'flex',
      gap: '10px',
      maxWidth: '80%'
    },
    messageSent: {
      alignSelf: 'flex-end',
      flexDirection: 'row-reverse' as const
    },
    messageAvatar: {
      width: '32px',
      height: '32px',
      borderRadius: '16px',
      background: background,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      color: 'black',
      fontSize: '14px',
      flexShrink: 0
    },
    messageContent: {
      flex: 1
    },
    messageHeader: {
      display: 'flex',
      alignItems: 'center',
      gap: '8px',
      marginBottom: '4px'
    },
    messageName: {
      fontSize: '12px',
      fontWeight: 600,
      color: 'black'
    },
    messageTime: {
      fontSize: '11px',
      color: 'black'
    },
    messageBubble: {
      background: 'white',
      padding: '10px 12px',
      borderRadius: '12px',
      fontSize: '14px',
      lineHeight: 1.5,
      color: 'black',
      boxShadow: '0 1px 2px rgba(0,0,0,0.05)'
    },
    messageBubbleSent: {
      background: firstPrimary,
      color: 'white'
    },
    quickReply: {
      display: 'flex',
      gap: '5px',
      overflowX: 'auto' as const,
      padding: '10px 15px',
      background: background,
      borderTop: '1px solid #f0f0f0',
      position: 'sticky' as const,
      bottom: 0,
      zIndex: 9
    },
    quickReplyBtn: {
      padding: '8px 12px',
      background: '#f3f4f6',
      borderTop: '1px solid #e5e7eb',
      borderRight: '1px solid #e5e7eb',
      borderBottom: '1px solid #e5e7eb',
      borderLeft: '1px solid #e5e7eb',
      borderRadius: '20px',
      fontSize: '13px',
      whiteSpace: 'nowrap' as const,
      cursor: 'pointer',
      color: 'black'
    },
    messageInputArea: {
      padding: '15px',
      background: background,
      borderTop: '1px solid #f0f0f0',
      display: 'flex',
      gap: '10px',
      alignItems: 'center',
      position: 'sticky' as const,
      bottom: 0,
      zIndex: 10
    },
    messageInput: {
      flex: 1,
      padding: '10px 15px',
      borderTop: '1px solid #e5e7eb',
      borderRight: '1px solid #e5e7eb',
      borderBottom: '1px solid #e5e7eb',
      borderLeft: '1px solid #e5e7eb',
      borderRadius: '20px',
      fontSize: '14px',
      fontFamily: 'inherit',
      outline: 'none',
      color: 'black'
    },
    sendBtn: {
      width: '36px',
      height: '36px',
      borderRadius: '18px',
      background: firstPrimary,
      color: 'white',
      borderTop: 'none',
      borderRight: 'none',
      borderBottom: 'none',
      borderLeft: 'none',
      cursor: 'pointer',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      fontSize: '18px'
    }
  }

  const renderChatContent = () => (
    <div style={styles.messagesContainer}>
      <div style={styles.contextBanner}>
        📋 일정 관련 대화<br />
        [08:30 약 복용 확인] 활동
      </div>

      <div style={styles.message}>
        <div style={styles.messageAvatar}>👨‍⚕️</div>
        <div style={styles.messageContent}>
          <div style={styles.messageHeader}>
            <span style={styles.messageName}>간병인 김미숙</span>
            <span style={styles.messageTime}>14:35</span>
          </div>
          <div style={styles.messageBubble}>
            어머니께서 오늘 손주 보고 싶다고 하시네요. 주말에 방문 가능하실까요?
          </div>
        </div>
      </div>

      <div style={{...styles.message, ...styles.messageSent}}>
        <div style={styles.messageAvatar}>👩</div>
        <div style={styles.messageContent}>
          <div style={styles.messageHeader}>
            <span style={styles.messageName}>나</span>
            <span style={styles.messageTime}>14:38</span>
          </div>
          <div style={{...styles.messageBubble, ...styles.messageBubbleSent}}>
            아, 그러셨구나. 토요일에 갈게요! 혹시 좋아하시는 간식 있을까요?
          </div>
        </div>
      </div>

      <div style={styles.message}>
        <div style={styles.messageAvatar}>👨‍⚕️</div>
        <div style={styles.messageContent}>
          <div style={styles.messageHeader}>
            <span style={styles.messageName}>간병인 김미숙</span>
            <span style={styles.messageTime}>14:40</span>
          </div>
          <div style={styles.messageBubble}>
            요즘 호두과자 좋아하세요 😊<br />단, 당뇨 고려해서 1-2개만 드리고 있어요.
          </div>
        </div>
      </div>

      <div style={{...styles.message, ...styles.messageSent}}>
        <div style={styles.messageAvatar}>👨</div>
        <div style={styles.messageContent}>
          <div style={styles.messageHeader}>
            <span style={styles.messageName}>아들 이준호</span>
            <span style={styles.messageTime}>14:42</span>
          </div>
          <div style={{...styles.messageBubble, ...styles.messageBubbleSent}}>
            알겠습니다. 제가 사갈게요.
          </div>
        </div>
      </div>
    </div>
  )

  return (
    <div style={styles.container}>
      <div style={styles.navBar}>
        <button style={styles.backBtn} onClick={() => router.push('/dashboard')}>‹</button>
        <div style={styles.navTitle}>메시지</div>
        <div style={{width: '20px'}}></div>
      </div>

      <div style={styles.tabBar}>
        <button
          style={{...styles.tab, ...(activeTab === 'chat' ? styles.tabActive : {})}}
          onClick={() => setActiveTab('chat')}
        >
          대화
        </button>
        <button
          style={{...styles.tab, ...(activeTab === 'notice' ? styles.tabActive : {})}}
          onClick={() => setActiveTab('notice')}
        >
          공지
        </button>
        <button
          style={{...styles.tab, ...(activeTab === 'notes' ? styles.tabActive : {})}}
          onClick={() => setActiveTab('notes')}
        >
          공유 메모
        </button>
      </div>

      <div style={styles.content}>
        {activeTab === 'chat' && renderChatContent()}
        {activeTab === 'notice' && (
          <div style={{padding: '15px'}}>
            <div style={{background: 'white', borderRadius: '12px', padding: '15px', marginBottom: '12px', boxShadow: '0 1px 3px rgba(0,0,0,0.05)'}}>
              <div style={{display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px'}}>
                <span style={{fontSize: '20px'}}>📢</span>
                <span style={{fontWeight: 600, color: 'black', fontSize: '14px'}}>간병인 일정 변경 요청</span>
                <span style={{fontSize: '12px', color: 'black', marginLeft: 'auto'}}>2시간 전</span>
              </div>
              <div style={{fontSize: '13px', lineHeight: 1.5, color: 'black', marginBottom: '10px'}}>
                병원 진료가 있어 출근 시간을 10시로 조정 가능할까요?
              </div>
              <div style={{display: 'flex', gap: '8px'}}>
                <button style={{flex: 1, padding: '8px', borderRadius: '6px', border: 'none', fontSize: '13px', cursor: 'pointer', background: firstPrimary, color: 'white', fontWeight: 500}}>승인</button>
                <button style={{flex: 1, padding: '8px', borderRadius: '6px', border: '1px solid #e5e7eb', fontSize: '13px', cursor: 'pointer', background: 'white', fontWeight: 500, color: 'black'}}>거절</button>
                <button style={{flex: 1, padding: '8px', borderRadius: '6px', border: '1px solid #e5e7eb', fontSize: '13px', cursor: 'pointer', background: 'white', fontWeight: 500, color: 'black'}}>대화하기</button>
              </div>
            </div>

            <div style={{background: 'white', borderRadius: '12px', padding: '15px', boxShadow: '0 1px 3px rgba(0,0,0,0.05)'}}>
              <div style={{display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px'}}>
                <span style={{fontSize: '20px'}}>🔔</span>
                <span style={{fontWeight: 600, color: 'black', fontSize: '14px'}}>약물 재처방 필요</span>
                <span style={{fontSize: '12px', color: 'black', marginLeft: 'auto'}}>1일 전</span>
              </div>
              <div style={{fontSize: '13px', lineHeight: 1.5, color: 'black', marginBottom: '10px'}}>
                메트포민 500mg의 복용 가능 일수가 3일 남았습니다. 병원 예약을 고려해주세요.
              </div>
              <div style={{display: 'flex', gap: '8px'}}>
                <button style={{flex: 1, padding: '8px', borderRadius: '6px', border: 'none', fontSize: '13px', cursor: 'pointer', background: firstPrimary, color: 'white', fontWeight: 500}}>병원 예약하기</button>
                <button style={{flex: 1, padding: '8px', borderRadius: '6px', border: '1px solid #e5e7eb', fontSize: '13px', cursor: 'pointer', background: 'white', fontWeight: 500, color: 'black'}}>나중에 알림</button>
              </div>
            </div>
          </div>
        )}
        {activeTab === 'notes' && (
          <div style={{padding: '15px'}}>
            <button style={{width: '100%', padding: '15px', background: firstPrimary, color: 'white', border: 'none', borderRadius: '12px', fontSize: '14px', fontWeight: 600, cursor: 'pointer', marginBottom: '15px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px'}}>
              <span>➕</span>
              <span>새 메모 추가</span>
            </button>

            <div style={{background: 'white', borderRadius: '12px', padding: '15px', marginBottom: '12px', boxShadow: '0 1px 3px rgba(0,0,0,0.05)'}}>
              <div style={{display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '10px'}}>
                <span>📝</span>
                <span style={{flex: 1, fontWeight: 600, color: 'black', fontSize: '14px'}}>11/10 병원 진료 요약</span>
                <span style={{fontSize: '12px', color: 'black'}}>딸 박지은</span>
              </div>
              <div style={{fontSize: '13px', lineHeight: 1.6, color: 'black', marginBottom: '10px'}}>
                • 담당의: 김OO 선생님<br />
                • 진료 내용: 혈압약 용량 조정<br />
                • 변경 사항: 암로디핀 5mg → 10mg<br />
                • 다음 진료: 12/10 (한 달 후)
              </div>
              <div style={{display: 'flex', alignItems: 'center', gap: '12px', paddingTop: '10px', borderTop: '1px solid #f0f0f0', fontSize: '12px', color: 'black'}}>
                <span>💬 댓글 2개</span>
                <span>•</span>
                <span>2일 전</span>
              </div>
            </div>

            <div style={{background: 'white', borderRadius: '12px', padding: '15px', boxShadow: '0 1px 3px rgba(0,0,0,0.05)'}}>
              <div style={{display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '10px'}}>
                <span>📝</span>
                <span style={{flex: 1, fontWeight: 600, color: 'black', fontSize: '14px'}}>좋아하시는 음식 목록</span>
                <span style={{fontSize: '12px', color: 'black'}}>간병인 김미숙</span>
              </div>
              <div style={{fontSize: '13px', lineHeight: 1.6, color: 'black', marginBottom: '10px'}}>
                ✅ 호박죽<br />
                ✅ 닭가슴살 샐러드<br />
                ✅ 두부 조림<br />
                ❌ 자극적인 찌개류 (속 안 좋아하심)
              </div>
              <div style={{display: 'flex', alignItems: 'center', gap: '12px', paddingTop: '10px', borderTop: '1px solid #f0f0f0', fontSize: '12px', color: 'black'}}>
                <span>💬 댓글 5개</span>
                <span>•</span>
                <span>5일 전</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {activeTab === 'chat' && (
        <>
          <div style={styles.quickReply}>
            <button style={styles.quickReplyBtn}>감사합니다</button>
            <button style={styles.quickReplyBtn}>확인했어요</button>
            <button style={styles.quickReplyBtn}>조금 이따 연락드릴게요</button>
          </div>
          <div style={styles.messageInputArea}>
            <input
              type="text"
              style={styles.messageInput}
              placeholder="메시지를 입력하세요..."
              value={message}
              onChange={(e) => setMessage(e.target.value)}
            />
            <button style={styles.sendBtn}>↑</button>
          </div>
        </>
      )}
    </div>
  )
}
