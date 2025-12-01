'use client'

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import Image from "next/image"
import Link from "next/link"
import {
  Settings,
  ChevronDown,
  Search,
  Calendar,
  AlertCircle,
  Phone,
  ChevronRight
} from "lucide-react"
import { apiGet } from "@/utils/api"

interface Patient {
  patient_id: number
  name: string
  age: number
  gender: string
  created_at: string
}

interface Caregiver {
  caregiver_id: number
  name: string
  experience_years?: number
  specialties?: string[]
}

export default function HomePage() {
  const router = useRouter()
  const [patientName, setPatientName] = useState<string>("김철수님")
  const [patientId, setPatientId] = useState<number | null>(null)
  const [patients, setPatients] = useState<Patient[]>([])
  const [caregiver, setCaregiver] = useState<Caregiver | null>(null)
  const [loading, setLoading] = useState(true)
  const [showDropdown, setShowDropdown] = useState(false)

  // 🔧 FETCH PATIENTS: Get all patients and show latest
  useEffect(() => {
    const fetchPatients = async () => {
      try {
        const token = localStorage.getItem('access_token')
        if (!token) {
          console.log('[Home] No token found')
          setLoading(false)
          return
        }

        // 환자 목록 조회 (최신순)
        const response = await apiGet<any>('/api/patients/me')
        console.log('[Home] Patients data:', response)

        if (response?.patients && response.patients.length > 0) {
          setPatients(response.patients)

          // sessionStorage에서 선택된 환자 확인
          const savedPatientId = sessionStorage.getItem('selected_patient_id')

          if (savedPatientId) {
            // 저장된 환자가 있으면 그 환자 선택
            const selectedPatient = response.patients.find(
              (p: Patient) => p.patient_id === parseInt(savedPatientId)
            )
            if (selectedPatient) {
              setPatientId(selectedPatient.patient_id)
              setPatientName(selectedPatient.name)
            } else {
              // 저장된 환자가 없으면 최신 환자 선택
              const latestPatient = response.latest_patient || response.patients[0]
              setPatientId(latestPatient.patient_id)
              setPatientName(latestPatient.name)
              sessionStorage.setItem('selected_patient_id', latestPatient.patient_id.toString())
            }
          } else {
            // 저장된 환자가 없으면 최신 환자 선택
            const latestPatient = response.latest_patient || response.patients[0]
            setPatientId(latestPatient.patient_id)
            setPatientName(latestPatient.name)
            sessionStorage.setItem('selected_patient_id', latestPatient.patient_id.toString())
          }
        }
      } catch (err) {
        console.error('[Home] Error fetching patients:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchPatients()
  }, [])

  // 🔧 환자의 간병인 정보 불러오기
  const fetchCaregiverInfo = async (patientId: number) => {
    try {
      const response = await apiGet<any>(`/api/patients/${patientId}/caregiver`)
      console.log('[Home] Caregiver info:', response)
      if (response?.caregiver_id) {
        setCaregiver({
          caregiver_id: response.caregiver_id,
          name: response.caregiver_name || '할당된 간병인',
          experience_years: response.experience_years,
          specialties: response.specialties
        })
      } else {
        setCaregiver(null)
      }
    } catch (err) {
      console.log('[Home] No caregiver assigned:', err)
      setCaregiver(null)
    }
  }

  // 환자 선택 핸들러
  const handleSelectPatient = (patient: Patient) => {
    setPatientId(patient.patient_id)
    setPatientName(patient.name)
    sessionStorage.setItem('selected_patient_id', patient.patient_id.toString())
    setShowDropdown(false)
    fetchCaregiverInfo(patient.patient_id)
    console.log('[Home] Selected patient:', patient.name, 'ID:', patient.patient_id)
  }

  // 환자 ID 변경 시 간병인 정보 업데이트
  useEffect(() => {
    if (patientId) {
      fetchCaregiverInfo(patientId)
    }
  }, [patientId])

  return (
    <div className="flex flex-col min-h-screen bg-[#F9F9F9] font-['Pretendard'] pb-24">
      {/* Header */}
      <div className="px-6 pt-8 pb-6 bg-white rounded-b-[30px] shadow-sm">
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-3">
            <div className="w-[50px] h-[50px] rounded-full bg-[#18d4c6] flex items-center justify-center">
              <Image
                src="/assets/user.svg"
                alt="User"
                width={28}
                height={28}
                className="w-7 h-7 object-contain"
              />
            </div>
            <div className="flex flex-col">
              <span className="text-xs text-[#828282] font-medium">나의 돌봄 환자</span>
              <div className="flex items-center gap-1 relative">
                <button
                  onClick={() => setShowDropdown(!showDropdown)}
                  className="flex items-center gap-1 active:opacity-70 transition-opacity duration-150"
                >
                  <span className="text-xl font-bold text-[#353535]">{patientName}</span>
                  <ChevronDown className={`w-5 h-5 text-[#353535] transition-transform duration-200 ${showDropdown ? 'rotate-180' : ''}`} />
                </button>

                {/* Dropdown List */}
                {showDropdown && patients.length > 0 && (
                  <div className="absolute top-full left-0 mt-2 w-48 bg-white rounded-[15px] shadow-lg border border-[#f0f0f0] z-50">
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
                          {patientId === patient.patient_id && (
                            <div className="w-2 h-2 rounded-full bg-[#18d4c6]"></div>
                          )}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <button className="p-1">
              <Settings className="w-6 h-6 text-[#828282]" />
            </button>
            <button className="p-1">
              <Image
                src="/assets/alarm.svg"
                alt="Alarm"
                width={24}
                height={24}
                className="w-6 h-6"
              />
            </button>
          </div>
        </div>

        {/* Main Actions */}
        <div className="grid grid-cols-2 gap-4">
          {/* My Caregiver */}
          <button onClick={() => router.push('/guardians')} className="bg-[#18d4c6] rounded-[20px] p-5 h-[160px] flex flex-col justify-between shadow-md relative overflow-hidden group active:scale-95 active:shadow-sm hover:shadow-lg transition-all duration-200 cursor-pointer">
            <div className="w-12 h-12 bg-white rounded-full flex items-center justify-center shadow-sm group-active:scale-90 transition-transform duration-200">
              <Search className="w-6 h-6 text-[#18d4c6]" />
            </div>
            <div className="text-left relative z-10">
              <p className="text-lg font-bold text-white leading-tight">간병인 찾기</p>
              <p className="text-xs text-white/80 mt-1">AI 기반 안심 매치</p>
            </div>
          </button>

          {/* Add Schedule */}
          <button onClick={() => router.push('/schedule')} className="bg-white rounded-[20px] p-5 h-[160px] flex flex-col justify-between shadow-md border border-[#f0f0f0] group active:scale-95 active:shadow-sm hover:shadow-lg transition-all duration-200 cursor-pointer">
            <div className="w-12 h-12 bg-[#FFF0F0] rounded-full flex items-center justify-center">
              <Calendar className="w-6 h-6 text-[#FF6B6B]" />
            </div>
            <div className="text-left">
              <p className="text-lg font-bold text-[#353535] leading-tight">일정 추가</p>
              <p className="text-xs text-[#828282] mt-1">병원 동행, 식사 등</p>
            </div>
          </button>
        </div>
      </div>

      {/* Current Status Section */}
      <div className="px-6 mt-8">
        <h3 className="text-sm font-medium text-[#828282] mb-4">현재 돌봄 현황</h3>

        <div className="space-y-4">
          {/* Alert Card */}
          <div className="w-full bg-[#FFF0F0] rounded-[20px] p-5 flex items-center gap-4 shadow-sm cursor-pointer hover:shadow-md transition-shadow duration-200">
            <div className="w-12 h-12 rounded-full border-2 border-[#FF6B6B] flex items-center justify-center bg-white shrink-0">
              <span className="text-[#FF6B6B] text-2xl font-bold">!</span>
            </div>
            <div className="flex flex-col">
              <span className="text-[#FF6B6B] font-bold text-lg">혈압 확인 필요</span>
              <span className="text-[#FF6B6B] text-xs">평소보다 수치가 높습니다(135/82)</span>
            </div>
          </div>

          {/* Caregiver Status Card */}
          {caregiver ? (
            <div className="w-full bg-white rounded-[20px] p-5 flex items-center justify-between shadow-sm border border-[#f0f0f0] cursor-pointer hover:shadow-md active:scale-95 transition-all duration-200">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-full bg-[#18d4c6] flex items-center justify-center shrink-0">
                  <Image
                    src="/assets/user.svg"
                    alt="Caregiver"
                    width={24}
                    height={24}
                    className="w-6 h-6 object-contain"
                  />
                </div>
                <div className="flex flex-col">
                  <span className="text-[#353535] font-bold text-lg">{caregiver.name}</span>
                  <span className="text-[#828282] text-xs">오늘 09:00 ~ 18:00 예정</span>
                </div>
              </div>
              <button className="w-10 h-10 rounded-full bg-[#F5F5F5] flex items-center justify-center active:scale-90 active:bg-[#E8E8E8] hover:bg-[#EBEBEB] transition-all duration-150 cursor-pointer">
                <Phone className="w-5 h-5 text-[#555555]" />
              </button>
            </div>
          ) : (
            <div className="w-full bg-[#FFF5F5] rounded-[20px] p-5 flex items-center justify-between shadow-sm border border-[#FFE0E0] cursor-pointer hover:shadow-md active:scale-95 transition-all duration-200">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-full bg-[#FFE0E0] flex items-center justify-center shrink-0">
                  <AlertCircle className="w-6 h-6 text-[#FF6B6B]" />
                </div>
                <div className="flex flex-col">
                  <span className="text-[#FF6B6B] font-bold text-lg">간병인 미할당</span>
                  <span className="text-[#FF6B6B] text-xs">간병인 찾기를 통해 할당해주세요</span>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Activity Log Section */}
      <div className="px-6 mt-8">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-medium text-[#828282]">오늘 활동 로그</h3>
          <button className="flex items-center text-xs text-[#828282]">
            내 정보 수정 <ChevronRight className="w-3 h-3 ml-1" />
          </button>
        </div>

        <div className="bg-white rounded-[20px] p-6 shadow-sm border border-[#f0f0f0]">
          <div className="relative">
            {/* Vertical Line */}
            <div className="absolute left-[9px] top-2 bottom-2 w-[2px] bg-[#E0E0E0]"></div>

            {/* Timeline Items */}
            <div className="space-y-8">
              {/* Item 1 */}
              <div className="relative flex gap-4">
                <div className="relative z-10 w-5 h-5 rounded-full border-[3px] border-[#18d4c6] bg-white shrink-0 mt-1"></div>
                <div className="flex flex-col">
                  <span className="text-[#353535] font-bold text-base">낮잠 / 휴식</span>
                  <span className="text-[#828282] text-xs mt-1">14:32 / 1시간 30분 주무셨습니다.</span>
                </div>
              </div>

              {/* Item 2 */}
              <div className="relative flex gap-4">
                <div className="relative z-10 w-5 h-5 rounded-full border-[3px] border-[#18d4c6] bg-white shrink-0 mt-1"></div>
                <div className="flex flex-col">
                  <span className="text-[#353535] font-bold text-base">점심 식사</span>
                  <span className="text-[#828282] text-xs mt-1">12:15 / 식사량 80% 완료 (사진 있음)</span>
                </div>
              </div>

              {/* Item 3 */}
              <div className="relative flex gap-4">
                <div className="relative z-10 w-5 h-5 rounded-full border-[3px] border-[#828282] bg-white shrink-0 mt-1"></div>
                <div className="flex flex-col">
                  <span className="text-[#353535] font-bold text-base">약 복용</span>
                  <span className="text-[#828282] text-xs mt-1">08:05 / 아침약 복용 완료</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
