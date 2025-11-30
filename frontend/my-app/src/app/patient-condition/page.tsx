'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import PatientCondition1 from '@/components/pages/PatientCondition1'
import PatientCondition2 from '@/components/pages/PatientCondition2'
import PatientCondition3 from '@/components/pages/PatientCondition3'

export default function PatientConditionPage() {
  const router = useRouter()
  const [step, setStep] = useState(1)
  const [formData, setFormData] = useState({
    // Step 1 data
    name: '',
    birthDate: '',
    gender: 'female',
    relationship: '',
    // Step 2 data
    selectedDiseases: ['dementia', 'diabetes', 'hypertension'],
    selectedMobility: 'assistive-device',
    otherDisease: '',
    // Step 3 data
    medications: ['아스피린 100mg', '메트포민 500mg', '암로디핀 5mg'],
    notes: ''
  })

  const handleDataChange = (stepData: any) => {
    setFormData(prev => ({ ...prev, ...stepData }))
  }

  const handleNextStep = () => {
    if (step < 3) {
      setStep(step + 1)
    } else {
      // 모든 단계 완료 후 다음 페이지로 이동
      router.push('/caregiver-finder')
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
        <PatientCondition1
          onNext={handleNextStep}
          initialData={formData}
          onDataChange={handleDataChange}
        />
      )}
      {step === 2 && (
        <PatientCondition2
          onNext={handleNextStep}
          onPrev={handlePrevStep}
          initialData={formData}
          onDataChange={handleDataChange}
        />
      )}
      {step === 3 && (
        <PatientCondition3
          onNext={handleNextStep}
          onPrev={handlePrevStep}
          initialData={formData}
          onDataChange={handleDataChange}
        />
      )}
    </>
  )
}
