'use client'
import { useState, useEffect, useRef } from 'react'
import { useRouter } from 'next/navigation'
import { ChevronLeft, Send } from 'lucide-react'

interface Message {
  id: number
  sender: 'caregiver' | 'user' | 'family'
  senderName: string
  time: string
  content: string
  avatar: string
}

const mockMessages: Message[] = [
  {
    id: 1,
    sender: 'caregiver',
    senderName: '간병인 김미숙',
    time: '09:15',
    content: '안녕하세요! 오늘 아침 혈압 체크 완료했습니다. 120/80으로 안정적이에요.',
    avatar: '👨‍⚕️'
  },
  {
    id: 2,
    sender: 'user',
    senderName: '나',
    time: '09:18',
    content: '네, 확인했습니다. 감사합니다!',
    avatar: '👩'
  },
  {
    id: 3,
    sender: 'caregiver',
    senderName: '간병인 김미숙',
    time: '10:30',
    content: '아침 식사도 잘 드셨어요. 오늘은 호박죽이랑 계란찜 준비해드렸습니다.',
    avatar: '👨‍⚕️'
  },
  {
    id: 4,
    sender: 'user',
    senderName: '나',
    time: '10:35',
    content: '어머니가 좋아하시는 메뉴네요. 고생 많으세요!',
    avatar: '👩'
  },
  {
    id: 5,
    sender: 'caregiver',
    senderName: '간병인 김미숙',
    time: '12:45',
    content: '점심 후 약 복용도 완료했습니다. 오늘 컨디션이 많이 좋으신 것 같아요 😊',
    avatar: '👨‍⚕️'
  },
  {
    id: 6,
    sender: 'user',
    senderName: '나',
    time: '12:50',
    content: '다행이네요. 혹시 오늘 산책은 하셨나요?',
    avatar: '👩'
  },
  {
    id: 7,
    sender: 'caregiver',
    senderName: '간병인 김미숙',
    time: '13:00',
    content: '네, 오후 2시에 날씨가 따뜻할 때 집 앞 공원에서 20분 정도 산책할 예정입니다.',
    avatar: '👨‍⚕️'
  },
  {
    id: 8,
    sender: 'user',
    senderName: '나',
    time: '13:05',
    content: '좋아요. 무리하지 않는 선에서 부탁드립니다.',
    avatar: '👩'
  },
  {
    id: 9,
    sender: 'caregiver',
    senderName: '간병인 김미숙',
    time: '14:35',
    content: '어머니께서 오늘 손주 보고 싶다고 하시네요. 주말에 방문 가능하실까요?',
    avatar: '👨‍⚕️'
  },
  {
    id: 10,
    sender: 'user',
    senderName: '나',
    time: '14:38',
    content: '아, 그러셨구나. 토요일에 갈게요! 혹시 좋아하시는 간식 있을까요?',
    avatar: '👩'
  },
  {
    id: 11,
    sender: 'caregiver',
    senderName: '간병인 김미숙',
    time: '14:40',
    content: '요즘 호두과자 좋아하세요 😊\n단, 당뇨 고려해서 1-2개만 드리고 있어요.',
    avatar: '👨‍⚕️'
  },
  {
    id: 12,
    sender: 'family',
    senderName: '아들 이준호',
    time: '14:42',
    content: '알겠습니다. 제가 사갈게요.',
    avatar: '👨'
  },
  {
    id: 13,
    sender: 'caregiver',
    senderName: '간병인 김미숙',
    time: '15:30',
    content: '참고로 다음주 월요일에 병원 진료 예약되어 있습니다. 오전 10시 30분이에요.',
    avatar: '👨‍⚕️'
  },
  {
    id: 14,
    sender: 'user',
    senderName: '나',
    time: '15:35',
    content: '네, 캘린더에 표시해두었습니다. 제가 동행할게요.',
    avatar: '👩'
  },
  {
    id: 15,
    sender: 'caregiver',
    senderName: '간병인 김미숙',
    time: '15:40',
    content: '알겠습니다! 검사 결과지와 약 처방전도 미리 준비해두겠습니다.',
    avatar: '👨‍⚕️'
  }
]

