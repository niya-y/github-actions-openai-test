"use client"

import React, { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { ChevronLeft, Bell, ChevronDown, ChevronRight, Check, Image as ImageIcon, Plus } from "lucide-react"
import { cn } from "@/utils/cn"
import { apiGet } from "@/utils/api"

interface Patient {
  patient_id: number
  name: string
  age: number
  gender: string
  created_at: string
}

export default function SchedulePage() {
    const router = useRouter()
    const [patients, setPatients] = useState<Patient[]>([])
    const [selectedPatient, setSelectedPatient] = useState<Patient | null>(null)
    const [patientName, setPatientName] = useState<string>("김철수님")
    const [showPatientDropdown, setShowPatientDropdown] = useState(false)
    const [isCalendarExpanded, setIsCalendarExpanded] = useState(false)
    const [currentDate, setCurrentDate] = useState(new Date(2025, 11, 5)) // Dec 5, 2025
    const [selectedDate, setSelectedDate] = useState<Date | null>(new Date(2025, 11, 5))

    // 🔧 환자 목록 불러오기
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
                            (p: Patient) => p.patient_id === parseInt(savedPatientId)
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

    const handleSelectPatient = (patient: Patient) => {
        setSelectedPatient(patient)
        setPatientName(patient.name)
        sessionStorage.setItem('selected_patient_id', patient.patient_id.toString())
        setShowPatientDropdown(false)
        console.log('[Schedule] Selected patient:', patient.name, 'ID:', patient.patient_id)
    }

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

        // Next month's days
        const remainingDays = 42 - days.length
        for (let i = 1; i <= remainingDays; i++) {
            days.push({ day: i, isCurrentMonth: false })
        }

        return days
    }

    const calendarDays = generateCalendarDays()
    const monthYear = currentDate.toLocaleDateString('ko-KR', { year: 'numeric', month: 'long' })

    return (
        <div className="min-h-screen bg-gray-50 pb-[80px]">
            {/* Header */}
            <header className="sticky top-0 z-10 bg-white px-4 h-[60px] flex items-center justify-between border-b border-gray-100">
                <button
                    onClick={() => router.back()}
                    className="p-2 -ml-2 text-gray-600 active:scale-95 transition-transform"
                    aria-label="Go back"
                >
                    <ChevronLeft className="w-6 h-6" />
                </button>

                <h1 className="text-lg font-semibold text-gray-800">일정 관리</h1>

                <button
                    className="p-2 -mr-2 text-gray-600 active:scale-95 transition-transform"
                    aria-label="Notifications"
                >
                    <Bell className="w-6 h-6" />
                </button>
            </header>

            <main className="px-4 py-6 space-y-6">
                {/* User Selector */}
                <div className="relative">
                    <button
                        onClick={() => setShowPatientDropdown(!showPatientDropdown)}
                        className="w-full bg-[#18d4c6] text-white rounded-xl p-4 flex items-center justify-center gap-2 shadow-sm active:scale-95 hover:shadow-md transition-all"
                    >
                        <span className="text-lg font-bold">{patientName}</span>
                        <ChevronDown className={`w-5 h-5 transition-transform duration-200 ${showPatientDropdown ? 'rotate-180' : ''}`} />
                    </button>

                    {/* Patient Dropdown */}
                    {showPatientDropdown && patients.length > 0 && (
                        <div className="absolute top-full left-0 right-0 mt-2 bg-white rounded-[15px] shadow-lg border border-[#f0f0f0] z-50">
                            <div className="py-2">
                                {patients.map((patient, index) => (
                                    <button
                                        key={patient.patient_id}
                                        onClick={() => handleSelectPatient(patient)}
                                        className={`w-full px-4 py-3 text-left flex items-center justify-between hover:bg-[#F9F9F9] active:bg-[#F0F0F0] transition-colors duration-150 ${
                                            index !== patients.length - 1 ? 'border-b border-[#f0f0f0]' : ''
                                        }`}
                                    >
                                        <div className="flex flex-col">
                                            <span className="text-sm font-semibold text-[#353535]">{patient.name}</span>
                                            <span className="text-xs text-[#828282]">{patient.age}세</span>
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
                <div className={`relative bg-white rounded-2xl p-5 shadow-sm transition-all duration-300 ${isCalendarExpanded ? 'z-50' : ''}`}>
                    <div className="flex items-center justify-between mb-4">
                        <h2 className="text-lg font-bold text-gray-900">{monthYear}</h2>
                        {isCalendarExpanded && (
                            <div className="flex gap-4">
                                <button
                                    onClick={() => setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1))}
                                    className="text-gray-400 hover:text-gray-600 active:scale-90 transition-all"
                                >
                                    <ChevronLeft className="w-5 h-5" />
                                </button>
                                <button
                                    onClick={() => setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1))}
                                    className="text-gray-400 hover:text-gray-600 active:scale-90 transition-all"
                                >
                                    <ChevronRight className="w-5 h-5" />
                                </button>
                            </div>
                        )}
                    </div>

                    <div className="grid grid-cols-7 gap-1 text-center mb-2">
                        {["일", "월", "화", "수", "목", "금", "토"].map((day) => (
                            <div key={day} className="text-xs text-gray-500 font-medium">
                                {day}
                            </div>
                        ))}
                    </div>

                    {/* Collapsible Calendar Grid */}
                    <div className={`overflow-hidden transition-all duration-300 ${isCalendarExpanded ? 'max-h-[400px]' : 'max-h-[50px]'}`}>
                        <div className="grid grid-cols-7 gap-1 text-center">
                            {calendarDays.map((dayObj, i) => {
                                const isCurrentMonth = dayObj.isCurrentMonth
                                const isToday = isCurrentMonth && dayObj.day === 5
                                const isSelected = selectedDate && isCurrentMonth && dayObj.day === selectedDate.getDate()

                                return (
                                    <button
                                        key={i}
                                        onClick={() => isCurrentMonth && setSelectedDate(new Date(currentDate.getFullYear(), currentDate.getMonth(), dayObj.day))}
                                        className={cn(
                                            "flex flex-col items-center gap-1 py-1",
                                            !isCurrentMonth && "opacity-40 cursor-default",
                                            isCurrentMonth && "hover:bg-gray-100 cursor-pointer rounded-lg transition-colors",
                                            isSelected && "bg-[#18d4c6] text-white rounded-lg"
                                        )}
                                    >
                                        <span className={cn(
                                            "text-sm font-medium",
                                            isToday ? "font-bold text-gray-900" : isSelected ? "text-white" : "text-gray-500"
                                        )}>
                                            {dayObj.day}
                                        </span>
                                        {isToday && (
                                            <div className={cn("w-1.5 h-1.5 rounded-full", isSelected ? "bg-white" : "bg-[#18d4c6]")} />
                                        )}
                                    </button>
                                )
                            })}
                        </div>
                    </div>

                    {/* Drag handle */}
                    <button
                        onClick={() => setIsCalendarExpanded(!isCalendarExpanded)}
                        className="w-full flex justify-center mt-2 py-1 active:bg-gray-50 rounded-lg transition-colors"
                    >
                        <div className={cn("w-10 h-1 bg-gray-200 rounded-full transition-transform duration-300", isCalendarExpanded && "rotate-180")} />
                    </button>
                </div>

                {/* Daily Plan Title */}
                <div>
                    <p className="text-sm text-gray-500 mb-1">
                        {selectedDate ? selectedDate.toLocaleDateString('ko-KR', { month: 'long', day: 'numeric' }) : '12월 5일'}
                    </p>
                    <h2 className="text-xl font-bold text-gray-900">
                        {selectedDate && selectedDate.toDateString() === new Date().toDateString() ? '오늘의 돌봄 계획' : '돌봄 계획'}
                    </h2>
                </div>

                {/* Task List */}
                <div className="space-y-4">

                    {/* Completed Task */}
                    <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100 flex items-start gap-4 hover:shadow-md active:scale-95 transition-all cursor-pointer">
                        <div className="w-6 h-6 rounded-full bg-[#18d4c6] flex items-center justify-center shrink-0 mt-0.5">
                            <Check className="w-4 h-4 text-white" />
                        </div>
                        <div>
                            <h3 className="text-base font-bold text-gray-600">아침 약 복용</h3>
                            <p className="text-sm text-gray-400 mt-0.5">08:00 / 식후 30분</p>
                        </div>
                    </div>

                    {/* Pending Task with Photo Button */}
                    <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100 flex gap-4 relative overflow-hidden hover:shadow-md transition-shadow cursor-pointer">
                        <div className="absolute left-0 top-0 bottom-0 w-1.5 bg-[#18d4c6]" />
                        <button className="w-6 h-6 rounded-full border-2 border-gray-300 shrink-0 mt-0.5 ml-2 hover:border-[#18d4c6] transition-colors active:scale-90" />
                        <div className="flex-1">
                            <h3 className="text-base font-bold text-gray-900">점심식사</h3>
                            <p className="text-sm text-gray-500 mt-0.5">12:30 / 일반식(저염)</p>

                            <button className="mt-3 w-full max-w-[160px] h-10 border border-gray-200 rounded-lg flex items-center justify-center gap-2 text-gray-500 hover:bg-gray-50 active:bg-gray-100 transition-colors">
                                <ImageIcon className="w-4 h-4" />
                                <span className="text-xs font-medium">사진보기</span>
                            </button>
                        </div>
                    </div>

                    {/* Pending Task with FAB */}
                    <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100 flex items-center justify-between hover:shadow-md transition-shadow">
                        <div className="flex items-start gap-4">
                            <button className="w-6 h-6 rounded-full border-2 border-gray-300 shrink-0 mt-0.5 hover:border-[#18d4c6] transition-colors active:scale-90" />
                            <div>
                                <h3 className="text-base font-bold text-gray-900">산책 및 말벗</h3>
                                <p className="text-sm text-gray-500 mt-0.5">15:00 / 날씨 맑음</p>
                            </div>
                        </div>

                        <button className="w-10 h-10 bg-[#18d4c6] rounded-full flex items-center justify-center text-white shadow-md hover:bg-[#15b5aa] active:scale-90 transition-all">
                            <Plus className="w-6 h-6" />
                        </button>
                    </div>

                </div>
            </main>
        </div>
    )
}
