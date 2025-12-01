'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { apiPost } from '@/utils/api'
import CarePlanCreate1 from '@/components/pages/CarePlanCreate1'
import CarePlanCreate2 from '@/components/pages/CarePlanCreate2'
import CarePlanCreate3 from '@/components/pages/CarePlanCreate3'
import CarePlanCreate4 from '@/components/pages/CarePlanCreate4'

export default function CarePlanCreatePage() {
  const router = useRouter()
  const [step, setStep] = useState(1)
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState({
    // AI로부터 생성된 케어 플랜 데이터
  })

  // 컴포넌트 마운트 시 AI로부터 케어 플랜 생성
  useEffect(() => {
    const generateCarePlan = async () => {
      try {
        setLoading(true)

        // sessionStorage에서 필요한 정보 추출
        const patientId = sessionStorage.getItem('selected_patient_id')
        const matchingId = sessionStorage.getItem('matching_id')
        const selectedCaregiverStr = sessionStorage.getItem('selectedCaregiver')
        const personalityScoresStr = sessionStorage.getItem('personality_scores')

        console.log('[Care Plan Create] Starting API call...')
        console.log('patientId:', patientId)
        console.log('matchingId:', matchingId)
        console.log('selectedCaregiver:', selectedCaregiverStr ? JSON.parse(selectedCaregiverStr) : null)
        console.log('personalityScores:', personalityScoresStr ? JSON.parse(personalityScoresStr) : null)

        if (!patientId || !matchingId || !selectedCaregiverStr) {
          console.warn('필요한 정보가 부족합니다')
          return
        }

        const selectedCaregiver = JSON.parse(selectedCaregiverStr)
        const personalityScores = personalityScoresStr ? JSON.parse(personalityScoresStr) : {
          empathy_score: 50,
          activity_score: 50,
          patience_score: 50,
          independence_score: 50
        }

        // 🔴 FIX ISSUE #2: care_requirements를 sessionStorage에서 가져오기
        const careRequirementsStr = sessionStorage.getItem('care_requirements')
        let careRequirements = {
          care_type: 'nursing-aide',
          time_slots: ['morning', 'afternoon'],
          gender: 'any',
          skills: []
        }

        if (careRequirementsStr) {
          try {
            const parsed = JSON.parse(careRequirementsStr)
            careRequirements = {
              care_type: parsed.care_type || 'nursing-aide',
              time_slots: parsed.time_slots || ['morning', 'afternoon'],
              gender: parsed.gender || 'any',
              skills: parsed.skills || []
            }
            console.log('[Care Plan Create] ✅ care_requirements loaded from sessionStorage:', careRequirements)
          } catch (e) {
            console.warn('[Care Plan Create] Failed to parse care_requirements, using defaults:', e)
          }
        } else {
          console.warn('[Care Plan Create] ⚠️ care_requirements not found in sessionStorage, using defaults')
        }

        const requestPayload = {
          patient_id: parseInt(patientId),
          caregiver_id: selectedCaregiver.caregiver_id,
          patient_personality: personalityScores,
          care_requirements: careRequirements
        }

        console.log('[Care Plan Create] Request payload:', requestPayload)

        // 백엔드로 케어 플랜 생성 요청
        const response = await apiPost<any>(
          '/api/care-plans/generate',
          requestPayload
        )

        console.log('[Care Plan Create] API Response received:', response)

        if (response.success) {
          // 생성된 케어 플랜을 formData에 저장
          setFormData({
            carePlan: response.data,
            patientId,
            caregiverId: selectedCaregiver.caregiver_id
          })
          console.log('[Care Plan Create] 케어 플랜이 생성되었습니다:', response.data)
        } else {
          console.warn('[Care Plan Create] API response not successful:', response)
        }
      } catch (err) {
        console.error('[Care Plan Create] 케어 플랜 생성 실패:', err)
        // 에러 발생 시에도 계속 진행 (모의 데이터 사용)
      } finally {
        setLoading(false)
      }
    }

    generateCarePlan()
  }, [])

  const handleDataChange = (stepData: any) => {
    setFormData(prev => ({ ...prev, ...stepData }))
  }

  const handleNextStep = () => {
    if (step < 4) {
      setStep(step + 1)
    } else {
      // All steps completed, navigate to dashboard
      router.push('/mypage-dashboard')
    }
  }

  const handlePrevStep = () => {
    if (step > 1) {
      setStep(step - 1)
    }
  }

  return (
    <>
      {step === 1 && (
        <CarePlanCreate1
          onNext={handleNextStep}
          initialData={formData}
        />
      )}
      {step === 2 && (
        <CarePlanCreate2
          onNext={handleNextStep}
          onPrev={handlePrevStep}
          initialData={formData}
          onDataChange={handleDataChange}
        />
      )}
      {step === 3 && (
        <CarePlanCreate3
          onNext={handleNextStep}
          onPrev={handlePrevStep}
          initialData={formData}
          onDataChange={handleDataChange}
        />
      )}
      {step === 4 && (
        <CarePlanCreate4
          onNext={handleNextStep}
          onPrev={handlePrevStep}
          initialData={formData}
          onDataChange={handleDataChange}
        />
      )}
    </>
  )
}
