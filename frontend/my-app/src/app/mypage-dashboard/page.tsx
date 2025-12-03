"use client"

import { useRouter } from "next/navigation"
import Image from "next/image"
import { useEffect, useState } from "react"
import {
  ChevronLeft,
  ChevronRight,
  Bell,
  User,
  Plus,
  CreditCard,
  FileText,
  Headphones,
  Calendar,
  MessageCircle,
  Home,
  Settings
} from "lucide-react"
import { apiGet } from "@/utils/api"

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
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchUserInfo = async () => {
      try {
        const response = await apiGet<any>("/api/users/me/dashboard")
        if (response && response.user && response.user.name) {
          setUserName(response.user.name)
        }
      } catch (error) {
        console.error("사용자 정보 조회 실패:", error)
        setUserName("사용자")
      } finally {
        setLoading(false)
      }
    }

    fetchUserInfo()
  }, [])

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
          {/* Existing Patient Card */}
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
            <div className="flex flex-col items-start">
              <span className="text-lg font-bold text-[#353535]">김철수님(부)</span>
              <span className="text-xs font-medium text-[#646464]">서울시 서초구 반포..</span>
            </div>
            <button className="absolute right-5 p-2 hover:bg-gray-50 rounded-full transition-colors">
              <Settings className="w-5 h-5 text-[#c8c8c8]" />
            </button>
          </div>

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
    </div>
  )
}
