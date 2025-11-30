'use client'

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { Card, CardContent } from "@/components/ui/card"
import { Calendar, ChevronRight, Search, User, Sparkles, Clock, ClipboardList, LogOut } from "lucide-react"
import { apiGet } from "@/utils/api"

export default function HomePage() {
  const router = useRouter()
  const [patientName, setPatientName] = useState<string>("")
  const [loading, setLoading] = useState(true)

  // 🔧 로그아웃 함수
  const handleLogout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('patient_id')
    sessionStorage.clear()
    console.log('[Home] User logged out')
    router.push('/login')
  }

  // 🔧 FETCH USER DATA: Get patient info from API
  useEffect(() => {
    const fetchUserData = async () => {
      try {
        const token = localStorage.getItem('access_token')
        if (!token) {
          router.push('/login')
          return
        }

        // Get current user info
        const userData = await apiGet<any>('/auth/me')
        console.log('[Home] User data fetched:', userData)

        // Get patient info - assume first patient (most cases have 1 patient per guardian)
        if (userData?.patient_id) {
          const patientData = await apiGet<any>(`/api/patients/${userData.patient_id}`)
          setPatientName(patientData?.name || "환자")
          console.log('[Home] Patient data fetched:', patientData)
        }
      } catch (err) {
        console.error('[Home] Error fetching user data:', err)
        // Show default if error
        setPatientName("환자")
      } finally {
        setLoading(false)
      }
    }

    fetchUserData()
  }, [router])

  return (
    <div className="flex flex-col min-h-screen bg-gray-50 pb-24">
      {/* Header Section with Gradient Banner */}
      <div className="bg-gradient-to-br from-primary/90 to-teal-400 px-6 pt-20 pb-8 rounded-b-[2.5rem] shadow-lg shadow-primary/20 relative overflow-hidden">
        {/* Decorative Elements */}
        <div className="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full blur-3xl -mr-16 -mt-16 pointer-events-none" />
        <div className="absolute bottom-0 left-0 w-48 h-48 bg-teal-300/20 rounded-full blur-2xl -ml-10 -mb-10 pointer-events-none" />

        <div className="relative z-10">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-2xl font-bold text-white leading-tight">
                안녕하세요, <br />
                <span className="text-white/90">{loading ? "로딩 중..." : `${patientName} 보호자님`}</span>
              </h1>
            </div>
            <div className="flex gap-2">
              <button
                onClick={handleLogout}
                className="h-12 w-12 bg-white/20 backdrop-blur-md rounded-full flex items-center justify-center border border-white/30 hover:bg-red-500/40 transition-all duration-200"
                title="로그아웃"
              >
                <LogOut className="h-6 w-6 text-white" />
              </button>
              <div className="h-12 w-12 bg-white/20 backdrop-blur-md rounded-full flex items-center justify-center border border-white/30">
                <User className="h-6 w-6 text-white" />
              </div>
            </div>
          </div>

          {/* Main Feature Banner */}
          <div className="bg-white/10 backdrop-blur-md rounded-2xl p-5 border border-white/20 text-white">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-white/80 text-sm font-medium mb-1">주요 기능</p>
                <h2 className="text-lg font-bold mb-2">AI 맞춤 간병인 매칭</h2>
                <p className="text-xs text-white/70 leading-relaxed max-w-[200px]">
                  환자의 상태를 분석하여<br />최적의 전문가를 추천해드립니다.
                </p>
              </div>
              <div className="bg-white/20 p-3 rounded-full">
                <Sparkles className="h-6 w-6 text-yellow-300 fill-yellow-300" />
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="px-6 -mt-6 relative z-20 space-y-5">
        {/* Find Caregiver Button (Prominent) */}
        <Link href="/initialize" className="block group">
          <Card className="border-none shadow-lg bg-white hover:shadow-xl transition-all duration-300 overflow-hidden relative">
            <div className="absolute top-0 right-0 w-32 h-32 bg-primary/5 rounded-full blur-2xl -mr-10 -mt-10 transition-all group-hover:bg-primary/10" />
            <CardContent className="p-0">
              <div className="p-6 flex items-center justify-between relative z-10">
                <div className="flex flex-col">
                  <span className="text-lg font-bold text-gray-900 group-hover:text-primary transition-colors">간병인 찾기</span>
                  <span className="text-sm text-gray-500 mt-1">3분 만에 매칭 시작하기</span>
                </div>
                <div className="h-14 w-14 bg-gradient-to-br from-primary/10 to-teal-50 rounded-2xl flex items-center justify-center group-hover:from-primary group-hover:to-teal-400 group-hover:text-white transition-all duration-300 shadow-sm">
                  <Search className="h-7 w-7 text-primary group-hover:text-white transition-colors stroke-[1.5]" />
                </div>
              </div>
              <div className="h-1 w-full bg-gray-50">
                <div className="h-full w-1/3 bg-gradient-to-r from-primary to-teal-400 rounded-r-full" />
              </div>
            </CardContent>
          </Card>
        </Link>

        <div className="grid grid-cols-2 gap-4">
          {/* My Caregiver */}
          <Link href="/mypage-mycaregiver" className="block group">
            <Card className="h-full border-none shadow-md bg-white hover:shadow-lg transition-all duration-300 relative overflow-hidden">
              <div className="absolute bottom-0 left-0 w-20 h-20 bg-purple-50 rounded-full blur-xl -ml-5 -mb-5 transition-all group-hover:bg-purple-100" />
              <CardContent className="p-5 flex flex-col justify-between h-full relative z-10">
                <div className="mb-4">
                  <div className="h-12 w-12 bg-gradient-to-br from-purple-50 to-white border border-purple-100 rounded-2xl flex items-center justify-center mb-3 shadow-sm group-hover:scale-105 transition-transform">
                    <User className="h-6 w-6 text-purple-500 stroke-[1.5]" />
                  </div>
                  <span className="font-bold text-gray-900 block">나의 간병인</span>
                </div>
                <div className="flex items-center justify-between text-xs text-gray-500">
                  <span>관리하기</span>
                  <div className="h-2 w-2 bg-green-500 rounded-full animate-pulse shadow-[0_0_8px_rgba(34,197,94,0.5)]" />
                </div>
              </CardContent>
            </Card>
          </Link>

          {/* Create Schedule */}
          <Link href="/schedule" className="block group">
            <Card className="h-full border-none shadow-md bg-white hover:shadow-lg transition-all duration-300 relative overflow-hidden">
              <div className="absolute top-0 right-0 w-20 h-20 bg-orange-50 rounded-full blur-xl -mr-5 -mt-5 transition-all group-hover:bg-orange-100" />
              <CardContent className="p-5 flex flex-col justify-between h-full relative z-10">
                <div className="mb-4">
                  <div className="h-12 w-12 bg-gradient-to-br from-orange-50 to-white border border-orange-100 rounded-2xl flex items-center justify-center mb-3 shadow-sm group-hover:scale-105 transition-transform">
                    <Calendar className="h-6 w-6 text-orange-500 stroke-[1.5]" />
                  </div>
                  <span className="font-bold text-gray-900 block">일정 생성</span>
                </div>
                <span className="text-xs text-gray-400 group-hover:text-orange-500 transition-colors">새 일정 추가 +</span>
              </CardContent>
            </Card>
          </Link>

          {/* Patient Info */}
          <Link href="/patient-condition" className="block group col-span-2">
            <Card className="h-full border-none shadow-md bg-white hover:shadow-lg transition-all duration-300 relative overflow-hidden">
              <div className="absolute top-0 left-0 w-20 h-20 bg-blue-50 rounded-full blur-xl -ml-5 -mt-5 transition-all group-hover:bg-blue-100" />
              <CardContent className="p-5 flex items-center justify-between relative z-10">
                <div className="flex items-center gap-4">
                  <div className="h-12 w-12 bg-gradient-to-br from-blue-50 to-white border border-blue-100 rounded-2xl flex items-center justify-center shadow-sm group-hover:scale-105 transition-transform">
                    <ClipboardList className="h-6 w-6 text-blue-500 stroke-[1.5]" />
                  </div>
                  <div>
                    <span className="font-bold text-gray-900 block">환자 정보</span>
                    <span className="text-xs text-gray-500">환자 상세 정보 관리</span>
                  </div>
                </div>
                <ChevronRight className="h-5 w-5 text-gray-300 group-hover:text-blue-500 transition-colors" />
              </CardContent>
            </Card>
          </Link>
        </div>

        {/* Recent Activity / Status */}
        <div>
          <h3 className="text-lg font-bold text-gray-900 mb-3 px-1">최근 활동</h3>
          <Card className="border-none shadow-sm bg-white">
            <CardContent className="p-0">
              <div className="p-4 flex items-center gap-4 border-b border-gray-50 last:border-0">
                <div className="h-10 w-10 rounded-full bg-blue-50 flex items-center justify-center shrink-0">
                  <Clock className="h-5 w-5 text-blue-500" />
                </div>
                <div className="flex-1">
                  <p className="text-sm font-bold text-gray-900">혈압 측정 완료</p>
                  <p className="text-xs text-gray-500">오후 2:30 • 정상 범위</p>
                </div>
                <ChevronRight className="h-4 w-4 text-gray-300" />
              </div>
              <div className="p-4 flex items-center gap-4">
                <div className="h-10 w-10 rounded-full bg-green-50 flex items-center justify-center shrink-0">
                  <Clock className="h-5 w-5 text-green-500" />
                </div>
                <div className="flex-1">
                  <p className="text-sm font-bold text-gray-900">점심 식사</p>
                  <p className="text-xs text-gray-500">오후 12:30 • 전량 섭취</p>
                </div>
                <ChevronRight className="h-4 w-4 text-gray-300" />
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
