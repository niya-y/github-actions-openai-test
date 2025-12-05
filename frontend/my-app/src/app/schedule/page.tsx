"use client"

import React, { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { ChevronLeft, Bell, ChevronDown, ChevronRight, Check } from "lucide-react"
import { cn } from "@/utils/cn"
import { apiGet, apiPut } from "@/utils/api"
import type { PatientResponse, CareLog, ScheduleResponse } from "@/types/api"
import { validateCareLogArray, validateScheduleResponse } from "@/types/guards"
import { useAppContext, useCurrentPatient, useCarePlan } from "@/context/AppContext"

// 화면 전용 확장 타입
interface PatientWithLatest extends PatientResponse {
  created_at: string
}

export default function SchedulePage() {
    const router = useRouter()
    const appContext = useAppContext()
    const { currentPatient, setCurrentPatient } = useCurrentPatient()
    const { carePlan, setCarePlan } = useCarePlan()

    const [patients, setPatients] = useState<PatientWithLatest[]>([])
    const [selectedPatient, setSelectedPatient] = useState<PatientWithLatest | null>(null)
    const [patientName, setPatientName] = useState<string>("환자")
    const [showPatientDropdown, setShowPatientDropdown] = useState(false)
    const [isHydrated, setIsHydrated] = useState(false)

    // 초기 날짜는 null로 시작 (hydration 에러 방지)
    const [currentDate, setCurrentDate] = useState<Date | null>(null)
    const [selectedDate, setSelectedDate] = useState<Date | null>(null)
    const [careLogs, setCareLogs] = useState<CareLog[]>([])
    const [loading, setLoading] = useState(false)
    const [isCalendarExpanded, setIsCalendarExpanded] = useState(false)
    const [scheduleDates, setScheduleDates] = useState<Set<string>>(new Set())

    // 클라이언트에서만 초기 날짜 설정 (hydration 에러 방지)
    useEffect(() => {
        const getCareStartDate = (): Date => {
            const careRequirementsStr = sessionStorage.getItem('care_requirements')
            if (careRequirementsStr) {
                try {
                    const careRequirements = JSON.parse(careRequirementsStr)
                    if (careRequirements.care_start_date) {
                        console.log('[Schedule] 케어 시작일:', careRequirements.care_start_date)
                        return new Date(careRequirements.care_start_date)
                    }
                } catch (e) {
                    console.log('[Schedule] 케어 시작일 파싱 실패')
                }
            }
            return new Date()
        }

        const startDate = getCareStartDate()
        setCurrentDate(startDate)
        setSelectedDate(startDate)
        setIsHydrated(true)
    }, [])

    // 환자 목록 불러오기
    useEffect(() => {
        const fetchPatients = async () => {
            try {
                const token = localStorage.getItem('access_token')
                if (!token) {
                    console.log('[Schedule] No token found')
                    return
                }

                const response = await apiGet<any>('/api/patients/me')
                console.log('[Schedule] Patients data:', response)

                if (response?.patients && response.patients.length > 0) {
                    setPatients(response.patients)

                    const savedPatientId = sessionStorage.getItem('selected_patient_id')
                    if (savedPatientId) {
                        const selected = response.patients.find(
                            (p: any) => p.patient_id === parseInt(savedPatientId)
                        )
                        if (selected) {
                            setSelectedPatient(selected)
                            setPatientName(selected.name)
                        } else {
                            const latestPatient = response.latest_patient || response.patients[0]
                            setSelectedPatient(latestPatient)
                            setPatientName(latestPatient.name)
                        }
                    } else {
                        const latestPatient = response.latest_patient || response.patients[0]
                        setSelectedPatient(latestPatient)
                        setPatientName(latestPatient.name)
                    }
                }
            } catch (err) {
                console.error('[Schedule] Error fetching patients:', err)
            }
        }

        fetchPatients()
    }, [])

    const handleSelectPatient = (patient: PatientWithLatest) => {
        setSelectedPatient(patient)
        setPatientName(patient.name)
        sessionStorage.setItem('selected_patient_id', patient.patient_id.toString())
        setShowPatientDropdown(false)
        console.log('[Schedule] Selected patient:', patient.name, 'ID:', patient.patient_id)
    }

    // 전체 스케줄 날짜 조회 (달력 표시용)
    const fetchAllScheduleDates = async (patientId: number) => {
        try {
            // 모든 상태의 스케줄 조회 (날짜 필터 없이)
            const response = await apiGet<ScheduleResponse>(`/api/patients/${patientId}/schedules`)
            console.log('[Schedule] All schedules response:', response)

            if (response && validateScheduleResponse(response) && validateCareLogArray(response.care_logs)) {
                // 스케줄 날짜 추출
                const dates = new Set<string>()
                response.care_logs.forEach((log: CareLog) => {
                    if (log.care_date) {
                        dates.add(log.care_date)
                    }
                })
                console.log('[Schedule] Schedule dates:', dates)
                setScheduleDates(dates)
            }
        } catch (err) {
            console.error('[Schedule] Error fetching all schedule dates:', err)
        }
    }

    // 로컬 날짜를 YYYY-MM-DD 형식으로 변환 (UTC 변환 없이)
    const formatLocalDate = (date: Date): string => {
        const year = date.getFullYear()
        const month = String(date.getMonth() + 1).padStart(2, '0')
        const day = String(date.getDate()).padStart(2, '0')
        return `${year}-${month}-${day}`
    }

    // 스케줄 조회 함수 (선택된 날짜용)
    const fetchSchedules = async (patientId: number, date: Date) => {
        if (!patientId) return

        setLoading(true)
        try {
            // 로컬 날짜 사용 (toISOString은 UTC로 변환되어 날짜가 하루 밀릴 수 있음)
            const dateStr = formatLocalDate(date)
            console.log('[Schedule] Fetching schedules for patient:', patientId, 'date:', dateStr)

            // 모든 상태의 스케줄 조회
            const response = await apiGet<ScheduleResponse>(`/api/patients/${patientId}/schedules?date=${dateStr}`)
            console.log('[Schedule] Schedules response:', response)

            // 응답 검증 - 타입 가드 함수 사용
            if (!response) {
                console.log('[Schedule] No response from API')
                setCareLogs([])
                return
            }

            if (!validateScheduleResponse(response)) {
                console.error('[Schedule] Invalid response structure:', response)
                setCareLogs([])
                return
            }

            // care_logs 배열 검증
            if (!validateCareLogArray(response.care_logs)) {
                console.log('[Schedule] Invalid care_logs array')
                setCareLogs([])
                return
            }

            // Context와 로컬 상태에 케어 플랜 저장
            setCarePlan({
                patient_id: patientId,
                status: 'confirmed',
                schedules: response.care_logs,
                lastUpdated: new Date().toISOString()
            })
            setCareLogs(response.care_logs)
        } catch (err) {
            console.error('[Schedule] Error fetching schedules:', err)
            setCareLogs([])
        } finally {
            setLoading(false)
        }
    }

    // 일정 완료 토글 함수
    const handleToggleComplete = async (log: CareLog) => {
        if (!log.log_id) return

        const newCompletedStatus = !log.is_completed

        // 낙관적 업데이트: UI 먼저 변경
        setCareLogs(prev => prev.map(l =>
            l.log_id === log.log_id
                ? { ...l, is_completed: newCompletedStatus }
                : l
        ))

        try {
            // 백엔드 API 호출
            await apiPut(`/api/care/care_logs/${log.log_id}`, {
                is_completed: newCompletedStatus,
                completed_at: newCompletedStatus ? new Date().toISOString() : null
            })
            console.log('[Schedule] CareLog updated:', log.log_id, 'is_completed:', newCompletedStatus)
        } catch (err) {
            console.error('[Schedule] Error updating care log:', err)
            // 실패 시 롤백
            setCareLogs(prev => prev.map(l =>
                l.log_id === log.log_id
                    ? { ...l, is_completed: !newCompletedStatus }
                    : l
            ))
            alert('일정 상태 업데이트에 실패했습니다.')
        }
    }

    // 환자 선택 시 전체 스케줄 날짜 조회
    useEffect(() => {
        if (selectedPatient) {
            fetchAllScheduleDates(selectedPatient.patient_id)
        }
    }, [selectedPatient])

    // 환자나 날짜가 변경될 때 스케줄 조회
    useEffect(() => {
        if (selectedPatient && selectedDate) {
            fetchSchedules(selectedPatient.patient_id, selectedDate)
        }
    }, [selectedPatient, selectedDate])

    // 달력 날짜 생성
    const getDaysInMonth = (date: Date) => {
        return new Date(date.getFullYear(), date.getMonth() + 1, 0).getDate()
    }

    const getFirstDayOfMonth = (date: Date) => {
        return new Date(date.getFullYear(), date.getMonth(), 1).getDay()
    }

    const generateCalendarDays = () => {
        if (!currentDate) return [] // safety check (should not reach here after early return)
        const daysInMonth = getDaysInMonth(currentDate)
        const firstDay = getFirstDayOfMonth(currentDate)
        const days = []

        // Previous month's days
        const prevMonthDays = getDaysInMonth(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1, 1))
        for (let i = firstDay - 1; i >= 0; i--) {
            days.push({ day: prevMonthDays - i, isCurrentMonth: false })
        }

        // Current month's days
        for (let i = 1; i <= daysInMonth; i++) {
            days.push({ day: i, isCurrentMonth: true })
        }

        // Next month's days to fill the last row
        const remainingDays = 7 - (days.length % 7)
        if (remainingDays < 7) {
            for (let i = 1; i <= remainingDays; i++) {
                days.push({ day: i, isCurrentMonth: false })
            }
        }

        return isCalendarExpanded ? days : days.slice(0, 7) // 확장 시 전체 표시, 축소 시 첫 주만
    }

    const today = new Date()

    // 로딩 상태 표시 (hydration 전)
    if (!currentDate || !selectedDate) {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="text-gray-400">로딩 중...</div>
            </div>
        )
    }

    // 이 아래는 currentDate와 selectedDate가 null이 아님이 보장됨
    const calendarDays = generateCalendarDays()
    const monthYear = currentDate.toLocaleDateString('ko-KR', { year: 'numeric', month: 'long' })

    const isToday = (day: number) => {
        return currentDate.getFullYear() === today.getFullYear() &&
               currentDate.getMonth() === today.getMonth() &&
               day === today.getDate()
    }

    // 선택된 날짜인지 확인
    const isSelectedDate = (day: number) => {
        return currentDate.getFullYear() === selectedDate.getFullYear() &&
               currentDate.getMonth() === selectedDate.getMonth() &&
               day === selectedDate.getDate()
    }

    return (
        <div className="min-h-screen bg-gray-50 pb-[80px]">
            {/* Header */}
            <header className="sticky top-0 z-10 bg-white px-4 h-[60px] flex items-center justify-between border-b border-gray-100">
                <button
                    onClick={() => router.back()}
                    className="p-2 -ml-2 text-gray-600"
                    aria-label="Go back"
                >
                    <ChevronLeft className="w-6 h-6" />
                </button>

                <h1 className="text-lg font-semibold text-gray-800">일정 관리</h1>

                <button
                    className="p-2 -mr-2 text-gray-600"
                    aria-label="Notifications"
                >
                    <Bell className="w-6 h-6" />
                </button>
            </header>

            <main className="px-4 py-6 space-y-6">
                {/* User Selector */}
                <div className="relative">
                    <button
                        onClick={(e) => {
                            e.stopPropagation()
                            setShowPatientDropdown(!showPatientDropdown)
                        }}
                        className="w-full bg-[#18d4c6] text-white rounded-xl p-4 flex items-center justify-center gap-2 shadow-sm"
                    >
                        <span className="text-lg font-bold">{patientName}님</span>
                        <ChevronDown className={`w-5 h-5 transition-transform duration-200 ${showPatientDropdown ? 'rotate-180' : ''}`} />
                    </button>

                    {/* Patient Dropdown */}
                    {showPatientDropdown && patients.length > 0 && (
                        <div className="absolute top-full left-0 right-0 mt-2 bg-white rounded-xl shadow-lg border border-gray-200 z-50">
                            <div className="py-2">
                                {patients.map((patient, index) => (
                                    <button
                                        key={patient.patient_id}
                                        onClick={() => handleSelectPatient(patient)}
                                        className={`w-full px-4 py-3 text-left flex items-center justify-between hover:bg-gray-50 transition-colors ${
                                            index !== patients.length - 1 ? 'border-b border-gray-100' : ''
                                        }`}
                                    >
                                        <div className="flex flex-col">
                                            <span className="text-sm font-semibold text-gray-900">{patient.name}님</span>
                                            <span className="text-xs text-gray-500">{patient.age}세</span>
                                        </div>
                                        {selectedPatient?.patient_id === patient.patient_id && (
                                            <div className="w-2 h-2 rounded-full bg-[#18d4c6]"></div>
                                        )}
                                    </button>
                                ))}
                            </div>
                        </div>
                    )}
                </div>

                {/* Calendar Section */}
                <div className="bg-white rounded-2xl p-5 shadow-sm">
                    <div className="flex items-center justify-between mb-4">
                        <h2 className="text-lg font-bold text-gray-900">{monthYear}</h2>
                        <div className="flex gap-4 text-gray-400">
                            <button
                                onClick={() => setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1))}
                            >
                                <ChevronLeft className="w-5 h-5" />
                            </button>
                            <button
                                onClick={() => setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1))}
                            >
                                <ChevronRight className="w-5 h-5" />
                            </button>
                        </div>
                    </div>

                    <div className="grid grid-cols-7 gap-1 text-center mb-2">
                        {["일", "월", "화", "수", "목", "금", "토"].map((day) => (
                            <div key={day} className="text-xs text-gray-500 font-medium">
                                {day}
                            </div>
                        ))}
                    </div>

                    <div className="grid grid-cols-7 gap-1 text-center">
                        {calendarDays.map((dayObj, i) => {
                            const isTodayDate = dayObj.isCurrentMonth && isToday(dayObj.day)
                            const isSelected = dayObj.isCurrentMonth && isSelectedDate(dayObj.day)
                            // 실제 스케줄 데이터 기반으로 일정 표시
                            const dateStr = dayObj.isCurrentMonth
                                ? `${currentDate.getFullYear()}-${String(currentDate.getMonth() + 1).padStart(2, '0')}-${String(dayObj.day).padStart(2, '0')}`
                                : ''
                            const hasSchedule = scheduleDates.has(dateStr)

                            return (
                                <button
                                    key={i}
                                    onClick={() => {
                                        if (dayObj.isCurrentMonth && selectedPatient) {
                                            const newDate = new Date(currentDate.getFullYear(), currentDate.getMonth(), dayObj.day)
                                            setSelectedDate(newDate)
                                        }
                                    }}
                                    className="flex flex-col items-center py-1 hover:bg-gray-50 rounded transition-colors"
                                >
                                    {/* 날짜 표시 - 케어플랜이 있는 날에 하늘색 동그라미 */}
                                    <span className={cn(
                                        "w-8 h-8 flex items-center justify-center rounded-full text-sm font-medium transition-colors",
                                        // 선택된 날짜
                                        isSelected && "bg-[#18d4c6] text-white",
                                        // 케어플랜이 있는 날 (선택되지 않은 경우)
                                        hasSchedule && !isSelected && "bg-[#E8FFFD] text-[#18d4c6] border-2 border-[#18d4c6]",
                                        // 오늘 날짜 (케어플랜 없고 선택되지 않은 경우)
                                        isTodayDate && !isSelected && !hasSchedule && "font-bold text-gray-900",
                                        // 일반 날짜
                                        !isTodayDate && !isSelected && !hasSchedule && "text-gray-500",
                                        // 현재 월이 아닌 날짜
                                        !dayObj.isCurrentMonth && "opacity-40"
                                    )}>
                                        {dayObj.day}
                                    </span>
                                </button>
                            )
                        })}
                    </div>

                    {/* Drag handle - 클릭하면 달력 확장/축소 */}
                    <button
                        onClick={() => setIsCalendarExpanded(!isCalendarExpanded)}
                        className="flex justify-center mt-2 w-full py-2 hover:bg-gray-50 rounded transition-colors"
                        aria-label={isCalendarExpanded ? "달력 축소" : "달력 확장"}
                    >
                        <div className="w-10 h-1 bg-gray-200 rounded-full" />
                    </button>
                </div>

                {/* Daily Plan Title */}
                <div>
                    <p className="text-sm text-gray-500 mb-1">
                        {selectedDate.toLocaleDateString('ko-KR', { month: 'long', day: 'numeric' })}
                    </p>
                    <h2 className="text-xl font-bold text-gray-900">오늘의 돌봄 계획</h2>
                </div>

                {/* Task List - 스크롤 가능하도록 최대 높이 설정 */}
                <div className="space-y-4 max-h-[calc(100vh-500px)] overflow-y-auto">
                    {loading ? (
                        <div className="text-center py-8 text-gray-400">로딩 중...</div>
                    ) : careLogs.length === 0 ? (
                        <div className="bg-white rounded-xl p-8 shadow-sm border border-gray-100 text-center">
                            <p className="text-gray-400">이 날짜에 등록된 일정이 없습니다.</p>
                            <p className="text-xs text-gray-300 mt-2">케어 플랜을 생성하면 일정이 표시됩니다.</p>
                        </div>
                    ) : (
                        careLogs.map((log) => (
                            <div
                                key={log.log_id}
                                className={cn(
                                    "bg-white rounded-xl p-5 shadow-sm border border-gray-100 flex gap-4 relative overflow-hidden",
                                    !log.is_completed && "border-l-4 border-l-[#18d4c6]"
                                )}
                            >
                                {/* Completion indicator - 클릭 가능 */}
                                <button
                                    onClick={() => handleToggleComplete(log)}
                                    className={cn(
                                        "w-6 h-6 rounded-full flex items-center justify-center shrink-0 mt-0.5 transition-colors cursor-pointer",
                                        log.is_completed
                                            ? "bg-[#18d4c6] hover:bg-[#15b5aa]"
                                            : "border-2 border-gray-300 hover:border-[#18d4c6] hover:bg-gray-50"
                                    )}
                                    aria-label={log.is_completed ? "완료 취소" : "완료 표시"}
                                >
                                    {log.is_completed && <Check className="w-4 h-4 text-white" />}
                                </button>

                                {/* Task content */}
                                <div className="flex-1">
                                    <h3 className={cn(
                                        "text-base font-bold",
                                        log.is_completed ? "text-gray-400 line-through" : "text-gray-900"
                                    )}>
                                        {log.task_name}
                                    </h3>
                                    <p className={cn(
                                        "text-sm mt-0.5",
                                        log.is_completed ? "text-gray-300" : "text-gray-500"
                                    )}>
                                        {log.scheduled_time || "시간 미정"} / {log.note || log.category}
                                    </p>
                                </div>
                            </div>
                        ))
                    )}
                </div>
            </main>
        </div>
    )
}
