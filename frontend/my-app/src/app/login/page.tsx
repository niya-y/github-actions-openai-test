"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import Image from "next/image"
import { Button } from "@/components/ui/button"
import { apiPost, apiGet } from "@/utils/api"
import ErrorAlert from "@/components/ErrorAlert"

export default function LoginPage() {
    const router = useRouter()
    const [isEmailLogin, setIsEmailLogin] = useState(false)
    const [email, setEmail] = useState("")
    const [password, setPassword] = useState("")
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState<Error | null>(null)

    // 🔧 AUTH REDIRECT: Already logged-in users should go to /home
    useEffect(() => {
        const token = localStorage.getItem('access_token')
        if (token) {
            router.push('/home')
            console.log('[Login] Authenticated user → Redirecting to /home')
        }
    }, [router])

    const handleKakaoLogin = async () => {
        setLoading(true)
        setError(null)

        try {
            // 백엔드에서 카카오 로그인 URL 가져오기
            const response = await apiGet<{ url: string }>("/auth/kakao/login")
            // 카카오 로그인 페이지로 리다이렉트
            window.location.href = response.url
        } catch (err) {
            console.error("카카오 로그인 URL 요청 실패:", err)
            setError(err as Error)
            setLoading(false)
        }
    }

    const handleEmailLogin = async (e: React.FormEvent) => {
        e.preventDefault()
        setLoading(true)
        setError(null)

        try {
            const response = await apiPost("/auth/login", {
                email,
                password
            }, { includeAuth: false }) as any

            // JWT 토큰을 localStorage에 저장
            localStorage.setItem("access_token", response.access_token)
            localStorage.setItem("token_type", response.token_type)

            // sessionStorage에서 성향 테스트 결과 읽기
            const personalityScoresStr = sessionStorage.getItem("personality_scores")
            const personalityAnswersStr = sessionStorage.getItem("personality_answers")

            // 테스트 결과가 있으면 API로 저장
            if (personalityScoresStr && personalityAnswersStr) {
                try {
                    const answers = JSON.parse(personalityAnswersStr)

                    // JWT 토큰이 들어간 상태에서 API 호출
                    await apiPost("/api/personality/tests", {
                        user_type: "guardian",
                        answers: answers, // 테스트 단계에서 저장한 답변
                    })

                    console.log("성향 테스트 결과 저장 완료")

                    // 저장 완료 후 sessionStorage 정리
                    sessionStorage.removeItem("personality_scores")
                    sessionStorage.removeItem("personality_answers")
                } catch (err) {
                    console.error("성향 테스트 결과 저장 실패:", err)
                    // 저장 실패해도 계속 진행 (사용자 경험 우선)
                }
            }

            // onboarding으로 이동
            router.push("/onboarding")
        } catch (err) {
            console.error("로그인 실패:", err)
            setError(err as Error)
        } finally {
            setLoading(false)
        }
    }

    if (isEmailLogin) {
        return (
            <div className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-br from-purple-50/30 via-pink-50/20 to-blue-50/30 max-w-[430px] mx-auto p-6">
                <ErrorAlert error={error} onClose={() => setError(null)} />

                <div className="mb-6">
                    <Image
                        src="/assets/logo_down.png"
                        alt="늘봄케어"
                        width={360}
                        height={120}
                        className="h-36 w-auto"
                    />
                </div>

                <div className="text-center mb-8">
                    <h1 className="text-2xl font-bold text-gray-900 mb-2">
                        로그인
                    </h1>
                    <p className="text-gray-600 text-sm">
                        이메일로 로그인하세요
                    </p>
                </div>

                <form onSubmit={handleEmailLogin} className="w-full max-w-sm space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            이메일
                        </label>
                        <input
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            placeholder="example@email.com"
                            required
                            disabled={loading}
                            className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 disabled:bg-gray-50"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            비밀번호
                        </label>
                        <input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            placeholder="••••••••"
                            required
                            disabled={loading}
                            className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 disabled:bg-gray-50"
                        />
                    </div>

                    <Button
                        type="submit"
                        disabled={loading || !email || !password}
                        className="w-full h-12 bg-[#18D4C6] hover:bg-[#15b5a9] text-white font-semibold rounded-lg disabled:opacity-50"
                    >
                        {loading ? "로그인 중..." : "로그인"}
                    </Button>
                </form>

                <button
                    onClick={() => setIsEmailLogin(false)}
                    className="mt-6 text-sm text-gray-600 hover:text-gray-900 underline"
                >
                    다른 방법으로 로그인
                </button>
            </div>
        )
    }

    return (
        <div className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-br from-purple-50/30 via-pink-50/20 to-blue-50/30 max-w-[430px] mx-auto p-6">
            {/* Logo */}
            <div className="mb-6">
                <Image
                    src="/assets/logo_down.png"
                    alt="늘봄케어"
                    width={360}
                    height={120}
                    className="h-36 w-auto"
                />
            </div>

            {/* Welcome Text */}
            <div className="text-center mb-12">
                <h1 className="text-2xl font-bold text-gray-900 mb-2">
                    환영합니다!
                </h1>
                <p className="text-gray-600 text-sm">
                    간편하게 시작해보세요
                </p>
            </div>

            {/* Login Buttons */}
            <div className="w-full max-w-sm">
                <Button
                    onClick={handleKakaoLogin}
                    disabled={loading}
                    className="w-full h-14 bg-[#FEE500] hover:bg-[#FEE500]/90 text-[#000000] font-semibold rounded-xl flex items-center justify-center gap-3 shadow-lg disabled:opacity-50"
                >
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                        <path d="M12 3C6.48 3 2 6.58 2 11C2 13.5 3.5 15.72 5.84 17.12L4.5 21.5L9.5 18.92C10.28 19.08 11.13 19.17 12 19.17C17.52 19.17 22 15.59 22 11.17C22 6.58 17.52 3 12 3Z" fill="currentColor" />
                    </svg>
                    {loading ? "로그인 중..." : "카카오톡으로 시작하기"}
                </Button>

                <Button
                    onClick={() => setIsEmailLogin(true)}
                    className="w-full h-14 bg-gray-100 hover:bg-gray-200 text-gray-900 font-semibold rounded-xl flex items-center justify-center gap-3 mt-4 shadow-lg"
                >
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <rect x="2" y="4" width="20" height="16" rx="2" />
                        <path d="m22 7-10 5L2 7" />
                    </svg>
                    이메일로 로그인
                </Button>

                <p className="text-xs text-gray-500 text-center mt-6">
                    로그인 시 <Link href="#" className="underline">이용약관</Link> 및{" "}
                    <Link href="#" className="underline">개인정보처리방침</Link>에 동의하게 됩니다.
                </p>
            </div>
        </div>
    )
}
