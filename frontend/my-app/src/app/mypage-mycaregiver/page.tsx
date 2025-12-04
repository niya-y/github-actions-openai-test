'use client'

import { useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'
import { ChevronLeft, Bell, MessageCircle, Calendar, Star } from 'lucide-react'
import ErrorAlert from '@/components/ErrorAlert'

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

export default function MypageMyCaregiverPage() {
  const router = useRouter()
  const [caregiver, setCaregiver] = useState<Caregiver | null>(null)
  const [showBanner, setShowBanner] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    // sessionStorage에서 선택된 간병인 정보 가져오기
    const stored = sessionStorage.getItem('selectedCaregiver')
    if (stored) {
      try {
        const parsed = JSON.parse(stored)
        console.log('[MyCaregiver] Loaded caregiver:', parsed)
        setCaregiver(parsed)
      } catch (err) {
        console.error('[MyCaregiver] Error parsing caregiver data:', err)
        setError(err as Error)
      }
    } else {
      console.log('[MyCaregiver] No caregiver data found in sessionStorage')
    }

    // 배너 자동 숨김 (5초 후)
    const timer = setTimeout(() => {
      setShowBanner(false)
    }, 5000)

    return () => clearTimeout(timer)
  }, [])

  const displayName = caregiver?.caregiver_name || caregiver?.name || '간병인'
  const displayRating = caregiver?.avg_rating || caregiver?.rating || 0
  const displayReviews = caregiver?.reviews || 0
  const displayJobTitle = caregiver?.job_title || caregiver?.certification || '요양보호사'
  const displayExperience = caregiver?.experience_years
    ? `경력 ${caregiver.experience_years}년`
    : caregiver?.experience || '경력 정보 없음'
  const displaySpecialties = caregiver?.specialties && caregiver.specialties.length > 0
    ? caregiver.specialties
    : ['기본 돌봄']
  const displayRate = caregiver?.hourly_rate || caregiver?.rate || 0
  const displayIntro = caregiver?.intro || '친절하고 성실한 간병을 제공하겠습니다.'

  return (
    <div className="min-h-screen bg-white flex flex-col">
      <ErrorAlert error={error} onClose={() => setError(null)} />

      {/* Header */}
      <header className="sticky top-0 z-10 bg-white px-4 h-[60px] flex items-center justify-between border-b border-gray-100">
        <button
          onClick={() => router.back()}
          className="p-2 -ml-2 text-[#828282]"
          aria-label="Go back"
        >
          <ChevronLeft className="w-6 h-6" />
        </button>
        <h1 className="text-lg font-bold text-[#353535]">나의 간병인</h1>
        <button className="p-2 -mr-2 text-[#828282]">
          <Bell className="w-6 h-6" />
        </button>
      </header>

      {/* Success Banner */}
      {showBanner && (
        <div className="mx-6 mt-4 mb-2 bg-[#d1fae5] border border-[#10b981] rounded-[10px] px-4 py-3 flex items-center justify-between animate-[slideDown_0.5s_ease-out]">
          <div className="flex items-center gap-2">
            <span className="text-2xl">✅</span>
            <div>
              <p className="text-sm font-bold text-[#065f46]">매칭되었습니다!</p>
              <p className="text-xs text-[#047857]">간병인과의 관계가 시작되었습니다</p>
            </div>
          </div>
          <button
            onClick={() => setShowBanner(false)}
            className="text-[#065f46] text-xl leading-none p-1"
          >
            ×
          </button>
        </div>
      )}

      <style>{`
        @keyframes slideDown {
          from {
            opacity: 0;
            transform: translateY(-20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
      `}</style>

      {/* Main Content */}
      <main className="flex-1 px-6 pt-6 pb-8 overflow-y-auto">
        {!caregiver ? (
          <div className="text-center py-12">
            <p className="text-[#828282] font-semibold mb-4">간병인 정보를 불러올 수 없습니다.</p>
            <button
              onClick={() => router.push('/home')}
              className="px-6 py-2 bg-[#18d4c6] text-white font-bold rounded-[10px] hover:bg-[#15b0a8] transition-colors"
            >
              홈으로 가기
            </button>
          </div>
        ) : (
          <>
            {/* Caregiver Card */}
            <div className="bg-white rounded-[20px] p-6 shadow-sm border border-[#f0f0f0] mb-6">
              {/* Profile Section */}
              <div className="flex gap-4 mb-4 pb-4 border-b border-gray-100">
                {/* Avatar */}
                {caregiver.profile_image_url ? (
                  <img
                    src={caregiver.profile_image_url}
                    alt={displayName}
                    className="w-20 h-20 rounded-full object-cover border border-gray-100 shrink-0"
                  />
                ) : (
                  <div className="w-20 h-20 rounded-full bg-[#f0f4ff] flex items-center justify-center shrink-0 text-3xl">
                    {caregiver.avatar || '👨‍⚕️'}
                  </div>
                )}

                {/* Info */}
                <div className="flex-1 min-w-0">
                  <h2 className="text-xl font-bold text-[#353535] mb-1">{displayName}</h2>
                  <div className="flex items-center gap-2 mb-2">
                    <div className="flex items-center gap-1 text-[#18d4c6]">
                      <Star className="w-4 h-4 fill-current" />
                      <span className="text-sm font-bold">{displayRating.toFixed(1)}</span>
                    </div>
                    <span className="text-xs text-[#828282]">({displayReviews}건)</span>
                  </div>
                  <span className="inline-block px-3 py-1 bg-[#dbeafe] text-[#1e40af] text-xs font-bold rounded-full">
                    {displayJobTitle}
                  </span>
                </div>
              </div>

              {/* Experience */}
              <div className="mb-4">
                <p className="text-sm text-[#828282] font-semibold">{displayExperience}</p>
              </div>

              {/* Intro */}
              <div className="mb-4">
                <p className="text-sm text-[#555] italic leading-relaxed">
                  &ldquo;{displayIntro}&rdquo;
                </p>
              </div>

              {/* Specialties */}
              <div className="mb-4">
                <div className="flex flex-wrap gap-2">
                  {displaySpecialties.map((specialty, i) => (
                    <span
                      key={i}
                      className="px-3 py-1.5 bg-[#e8fffd] text-[#18d4c6] text-xs font-semibold rounded-full border border-[#18d4c6]"
                    >
                      {specialty}
                    </span>
                  ))}
                </div>
              </div>

              {/* Hourly Rate */}
              <div className="bg-[#f9fafb] rounded-[10px] px-4 py-3 flex items-center justify-between">
                <span className="text-sm text-[#666] font-semibold">시간당 요금</span>
                <span className="text-base font-bold text-[#18d4c6]">
                  {displayRate > 0 ? `₩${displayRate.toLocaleString()}` : '문의'}
                </span>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="space-y-3 mb-6">
              <button
                onClick={() => router.push('/care-plans-create-1')}
                className="w-full h-14 bg-[#18d4c6] rounded-[10px] flex items-center justify-center gap-2 shadow-[1px_1px_2px_rgba(125,140,139,0.5)] hover:bg-[#15b0a8] transition-colors"
              >
                <Calendar className="w-5 h-5 text-white" />
                <span className="text-base font-bold text-white">AI 맞춤 케어 일정 만들기</span>
              </button>

              <button
                onClick={() => router.push('/mypage-message')}
                className="w-full h-14 bg-white border-2 border-[#18d4c6] rounded-[10px] flex items-center justify-center gap-2 hover:bg-[#e8fffd] transition-colors"
              >
                <MessageCircle className="w-5 h-5 text-[#18d4c6]" />
                <span className="text-base font-bold text-[#18d4c6]">간병인과 채팅하기</span>
              </button>
            </div>

            {/* Info Card */}
            <div className="bg-white rounded-[20px] p-5 shadow-sm border border-[#f0f0f0]">
              <h3 className="text-base font-bold text-[#353535] mb-3 flex items-center gap-2">
                <span>📋</span>
                매칭 후 절차
              </h3>
              <div className="space-y-2 text-sm text-[#666]">
                <p className="flex items-start gap-2">
                  <span className="shrink-0">1️⃣</span>
                  <span>간병인과 채팅으로 세부사항 조율</span>
                </p>
                <p className="flex items-start gap-2">
                  <span className="shrink-0">2️⃣</span>
                  <span>AI가 추천하는 케어 플랜 검토</span>
                </p>
                <p className="flex items-start gap-2">
                  <span className="shrink-0">3️⃣</span>
                  <span>케어 시작 날짜 확정</span>
                </p>
                <p className="flex items-start gap-2">
                  <span className="shrink-0">4️⃣</span>
                  <span>케어 진행 상황 모니터링</span>
                </p>
              </div>
            </div>
          </>
        )}
      </main>
    </div>
  )
}
