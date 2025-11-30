"use client"

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Image from 'next/image'

export default function InitializePage() {
    const router = useRouter()

    useEffect(() => {
        // Clear session storage to reset the flow
        sessionStorage.removeItem('guardian_id')
        sessionStorage.removeItem('patient_id')

        // Optional: Clear other related keys if any
        // sessionStorage.clear() // Use with caution if other data needs to persist

        // Short delay for visual feedback, then redirect
        const timer = setTimeout(() => {
            router.push('/guardians')
        }, 1500)

        return () => clearTimeout(timer)
    }, [router])

    return (
        <div className="flex flex-col items-center justify-center h-screen bg-[#f9f7f2] font-['Pretendard']">
            <div className="flex flex-col items-center animate-pulse">
                <div className="w-24 h-24 relative mb-6">
                    <Image
                        src="/assets/logo_color.png"
                        alt="Neulbom Care Logo"
                        fill
                        className="object-contain"
                        priority
                    />
                </div>
                <h2 className="text-xl font-bold text-[#18D4C6] mb-2">늘봄케어</h2>
                <p className="text-gray-500 text-sm">새로운 매칭을 준비하고 있어요...</p>
            </div>
        </div>
    )
}
