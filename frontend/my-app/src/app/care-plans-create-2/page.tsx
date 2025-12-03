'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { background, firstPrimary } from '../colors'
import { apiGet, apiPost, apiPut } from '@/utils/api'
import ErrorAlert from '@/components/ErrorAlert'
import type { CarePlansResponse, Schedule, MealPlan, CareLog, ScheduleResponse } from '@/types/api'
import { validateScheduleResponse, validateCareLog, validateCareLogArray } from '@/types/guards'

export default function Screen9Schedule() {
  const router = useRouter()
  const [activeTab, setActiveTab] = useState<'schedule' | 'meal'>('schedule')
  const [schedules, setSchedules] = useState<Schedule[]>([])
  const [mealPlan, setMealPlan] = useState<MealPlan | null>(null)
  const [loading, setLoading] = useState(true)
  const [mealLoading, setMealLoading] = useState(false)
  const [error, setError] = useState<Error | null>(null)

  // 기본 활동 데이터 (API에서 데이터가 없을 경우 사용)
  const defaultActivities = [
    { time: '07:00', title: '기상 도움', assignee: '👨‍⚕️ 간병인 김미숙' },
    { time: '07:30', title: '아침 식사 준비', assignee: '👩 딸 박지은' },
    { time: '08:00', title: '약 복용 확인', assignee: '👨‍⚕️ 간병인 김미숙', note: '⚠️ 아스피린 100mg, 메트포민 500mg' },
    { time: '09:00', title: '가벼운 스트레칭', assignee: '👨‍⚕️ 간병인 김미숙' },
    { time: '10:00', title: '산책 (날씨 좋을 시)', assignee: '👩 딸 박지은' },
    { time: '12:00', title: '점심 식사 준비', assignee: '👨‍⚕️ 간병인 김미숙' }
  ]

  useEffect(() => {
    if (activeTab === 'schedule') {
      fetchCarePlans()
    } else if (activeTab === 'meal') {
      fetchMealPlan()
    }
  }, [activeTab])

  const fetchCarePlans = async () => {
    const patientId = sessionStorage.getItem('patient_id')
    console.log('[CarePlans] fetchCarePlans called, patient_id:', patientId)

    if (!patientId) {
      console.log('[CarePlans] No patient_id found in sessionStorage')
      setError(new Error('환자 정보를 찾을 수 없습니다. 다시 로그인해주세요.'))
      setSchedules([])
      setLoading(false)
      return
    }

    setLoading(true)
    setError(null)

    try {
      // pending_review 상태의 스케줄 조회
      const today = new Date().toISOString().split('T')[0]
      const apiUrl = `/api/patients/${patientId}/schedules?date=${today}&status=pending_review`
      console.log('[CarePlans] Fetching from:', apiUrl)

      const response = await apiGet<ScheduleResponse>(apiUrl)

      console.log('[CarePlans] API Response:', response)

      // 응답 검증 - 타입 가드 함수 사용
      if (!response) {
        throw new Error('서버에서 응답을 받지 못했습니다')
      }

      // 응답 타입 검증
      if (!validateScheduleResponse(response)) {
        console.error('[CarePlans] Invalid response structure:', response)
        throw new Error('유효하지 않은 응답 구조입니다')
      }

      // care_logs 배열 검증
      if (!validateCareLogArray(response.care_logs)) {
        console.log('[CarePlans] Invalid care_logs in response')
        setSchedules([])
        setLoading(false)
        return
      }

      if (response.care_logs.length === 0) {
        console.log('[CarePlans] No care_logs found, schedules will remain empty')
        setSchedules([])
        setLoading(false)
        return
      }

      // care_logs를 schedules 형식으로 변환 (모든 항목이 검증됨)
      const convertedSchedules: Schedule[] = response.care_logs
        .filter((log: CareLog) => validateCareLog(log))
        .map((log: CareLog) => ({
          schedule_id: log.schedule_id,
          title: log.task_name,
          start_time: log.scheduled_time || '00:00',
          end_time: '00:00', // API에서 제공하지 않는 경우
          category: log.category || 'other',
          is_completed: log.is_completed
        }))

      if (convertedSchedules.length === 0) {
        throw new Error('유효한 일정 데이터가 없습니다')
      }

      console.log('[CarePlans] Converted schedules:', convertedSchedules)
      setSchedules(convertedSchedules)
    } catch (err) {
      console.error('[CarePlans] 케어 플랜 조회 실패:', err)
      setError(err as Error)
      setSchedules([])
    } finally {
      setLoading(false)
    }
  }

  const fetchMealPlan = async () => {
    const patientId = sessionStorage.getItem('patient_id')
    if (!patientId) {
      setMealLoading(false)
      return
    }

    setMealLoading(true)
    setError(null)

    try {
      // 오늘 날짜로 점심 식단 생성 요청
      const today = new Date().toISOString().split('T')[0]
      const response = await apiPost<MealPlan>(
        `/api/meal-plans/patients/${patientId}/generate`,
        {
          meal_date: today,
          meal_type: 'lunch'
        }
      )
      setMealPlan(response)
    } catch (err) {
      console.error('식단 추천 생성 실패:', err)
      setError(err as Error)
    } finally {
      setMealLoading(false)
    }
  }

  // 스케줄을 활동 형식으로 변환
  const getActivities = () => {
    console.log('[CarePlans] getActivities called, schedules.length:', schedules.length)
    if (schedules.length > 0) {
      const activities = schedules.map(schedule => ({
        time: schedule.start_time.slice(0, 5), // HH:MM 형식
        title: schedule.title,
        assignee: `👨‍⚕️ ${schedule.category}`,
        note: schedule.is_completed ? '✅ 완료' : undefined
      }))
      console.log('[CarePlans] Returning DB activities:', activities)
      return activities
    }
    console.log('[CarePlans] Returning default hardcoded activities')
    return defaultActivities
  }

  // 식사 유형 한글 변환
  const getMealTypeKorean = (mealType: string) => {
    const types: Record<string, string> = {
      breakfast: '🌅 아침',
      lunch: '☀️ 점심',
      dinner: '🌙 저녁',
      snack: '🍪 간식'
    }
    return types[mealType] || mealType
  }

  // 영양정보 파싱 (문자열 또는 객체 처리)
  const parseNutritionInfo = (nutritionInfo: any) => {
    if (typeof nutritionInfo === 'string') {
      try {
        return JSON.parse(nutritionInfo)
      } catch {
        return null
      }
    }
    return nutritionInfo
  }

  const activities = getActivities()

  return (
    <div className="flex flex-col bg-white min-h-screen">
      <ErrorAlert error={error} onClose={() => setError(null)} />

      {/* Header Section */}
      <div className="self-stretch bg-white py-[77px] px-[34px]" style={{ boxShadow: "0px 4px 4px #00000040" }}>
        {/* Title & Description Box */}
        <div className="flex flex-col items-start self-stretch bg-white py-[17px] mb-9 gap-[18px] rounded-lg border border-solid border-[#18D4C6]" style={{ boxShadow: "0px 1px 4px #00000040" }}>
          <div className="flex flex-col items-start ml-5 gap-1">
            <span className="text-[#353535] text-[28px] font-bold mr-[113px]">케어 플랜</span>
            <span className="text-[#828282] text-base font-bold">
              {activeTab === 'schedule'
                ? 'AI가 생성한 7일 간병 일정입니다.'
                : 'AI가 환자 맞춤 식단을 추천합니다.'}
            </span>
          </div>

          {/* Divider */}
          <img
            src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 1'%3E%3Cline x1='0' y1='0' x2='100' y2='0' stroke='%23E0E0E0' stroke-width='1'/%3E%3C/svg%3E"
            className="self-stretch h-[1px] mx-[19px] object-fill"
          />

          {/* Summary Cards */}
          <div className="flex items-start self-stretch mx-[42px] gap-4">
            <div className="flex flex-1 flex-col items-center gap-0.5">
              <button
                className="flex flex-col items-center self-stretch text-left py-[18px] rounded-[50px] border-0"
                style={{ background: "linear-gradient(180deg, #F2FFFE, #FFF4F4)" }}
              >
                <span className="text-[#18D4C6] font-bold">{schedules.length > 0 ? schedules.length : 42}개</span>
              </button>
              <span className="text-[#828282] text-xs font-bold">총 활동</span>
            </div>

            <div className="flex flex-1 flex-col items-center gap-0.5">
              <button
                className="flex flex-col items-center self-stretch text-left py-[18px] rounded-[50px] border-0"
                style={{ background: "linear-gradient(180deg, #F2FFFE, #FFF4F4)" }}
              >
                <span className="text-[#18D4C6] font-bold">4명</span>
              </button>
              <span className="text-[#828282] text-xs font-bold">참여 인원</span>
            </div>

            <div className="flex flex-1 flex-col items-center gap-0.5">
              <button
                className="flex flex-col items-center self-stretch text-left py-[18px] rounded-[50px] border-0"
                style={{ background: "linear-gradient(180deg, #F2FFFE, #FFF4F4)" }}
              >
                <span className="text-[#18D4C6] font-bold">6시간</span>
              </button>
              <span className="text-[#828282] text-xs font-bold">일일 평균</span>
            </div>
          </div>
        </div>

        {/* Tab Buttons */}
        <div className="flex items-start self-stretch mb-3 gap-2">
          <button
            className={`flex flex-1 flex-col items-center text-left py-3.5 rounded-lg border border-solid ${
              activeTab === 'schedule'
                ? 'bg-[#E8FFFD] border-[#18D4C6]'
                : 'bg-white border-[#828282]'
            }`}
            onClick={() => setActiveTab('schedule')}
          >
            <span className={`text-base font-bold ${activeTab === 'schedule' ? 'text-[#353535]' : 'text-[#828282]'}`}>
              주간
            </span>
          </button>
          <button
            className={`flex flex-1 flex-col items-center text-left py-3.5 rounded-lg border border-solid ${
              activeTab === 'meal'
                ? 'bg-[#E8FFFD] border-[#18D4C6]'
                : 'bg-white border-[#828282]'
            }`}
            onClick={() => setActiveTab('meal')}
          >
            <span className={`text-base font-bold ${activeTab === 'meal' ? 'text-[#353535]' : 'text-[#828282]'}`}>
              추천 식단
            </span>
          </button>
        </div>

        {/* Content Section */}
        {activeTab === 'schedule' ? (
          <div className="flex flex-col items-start self-stretch bg-white py-[19px] pr-[19px] mb-9 rounded-lg" style={{ boxShadow: "0px 1px 4px #00000040" }}>
            <span className="text-[#353535] text-base font-bold mb-[11px] ml-5">월요일 일정</span>

            {/* Divider */}
            <img
              src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 1'%3E%3Cline x1='0' y1='0' x2='100' y2='0' stroke='%23E0E0E0' stroke-width='1'/%3E%3C/svg%3E"
              className="self-stretch h-[1px] mb-[17px] ml-[19px] object-fill"
            />

            {/* Activities List */}
            {loading ? (
              <div className="w-full text-center py-8 text-[#828282]">케어 플랜을 불러오는 중...</div>
            ) : (
              activities.map((activity, index) => (
                <div key={index} className="flex items-center self-stretch bg-[#F8F8F8] mb-2 ml-5 gap-[17px] rounded-[5px]">
                  <div className="bg-[#18D4C6] w-[5px] h-[62px] rounded-tl-[5px] rounded-bl-[5px]"></div>
                  <div className="flex shrink-0 items-center gap-[19px]">
                    <span className="text-[#18D4C6] text-lg font-bold">{activity.time}</span>
                    <div className="flex flex-col shrink-0 items-start">
                      <span className="text-[#353535] text-base font-bold">{activity.title}</span>
                      <span className="text-[#828282] text-xs">
                        {activity.assignee}
                        {activity.note && ` - ${activity.note}`}
                      </span>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        ) : (
          <div className="flex flex-col items-start self-stretch bg-white py-[19px] pr-5 mb-9 rounded-lg" style={{ boxShadow: "0px 1px 4px #00000040" }}>
            {mealLoading ? (
              <div className="w-full text-center py-8 text-[#828282]">🤖 AI가 맞춤 식단을 생성하고 있습니다...</div>
            ) : mealPlan ? (
              <>
                <span className="text-[#353535] text-lg font-bold mb-3 ml-5">추천 식단</span>
                <div className="text-[#353535] text-base font-bold mb-[11px] ml-5">{mealPlan.menu_name}</div>
                {mealPlan.ingredients && (
                  <div className="text-[#828282] text-xs ml-5 mb-3">
                    <span className="font-bold">재료:</span> {mealPlan.ingredients}
                  </div>
                )}
                {mealPlan.nutrition_info && (
                  <div className="text-[#828282] text-xs ml-5 mb-3">
                    <span className="font-bold">영양 정보:</span>{' '}
                    칼로리 {mealPlan.nutrition_info.calories || 'N/A'}kcal,
                    단백질 {mealPlan.nutrition_info.protein_g || 'N/A'}g,
                    탄수화물 {mealPlan.nutrition_info.carbs_g || 'N/A'}g,
                    지방 {mealPlan.nutrition_info.fat_g || 'N/A'}g
                  </div>
                )}
                {mealPlan.cooking_tips && (
                  <div className="bg-[#F8F8F8] mx-5 p-3 rounded-lg mb-3">
                    <div className="text-[#18D4C6] text-sm font-bold mb-2">💡 왜 이 식단이 좋은가요?</div>
                    <div className="text-[#353535] text-xs whitespace-pre-line">{mealPlan.cooking_tips}</div>
                  </div>
                )}
              </>
            ) : (
              <div className="w-full text-center py-8 text-[#828282]">식단 정보가 없습니다.</div>
            )}
          </div>
        )}

        {/* Expert Opinion Section */}
        <div className="flex flex-col items-start self-stretch bg-white py-[19px] pr-5 rounded-lg" style={{ boxShadow: "0px 1px 4px #00000040" }}>
          <span className="text-[#353535] text-lg font-bold mb-3 ml-5">전문가의 의견을 들어보세요</span>
          <span className="text-[#828282] text-sm mb-[15px] ml-5 whitespace-pre-line">
            간병인님께 이 일정에 대한 검토를 요청하시겠어요?
            전문가의 현장 경험이 더해지면 더 실용적인 케어
            플랜이 됩니다.
          </span>
          <div className="flex items-start self-stretch ml-5 gap-[9px]">
            <button
              className="flex flex-1 flex-col items-center bg-[#F2F2F2] text-left py-[11px] rounded-lg border border-solid border-[#828282]"
              onClick={() => router.push('/home')}
            >
              <span className="text-[#828282] text-base font-bold">나중에 하기</span>
            </button>
            <button
              className="flex flex-1 flex-col items-center bg-[#18D4C6] text-left py-[11px] rounded-lg border border-solid border-[#18D4C6]"
              onClick={async () => {
                try {
                  const patientId = sessionStorage.getItem('patient_id')
                  if (!patientId) {
                    alert('환자 정보를 찾을 수 없습니다.')
                    return
                  }

                  // status를 under_review로 업데이트
                  await apiPut('/api/care-plans/schedules/status', {
                    patient_id: parseInt(patientId),
                    status: 'under_review'
                  })

                  console.log('[CarePlans] Status updated to under_review')
                  router.push('/care-plans-create-4')
                } catch (err) {
                  console.error('[CarePlans] Failed to update status:', err)
                  alert('상태 업데이트 중 오류가 발생했습니다.')
                }
              }}
            >
              <span className="text-white text-base font-bold">요청하기</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
