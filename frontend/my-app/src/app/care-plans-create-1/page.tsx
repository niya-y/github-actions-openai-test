'use client'

import React, { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Image from 'next/image'
import { apiPost } from '@/utils/api'

export default function CarePlanCreate1Page() {
  const router = useRouter()
  const [progress, setProgress] = useState(0)

  useEffect(() => {
    const generatePlan = async () => {
      try {
        // patient_id 또는 selected_patient_id 사용 (일관성 유지)
        const patientId = sessionStorage.getItem('patient_id') || sessionStorage.getItem('selected_patient_id')
        const caregiverData = sessionStorage.getItem('selectedCaregiver')
        const careRequirementsStr = sessionStorage.getItem('care_requirements')

        if (!patientId) {
          console.error("환자 ID 누락")
        }

        let caregiverId = 1
        if (caregiverData) {
          try {
            const caregiver = JSON.parse(caregiverData)
            caregiverId = caregiver.caregiver_id || caregiver.id || 1
          } catch (e) {
            console.error("간병인 데이터 파싱 오류", e)
          }
        }

        let careRequirements: {
          care_type: string;
          time_slots: string[];
          gender: string;
          skills: string[];
          care_start_date?: string | null;
          care_end_date?: string | null;
        } = {
          care_type: "nursing-aide",
          time_slots: ["morning", "afternoon"],
          gender: "Female",
          skills: ["dementia", "diabetes"]
        }

        if (careRequirementsStr) {
          try {
            careRequirements = JSON.parse(careRequirementsStr)
            console.log("[케어 요구사항] 날짜 포함:", careRequirements.care_start_date, "~", careRequirements.care_end_date)
          } catch (e) {
            console.error("케어 요구사항 파싱 오류", e)
          }
        }

        // sessionStorage에서 성향 점수 읽기
        let patientPersonality = {
          empathy_score: 75,        // 기본값
          activity_score: 55,       // 기본값
          patience_score: 80,       // 기본값
          independence_score: 45    // 기본값
        }

        const personalityScoresStr = sessionStorage.getItem('personality_scores')
        if (personalityScoresStr) {
          try {
            const personalityScores = JSON.parse(personalityScoresStr)
            patientPersonality = {
              empathy_score: personalityScores.empathy_score || 75,
              activity_score: personalityScores.activity_score || 55,
              patience_score: personalityScores.patience_score || 80,
              independence_score: personalityScores.independence_score || 45
            }
            console.log('[성향 점수] sessionStorage에서 로드됨:', patientPersonality)
          } catch (e) {
            console.error("성향 점수 파싱 오류", e)
            console.log('[성향 점수] 기본값 사용')
          }
        } else {
          console.log('[성향 점수] sessionStorage에 데이터 없음, 기본값 사용')
        }

        console.log("AI 케어 플랜 생성 시작...")
        console.log("[케어 플랜 생성] 날짜 정보:", careRequirements.care_start_date, "~", careRequirements.care_end_date)

        // AI 생성 요청 (날짜 포함)
        await apiPost('/api/care-plans/generate', {
          patient_id: patientId ? parseInt(patientId) : 1,
          caregiver_id: caregiverId,
          patient_personality: patientPersonality,
          care_requirements: careRequirements,
          care_start_date: careRequirements.care_start_date || null,
          care_end_date: careRequirements.care_end_date || null
        })

        console.log("AI 케어 플랜 생성 완료!")
      } catch (err) {
        console.error("케어 플랜 생성 실패:", err)
      }
    }

    // 프로그래스 바 애니메이션
    const interval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 100) {
          clearInterval(interval)
          return 100
        }
        return prev + 1
      })
    }, 30) // 3초 동안 진행

    // 0.5초 후 AI 플랜 생성 시작 (화면 로딩 후)
    const timer = setTimeout(async () => {
      try {
        await generatePlan()  // ✅ 완료 대기
        console.log("✅ 케어 플랜 생성 및 저장 완료")
        router.push('/care-plans-create-2')
      } catch (err) {
        console.error("❌ 케어 플랜 생성 실패:", err)
        // 실패해도 진행 (API 호출은 성공했거나 폴백 로직이 있음)
        router.push('/care-plans-create-2')
      }
    }, 500)  // 0.5초 후 시작

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
          AI가 케어 플랜을<br />
          생성하고 있어요
        </h2>
        <p className="text-sm text-[#828282] font-medium">
          곧 완료됩니다
          <span className="inline-block after:content-['.'] after:animate-[dots_1.5s_infinite]"></span>
        </p>
      </div>
    </div>
  )
}
