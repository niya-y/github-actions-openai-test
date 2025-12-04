"use client"

import { useEffect, useState } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import { Suspense } from "react"

function CallbackContent() {
    const router = useRouter()
    const searchParams = useSearchParams()
    const [error, setError] = useState<string | null>(null)

    useEffect(() => {
        const token = searchParams.get("token")

        if (token) {
            // JWT 토큰을 localStorage에 저장
            localStorage.setItem("access_token", token)
            localStorage.setItem("token_type", "bearer")

            console.log("[Auth Callback] Token saved, redirecting to /onboarding")

            // onboarding 페이지로 이동
            router.push("/onboarding")
        } else {
            setError("로그인에 실패했습니다. 토큰이 없습니다.")
            console.error("[Auth Callback] No token in URL")

            // 3초 후 로그인 페이지로 리다이렉트
            setTimeout(() => {
                router.push("/login")
            }, 3000)
        }
    }, [router, searchParams])

    if (error) {
        return (
            <div className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-br from-purple-50/30 via-pink-50/20 to-blue-50/30 max-w-[430px] mx-auto p-6">
                <div className="text-center">
                    <div className="text-red-500 text-xl mb-4">로그인 실패</div>
                    <p className="text-gray-600">{error}</p>
                    <p className="text-gray-400 text-sm mt-2">잠시 후 로그인 페이지로 이동합니다...</p>
                </div>
            </div>
        )
    }

    return (
        <div className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-br from-purple-50/30 via-pink-50/20 to-blue-50/30 max-w-[430px] mx-auto p-6">
            <div className="text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#18D4C6] mx-auto mb-4"></div>
                <p className="text-gray-600">로그인 처리 중...</p>
            </div>
        </div>
    )
}

export default function AuthCallbackPage() {
    return (
        <Suspense fallback={
            <div className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-br from-purple-50/30 via-pink-50/20 to-blue-50/30 max-w-[430px] mx-auto p-6">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#18D4C6] mx-auto mb-4"></div>
                    <p className="text-gray-600">로딩 중...</p>
                </div>
            </div>
        }>
            <CallbackContent />
        </Suspense>
    )
}
