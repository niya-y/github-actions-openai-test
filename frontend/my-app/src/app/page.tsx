'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'

export default function RootPage() {
    const router = useRouter()

    useEffect(() => {
        // 🔧 AUTH REDIRECT: Check if user is logged in
        const token = localStorage.getItem('access_token')

        if (token) {
            // ✅ User is logged in → Show home page (main dashboard)
            router.push('/home')
            console.log('[Root] Authenticated user → Redirecting to /home')
        } else {
            // ❌ User is not logged in → Show welcome/onboarding
            router.push('/welcome')
            console.log('[Root] New/logged-out user → Redirecting to /welcome')
        }
    }, [router])

    // Show loading state while redirecting
    return (
        <div className="flex items-center justify-center h-screen">
            <div className="text-center">
                <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-primary border-t-transparent mb-4"></div>
                <p className="text-gray-600">로딩 중...</p>
            </div>
        </div>
    )
}