export default function MyPageMessagePage() {
  const router = useRouter()
  const [activeTab, setActiveTab] = useState('chat')
  const [message, setMessage] = useState('')
  const [visibleMessages, setVisibleMessages] = useState<Message[]>([])
  const [cycleKey, setCycleKey] = useState(0) // 사이클을 추적하는 키
  const chatEndRef = useRef<HTMLDivElement>(null)

  // 메시지 애니메이션 효과
  useEffect(() => {
    if (activeTab === 'chat') {
      const showMessages = () => {
        // 초기화
        setVisibleMessages([])
        setCycleKey(prev => prev + 1) // 새 사이클 시작

        // 순차적으로 메시지 표시
        mockMessages.forEach((msg, index) => {
          setTimeout(() => {
            setVisibleMessages(prev => [...prev, msg])
          }, index * 1500) // 1.5초 간격으로 메시지 추가
        })

        // 모든 메시지 표시 후 2초 대기하고 다시 시작
        setTimeout(() => {
          showMessages()
        }, mockMessages.length * 1500 + 2000) // 전체 시간 + 2초 대기
      }

      showMessages()
    }
  }, [activeTab])

  // 새 메시지가 추가될 때마다 스크롤 하단으로 이동
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [visibleMessages])

  const renderChatContent = () => (
    <div className="p-4 space-y-4 bg-[#F9F9F9]">
      {/* Context Banner */}
      <div className="bg-[#E8FFFD] border-l-4 border-[#18d4c6] rounded-xl p-3 text-center animate-[fadeIn_0.5s_ease-out]">
        <p className="text-xs font-semibold text-[#353535]">📋 일정 관련 대화</p>
        <p className="text-xs text-[#828282] mt-1">[08:30 약 복용 확인] 활동</p>
      </div>

      {/* Messages */}
      {visibleMessages.map((msg, index) => (
        <div
          key={`${cycleKey}-${msg.id}-${index}`}
          className={`flex gap-3 max-w-[80%] animate-[slideUp_0.4s_ease-out] ${
            msg.sender === 'user' || msg.sender === 'family'
              ? 'self-end ml-auto flex-row-reverse'
              : ''
          }`}
        >
          <div className={`w-10 h-10 rounded-full flex items-center justify-center text-lg shrink-0 ${
            msg.sender === 'caregiver' ? 'bg-[#18d4c6]' : 'bg-[#E8E8E8]'
          }`}>
            {msg.avatar}
          </div>
          <div className="flex-1">
            <div className={`flex items-center gap-2 mb-1 ${
              msg.sender === 'user' || msg.sender === 'family' ? 'justify-end' : ''
            }`}>
              {msg.sender === 'user' || msg.sender === 'family' ? (
                <>
                  <span className="text-xs text-[#828282]">{msg.time}</span>
                  <span className="text-xs font-semibold text-[#353535]">{msg.senderName}</span>
                </>
              ) : (
                <>
                  <span className="text-xs font-semibold text-[#353535]">{msg.senderName}</span>
                  <span className="text-xs text-[#828282]">{msg.time}</span>
                </>
              )}
            </div>
            <div className={`rounded-2xl p-3 shadow-sm ${
              msg.sender === 'caregiver'
                ? 'bg-white border border-[#f0f0f0] rounded-tl-sm'
                : 'bg-[#18d4c6] rounded-tr-sm'
            }`}>
              <p className={`text-sm leading-relaxed whitespace-pre-line ${
                msg.sender === 'caregiver' ? 'text-[#353535]' : 'text-white'
              }`}>
                {msg.content}
              </p>
            </div>
          </div>
        </div>
      ))}

      {/* Scroll anchor */}
      <div ref={chatEndRef} />
    </div>
  )

  return (
    <div className="flex flex-col min-h-screen bg-white font-['Pretendard'] pb-0">
      <style>{`
        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: translateY(-10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        @keyframes slideUp {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
      `}</style>

      {/* Header */}
      <header className="sticky top-0 z-10 bg-white border-b border-[#f0f0f0]">
        <div className="flex items-center justify-between h-[60px] px-6">
          <button
            onClick={() => router.push('/home')}
            className="p-2 -ml-2 hover:bg-gray-50 rounded-full transition-colors"
          >
            <ChevronLeft className="w-6 h-6 text-[#353535]" />
          </button>
          <h1 className="text-lg font-bold text-[#353535]">메시지</h1>
          <div className="w-10" />
        </div>

        {/* Tab Bar */}
        <div className="flex border-b border-[#f0f0f0]">
          <button
            onClick={() => setActiveTab('chat')}
            className={`flex-1 py-3 text-sm font-semibold transition-colors ${
              activeTab === 'chat'
                ? 'text-[#18d4c6] border-b-2 border-[#18d4c6]'
                : 'text-[#828282] border-b-2 border-transparent'
            }`}
          >
            대화
          </button>
          <button
            onClick={() => setActiveTab('notice')}
            className={`flex-1 py-3 text-sm font-semibold transition-colors ${
              activeTab === 'notice'
                ? 'text-[#18d4c6] border-b-2 border-[#18d4c6]'
                : 'text-[#828282] border-b-2 border-transparent'
            }`}
          >
            공지
          </button>
          <button
            onClick={() => setActiveTab('notes')}
            className={`flex-1 py-3 text-sm font-semibold transition-colors ${
              activeTab === 'notes'
                ? 'text-[#18d4c6] border-b-2 border-[#18d4c6]'
                : 'text-[#828282] border-b-2 border-transparent'
            }`}
          >
            공유 메모
          </button>
        </div>
      </header>

      {/* Content */}
      <main className="flex-1 overflow-y-auto bg-[#F9F9F9]">
        {activeTab === 'chat' && renderChatContent()}

        {activeTab === 'notice' && (
          <div className="p-4 space-y-4">
            {/* Notice Card 1 */}
            <div className="bg-white rounded-[20px] p-5 shadow-sm border border-[#f0f0f0]">
              <div className="flex items-center gap-3 mb-3">
                <span className="text-2xl">📢</span>
                <span className="flex-1 font-bold text-[#353535]">간병인 일정 변경 요청</span>
                <span className="text-xs text-[#828282]">2시간 전</span>
              </div>
              <p className="text-sm text-[#646464] leading-relaxed mb-4">
                병원 진료가 있어 출근 시간을 10시로 조정 가능할까요?
              </p>
              <div className="flex gap-2">
                <button className="flex-1 py-2.5 bg-[#18d4c6] text-white rounded-lg text-sm font-semibold hover:bg-[#15b0a8] transition-colors">
                  승인
                </button>
                <button className="flex-1 py-2.5 bg-white text-[#646464] border border-[#e5e7eb] rounded-lg text-sm font-semibold hover:bg-[#F9F9F9] transition-colors">
                  거절
                </button>
                <button className="flex-1 py-2.5 bg-white text-[#646464] border border-[#e5e7eb] rounded-lg text-sm font-semibold hover:bg-[#F9F9F9] transition-colors">
                  대화하기
                </button>
              </div>
            </div>

            {/* Notice Card 2 */}
            <div className="bg-white rounded-[20px] p-5 shadow-sm border border-[#f0f0f0]">
              <div className="flex items-center gap-3 mb-3">
                <span className="text-2xl">🔔</span>
                <span className="flex-1 font-bold text-[#353535]">약물 재처방 필요</span>
                <span className="text-xs text-[#828282]">1일 전</span>
              </div>
              <p className="text-sm text-[#646464] leading-relaxed mb-4">
                메트포민 500mg의 복용 가능 일수가 3일 남았습니다. 병원 예약을 고려해주세요.
              </p>
              <div className="flex gap-2">
                <button className="flex-1 py-2.5 bg-[#18d4c6] text-white rounded-lg text-sm font-semibold hover:bg-[#15b0a8] transition-colors">
                  병원 예약하기
                </button>
                <button className="flex-1 py-2.5 bg-white text-[#646464] border border-[#e5e7eb] rounded-lg text-sm font-semibold hover:bg-[#F9F9F9] transition-colors">
                  나중에 알림
                </button>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'notes' && (
          <div className="p-4 space-y-4">
            {/* Add Note Button */}
            <button className="w-full py-4 bg-[#18d4c6] text-white rounded-[20px] font-semibold shadow-sm hover:bg-[#15b0a8] transition-colors flex items-center justify-center gap-2">
              <span className="text-lg">➕</span>
              <span>새 메모 추가</span>
            </button>

            {/* Note Card 1 */}
            <div className="bg-white rounded-[20px] p-5 shadow-sm border border-[#f0f0f0]">
              <div className="flex items-center gap-3 mb-3">
                <span className="text-xl">📝</span>
                <span className="flex-1 font-bold text-[#353535]">11/10 병원 진료 요약</span>
                <span className="text-xs text-[#828282]">딸 박지은</span>
              </div>
              <div className="text-sm text-[#646464] leading-relaxed mb-4">
                • 담당의: 김OO 선생님<br />
                • 진료 내용: 혈압약 용량 조정<br />
                • 변경 사항: 암로디핀 5mg → 10mg<br />
                • 다음 진료: 12/10 (한 달 후)
              </div>
              <div className="flex items-center gap-3 pt-3 border-t border-[#f0f0f0] text-xs text-[#828282]">
                <span>💬 댓글 2개</span>
                <span>•</span>
                <span>2일 전</span>
              </div>
            </div>

            {/* Note Card 2 */}
            <div className="bg-white rounded-[20px] p-5 shadow-sm border border-[#f0f0f0]">
              <div className="flex items-center gap-3 mb-3">
                <span className="text-xl">📝</span>
                <span className="flex-1 font-bold text-[#353535]">좋아하시는 음식 목록</span>
                <span className="text-xs text-[#828282]">간병인 김미숙</span>
              </div>
              <div className="text-sm text-[#646464] leading-relaxed mb-4">
                ✅ 호박죽<br />
                ✅ 닭가슴살 샐러드<br />
                ✅ 두부 조림<br />
                ❌ 자극적인 찌개류 (속 안 좋아하심)
              </div>
              <div className="flex items-center gap-3 pt-3 border-t border-[#f0f0f0] text-xs text-[#828282]">
                <span>💬 댓글 5개</span>
                <span>•</span>
                <span>5일 전</span>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Quick Reply & Message Input (Chat tab only) */}
      {activeTab === 'chat' && (
        <div className="bg-white border-t border-[#f0f0f0]">
          {/* Quick Reply */}
          <div className="flex gap-2 px-4 py-3 overflow-x-auto">
            <button className="px-4 py-2 bg-[#F5F5F5] text-[#646464] text-sm font-medium rounded-full whitespace-nowrap hover:bg-[#EBEBEB] transition-colors">
              감사합니다
            </button>
            <button className="px-4 py-2 bg-[#F5F5F5] text-[#646464] text-sm font-medium rounded-full whitespace-nowrap hover:bg-[#EBEBEB] transition-colors">
              확인했어요
            </button>
            <button className="px-4 py-2 bg-[#F5F5F5] text-[#646464] text-sm font-medium rounded-full whitespace-nowrap hover:bg-[#EBEBEB] transition-colors">
              조금 이따 연락드릴게요
            </button>
          </div>

          {/* Message Input */}
          <div className="flex items-center gap-3 px-4 py-4 border-t border-[#f0f0f0]">
            <input
              type="text"
              placeholder="메시지를 입력하세요..."
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              className="flex-1 px-4 py-3 bg-[#F5F5F5] rounded-full text-sm placeholder:text-[#828282] focus:outline-none focus:ring-2 focus:ring-[#18d4c6]/20"
            />
            <button className="w-10 h-10 bg-[#18d4c6] rounded-full flex items-center justify-center hover:bg-[#15b0a8] transition-colors shadow-sm">
              <Send className="w-5 h-5 text-white" />
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
