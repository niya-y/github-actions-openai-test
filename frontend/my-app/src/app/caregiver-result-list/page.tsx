"use client"

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { ChevronLeft, Bell, ChevronRight } from 'lucide-react'
import { cn } from '@/utils/cn'
import { apiGet, apiPost } from '@/utils/api'
import ErrorAlert from '@/components/ErrorAlert'
import type { CaregiverMatch, MatchingResponse } from '@/types/api'

export default function CaregiverResultListPage() {
  const router = useRouter()
  const [matches, setMatches] = useState<CaregiverMatch[]>([])
  const [patientName, setPatientName] = useState<string>('고객')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)
  const [flippedCards, setFlippedCards] = useState<{ [key: number]: boolean }>({})

  useEffect(() => {
    const fetchMatchingResults = async () => {
      try {
        // 환자 이름 로드
        const patientNameStored = sessionStorage.getItem('patient_name') || '고객'
        setPatientName(patientNameStored)

        // 1단계: API에서 매칭 결과 조회
        try {
          console.log('[Caregiver Result List] Fetching from API...')
          const response = await apiGet<MatchingResponse>('/api/matching/results')

          if (response?.matches && Array.isArray(response.matches) && response.matches.length > 0) {
            console.log('[Caregiver Result List] Matches from API:', response.matches.length, 'caregivers')
            setMatches(response.matches)
            // sessionStorage에도 저장 (캐싱)
            sessionStorage.setItem('matching_results', JSON.stringify(response))
            setLoading(false)
            return
          }
        } catch (apiErr) {
          console.warn('[Caregiver Result List] API fetch failed, trying sessionStorage fallback:', apiErr)
        }

        // 2단계: API 실패 시 sessionStorage에서 조회
        const storedResults = sessionStorage.getItem('matching_results')
        if (storedResults) {
          try {
            const parsed: MatchingResponse = JSON.parse(storedResults)
            if (parsed.matches && Array.isArray(parsed.matches) && parsed.matches.length > 0) {
              console.log('[Caregiver Result List] Matches from sessionStorage (fallback):', parsed.matches.length, 'caregivers')
              setMatches(parsed.matches)
              setLoading(false)
              return
            }
          } catch (e) {
            console.error('[Caregiver Result List] Session storage parsing error:', e)
          }
        }

        // 3단계: 모두 실패
        console.log('[Caregiver Result List] No matching results available')
        setMatches([])
        setError(new Error('매칭 결과를 불러올 수 없습니다. 다시 시도해주세요.'))
      } catch (err) {
        console.error('[Caregiver Result List] Error:', err)
        setError(err as Error)
        setMatches([])
      } finally {
        setLoading(false)
      }
    }

    fetchMatchingResults()
  }, [])

  const toggleFlip = (caregiverId: number) => {
    setFlippedCards(prev => ({
      ...prev,
      [caregiverId]: !prev[caregiverId]
    }))
  }

  const handleSelectCaregiver = async (caregiver: CaregiverMatch) => {
    try {
      setLoading(true)
      setError(null)

      // 1. matching_id 검증
      if (!caregiver.matching_id) {
        throw new Error('간병인 매칭 ID가 없습니다')
      }

      // 2. API 호출 필수
      console.log('[Caregiver Result List] Selecting caregiver:', caregiver.caregiver_name)
      const response = await apiPost<any>(`/api/matching/${caregiver.matching_id}/select`, {})

      // 3. 응답 검증
      if (!response || response.status === 'error') {
        throw new Error('간병인 선택 실패 - 서버 오류')
      }

      console.log('[Caregiver Result List] Caregiver selected successfully:', caregiver.caregiver_name)

      // 4. 성공 시에만 sessionStorage에 저장
      sessionStorage.setItem('selectedCaregiver', JSON.stringify(caregiver))
      sessionStorage.setItem('matching_id', caregiver.matching_id.toString())

      // 5. 성공 시에만 페이지 이동
      router.push('/mypage-mycaregiver')
    } catch (err) {
      console.error('[Caregiver Result List] Error selecting caregiver:', err)
      setError(err as Error)
      // 에러 발생 시 페이지 이동 안함
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-center">
          <div className="inline-flex items-center justify-center w-12 h-12 mb-4 bg-[#18d4c6] rounded-full">
            <div className="w-6 h-6 border-2 border-[#18d4c6] border-t-transparent rounded-full animate-spin"></div>
          </div>
          <p className="font-semibold text-[#353535]">매칭 결과를 불러오는 중...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-white flex flex-col">
      <style>{`
        .flip-card {
          perspective: 1000px;
          cursor: pointer;
        }

        .flip-card-inner {
          position: relative;
          width: 100%;
          height: 280px;
          transition: transform 0.6s;
          transform-style: preserve-3d;
        }

        .flip-card-inner.flipped {
          transform: rotateY(180deg);
        }

        .flip-card-front,
        .flip-card-back {
          backface-visibility: hidden;
          -webkit-backface-visibility: hidden;
          width: 100%;
          height: 100%;
          position: absolute;
          top: 0;
          left: 0;
        }

        .flip-card-back {
          transform: rotateY(180deg);
        }
      `}</style>

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
        <h1 className="text-lg font-bold text-[#353535]">추천 간병인</h1>
        <button className="p-2 -mr-2 text-[#828282]">
          <Bell className="w-6 h-6" />
        </button>
      </header>

      {/* Main Content */}
      <main className="flex-1 px-6 pt-8 pb-8 overflow-y-auto">
        {/* Title Section */}
        <div className="mb-8">
          <h2 className="text-[28px] font-bold text-[#353535] mb-2 leading-tight">
            {patientName}님에게 적합한 간병인
          </h2>
          <p className="text-base font-bold text-[#828282]">
            {matches.length}명의 전문가를 찾았습니다.
          </p>
        </div>

        {/* No Results */}
        {matches.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-[#828282] font-semibold mb-4">매칭된 간병인을 찾을 수 없습니다.</p>
            <button
              onClick={() => router.back()}
              className="px-6 py-2 bg-[#18d4c6] text-white font-bold rounded-[10px] hover:bg-[#15b0a8] transition-colors"
            >
              돌아가기
            </button>
          </div>
        ) : (
          /* Caregiver Cards */
          <div className="space-y-6">
            {matches.map((caregiver, index) => {
              const isFlipped = flippedCards[caregiver.caregiver_id] || false
              const isBest = index === 0

              return (
                <div
                  key={caregiver.caregiver_id}
                  className="flip-card rounded-[10px] border border-[#18d4c6] bg-white overflow-hidden shadow-[1px_3px_3px_rgba(74,73,73,0.25)]"
                  onClick={() => toggleFlip(caregiver.caregiver_id)}
                >
                  <div className={cn('flip-card-inner', isFlipped && 'flipped')}>
                    {/* Front Side - Basic Info */}
                    <div className="flip-card-front px-4 pt-4 pb-3 flex flex-col gap-2">
                      {/* Tags */}
                      <div className="flex gap-2 mb-2 flex-wrap">
                        <span className="bg-[#18d4c6] text-white text-sm font-bold px-3.5 py-[9px] rounded-[5px]">
                          {caregiver.job_title}
                        </span>
                        <span className="bg-[#18d4c6] text-white text-sm font-bold px-3.5 py-[9px] rounded-[5px]">
                          경력 {caregiver.experience_years}년
                        </span>
                      </div>

                      {/* Profile Info */}
                      <div className="flex items-start gap-3 mb-2">
                        {caregiver.profile_image_url ? (
                          <img
                            src={caregiver.profile_image_url}
                            alt={caregiver.caregiver_name}
                            className="w-[62px] h-[62px] rounded-full object-cover border border-gray-100 shrink-0"
                          />
                        ) : (
                          <div className="w-[62px] h-[62px] rounded-full bg-[#e8fffd] border border-gray-100 flex items-center justify-center shrink-0 text-2xl">
                            👤
                          </div>
                        )}
                        <div className="flex flex-col flex-1 min-w-0">
                          <span className="text-lg font-bold text-[#353535] mb-0.5">{caregiver.caregiver_name}</span>
                          <span className="text-xs text-[#828282] mb-1 line-clamp-2">
                            {caregiver.specialties && Array.isArray(caregiver.specialties) && caregiver.specialties.length > 0
                              ? caregiver.specialties.join(' / ')
                              : '돌봄 서비스'}
                          </span>
                          <span className="text-sm font-bold text-[#353535]">
                            ₩{caregiver.hourly_rate?.toLocaleString()}/시간
                          </span>
                        </div>
                      </div>

                      {/* Match Score & Flip Button */}
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-1 text-[#828282]">
                          <ChevronRight className="w-4 h-4" />
                          <span className="text-xs">매칭 근거 확인하기</span>
                        </div>
                        <span
                          className={cn(
                            'font-bold text-lg',
                            caregiver.match_score >= 90 ? 'text-[#FF7E7E]' : 'text-[#828282]'
                          )}
                        >
                          {caregiver.match_score}% 매칭
                        </span>
                      </div>

                      {/* Divider */}
                      <div className="h-px bg-gray-200 mb-2" />

                      {/* Button */}
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          handleSelectCaregiver(caregiver)
                        }}
                        className="w-full py-3 border rounded-md text-base font-bold transition-colors bg-[#18d4c6] border-[#18d4c6] text-white hover:bg-[#15b0a8]"
                      >
                        선택하기
                      </button>
                    </div>

                    {/* Back Side - Matching Reason */}
                    <div className="flip-card-back px-4 pt-4 pb-3 flex flex-col gap-2">
                      {/* Title */}
                      <div className="mb-1">
                        <h3 className="text-base font-bold text-[#353535] mb-1">매칭 근거</h3>
                        <div className="w-10 h-0.5 bg-[#18d4c6] rounded-full" />
                      </div>

                      {/* Matching Reason Text */}
                      <p className="text-xs text-[#353535] leading-snug line-clamp-3 mb-2">
                        {caregiver.matching_reason || '최선의 돌봄을 제공할 것입니다.'}
                      </p>

                      {/* Stats */}
                      <div className="grid grid-cols-3 gap-1.5 mb-2">
                        <div className="text-center p-1.5 bg-[#e8fffd] rounded-lg">
                          <div className="text-base font-bold text-[#18d4c6] leading-tight">
                            {caregiver.match_score}%
                          </div>
                          <div className="text-xs text-[#828282] mt-0.5">호환도</div>
                        </div>
                        <div className="text-center p-1.5 bg-[#e8fffd] rounded-lg">
                          <div className="text-base font-bold text-[#18d4c6] leading-tight">
                            {caregiver.experience_years}년
                          </div>
                          <div className="text-xs text-[#828282] mt-0.5">경력</div>
                        </div>
                        <div className="text-center p-1.5 bg-[#e8fffd] rounded-lg">
                          <div className="text-base font-bold text-[#18d4c6] leading-tight">
                            {caregiver.avg_rating?.toFixed(1) || '0.0'}
                          </div>
                          <div className="text-xs text-[#828282] mt-0.5">평점</div>
                        </div>
                      </div>

                      {/* Info text */}
                      <p className="text-xs text-[#828282] text-center mt-auto">클릭하여 돌아가기</p>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </main>
    </div>
  )
}
