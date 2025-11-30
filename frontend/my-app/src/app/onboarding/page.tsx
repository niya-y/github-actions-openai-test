"use client"

import Image from "next/image"
import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { motion, AnimatePresence } from "framer-motion"
import { Button } from "@/components/ui/button"
import { Calendar, ChevronRight, LogOut } from "lucide-react"
import { apiGet, apiPost } from "@/utils/api"

interface User {
    user_id: number
    email: string
    nickname?: string
}

export default function OnboardingPage() {
    const router = useRouter()
    const [step, setStep] = useState(1)
    const [user, setUser] = useState<User | null>(null)
    const [isLoading, setIsLoading] = useState(true)

    useEffect(() => {
        const fetchUserInfo = async () => {
            try {
                const token = localStorage.getItem('access_token')
                if (!token) {
                    router.push('/login')
                    return
                }

                const userData = await apiGet<User>('/auth/me')
                setUser(userData)

                // 🔴 CRITICAL FIX: personality_scores 저장
                // personality test 에서 sessionStorage에 저장된 답변을 DB에 저장
                const personalityAnswersStr = sessionStorage.getItem('personality_answers')
                if (personalityAnswersStr) {
                    try {
                        const personalityAnswers = JSON.parse(personalityAnswersStr)
                        console.log('[Onboarding] Saving personality test to DB:', personalityAnswers)

                        // POST /api/personality/tests 호출
                        const response = await apiPost<any>('/personality/tests', {
                            user_type: 'guardian',  // 환자 보호자로 설정
                            answers: personalityAnswers
                        })

                        if (response.success || response.data) {
                            console.log('[Onboarding] ✅ Personality test saved to DB successfully')
                            // DB에 저장되었으므로 sessionStorage의 임시 데이터는 유지 (추후 필요시 사용)
                        } else {
                            console.warn('[Onboarding] ⚠️  Personality test save response unclear:', response)
                        }
                    } catch (personalityError) {
                        console.error('[Onboarding] ❌ Failed to save personality test:', personalityError)
                        // 에러가 발생해도 계속 진행 (UI 차단하지 않음)
                    }
                }
            } catch (error) {
                console.error('사용자 정보 조회 실패:', error)
                router.push('/login')
            } finally {
                setIsLoading(false)
            }
        }

        fetchUserInfo()
    }, [router])

    const handleNext = () => {
        if (step === 1) {
            setStep(2)
        } else {
            // 온보딩 완료 플래그 저장
            localStorage.setItem('onboarded', 'true')
            router.push("/home")
        }
    }

    const handleSkip = () => {
        // 온보딩 완료 플래그 저장
        localStorage.setItem('onboarded', 'true')
        router.push("/home")
    }

    const handleLogout = () => {
        localStorage.removeItem('access_token')
        localStorage.removeItem('token_type')
        localStorage.removeItem('onboarded')
        router.push('/login')
    }

    if (isLoading) {
        return (
            <div className="flex flex-col min-h-screen bg-[#f9f7f2] relative overflow-hidden max-w-[430px] mx-auto font-['Pretendard'] items-center justify-center">
                <div className="text-gray-500">로딩 중...</div>
            </div>
        )
    }

    return (
        <div className="flex flex-col min-h-screen bg-[#f9f7f2] relative overflow-hidden max-w-[430px] mx-auto font-['Pretendard']">
            {/* Background Gradients */}
            <div className="absolute top-0 left-0 w-full h-full overflow-hidden z-0 pointer-events-none">
                <div className="absolute top-[-10%] right-[-20%] w-[400px] h-[400px] bg-purple-100/40 rounded-full blur-3xl" />
                <div className="absolute bottom-[-10%] left-[-20%] w-[400px] h-[400px] bg-pink-100/40 rounded-full blur-3xl" />
            </div>

            {/* Header - 로그인 상태 표시 */}
            <div className="relative z-10 bg-white/80 backdrop-blur-sm border-b border-gray-100 px-6 py-4 flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-400 to-pink-400 flex items-center justify-center text-white text-sm font-semibold">
                        {user?.email?.charAt(0).toUpperCase() || '?'}
                    </div>
                    <div className="flex flex-col">
                        <span className="text-sm font-semibold text-gray-900">{user?.email || 'Unknown'}</span>
                        <span className="text-xs text-green-600 font-medium">로그인됨 ✓</span>
                    </div>
                </div>
                <button
                    onClick={handleLogout}
                    className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                    title="로그아웃"
                >
                    <LogOut className="w-5 h-5 text-gray-600" />
                </button>
            </div>

            <div className="relative z-10 flex flex-col flex-1 px-6 pt-20 pb-10">
                <div className="flex-1 flex flex-col items-center justify-center text-center">
                    <AnimatePresence mode="wait">
                        {step === 1 ? (
                            <motion.div
                                key="step1"
                                initial={{ opacity: 0, x: 20 }}
                                animate={{ opacity: 1, x: 0 }}
                                exit={{ opacity: 0, x: -20 }}
                                transition={{ duration: 0.3 }}
                                className="w-full"
                            >
                                <div className="w-24 h-24 flex items-center justify-center mx-auto mb-8">
                                    <Image
                                        src="/assets/logo_color.png"
                                        alt="Neulbom Care Logo"
                                        width={96}
                                        height={96}
                                        className="w-full h-full object-contain"
                                        priority
                                    />
                                </div>
                                <h1 className="text-2xl font-bold text-gray-900 mb-4 leading-tight">
                                    쉬운 간병 경험을 <br />
                                    시작해보세요
                                </h1>
                                <p className="text-gray-500 leading-relaxed">
                                    늘봄케어와 함께라면 <br />
                                    복잡한 간병 업무도 쉬워집니다.
                                </p>
                            </motion.div>
                        ) : (
                            <motion.div
                                key="step2"
                                initial={{ opacity: 0, x: 20 }}
                                animate={{ opacity: 1, x: 0 }}
                                exit={{ opacity: 0, x: -20 }}
                                transition={{ duration: 0.3 }}
                                className="w-full"
                            >
                                <div className="w-24 h-24 bg-gradient-to-br from-purple-100 to-pink-100 rounded-3xl flex items-center justify-center mx-auto mb-8 shadow-sm">
                                    <Calendar className="w-12 h-12 text-purple-500" />
                                </div>
                                <h1 className="text-2xl font-bold text-gray-900 mb-4 leading-tight">
                                    간병 일정이 필요하신가요? <br />
                                    지금 생성해봐요!
                                </h1>
                                <p className="text-gray-500 leading-relaxed">
                                    맞춤형 일정을 생성하고 <br />
                                    체계적으로 관리할 수 있습니다.
                                </p>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>

                {/* Bottom Buttons */}
                <div className="space-y-3 mt-8">
                    <Button
                        onClick={handleNext}
                        className="w-full h-14 text-lg font-bold rounded-2xl shadow-lg shadow-primary/20 bg-primary hover:bg-primary/90"
                    >
                        {step === 1 ? "다음" : "시작하기"} <ChevronRight className="ml-1 w-5 h-5" />
                    </Button>
                    <Button
                        variant="ghost"
                        onClick={handleSkip}
                        className="w-full text-gray-400 hover:text-gray-600 hover:bg-transparent"
                    >
                        건너뛰기
                    </Button>
                </div>
            </div>
        </div>
    )
}
