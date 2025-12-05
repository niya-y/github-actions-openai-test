"use client"

import { useRouter } from 'next/navigation'
import { useState, useEffect } from 'react'
import { ChevronLeft, Bell, Calendar, Heart, ChevronDown } from 'lucide-react'
import { apiGet } from '@/utils/api'

// 백엔드 CareReportResponse 스키마에 맞는 인터페이스
interface CareReport {
  report_id: number
  patient_id: number
  report_type: 'daily' | 'weekly'
  start_date: string
  end_date: string
  medication_completion_rate: number | null
  meal_completion_rate: number | null
  health_status_summary: string | null
  improvement_suggestions: string | null
  created_at: string
}

// CareLog 인터페이스
interface CareLog {
  log_id: number
  schedule_id: number
  care_date: string
  task_name: string
  category: string
  scheduled_time: string | null
  is_completed: boolean
  completed_at: string | null
  note: string
}

// 스케줄 응답 인터페이스
interface ScheduleResponse {
  patient_id: number
  date: string | null
  care_logs: CareLog[]
}

// 환자 정보 인터페이스
interface Patient {
  patient_id: number
  name: string
}

// /api/patients/me 응답 인터페이스
interface PatientsResponse {
  patients: Array<{
    patient_id: number
    name: string
    age: number
    gender: string
  }>
  latest_patient: {
    patient_id: number
    name: string
  }
  total: number
}

