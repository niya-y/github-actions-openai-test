"use client"

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { ChevronLeft, ChevronRight } from 'lucide-react'
import { apiPost, apiGet } from '@/utils/api'
import ErrorAlert from '@/components/ErrorAlert'
import MedicationOCR from '@/components/MedicationOCR'
import type { MedicationsCreateRequest, MedicationResponse, DietaryPreferencesCreateRequest, DietaryPreferencesApiResponse } from '@/types/api'

export default function PatientCondition3Page() {
  const router = useRouter()
  const [currentMed, setCurrentMed] = useState('')
  const [medicine_names, setMedicineNames] = useState<string[]>([])
  const [loading, setLoading] = useState(false)
  const [dataLoading, setDataLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)
  const [patientId, setPatientId] = useState<number | null>(null)

  // 식이 선호 상태
  const [currentAllergy, setCurrentAllergy] = useState('')
  const [allergyFoods, setAllergyFoods] = useState<string[]>([])
  const [currentRestriction, setCurrentRestriction] = useState('')
  const [restrictionFoods, setRestrictionFoods] = useState<string[]>([])


  const handleAddMedication = (e?: React.KeyboardEvent | React.MouseEvent) => {
    // KeyboardEvent인 경우 Enter 키만 처리
    if (e && 'key' in e && e.key !== 'Enter') return

    if (currentMed.trim()) {
      const updated = [...medicine_names, currentMed.trim()]
      setMedicineNames(updated)
      setCurrentMed('')

      // ✅ 세션에 저장 (선택사항)
      sessionStorage.setItem('medicine_names', JSON.stringify(updated))
    }
  }

  const handleRemoveMedication = (index: number) => {
    const updated = medicine_names.filter((_, i) => i !== index)
    setMedicineNames(updated)

    // ✅ 세션 업데이트
    sessionStorage.setItem('medicine_names', JSON.stringify(updated))
  }

  // 알러지 음식 추가/삭제
  const handleAddAllergy = (e?: React.KeyboardEvent) => {
    if (e && e.key !== 'Enter') return
    if (currentAllergy.trim()) {
      setAllergyFoods([...allergyFoods, currentAllergy.trim()])
      setCurrentAllergy('')
    }
  }

  const handleRemoveAllergy = (index: number) => {
    setAllergyFoods(allergyFoods.filter((_, i) => i !== index))
  }

  // 식이 제한 음식 추가/삭제
  const handleAddRestriction = (e?: React.KeyboardEvent) => {
    if (e && e.key !== 'Enter') return
    if (currentRestriction.trim()) {
      setRestrictionFoods([...restrictionFoods, currentRestriction.trim()])
      setCurrentRestriction('')
    }
  }

  const handleRemoveRestriction = (index: number) => {
    setRestrictionFoods(restrictionFoods.filter((_, i) => i !== index))
  }

  // 🔧 기존 약물 정보 및 식이 선호 불러오기
  useEffect(() => {
    const loadData = async () => {
      try {
        const patientIdFromStorage = sessionStorage.getItem('patient_id')
        if (!patientIdFromStorage) {
          setDataLoading(false)
          return
        }

        setPatientId(Number(patientIdFromStorage))

        // 약물 정보 로드 (선택사항 - 실패해도 진행)
        try {
          const medResponse = await apiGet<any>(`/api/patients/${patientIdFromStorage}/medications`)
          console.log('[PatientCondition3] Medications loaded:', medResponse)
          if (medResponse?.medicine_names && medResponse.medicine_names.length > 0) {
            setMedicineNames(medResponse.medicine_names)
          }
        } catch (err) {
          console.log('[PatientCondition3] 기존 약물 정보 없음 (첫 등록):', err)
          // 에러 무시 - 새로운 환자일 수 있음
        }

        // 식이 선호 정보 로드
        try {
          const dietResponse = await apiGet<DietaryPreferencesApiResponse>(`/api/patients/${patientIdFromStorage}/dietary-preferences`)
          console.log('[PatientCondition3] Dietary preferences loaded:', dietResponse)
          if (dietResponse?.allergy_foods) {
            setAllergyFoods(dietResponse.allergy_foods)
          }
          if (dietResponse?.restriction_foods) {
            setRestrictionFoods(dietResponse.restriction_foods)
          }
        } catch (err) {
          console.log('[PatientCondition3] No existing dietary preferences:', err)
        }
      } finally {
        setDataLoading(false)
      }
    }

    loadData()
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    const patientId = sessionStorage.getItem('patient_id')
    if (!patientId) {
      alert('환자 정보를 먼저 등록해주세요.')
      router.push('/patient-condition-1')
      return
    }

    setLoading(true)
    setError(null)

    try {
      // 🔧 약물 정보 저장 (있는 경우)
      if (medicine_names.length > 0) {
        const payload: MedicationsCreateRequest = {
          medicine_names: medicine_names
        }

        const response = await apiPost<MedicationResponse>(
          `/api/patients/${patientId}/medications`,
          payload
        )

        console.log('[PatientCondition3] 약물 정보 저장 성공:', response)
      } else {
        console.log('[PatientCondition3] 약물 정보 없음 (선택사항)')
      }

      // 🔧 식이 선호 정보 저장 (있는 경우)
      if (allergyFoods.length > 0 || restrictionFoods.length > 0) {
        const dietPayload: DietaryPreferencesCreateRequest = {
          allergy_foods: allergyFoods,
          restriction_foods: restrictionFoods
        }

        const dietResponse = await apiPost<DietaryPreferencesApiResponse>(
          `/api/patients/${patientId}/dietary-preferences`,
          dietPayload
        )

        console.log('[PatientCondition3] 식이 선호 저장 성공:', dietResponse)
      } else {
        console.log('[PatientCondition3] 식이 선호 없음 (선택사항)')
      }

      // 🔧 모든 환자 정보 저장 완료
      console.log('[PatientCondition3] 환자 정보 저장 완료 (조건1+조건2+조건3)')
      console.log('[PatientCondition3] Patient ID:', patientId)

      // 다음 페이지로 이동 (모든 데이터가 저장됨)
      router.push('/caregiver-finder')
    } catch (err) {
      console.error('[PatientCondition3] 정보 저장 실패:', err)
      setError(err as Error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-white flex flex-col">
      <ErrorAlert error={error} onClose={() => setError(null)} />

      {/* Header */}
      <header className="sticky top-0 z-10 bg-white px-4 pt-4 pb-2">
        <div className="flex items-center mb-4">
          <button
            onClick={() => router.push('/patient-condition-2')}
            className="p-2 -ml-2 text-gray-600"
            aria-label="Go back"
          >
            <ChevronLeft className="w-6 h-6" />
          </button>

          {/* Progress Bar */}
          <div className="flex-1 flex gap-2 ml-4 mr-2">
            <div className="h-1 flex-1 bg-[#18d4c6] rounded-full" />
            <div className="h-1 flex-1 bg-[#18d4c6] rounded-full" />
            <div className="h-1 flex-1 bg-[#18d4c6] rounded-full" />
            <div className="h-1 flex-1 bg-[#18d4c6] rounded-full" />
            <div className="h-1 flex-1 bg-gray-200 rounded-full" />
          </div>
        </div>

        <div className="h-px bg-gray-100 -mx-4" />
      </header>

      <main className="flex-1 px-8 pt-6 pb-32 overflow-y-auto">
        <form onSubmit={handleSubmit}>
          {/* Medication Section */}
          <div className="mb-12">
            <div className="mb-8">
              <h1 className="text-[28px] font-bold text-[#353535] mb-2">복용 중인 약이 있나요?</h1>
              <p className="text-base font-bold text-[#828282]">정확한 복약 관리를 위해 필요합니다.</p>
            </div>
          {/* OCR 컴포넌트 - 실제 기능 */}
          {patientId && (
            <div className="mb-8">
              <MedicationOCR
                patientId={patientId}
                onMedicinesSelected={(medicines) => {
                  console.log('[PatientCondition3] OCR에서 선택된 약물:', medicines)
                  // OCR에서 추출된 약물을 기존 목록에 병합
                  setMedicineNames((prev) => {
                    const newMedicines = medicines.filter((m) => !prev.includes(m))
                    const updated = [...prev, ...newMedicines]

                    // ✅ 세션에 저장
                    sessionStorage.setItem('medicine_names', JSON.stringify(updated))

                    return updated
                  })
                }}
                onConfirmMedicines={(medicines) => {
                  console.log('[PatientCondition3] 사용자가 약물 선택 확정:', medicines)
                  // "확인" 버튼 클릭 시 약물 목록에 추가
                  setMedicineNames((prev) => {
                    const newMedicines = medicines.filter((m) => !prev.includes(m))
                    const updated = [...prev, ...newMedicines]

                    // ✅ 세션에 저장
                    sessionStorage.setItem('medicine_names', JSON.stringify(updated))

                    return updated
                  })
                }}
              />
            </div>
          )}

          {/* Medication List Input */}
          <div className="space-y-2 mb-4">
            <label className="text-lg font-bold text-[#353535]">약물 목록</label>
            <div className="flex gap-2">
              <input
                name="currentMed"
                type="text"
                className="flex-1 h-12 px-5 rounded-[10px] border border-[#828282] text-sm placeholder:text-[#828282] focus:outline-none focus:border-[#18d4c6]"
                placeholder="약 이름을 입력하세요 (예:아스피린, 메트포민...)"
                value={currentMed}
                onChange={(e) => setCurrentMed(e.target.value)}
                onKeyDown={handleAddMedication}
              />
              <button
                type="button"
                onClick={handleAddMedication}
                className="px-4 bg-[#18d4c6] text-white font-semibold rounded-[10px] hover:bg-[#15b0a8] transition-colors shrink-0"
              >
                추가
              </button>
            </div>
          </div>

            <div className="flex flex-wrap gap-2 mb-6">
              {medicine_names.map((med, index) => (
                <div key={index} className="inline-flex items-center gap-1 bg-[#e8fffd] text-[#18d4c6] px-2 py-1 rounded-full text-[12px] border border-[#18d4c6]">
                  <span>#{med}</span>
                  <span
                    className="cursor-pointer font-bold text-sm leading-none text-[#a0a0a0] hover:text-[#606060]"
                    onClick={() => handleRemoveMedication(index)}
                  >
                    ×
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Dietary Section */}
          <div className="mb-8">
            <div className="mb-6">
              <h2 className="text-[28px] font-bold text-[#353535] mb-2">식이 정보 (선택사항)</h2>
              <p className="text-base font-bold text-[#828282]">알러지나 식이 제한이 있으면 입력해주세요</p>
            </div>

            {/* Allergy Input */}
            <div className="space-y-2 mb-3">
              <label className="text-lg font-bold text-[#353535]">알러지 음식</label>
              <input
                name="currentAllergy"
                type="text"
                className="w-full h-12 px-5 rounded-[10px] border border-[#828282] text-sm placeholder:text-[#828282] focus:outline-none focus:border-[#18d4c6]"
                placeholder="알러지 음식을 입력하세요 (예: 땅콩, 갑각류, 우유...)"
                value={currentAllergy}
                onChange={(e) => setCurrentAllergy(e.target.value)}
                onKeyDown={handleAddAllergy}
              />
            </div>

            <div className="flex flex-wrap gap-2 mb-3">
              {allergyFoods.map((food, index) => (
                <div key={index} className="inline-flex items-center gap-2 bg-red-100 text-red-900 px-3 py-2 rounded-full text-[14px]">
                  <span>{food}</span>
                  <span
                    className="cursor-pointer font-bold text-lg leading-none"
                    onClick={() => handleRemoveAllergy(index)}
                  >
                    ×
                  </span>
                </div>
              ))}
            </div>

            {/* Restricted Food Input */}
            <div className="space-y-2 mt-4">
              <label className="text-lg font-bold text-[#353535]">식이 제한 음식</label>
              <input
                name="currentRestriction"
                type="text"
                className="w-full h-12 px-5 rounded-[10px] border border-[#828282] text-sm placeholder:text-[#828282] focus:outline-none focus:border-[#18d4c6]"
                placeholder="피해야 할 음식을 입력하세요 (예: 짠 음식, 고지방 음식)"
                value={currentRestriction}
                onChange={(e) => setCurrentRestriction(e.target.value)}
                onKeyDown={handleAddRestriction}
              />
            </div>

            <div className="flex flex-wrap gap-2 mb-6">
              {restrictionFoods.map((food, index) => (
                <div key={index} className="inline-flex items-center gap-2 bg-orange-100 text-orange-900 px-3 py-2 rounded-full text-[14px]">
                  <span>{food}</span>
                  <span
                    className="cursor-pointer font-bold text-lg leading-none"
                    onClick={() => handleRemoveRestriction(index)}
                  >
                    ×
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Button */}
          <div className="mt-8 pb-32">
            <button
              type="submit"
              disabled={loading || dataLoading}
              className="w-full h-14 bg-[#18d4c6] rounded-[10px] flex items-center justify-center gap-1 shadow-[1px_1px_2px_rgba(125,140,139,0.5)] hover:bg-[#15b0a8] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span className="text-lg font-bold text-white">{loading ? '저장 중...' : '다음'}</span>
              <ChevronRight className="w-6 h-6 text-white" />
            </button>
          </div>
        </form>
      </main>
    </div>
  )
}
