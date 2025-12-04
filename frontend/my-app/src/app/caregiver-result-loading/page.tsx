'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Image from 'next/image'

export default function CaregiverResultLoading() {
  const router = useRouter()
  const [progress, setProgress] = useState(0)

  useEffect(() => {
    // 프로그레스 바 애니메이션
    const interval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 100) {
          clearInterval(interval)
          return 100
        }
        return prev + 1
      })
    }, 30) // 3초 동안 진행

    // 3초 후 결과 페이지로 이동
    const timer = setTimeout(() => {
      router.push('/caregiver-result-list')
    }, 3000)

    return () => {
      clearInterval(interval)
      clearTimeout(timer)
    }
  }, [router])

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-white px-8">
      {/* Logo */}
      <div className="mb-12">
        <Image
          src="/assets/logo.png"
          alt="Neulbom Care"
          width={120}
          height={120}
          className="object-contain"
          priority
        />
      </div>

      {/* Progress Bar */}
      <div className="w-full max-w-[240px] h-1.5 bg-gray-100 rounded-full overflow-hidden mb-10">
        <div
          className="h-full bg-[#18d4c6] transition-all duration-100 ease-linear rounded-full"
          style={{ width: `${progress}%` }}
        />
      </div>

      <style>{`
        @keyframes dots {
          0%, 20% { content: '.'; }
          40% { content: '..'; }
          60%, 100% { content: '...'; }
        }
      `}</style>

      {/* Text */}
      <div className="text-center">
        <h2 className="text-[22px] font-bold text-[#353535] mb-4 leading-tight">
          AI가 최적의 간병인<br />
          매칭을 찾고 있어요
        </h2>
        <p className="text-sm text-[#828282] font-medium">
          곧 완료됩니다
          <span className="inline-block after:content-['.'] after:animate-[dots_1.5s_infinite]"></span>
        </p>
      </div>
    </div>
  )
}