export default function CareReportPage() {
  const router = useRouter()
  const [selectedDate, setSelectedDate] = useState<string | null>(null)
  const [careReport, setCareReport] = useState<CareReport | null>(null)
  const [careLogs, setCareLogs] = useState<CareLog[]>([])
  const [availableDates, setAvailableDates] = useState<string[]>([])
  const [showDateDropdown, setShowDateDropdown] = useState(false)
  const [patient, setPatient] = useState<Patient | null>(null)
  const [patientId, setPatientId] = useState<number | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // 사용자 정보 및 환자 ID 가져오기
  useEffect(() => {
    const fetchUserInfo = async () => {
      try {
        const token = localStorage.getItem('access_token')
        if (!token) {
          setError('로그인이 필요합니다')
          setLoading(false)
          return
        }

        // 1. 먼저 sessionStorage에서 selected_patient_id 확인
        const storedPatientId = sessionStorage.getItem('selected_patient_id')
        if (storedPatientId) {
          setPatientId(parseInt(storedPatientId))
          return
        }

        // 2. /api/patients/me API로 환자 목록 가져오기
        try {
          const patientsData = await apiGet<PatientsResponse>('/api/patients/me')
          if (patientsData?.latest_patient?.patient_id) {
            setPatientId(patientsData.latest_patient.patient_id)
            sessionStorage.setItem('selected_patient_id', patientsData.latest_patient.patient_id.toString())
            return
          }
        } catch (err) {
          console.error('환자 목록 조회 오류:', err)
        }

        // 3. 환자를 찾을 수 없는 경우
        setError('등록된 환자가 없습니다. 환자 정보를 먼저 등록해주세요.')
        setLoading(false)
      } catch (err) {
        console.error('사용자 정보 조회 오류:', err)
        setError('사용자 정보를 불러오는 중 오류가 발생했습니다')
        setLoading(false)
      }
    }

    fetchUserInfo()
  }, [])

  // 케어 로그가 있는 날짜 목록 가져오기
  useEffect(() => {
    const fetchAvailableDates = async () => {
      if (!patientId) return

      try {
        // 전체 스케줄 조회 (날짜 필터 없이)
        const response = await apiGet<ScheduleResponse>(`/api/patients/${patientId}/schedules`)
        if (response?.care_logs && response.care_logs.length > 0) {
          // 중복 제거 및 정렬 (최신 날짜 먼저)
          const dates = [...new Set(response.care_logs.map(log => log.care_date))]
            .sort((a, b) => b.localeCompare(a))
          setAvailableDates(dates)
          // 가장 최신 날짜를 기본 선택
          if (dates.length > 0 && !selectedDate) {
            setSelectedDate(dates[0])
          }
        } else {
          setAvailableDates([])
        }

        // 환자 정보 가져오기
        try {
          const patientData = await apiGet<Patient>(`/api/patients/${patientId}`)
          setPatient(patientData)
        } catch (err) {
          console.error('환자 정보 조회 오류:', err)
        }

        setLoading(false)
      } catch (err) {
        console.error('스케줄 날짜 조회 오류:', err)
        setLoading(false)
      }
    }

    fetchAvailableDates()
  }, [patientId])

  // 선택된 날짜의 케어 로그 가져오기
  useEffect(() => {
    const fetchCareLogsByDate = async () => {
      if (!patientId || !selectedDate) return

      try {
        setLoading(true)
        setError(null)

        // 해당 날짜의 케어 로그 조회
        const response = await apiGet<ScheduleResponse>(`/api/patients/${patientId}/schedules?date=${selectedDate}`)
        if (response?.care_logs) {
          setCareLogs(response.care_logs)
        } else {
          setCareLogs([])
        }

        // 케어 리포트 목록에서 해당 날짜의 리포트 찾기
        try {
          const reports = await apiGet<CareReport[]>('/api/care/care_reports')
          const matchingReport = reports.find(r =>
            r.start_date <= selectedDate && r.end_date >= selectedDate
          )
          setCareReport(matchingReport || null)
        } catch (err) {
          console.error('케어 리포트 조회 오류:', err)
        }

      } catch (err) {
        console.error('케어 로그 조회 오류:', err)
        setCareLogs([])
      } finally {
        setLoading(false)
      }
    }

    fetchCareLogsByDate()
  }, [patientId, selectedDate])

  // PDF 내보내기 (직접 다운로드)
  const handleExportPDF = async () => {
    if (!patientId || !selectedDate) {
      alert('환자 정보를 찾을 수 없습니다')
      return
    }

    try {
      const token = localStorage.getItem('access_token')
      if (!token) {
        alert('로그인이 필요합니다')
        return
      }

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const response = await fetch(
        `${apiUrl}/api/care-reports/generate-pdf/${patientId}`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({
            start_date: selectedDate,
            end_date: selectedDate,
            report_type: 'daily'
          })
        }
      )

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || 'PDF 생성 실패')
      }

      // PDF 바이트를 Blob으로 변환
      const blob = await response.blob()

      // 파일명 추출 (Content-Disposition 헤더에서)
      const contentDisposition = response.headers.get('Content-Disposition')
      let fileName = `간병일지_${selectedDate.replace(/-/g, '')}.pdf`
      if (contentDisposition) {
        const match = contentDisposition.match(/filename\*=UTF-8''(.+)/)
        if (match) {
          fileName = decodeURIComponent(match[1])
        }
      }

      // 다운로드 링크 생성 및 클릭
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = fileName
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      window.URL.revokeObjectURL(url)
    } catch (err) {
      console.error('PDF 생성 오류:', err)
      alert(err instanceof Error ? err.message : 'PDF 생성 중 오류가 발생했습니다')
    }
  }

  // 날짜 포맷팅
  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    return `${date.getFullYear()}년 ${date.getMonth() + 1}월 ${date.getDate()}일`
  }

  // 날짜 선택 핸들러
  const handleDateSelect = (date: string) => {
    setSelectedDate(date)
    setShowDateDropdown(false)
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col max-w-md mx-auto">
      {/* Header */}
      <header className="flex items-center justify-between px-4 py-3 bg-white">
        <button className="p-2 -ml-2" onClick={() => router.back()}>
          <ChevronLeft className="w-6 h-6 text-gray-700" />
        </button>
        <h1 className="text-lg font-semibold text-gray-900">케어 리포트</h1>
        <button className="p-2 -mr-2">
          <Bell className="w-6 h-6 text-gray-700" />
        </button>
      </header>

      {/* Content */}
      <main className="flex-1 px-4 py-4 space-y-4 overflow-y-auto pb-24">
        {/* Date Dropdown */}
        <div className="flex justify-end relative">
          <button
            onClick={() => setShowDateDropdown(!showDateDropdown)}
            className="flex items-center gap-2 px-3 py-2 bg-white border border-gray-200 rounded-lg text-sm text-gray-600"
          >
            <Calendar className="w-4 h-4" />
            <span>{selectedDate ? formatDate(selectedDate) : '날짜 선택'}</span>
            <ChevronDown className="w-4 h-4" />
          </button>

          {showDateDropdown && availableDates.length > 0 && (
            <div className="absolute top-full right-0 mt-1 w-48 bg-white border border-gray-200 rounded-lg shadow-lg z-10 max-h-60 overflow-y-auto">
              {availableDates.map((date) => (
                <button
                  key={date}
                  onClick={() => handleDateSelect(date)}
                  className={`w-full px-4 py-2 text-left text-sm hover:bg-gray-50 ${
                    selectedDate === date ? 'bg-[#E8FFFD] text-[#18D4C6] font-medium' : 'text-gray-700'
                  }`}
                >
                  {formatDate(date)}
                </button>
              ))}
            </div>
          )}
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#18D4C6]"></div>
          </div>
        ) : error ? (
          <div className="bg-red-50 rounded-2xl p-5 text-center">
            <p className="text-red-600">{error}</p>
          </div>
        ) : availableDates.length === 0 ? (
          <div className="bg-white rounded-2xl p-8 text-center border-2" style={{ borderColor: "#E8FFFD" }}>
            <Calendar className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500 text-lg font-medium mb-2">케어 기록이 없습니다</p>
            <p className="text-gray-400 text-sm">케어 활동이 기록된 후 리포트를 확인할 수 있습니다.</p>
          </div>
        ) : selectedDate ? (
          <>
            {/* Main Report Card */}
            <div className="bg-white rounded-2xl p-5 border-2" style={{ borderColor: "#E8FFFD" }}>
              <p className="text-sm text-gray-500 mb-1">{formatDate(selectedDate)}</p>
              <h2 className="text-xl font-bold text-gray-900 mb-3">
                {patient?.name || '환자'}님 케어 리포트
              </h2>
              <div className="border-t border-gray-200 mb-3"></div>
              <div className="flex items-center gap-2 mb-2">
                <Heart className="w-5 h-5" style={{ color: "#18D4C6" }} fill="#18D4C6" />
                <span className="font-semibold text-gray-700">전반적인 상태</span>
              </div>
              <p className="text-sm text-gray-600 leading-relaxed">
                {careReport?.health_status_summary ||
                  `${patient?.name || '환자'}님은 전반적으로 양호한 상태를 보이셨습니다.`}
              </p>
            </div>

            {/* Care Logs Section */}
            <div className="bg-white rounded-2xl p-5 border-2" style={{ borderColor: "#E8FFFD" }}>
              <h3 className="text-lg font-bold text-gray-900 mb-1">케어 활동</h3>
              <div className="border-t border-gray-200 mb-4"></div>

              {careLogs.length > 0 ? (
                <div className="space-y-3">
                  {careLogs.map((log) => (
                    <CareLogItem key={log.log_id} log={log} />
                  ))}
                </div>
              ) : (
                <p className="text-gray-500 text-center py-4">해당 날짜의 케어 활동이 없습니다.</p>
              )}
            </div>

            {/* Today's Data Section */}
            {careLogs.length > 0 && (
              <div className="bg-white rounded-2xl p-5 border-2" style={{ borderColor: "#E8FFFD" }}>
                <h3 className="text-lg font-bold text-gray-900 mb-1">데이터 요약</h3>
                <div className="border-t border-gray-200 mb-4"></div>

                <div className="space-y-4">
                  <div className="pt-2 space-y-3">
                    <ProgressItem
                      label="케어 활동 완료율"
                      value={careLogs.length > 0 ? Math.round((careLogs.filter(l => l.is_completed).length / careLogs.length) * 100) : 0}
                    />
                    <ProgressItem
                      label="약물 복용률"
                      value={(() => {
                        const medLogs = careLogs.filter(l => l.category === 'medication')
                        return medLogs.length > 0 ? Math.round((medLogs.filter(l => l.is_completed).length / medLogs.length) * 100) : 0
                      })()}
                    />
                    <ProgressItem
                      label="식사 섭취율"
                      value={(() => {
                        const mealLogs = careLogs.filter(l => l.category === 'meal')
                        return mealLogs.length > 0 ? Math.round((mealLogs.filter(l => l.is_completed).length / mealLogs.length) * 100) : 0
                      })()}
                    />
                  </div>
                </div>
              </div>
            )}

            {/* Improvement Suggestions Section */}
            {careReport?.improvement_suggestions && (
              <div className="bg-white rounded-2xl p-5 border-2" style={{ borderColor: "#E8FFFD" }}>
                <h3 className="text-lg font-bold text-gray-900 mb-1">개선 제안</h3>
                <div className="border-t border-gray-200 mb-4"></div>
                <ul className="space-y-4">
                  {careReport.improvement_suggestions.split('\n').filter(Boolean).map((suggestion, idx) => (
                    <SuggestionItem key={idx} number={idx + 1} text={suggestion} />
                  ))}
                </ul>
              </div>
            )}

            {/* Action Buttons */}
            <div className="space-y-3 pt-2">
              <button
                onClick={handleExportPDF}
                className="w-full py-4 text-white font-semibold rounded-xl transition-colors hover:opacity-90 shadow-md"
                style={{ backgroundColor: "#18D4C6" }}
              >
                PDF 내보내기
              </button>
            </div>
          </>
        ) : null}
      </main>
    </div>
  )
}

