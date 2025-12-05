'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { apiGet, apiPut } from '@/utils/api'
import ErrorAlert from '@/components/ErrorAlert'
import type { Schedule, CareLog, ScheduleResponse } from '@/types/api'
import { validateScheduleResponse, validateCareLog, validateCareLogArray } from '@/types/guards'

// 케어 플랜 요약 정보 인터페이스
interface CarePlanSummary {
  totalActivities: number
  careDays: number
}

// 날짜 포맷 함수 (YYYY-MM-DD -> MM/DD (요일))
const formatDateLabel = (dateStr: string): string => {
  const date = new Date(dateStr)
  const days = ['일', '월', '화', '수', '목', '금', '토']
  const month = date.getMonth() + 1
  const day = date.getDate()
  const dayOfWeek = days[date.getDay()]
  return `${month}/${day} (${dayOfWeek})`
}

export default function Screen9Schedule() {
  const router = useRouter()
  const [selectedDate, setSelectedDate] = useState<string>('')
  const [availableDates, setAvailableDates] = useState<string[]>([])
  const [allSchedules, setAllSchedules] = useState<(Schedule & { care_date?: string })[]>([])
  const [schedules, setSchedules] = useState<Schedule[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)
  const [summary, setSummary] = useState<CarePlanSummary>({ totalActivities: 0, careDays: 0 })

  // 기본 활동 데이터 (API에서 데이터가 없을 경우 사용)
  const defaultActivities = [
    { time: '07:00', title: '기상 도움', assignee: '간병인' },
    { time: '07:30', title: '아침 식사 준비', assignee: '가족' },
    { time: '08:00', title: '약 복용 확인', assignee: '간병인', note: '처방된 약물 확인 필요' },
    { time: '09:00', title: '가벼운 스트레칭', assignee: '간병인' },
    { time: '10:00', title: '산책 (날씨 좋을 시)', assignee: '가족' },
    { time: '12:00', title: '점심 식사 준비', assignee: '간병인' }
  ]

  useEffect(() => {
    fetchCarePlans()
  }, [])

  // 선택된 날짜가 변경되면 해당 날짜의 스케줄만 필터링
  useEffect(() => {
    if (selectedDate && allSchedules.length > 0) {
      const filtered = allSchedules.filter(s => s.care_date === selectedDate)
      setSchedules(filtered)
    }
  }, [selectedDate, allSchedules])

  const fetchCarePlans = async () => {
    const patientId = sessionStorage.getItem('patient_id') || sessionStorage.getItem('selected_patient_id')
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
      const apiUrl = `/api/patients/${patientId}/schedules?status=pending_review`
      console.log('[CarePlans] Fetching from:', apiUrl)

      const response = await apiGet<ScheduleResponse>(apiUrl)

      console.log('[CarePlans] API Response:', response)

      if (!response) {
        throw new Error('서버에서 응답을 받지 못했습니다')
      }

      if (!validateScheduleResponse(response)) {
        console.error('[CarePlans] Invalid response structure:', response)
        throw new Error('유효하지 않은 응답 구조입니다')
      }

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

      // care_logs를 schedules 형식으로 변환 (날짜 포함)
      const convertedSchedules: (Schedule & { care_date?: string })[] = response.care_logs
        .filter((log: CareLog) => validateCareLog(log))
        .map((log: CareLog) => ({
          schedule_id: log.schedule_id,
          title: log.task_name,
          start_time: log.scheduled_time || '00:00',
          end_time: '00:00',
          category: log.category || 'other',
          is_completed: log.is_completed,
          care_date: log.care_date
        }))

      if (convertedSchedules.length === 0) {
        throw new Error('유효한 일정 데이터가 없습니다')
      }

      console.log('[CarePlans] Converted schedules:', convertedSchedules)
      setAllSchedules(convertedSchedules)

      // 고유 날짜 추출 및 정렬
      const uniqueDates = [...new Set(response.care_logs.map((log: CareLog) => log.care_date).filter(Boolean))] as string[]
      uniqueDates.sort()
      setAvailableDates(uniqueDates)

      // 첫 번째 날짜를 기본 선택
      if (uniqueDates.length > 0) {
        setSelectedDate(uniqueDates[0])
        const firstDaySchedules = convertedSchedules.filter(s => s.care_date === uniqueDates[0])
        setSchedules(firstDaySchedules)
      } else {
        setSchedules(convertedSchedules)
      }

      // 요약 정보 업데이트
      setSummary({
        totalActivities: convertedSchedules.length,
        careDays: uniqueDates.length || 7
      })
      console.log('[CarePlans] Summary updated:', { totalActivities: convertedSchedules.length, careDays: uniqueDates.length })
    } catch (err) {
      console.error('[CarePlans] 케어 플랜 조회 실패:', err)
      setError(err as Error)
      setSchedules([])
    } finally {
      setLoading(false)
    }
  }

  // 카테고리 이름에서 이모티콘 제거
  const cleanCategory = (category: string): string => {
    // 이모티콘 패턴 제거 (유니코드 이모티콘)
    return category.replace(/[\u{1F300}-\u{1F9FF}]|[\u{2600}-\u{26FF}]|[\u{2700}-\u{27BF}]|[\u{1F600}-\u{1F64F}]|[\u{1F680}-\u{1F6FF}]/gu, '').trim()
  }

  // 스케줄을 활동 형식으로 변환
  const getActivities = () => {
    console.log('[CarePlans] getActivities called, schedules.length:', schedules.length)
    if (schedules.length > 0) {
      const activities = schedules.map(schedule => ({
        time: schedule.start_time.slice(0, 5),
        title: schedule.title,
        assignee: cleanCategory(schedule.category),
        note: schedule.is_completed ? '완료' : undefined
      }))
      console.log('[CarePlans] Returning DB activities:', activities)
      return activities
    }
    console.log('[CarePlans] Returning default hardcoded activities')
    return defaultActivities
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
              AI가 생성한 {summary.careDays}일 간병 일정입니다.
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
                <span className="text-[#18D4C6] font-bold">{schedules.length > 0 ? schedules.length : '-'}개</span>
              </button>
              <span className="text-[#828282] text-xs font-bold">오늘 활동</span>
            </div>

            <div className="flex flex-1 flex-col items-center gap-0.5">
              <button
                className="flex flex-col items-center self-stretch text-left py-[18px] rounded-[50px] border-0"
                style={{ background: "linear-gradient(180deg, #F2FFFE, #FFF4F4)" }}
              >
                <span className="text-[#18D4C6] font-bold">{summary.careDays > 0 ? `${summary.careDays}일` : '-'}</span>
              </button>
              <span className="text-[#828282] text-xs font-bold">케어 기간</span>
            </div>

            <div className="flex flex-1 flex-col items-center gap-0.5">
              <button
                className="flex flex-col items-center self-stretch text-left py-[18px] rounded-[50px] border-0"
                style={{ background: "linear-gradient(180deg, #F2FFFE, #FFF4F4)" }}
              >
                <span className="text-[#18D4C6] font-bold">{summary.totalActivities > 0 ? `${summary.totalActivities}개` : '-'}</span>
              </button>
              <span className="text-[#828282] text-xs font-bold">총 활동</span>
            </div>
          </div>
        </div>

        {/* Date Toggle Buttons */}
        <div className="flex items-start self-stretch mb-3 gap-2 overflow-x-auto pb-2">
          {availableDates.length > 0 ? (
            availableDates.map((date) => (
              <button
                key={date}
                className={`flex shrink-0 flex-col items-center text-left py-3 px-4 rounded-lg border border-solid ${
                  selectedDate === date
                    ? 'bg-[#E8FFFD] border-[#18D4C6]'
                    : 'bg-white border-[#828282]'
                }`}
                onClick={() => setSelectedDate(date)}
              >
                <span className={`text-sm font-bold whitespace-nowrap ${selectedDate === date ? 'text-[#353535]' : 'text-[#828282]'}`}>
                  {formatDateLabel(date)}
                </span>
              </button>
            ))
          ) : (
            <button
              className="flex flex-1 flex-col items-center text-left py-3.5 rounded-lg border border-solid bg-[#E8FFFD] border-[#18D4C6]"
            >
              <span className="text-base font-bold text-[#353535]">전체</span>
            </button>
          )}
        </div>

        {/* Schedule Content */}
        <div className="flex flex-col items-start self-stretch bg-white py-[19px] pr-[19px] mb-9 rounded-lg" style={{ boxShadow: "0px 1px 4px #00000040" }}>
          <span className="text-[#353535] text-base font-bold mb-[11px] ml-5">
            {selectedDate ? formatDateLabel(selectedDate) : '일정'}
          </span>

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
                    {/* <span className="text-[#828282] text-xs">
                      {activity.assignee}
                      {activity.note && ` - ${activity.note}`}
                    </span> */}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>

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
                  const patientId = sessionStorage.getItem('patient_id') || sessionStorage.getItem('selected_patient_id')
                  if (!patientId) {
                    alert('환자 정보를 찾을 수 없습니다.')
                    return
                  }

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
