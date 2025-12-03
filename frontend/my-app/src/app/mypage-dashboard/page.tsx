"use client"

import { useRouter } from "next/navigation"
import Image from "next/image"
import { useEffect, useState } from "react"
import {
  ChevronLeft,
  ChevronRight,
  ChevronDown,
  Bell,
  User,
  Plus,
  CreditCard,
  FileText,
  Headphones,
  Calendar,
  MessageCircle,
  Home,
  Settings,
  Trash2
} from "lucide-react"
import { apiGet, apiDelete } from "@/utils/api"

interface Patient {
  patient_id: number
  name: string
  birth_date: string
  gender: string
  care_address: string
  relationship?: string
}

interface DashboardData {
  user: {
    name: string
    email: string
    phone: string
    user_type: string
  }
}

export default function MyPageDashboard() {
  const router = useRouter()
  const [userName, setUserName] = useState<string>("사용자")
  const [selectedPatient, setSelectedPatient] = useState<Patient | null>(null)
  const [patients, setPatients] = useState<Patient[]>([])
  const [showDropdown, setShowDropdown] = useState(false)
  const [loading, setLoading] = useState(true)
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)
  const [patientToDelete, setPatientToDelete] = useState<Patient | null>(null)

  // 환자 선택 핸들러
  const handleSelectPatient = (patient: Patient) => {
    setSelectedPatient(patient)
    sessionStorage.setItem('selected_patient_id', patient.patient_id.toString())
    setShowDropdown(false)
  }

  // 삭제 확인 팝업 열기
  const handleDeleteClick = (patient: Patient, e: React.MouseEvent) => {
    e.stopPropagation() // 드롭다운 닫힘 방지
    setPatientToDelete(patient)
    setShowDeleteConfirm(true)
  }

  // 삭제 실행
  const handleConfirmDelete = async () => {
    if (!patientToDelete) return

    try {
      await apiDelete(`/api/patients/${patientToDelete.patient_id}`)

      // 삭제 성공: 목록에서 제거
      const updatedPatients = patients.filter(p => p.patient_id !== patientToDelete.patient_id)
      setPatients(updatedPatients)

      // 삭제된 환자가 현재 선택된 환자였다면 다른 환자 선택
      if (selectedPatient?.patient_id === patientToDelete.patient_id) {
        if (updatedPatients.length > 0) {
          setSelectedPatient(updatedPatients[0])
          sessionStorage.setItem('selected_patient_id', updatedPatients[0].patient_id.toString())
        } else {
          setSelectedPatient(null)
          sessionStorage.removeItem('selected_patient_id')
        }
      }

      setShowDeleteConfirm(false)
      setPatientToDelete(null)
    } catch (error) {
      console.error('환자 삭제 실패:', error)
      alert('환자 삭제에 실패했습니다.')
    }
  }

  // 삭제 취소
  const handleCancelDelete = () => {
    setShowDeleteConfirm(false)
    setPatientToDelete(null)
  }

  useEffect(() => {
    const fetchData = async () => {
      try {
        // 사용자 정보 가져오기
        const dashboardResponse = await apiGet<DashboardData>("/api/users/me/dashboard")
        if (dashboardResponse && dashboardResponse.user && dashboardResponse.user.name) {
          setUserName(dashboardResponse.user.name)
        }

        // 환자 정보 가져오기 (home 화면과 동일한 메커니즘)
        const patientsResponse = await apiGet<any>('/api/patients/me')

        if (patientsResponse?.patients && patientsResponse.patients.length > 0) {
          setPatients(patientsResponse.patients)

          // sessionStorage에서 선택된 환자 확인
          const savedPatientId = sessionStorage.getItem('selected_patient_id')

          if (savedPatientId) {
            const patient = patientsResponse.patients.find(
              (p: Patient) => p.patient_id === parseInt(savedPatientId)
            )
            if (patient) {
              setSelectedPatient(patient)
            } else {
              // 저장된 환자가 없으면 최신 환자 선택
              const latestPatient = patientsResponse.latest_patient || patientsResponse.patients[0]
              setSelectedPatient(latestPatient)
            }
          } else {
            // 저장된 환자가 없으면 최신 환자 선택
            const latestPatient = patientsResponse.latest_patient || patientsResponse.patients[0]
            setSelectedPatient(latestPatient)
          }
        }

        setLoading(false)
      } catch (error) {
        console.error("데이터 가져오기 실패:", error)
        setUserName("사용자")
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  // 드롭다운 외부 클릭 시 닫기
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (showDropdown) {
        setShowDropdown(false)
      }
    }

    if (showDropdown) {
      document.addEventListener('click', handleClickOutside)
    }

    return () => {
      document.removeEventListener('click', handleClickOutside)
    }
  }, [showDropdown])

  return (
    <div className="flex flex-col min-h-screen bg-white font-['Pretendard'] pb-24">
      {/* Header */}
      <div className="relative flex items-center justify-between h-[60px] px-6 mt-4">
        <button onClick={() => router.push('/home')} className="p-2 -ml-2 hover:bg-gray-50 rounded-full transition-colors">
          <Image
            src="/assets/left_arrow.svg"
            alt="Back"
            width={16}
            height={16}
            className="w-4 h-4"
          />
        </button>
        <span className="text-lg font-bold text-[#656565] absolute left-1/2 transform -translate-x-1/2">마이페이지</span>
        <button className="p-2 -mr-2 hover:bg-gray-50 rounded-full transition-colors">
          <Image
            src="/assets/alarm.svg"
            alt="Alarm"
            width={20}
            height={20}
            className="w-5 h-5"
          />
        </button>
      </div>

      {/* Divider */}
      <div className="w-full h-[1px] bg-[#f0f0f0] my-2" />

      {/* Profile Section */}
      <div className="flex items-center px-6 mt-6 mb-8 gap-4">
        <div className="w-[60px] h-[60px] rounded-full overflow-hidden bg-[#838383] flex items-center justify-center">
          <Image
            src="/assets/user.svg"
            alt="Profile"
            width={40}
            height={40}
            className="w-10 h-10 object-contain"
          />
        </div>
        <div className="flex flex-col">
          <h2 className="text-xl font-bold text-[#353535] mb-1">{userName} 님</h2>
          <button className="flex items-center gap-1 text-sm font-medium text-[#828282] hover:text-[#646464] transition-colors">
            내 정보 수정 <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Divider */}
      <div className="w-full h-[1px] bg-[#f0f0f0] mb-6" />

      {/* Patient Management Section */}
      <div className="px-6 mb-8">
        <h3 className="text-sm font-medium text-[#828282] mb-4">환자 관리</h3>

        <div className="space-y-4">
          {/* Existing Patient Card with Dropdown */}
          {selectedPatient && (
            <div className="relative">
              <div className="w-full h-[76px] bg-white rounded-[10px] shadow-[0px_1px_4px_#00000040] flex items-center px-5 relative">
                <div className="w-10 h-10 bg-[#18d4c6] rounded-full flex items-center justify-center mr-4 overflow-hidden">
                  <Image
                    src="/assets/user.svg"
                    alt="Patient"
                    width={24}
                    height={24}
                    className="w-6 h-6 object-contain"
                  />
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    setShowDropdown(!showDropdown)
                  }}
                  className="flex-1 flex items-center justify-between hover:opacity-80 transition-opacity"
                >
                  <div className="flex flex-col items-start">
                    <div className="flex items-center gap-1">
                      <span className="text-lg font-bold text-[#353535]">
                        {selectedPatient.name}님{selectedPatient.relationship ? `(${selectedPatient.relationship})` : ''}
                      </span>
                      <ChevronDown className={`w-4 h-4 text-[#353535] transition-transform duration-200 ${showDropdown ? 'rotate-180' : ''}`} />
                    </div>
                    {selectedPatient.care_address && (
                      <span className="text-xs font-medium text-[#646464]">
                        {selectedPatient.care_address.substring(0, 20)}...
                      </span>
                    )}
                  </div>
                </button>
                <button className="p-2 hover:bg-gray-50 rounded-full transition-colors">
                  <Settings className="w-5 h-5 text-[#c8c8c8]" />
                </button>
              </div>

              {/* Dropdown List */}
              {showDropdown && patients.length > 0 && (
                <div className="absolute top-full left-0 right-0 mt-2 bg-white rounded-[10px] shadow-lg border border-[#f0f0f0] z-50">
                  <div className="py-2">
                    {patients.map((patient, index) => (
                      <div
                        key={patient.patient_id}
                        className={`w-full px-5 py-3 flex items-center justify-between hover:bg-[#F9F9F9] transition-colors duration-150 ${
                          index !== patients.length - 1 ? 'border-b border-[#f0f0f0]' : ''
                        } ${selectedPatient?.patient_id === patient.patient_id ? 'bg-[#F9F9F9]' : ''}`}
                      >
                        <button
                          onClick={() => handleSelectPatient(patient)}
                          className="flex-1 flex items-center justify-between text-left"
                        >
                          <div className="flex flex-col">
                            <span className="text-sm font-semibold text-[#353535]">{patient.name}님</span>
                            <span className="text-xs text-[#828282]">{patient.care_address?.substring(0, 20)}...</span>
                          </div>
                          {selectedPatient?.patient_id === patient.patient_id && (
                            <div className="w-2 h-2 bg-[#18d4c6] rounded-full"></div>
                          )}
                        </button>
                        <button
                          onClick={(e) => handleDeleteClick(patient, e)}
                          className="ml-3 p-2 hover:bg-red-50 rounded-full transition-colors"
                        >
                          <Trash2 className="w-4 h-4 text-red-500" />
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* New Patient Card */}
          <button className="w-full h-[76px] bg-white rounded-[10px] shadow-[0px_1px_4px_#00000040] flex items-center px-6 hover:bg-gray-50 transition-colors">
            <div className="w-[30px] h-[30px] rounded-full border-[0.75px] border-[#353535] flex items-center justify-center mr-4">
              <Plus className="w-4 h-4 text-[#353535]" />
            </div>
            <span className="text-lg font-bold text-[#353535]">새 환자 등록하기</span>
          </button>
        </div>
      </div>

      {/* Care Record Section */}
      <div className="px-6 mb-8">
        <h3 className="text-sm font-medium text-[#828282] mb-4">돌봄 기록</h3>

        <div className="space-y-4">
          {/* Weekly Report */}
          <button onClick={() => router.push('/mypage-care-report')} className="w-full h-[76px] bg-white rounded-[10px] shadow-[0px_1px_4px_#00000040] flex items-center justify-between px-6 hover:bg-gray-50 transition-colors">
            <span className="text-lg font-semibold text-[#353535]">지난 주간 리포트 모아보기</span>
            <ChevronRight className="w-5 h-5 text-[#c8c8c8]" />
          </button>

          {/* Past History */}
          <button className="w-full h-[76px] bg-white rounded-[10px] shadow-[0px_1px_4px_#00000040] flex items-center justify-between px-6 hover:bg-gray-50 transition-colors">
            <span className="text-lg font-semibold text-[#353535]">이전 간병인 내역 / 찜목록</span>
            <ChevronRight className="w-5 h-5 text-[#c8c8c8]" />
          </button>
        </div>
      </div>

      {/* Payment & Settings Section */}
      <div className="px-6 mb-8">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-medium text-[#828282]">결제 및 설정</h3>
          <span className="text-xs font-semibold text-[#828282]">국민카드 등록됨</span>
        </div>

        <div className="space-y-4">
          {/* Payment Method */}
          <button className="w-full h-[76px] bg-white rounded-[10px] shadow-[0px_1px_4px_#00000040] flex items-center justify-between px-6 hover:bg-gray-50 transition-colors">
            <span className="text-lg font-semibold text-[#353535]">결제 수단 관리</span>
            <ChevronRight className="w-5 h-5 text-[#c8c8c8]" />
          </button>

          {/* Payment History */}
          <button className="w-full h-[76px] bg-white rounded-[10px] shadow-[0px_1px_4px_#00000040] flex items-center justify-between px-6 hover:bg-gray-50 transition-colors">
            <span className="text-lg font-semibold text-[#353535]">결제 내역 / 영수증</span>
            <ChevronRight className="w-5 h-5 text-[#c8c8c8]" />
          </button>

          {/* Customer Center */}
          <button className="w-full h-[76px] bg-white rounded-[10px] shadow-[0px_1px_4px_#00000040] flex items-center justify-between px-6 hover:bg-gray-50 transition-colors">
            <span className="text-lg font-semibold text-[#353535]">고객센터 / 문의하기</span>
            <ChevronRight className="w-5 h-5 text-[#c8c8c8]" />
          </button>

          {/* Logout Button */}
          <button
            onClick={() => {
              localStorage.removeItem('access_token')
              localStorage.removeItem('patient_id')
              sessionStorage.clear()
              router.push('/login')
            }}
            className="w-full h-[76px] bg-white rounded-[10px] shadow-[0px_1px_4px_#00000040] flex items-center justify-between px-6 hover:bg-gray-50 transition-colors mt-4"
          >
            <span className="text-lg font-semibold text-[#FF6B6B]">로그아웃</span>
            <ChevronRight className="w-5 h-5 text-[#c8c8c8]" />
          </button>
        </div>
      </div>

      {/* 삭제 확인 팝업 */}
      {showDeleteConfirm && patientToDelete && (
        <div className="fixed inset-0 flex items-center justify-center z-50 px-6 pointer-events-none">
          <div className="bg-white rounded-[20px] p-6 max-w-sm w-full shadow-2xl border-2 border-gray-200 pointer-events-auto">
            <h3 className="text-lg font-bold text-[#353535] mb-2">환자 삭제 확인</h3>
            <p className="text-sm text-[#646464] mb-6">
              <span className="font-semibold text-[#353535]">{patientToDelete.name}님</span>을(를) 정말 삭제하시겠습니까?
              <br />
              <span className="text-xs text-[#828282] mt-2 block">
                삭제된 환자는 목록에서 사라지지만, 매칭 기록은 보존됩니다.
              </span>
            </p>
            <div className="flex gap-3">
              <button
                onClick={handleCancelDelete}
                className="flex-1 py-3 bg-gray-100 text-[#646464] rounded-lg font-semibold hover:bg-gray-200 transition-colors"
              >
                취소
              </button>
              <button
                onClick={handleConfirmDelete}
                className="flex-1 py-3 bg-red-500 text-white rounded-lg font-semibold hover:bg-red-600 transition-colors"
              >
                삭제
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
