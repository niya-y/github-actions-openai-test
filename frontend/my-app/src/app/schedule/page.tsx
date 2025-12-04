"use client"

import React, { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { ChevronLeft, Bell, ChevronDown, ChevronRight, Check, Image as ImageIcon, Plus } from "lucide-react"
import { cn } from "@/utils/cn"
import { apiGet } from "@/utils/api"
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
    const [currentDate, setCurrentDate] = useState(new Date())
    const [selectedDate, setSelectedDate] = useState<Date>(new Date())
    const [careLogs, setCareLogs] = useState<CareLog[]>([])
    const [loading, setLoading] = useState(false)
    const [isCalendarExpanded, setIsCalendarExpanded] = useState(false)
    const [scheduleDates, setScheduleDates] = useState<Set<string>>(new Set())

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

    // 스케줄 조회 함수
    const fetchSchedules = async (patientId: number, date: Date) => {
        if (!patientId) return

        setLoading(true)
        try {
            const dateStr = date.toISOString().split('T')[0] // YYYY-MM-DD
            console.log('[Schedule] Fetching schedules for patient:', patientId, 'date:', dateStr)

            // confirmed 상태의 스케줄만 조회
            const response = await apiGet<ScheduleResponse>(`/api/patients/${patientId}/schedules?date=${dateStr}&status=confirmed`)
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

            // 스케줄 날짜 추출하여 달력에 표시
            const dates = new Set<string>()
            response.care_logs.forEach((log: CareLog) => {
                if (log.scheduled_time) {
                    const date = log.scheduled_time.split('T')[0] // YYYY-MM-DD 형식
                    dates.add(date)
                }
            })
            setScheduleDates(dates)
        } catch (err) {
            console.error('[Schedule] Error fetching schedules:', err)
            setCareLogs([])
        } finally {
            setLoading(false)
        }
    }

    // 환자나 날짜가 변경될 때 스케줄 조회
    useEffect(() => {
        if (selectedPatient) {
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

    const calendarDays = generateCalendarDays()
    const monthYear = currentDate.toLocaleDateString('ko-KR', { year: 'numeric', month: 'long' })
    const today = new Date()
    const isToday = (day: number) => {
        return currentDate.getFullYear() === today.getFullYear() &&
               currentDate.getMonth() === today.getMonth() &&
               day === today.getDate()
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
                                    className="flex flex-col items-center gap-1 py-1 hover:bg-gray-50 rounded transition-colors"
                                >
                                    <span className={cn(
                                        "text-sm font-medium",
                                        isTodayDate ? "text-gray-900 font-bold" : "text-gray-500",
                                        !dayObj.isCurrentMonth && "opacity-40"
                                    )}>
                                        {dayObj.day}
                                    </span>
                                    {hasSchedule && (
                                        <div className="w-1.5 h-1.5 rounded-full bg-[#18d4c6]" />
                                    )}
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
                                {/* Completion indicator */}
                                <div className={cn(
                                    "w-6 h-6 rounded-full flex items-center justify-center shrink-0 mt-0.5",
                                    log.is_completed
                                        ? "bg-[#18d4c6]"
                                        : "border-2 border-gray-300"
                                )}>
                                    {log.is_completed && <Check className="w-4 h-4 text-white" />}
                                </div>

                                {/* Task content */}
                                <div className="flex-1">
                                    <h3 className={cn(
                                        "text-base font-bold",
                                        log.is_completed ? "text-gray-600" : "text-gray-900"
                                    )}>
                                        {log.task_name}
                                    </h3>
                                    <p className={cn(
                                        "text-sm mt-0.5",
                                        log.is_completed ? "text-gray-400" : "text-gray-500"
                                    )}>
                                        {log.scheduled_time || "시간 미정"} / {log.note || log.category}
                                    </p>

                                    {/* Photo button if photo exists */}
                                    {log.photo_url && (
                                        <button className="mt-3 w-full max-w-[160px] h-10 border border-gray-200 rounded-lg flex items-center justify-center gap-2 text-gray-500 hover:bg-gray-50 transition-colors">
                                            <ImageIcon className="w-4 h-4" />
                                            <span className="text-xs font-medium">사진보기</span>
                                        </button>
                                    )}
                                </div>

                                {/* Action button for incomplete tasks */}
                                {!log.is_completed && (
                                    <button className="w-10 h-10 bg-[#18d4c6] rounded-full flex items-center justify-center text-white shadow-md hover:bg-[#15b5aa] transition-colors">
                                        <Plus className="w-6 h-6" />
                                    </button>
                                )}
                            </div>
                        ))
                    )}
                </div>
            </main>
        </div>
    )
}
