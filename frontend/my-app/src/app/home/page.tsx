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

export default function HomePage() {
  const router = useRouter()
  const [patientName, setPatientName] = useState<string>("김철수님")
  const [loading, setLoading] = useState(true)

  // 🔧 FETCH USER DATA: Get patient info from API
  useEffect(() => {
    const fetchUserData = async () => {
      try {
        const token = localStorage.getItem('access_token')
        if (!token) {
          // For development/demo purposes, we might not want to redirect immediately if just testing UI
          // router.push('/login')
          // return
        }

        // Get current user info
        const userData = await apiGet<any>('/auth/me')

        // Get patient info
        if (userData?.patient_id) {
          const patientData = await apiGet<any>(`/api/patients/${userData.patient_id}`)
          setPatientName(patientData?.name || "김철수님")
        }
      } catch (err) {
        console.error('[Home] Error fetching user data:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchUserData()
  }, [router])

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
              <div className="flex items-center gap-1">
                <span className="text-xl font-bold text-[#353535]">{patientName}</span>
                <ChevronDown className="w-5 h-5 text-[#353535]" />
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
          <button className="bg-[#18d4c6] rounded-[20px] p-5 h-[160px] flex flex-col justify-between shadow-md relative overflow-hidden group">
            <div className="w-12 h-12 bg-white rounded-full flex items-center justify-center shadow-sm">
              <Search className="w-6 h-6 text-[#18d4c6]" />
            </div>
            <div className="text-left relative z-10">
              <p className="text-lg font-bold text-white leading-tight">나의 간병인</p>
              <p className="text-xs text-white/80 mt-1">관리하기</p>
            </div>
          </button>

          {/* Add Schedule */}
          <button onClick={() => router.push('/schedule')} className="bg-white rounded-[20px] p-5 h-[160px] flex flex-col justify-between shadow-md border border-[#f0f0f0] group">
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
          <div className="w-full bg-[#FFF0F0] rounded-[20px] p-5 flex items-center gap-4 shadow-sm">
            <div className="w-12 h-12 rounded-full border-2 border-[#FF6B6B] flex items-center justify-center bg-white shrink-0">
              <span className="text-[#FF6B6B] text-2xl font-bold">!</span>
            </div>
            <div className="flex flex-col">
              <span className="text-[#FF6B6B] font-bold text-lg">혈압 확인 필요</span>
              <span className="text-[#FF6B6B] text-xs">평소보다 수치가 높습니다(135/82)</span>
            </div>
          </div>

          {/* Caregiver Status Card */}
          <div className="w-full bg-white rounded-[20px] p-5 flex items-center justify-between shadow-sm border border-[#f0f0f0]">
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
                <span className="text-[#353535] font-bold text-lg">안현정 간병인</span>
                <span className="text-[#828282] text-xs">오늘 09:00 ~ 18:00 예정</span>
              </div>
            </div>
            <button className="w-10 h-10 rounded-full bg-[#F5F5F5] flex items-center justify-center">
              <Phone className="w-5 h-5 text-[#555555]" />
            </button>
          </div>
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
