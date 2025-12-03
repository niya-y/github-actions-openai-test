'use client'
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { ChevronLeft, Send } from 'lucide-react'

export default function Screen16Messages() {
  const router = useRouter()
  const [activeTab, setActiveTab] = useState('chat')
  const [message, setMessage] = useState('')

  const renderChatContent = () => (
    <div className="p-4 space-y-4 bg-[#F9F9F9]">
      {/* Context Banner */}
      <div className="bg-[#E8FFFD] border-l-4 border-[#18d4c6] rounded-xl p-3 text-center">
        <p className="text-xs font-semibold text-[#353535]">📋 일정 관련 대화</p>
        <p className="text-xs text-[#828282] mt-1">[08:30 약 복용 확인] 활동</p>
      </div>

      {/* Message from caregiver */}
      <div className="flex gap-3 max-w-[80%]">
        <div className="w-10 h-10 rounded-full bg-[#18d4c6] flex items-center justify-center text-lg shrink-0">
          👨‍⚕️
        </div>
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-semibold text-[#353535]">간병인 김미숙</span>
            <span className="text-xs text-[#828282]">14:35</span>
          </div>
          <div className="bg-white rounded-2xl rounded-tl-sm p-3 shadow-sm border border-[#f0f0f0]">
            <p className="text-sm text-[#353535] leading-relaxed">
              어머니께서 오늘 손주 보고 싶다고 하시네요. 주말에 방문 가능하실까요?
            </p>
          </div>
        </div>
      </div>

      {/* Message sent by user */}
      <div className="flex gap-3 max-w-[80%] self-end ml-auto flex-row-reverse">
        <div className="w-10 h-10 rounded-full bg-[#E8E8E8] flex items-center justify-center text-lg shrink-0">
          👩
        </div>
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1 justify-end">
            <span className="text-xs text-[#828282]">14:38</span>
            <span className="text-xs font-semibold text-[#353535]">나</span>
          </div>
          <div className="bg-[#18d4c6] rounded-2xl rounded-tr-sm p-3 shadow-sm">
            <p className="text-sm text-white leading-relaxed">
              아, 그러셨구나. 토요일에 갈게요! 혹시 좋아하시는 간식 있을까요?
            </p>
          </div>
        </div>
      </div>

      {/* Message from caregiver */}
      <div className="flex gap-3 max-w-[80%]">
        <div className="w-10 h-10 rounded-full bg-[#18d4c6] flex items-center justify-center text-lg shrink-0">
          👨‍⚕️
        </div>
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-semibold text-[#353535]">간병인 김미숙</span>
            <span className="text-xs text-[#828282]">14:40</span>
          </div>
          <div className="bg-white rounded-2xl rounded-tl-sm p-3 shadow-sm border border-[#f0f0f0]">
            <p className="text-sm text-[#353535] leading-relaxed">
              요즘 호두과자 좋아하세요 😊<br />단, 당뇨 고려해서 1-2개만 드리고 있어요.
            </p>
          </div>
        </div>
      </div>

      {/* Message sent by family member */}
      <div className="flex gap-3 max-w-[80%] self-end ml-auto flex-row-reverse">
        <div className="w-10 h-10 rounded-full bg-[#E8E8E8] flex items-center justify-center text-lg shrink-0">
          👨
        </div>
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1 justify-end">
            <span className="text-xs text-[#828282]">14:42</span>
            <span className="text-xs font-semibold text-[#353535]">아들 이준호</span>
          </div>
          <div className="bg-[#18d4c6] rounded-2xl rounded-tr-sm p-3 shadow-sm">
            <p className="text-sm text-white leading-relaxed">
              알겠습니다. 제가 사갈게요.
            </p>
          </div>
        </div>
      </div>
    </div>
  )

  return (
    <div className="flex flex-col min-h-screen bg-white font-['Pretendard'] pb-0">
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