function ProgressItem({ label, value }: { label: string; value: number }) {
  return (
    <div>
      <div className="flex items-center justify-between mb-1">
        <span className="text-sm text-gray-700">{label}</span>
        <span className="text-sm font-medium text-gray-900">{value}%</span>
      </div>
      <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
        <div className="h-full rounded-full transition-all" style={{ width: `${value}%`, backgroundColor: "#18D4C6" }} />
      </div>
    </div>
  )
}

function SuggestionItem({ number, text }: { number: number; text: string }) {
  return (
    <li className="flex items-start gap-3">
      <span
        className="w-6 h-6 rounded-full text-white text-xs font-bold flex items-center justify-center flex-shrink-0 mt-0.5"
        style={{ backgroundColor: "#18D4C6" }}
      >
        {number}
      </span>
      <span className="text-sm text-gray-700 leading-relaxed">{text}</span>
    </li>
  )
}

function CareLogItem({ log }: { log: CareLog }) {
  const getCategoryStyle = (category: string) => {
    switch (category) {
      case 'medication':
        return { icon: '💊', label: '약물', color: '#FF6B6B' }
      case 'meal':
        return { icon: '🍽️', label: '식사', color: '#4ECDC4' }
      case 'exercise':
        return { icon: '🏃', label: '운동', color: '#45B7D1' }
      case 'hygiene':
        return { icon: '🧼', label: '위생', color: '#96CEB4' }
      case 'vital_check':
        return { icon: '❤️', label: '건강체크', color: '#FF6B6B' }
      case 'rest':
        return { icon: '😴', label: '휴식', color: '#A78BFA' }
      default:
        return { icon: '📋', label: '기타', color: '#6B7280' }
    }
  }

  const style = getCategoryStyle(log.category)

  return (
    <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
      <div
        className="w-10 h-10 rounded-full flex items-center justify-center text-lg"
        style={{ backgroundColor: `${style.color}20` }}
      >
        {style.icon}
      </div>
      <div className="flex-1">
        <div className="flex items-center gap-2">
          <span className="font-medium text-gray-900">{log.task_name}</span>
          <span
            className="text-xs px-2 py-0.5 rounded-full"
            style={{ backgroundColor: `${style.color}20`, color: style.color }}
          >
            {style.label}
          </span>
        </div>
        <div className="flex items-center gap-2 text-sm text-gray-500">
          {log.scheduled_time && <span>{log.scheduled_time}</span>}
          {log.note && <span>• {log.note}</span>}
        </div>
      </div>
      <div className={`w-6 h-6 rounded-full flex items-center justify-center ${log.is_completed ? 'bg-green-100' : 'bg-gray-200'}`}>
        {log.is_completed ? (
          <span className="text-green-600 text-sm">✓</span>
        ) : (
          <span className="text-gray-400 text-sm">○</span>
        )}
      </div>
    </div>
  )
}
