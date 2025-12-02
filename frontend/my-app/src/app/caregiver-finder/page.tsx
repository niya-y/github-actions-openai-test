"use client"

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { ChevronLeft, Check } from 'lucide-react'
import { apiPost } from '@/utils/api'
import ErrorAlert from '@/components/ErrorAlert'
import { cn } from '@/utils/cn'
import type { MatchingRequest, MatchingResponse } from '@/types/api'

export default function CaregiverFinder() {
  const router = useRouter()
  const [careType, setCareType] = useState('nursing-aide')
  const [timeSlots, setTimeSlots] = useState<string[]>(['morning', 'afternoon'])
  const [preferredDays, setPreferredDays] = useState<string[]>(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'])
  const [gender, setGender] = useState<'Male' | 'Female' | 'any'>('any')
  const [experience, setExperience] = useState('5plus')
  const [skills, setSkills] = useState<string[]>(['dementia', 'diabetes'])
  const [careStartDate, setCareStartDate] = useState<string>('')
  const [careEndDate, setCareEndDate] = useState<string>('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<Error | null>(null)

  const toggleTimeSlot = (slot: string) => {
    setTimeSlots(prev =>
      prev.includes(slot) ? prev.filter(s => s !== slot) : [...prev, slot]
    )
  }

  const toggleSkill = (skill: string) => {
    setSkills(prev =>
      prev.includes(skill) ? prev.filter(s => s !== skill) : [...prev, skill]
    )
  }

  const handleCareStartDateChange = (newDate: string) => {
    setCareStartDate(newDate)
    // 시작일을 선택하면 모든 요일 자동 선택
    if (newDate) {
      const allDays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
      setPreferredDays(allDays)
    }
  }

  const handleCareEndDateChange = (newDate: string) => {
    setCareEndDate(newDate)
    // 종료일을 선택하면 모든 요일 자동 선택 (이미 선택되어 있을 수 있음)
    if (newDate && careStartDate) {
      const allDays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
      setPreferredDays(allDays)
    }
  }

  const handleSubmit = async () => {
    const patientId = sessionStorage.getItem('patient_id')
    if (!patientId) {
      alert('환자 정보를 찾을 수 없습니다. 처음부터 다시 시작해주세요.')
      router.push('/patient-condition-1')
      return
    }

    if (timeSlots.length === 0) {
      alert('희망 시간을 최소 1개 이상 선택해주세요.')
      return
    }

    if (preferredDays.length === 0) {
      alert('희망 요일을 최소 1개 이상 선택해주세요.')
      return
    }

    // Validate care dates
    if (careStartDate && careEndDate) {
      if (new Date(careStartDate) >= new Date(careEndDate)) {
        alert('간병 시작일이 종료일보다 이전이어야 합니다.')
        return
      }
    }

    setLoading(true)
    setError(null)

    try {
      // SessionStorage에서 성격 점수 조회
      const personalityScoresStr = sessionStorage.getItem('personality_scores')
      let personalityScores = {
        empathy_score: 50,
        activity_score: 50,
        patience_score: 50,
        independence_score: 50
      }

      if (personalityScoresStr) {
        try {
          personalityScores = JSON.parse(personalityScoresStr)
        } catch (e) {
          console.warn('성격 점수 파싱 실패, 기본값 사용:', e)
        }
      }

      // XGBoost 기반 매칭 요청
      const payload = {
        patient_id: parseInt(patientId),
        patient_personality: personalityScores,
        preferred_days: preferredDays,
        preferred_time_slots: timeSlots,
        care_start_date: careStartDate || null,
        care_end_date: careEndDate || null,
        requirements: {
          care_type: careType,
          time_slots: timeSlots,
          gender: gender,
          experience: experience,
          skills: skills
        },
        top_k: 5
      }

      console.log('[Caregiver Finder] Submitting matching request:', payload)

      const response = await apiPost<any>(
        '/api/matching/recommend-xgboost',
        payload
      )

      console.log('XGBoost 매칭 요청 성공:', response)

      // 매칭 결과를 세션 스토리지에 저장
      sessionStorage.setItem('matching_results', JSON.stringify(response))

      // 🔴 FIX ISSUE #2: care_requirements를 세션 스토리지에 저장
      // (care-plans-create 페이지에서 하드코딩 대신 사용하기 위함)
      const careRequirements = {
        care_type: careType,
        time_slots: timeSlots,
        gender: gender,
        experience: experience,
        skills: skills,
        preferred_days: preferredDays,
        care_start_date: careStartDate || null,
        care_end_date: careEndDate || null
      }
      sessionStorage.setItem('care_requirements', JSON.stringify(careRequirements))
      console.log('[Caregiver Finder] ✅ care_requirements saved to sessionStorage:', careRequirements)

      // P12 로딩 페이지로 이동
      router.push('/caregiver-result-loading')
    } catch (err) {
      console.error('매칭 요청 실패:', err)
      setError(err as Error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-white flex flex-col">
      <ErrorAlert error={error} onClose={() => setError(null)} />

      {/* Header */}
      <header className="sticky top-0 z-10 bg-white px-4 pt-4 pb-2">
        <div className="flex items-center mb-2">
          <button
            onClick={() => router.push('/patient-condition-3')}
            className="p-2 -ml-2 text-[#828282]"
            aria-label="Go back"
          >
            <ChevronLeft className="w-6 h-6" />
          </button>

          {/* Progress Bar */}
          <div className="flex-1 flex gap-2 ml-4 mr-2">
            <div className="h-1 flex-1 bg-[#18d4c6] rounded-full" />
            <div className="h-1 flex-1 bg-[#18d4c6] rounded-full" />
            <div className="h-1 flex-1 bg-[#18d4c6] rounded-full" />
            <div className="h-1 flex-1 bg-[#18d4c6] rounded-full" />
            <div className="h-1 flex-1 bg-[#18d4c6] rounded-full" />
          </div>
        </div>

        <div className="text-center mb-3">
          <span className="text-xs text-[#828282]">마지막이에요, 다 왔어요!</span>
        </div>

        <div className="h-px bg-gray-100 -mx-4" />
      </header>

      <main className="flex-1 px-8 pt-6 pb-32 overflow-y-auto">
        {/* Title */}
        <div className="mb-8">
          <h1 className="text-[28px] font-bold text-[#353535]">어떤 분을 찾으시나요?</h1>
        </div>

        {/* Care Type */}
        <div className="mb-9">
          <h2 className="text-lg font-bold text-black mb-2 ml-1">돌봄 유형</h2>
          <div className="space-y-2">
            <button
              onClick={() => setCareType('nursing-aide')}
              className={cn(
                "w-full text-left p-4 rounded-[10px] border transition-all shadow-sm",
                careType === 'nursing-aide'
                  ? "bg-[#e8fffd] border-[#18d4c6]"
                  : "bg-white border-[#828282]"
              )}
            >
              <div className="flex items-center justify-between mb-0.5">
                <span className={cn("text-base font-bold", careType === 'nursing-aide' ? "text-[#353535]" : "text-[#646464]")}>요양보호사</span>
              </div>
              <span className={cn("text-xs leading-snug", careType === 'nursing-aide' ? "text-[#353535]" : "text-[#646464]")}>국가 공인 자격증 보유, 재가 방문 요양 전문</span>
            </button>

            <button
              onClick={() => setCareType('nursing-assistant')}
              className={cn(
                "w-full text-left p-4 rounded-[10px] border transition-all shadow-sm",
                careType === 'nursing-assistant'
                  ? "bg-[#e8fffd] border-[#18d4c6]"
                  : "bg-white border-[#828282]"
              )}
            >
              <div className="flex items-center justify-between mb-0.5">
                <span className={cn("text-base font-bold", careType === 'nursing-assistant' ? "text-[#353535]" : "text-[#646464]")}>간호조무사</span>
              </div>
              <span className={cn("text-xs leading-snug", careType === 'nursing-assistant' ? "text-[#353535]" : "text-[#646464]")}>기본 의료 보조 업무</span>
            </button>

            <button
              onClick={() => setCareType('nurse')}
              className={cn(
                "w-full text-left p-4 rounded-[10px] border transition-all shadow-sm",
                careType === 'nurse'
                  ? "bg-[#e8fffd] border-[#18d4c6]"
                  : "bg-white border-[#828282]"
              )}
            >
              <div className="flex items-center justify-between mb-0.5">
                <span className={cn("text-base font-bold", careType === 'nurse' ? "text-[#353535]" : "text-[#646464]")}>간호사</span>
              </div>
              <span className={cn("text-xs leading-snug", careType === 'nurse' ? "text-[#353535]" : "text-[#646464]")}>전문 의료 서비스</span>
            </button>
          </div>
        </div>

        {/* 간병 기간 */}
        <div className="mb-9">
          <h2 className="text-lg font-bold text-black mb-2 ml-1">간병 기간</h2>
          <div className="flex gap-3 mb-3">
            <div className="flex-1">
              <label className="text-xs text-[#828282] block mb-2">시작일</label>
              <input
                type="date"
                value={careStartDate}
                onChange={(e) => handleCareStartDateChange(e.target.value)}
                className="w-full h-10 px-3 rounded-[10px] border border-[#828282] text-sm focus:outline-none focus:border-[#18d4c6]"
              />
            </div>
            <div className="flex-1">
              <label className="text-xs text-[#828282] block mb-2">종료일</label>
              <input
                type="date"
                value={careEndDate}
                onChange={(e) => handleCareEndDateChange(e.target.value)}
                className="w-full h-10 px-3 rounded-[10px] border border-[#828282] text-sm focus:outline-none focus:border-[#18d4c6]"
              />
            </div>
          </div>
          <p className="text-xs text-[#828282]">간병 기간을 설정하면 이 기간에 이용 가능한 간병인을 찾습니다. (선택사항)</p>
        </div>

        {/* Time Selection */}
        <div className="mb-9">
          <div className="flex items-center gap-2 mb-2 ml-1">
            <h2 className="text-lg font-bold text-black">희망 시간</h2>
            <span className="text-xs text-[#828282]">중복 선택 가능</span>
          </div>

          <div className="grid grid-cols-4 gap-1.5">
            {[
              { id: 'morning', label: '오전', time: '09:00 ~ 12:00' },
              { id: 'afternoon', label: '오후', time: '12:00 ~ 18:00' },
              { id: 'evening', label: '저녁', time: '18:00 ~ 22:00' },
              { id: 'night', label: '야간', time: '22:00 ~ 09:00' }
            ].map((item) => {
              const isSelected = timeSlots.includes(item.id)
              return (
                <button
                  key={item.id}
                  onClick={() => toggleTimeSlot(item.id)}
                  className={cn(
                    "relative flex items-start p-2 rounded-lg border transition-all shadow-sm text-left",
                    isSelected
                      ? "bg-[#e8fffd] border-[#18d4c6]"
                      : "bg-white border-[#828282]"
                  )}
                >
                  <div className={cn(
                    "w-3.5 h-3.5 mt-0 mr-2 flex items-center justify-center rounded-[2px] border flex-shrink-0",
                    isSelected ? "bg-[#18d4c6] border-[#18d4c6]" : "bg-white border-[#828282]"
                  )}>
                    {isSelected && <Check className="w-2 h-2 text-white" />}
                  </div>
                  <div className="min-w-0">
                    <div className={cn("text-xs font-bold leading-tight", isSelected ? "text-[#353535]" : "text-[#828282]")}>{item.label}</div>
                    <div className={cn("text-[10px] leading-tight", isSelected ? "text-[#353535]" : "text-[#828282]")}>{item.time}</div>
                  </div>
                </button>
              )
            })}
          </div>
        </div>

        {/* Preferences */}
        <div className="mb-9">
          <h2 className="text-lg font-bold text-black mb-2 ml-1">선호 조건(선택)</h2>

          {/* Gender */}
          <div className="mb-4">
            <span className="text-xs text-[#828282] ml-1 mb-2 block">성별</span>
            <div className="flex gap-2">
              {[
                { id: 'Male', label: '남성' },
                { id: 'Female', label: '여성' },
                { id: 'any', label: '무관' }
              ].map(g => (
                <button
                  key={g.id}
                  onClick={() => setGender(g.id as any)}
                  className={cn(
                    "flex-1 py-2 rounded-md border text-sm font-bold transition-all",
                    gender === g.id
                      ? "bg-[#e8fffd] border-[#18d4c6] text-[#353535]"
                      : "bg-white border-[#828282] text-[#646464]"
                  )}
                >
                  {g.label}
                </button>
              ))}
            </div>
          </div>

          {/* Experience */}
          <div>
            <span className="text-xs text-[#828282] ml-1 mb-2 block">경력</span>
            <div className="grid grid-cols-4 gap-2">
              {[
                { id: 'less1', label: '1년 미만' },
                { id: '1-3', label: '1-3년' },
                { id: '3-5', label: '3-5년' },
                { id: '5plus', label: '5년 이상' }
              ].map(exp => (
                <button
                  key={exp.id}
                  onClick={() => setExperience(exp.id)}
                  className={cn(
                    "py-2 rounded-md border text-sm font-bold transition-all",
                    experience === exp.id
                      ? "bg-[#e8fffd] border-[#18d4c6] text-[#353535]"
                      : "bg-white border-[#828282] text-[#646464]"
                  )}
                >
                  {exp.label}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Skills */}
        <div className="mb-8">
          <span className="text-xs text-[#828282] ml-1 mb-2 block">필요 기술</span>
          <div className="space-y-2">
            {[
              { id: 'dementia', label: '치매 환자 케어' },
              { id: 'diabetes', label: '당뇨 환자 케어' },
              { id: 'bedsore', label: '욕창 관리' },
              { id: 'suction', label: '석션 가능' }
            ].map(skill => {
              const isSelected = skills.includes(skill.id)
              return (
                <button
                  key={skill.id}
                  onClick={() => toggleSkill(skill.id)}
                  className={cn(
                    "w-full flex items-center py-3 px-4 rounded-[10px] border transition-all shadow-sm",
                    isSelected
                      ? "bg-[#e8fffd] border-[#18d4c6]"
                      : "bg-white border-[#828282]"
                  )}
                >
                  <div className={cn(
                    "w-4 h-4 mr-3 flex items-center justify-center rounded-[2px] border",
                    isSelected ? "bg-[#18d4c6] border-[#18d4c6]" : "bg-white border-[#828282]"
                  )}>
                    {isSelected && <Check className="w-3 h-3 text-white" />}
                  </div>
                  <span className={cn("text-sm font-bold", isSelected ? "text-[#353535]" : "text-[#646464]")}>
                    {skill.label}
                  </span>
                </button>
              )
            })}
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="fixed bottom-0 left-0 right-0 bg-white px-8 pb-8 pt-4">
        <button
          onClick={handleSubmit}
          disabled={loading}
          className="w-full h-14 bg-[#18d4c6] rounded-[10px] flex items-center justify-center shadow-[0px_2px_8px_rgba(188,188,188,0.8)] hover:bg-[#15b0a8] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <span className="text-lg font-bold text-white">{loading ? '매칭 중...' : '매칭 시작하기'}</span>
        </button>
      </footer>
    </div>
  )
}
