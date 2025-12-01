"use client"

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { ChevronLeft } from 'lucide-react'
import { apiPost, apiGet } from '@/utils/api'
import ErrorAlert from '@/components/ErrorAlert'
import MedicationOCR from '@/components/MedicationOCR'
import type { MedicationsCreateRequest, MedicationResponse } from '@/types/api'

export default function PatientCondition3Page() {
  const router = useRouter()
  const [currentMed, setCurrentMed] = useState('')
  const [medicine_names, setMedicineNames] = useState<string[]>([])
  const [loading, setLoading] = useState(false)
  const [dataLoading, setDataLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)
  const [patientId, setPatientId] = useState<number | null>(null)

  const handleAddMedication = (e?: React.KeyboardEvent) => {
    if (e && e.key !== 'Enter') return
    if (currentMed.trim()) {
      setMedicineNames([...medicine_names, currentMed.trim()])
      setCurrentMed('')
    }
  }

  const handleRemoveMedication = (index: number) => {
    setMedicineNames(medicine_names.filter((_, i) => i !== index))
  }

  // 🔧 기존 약물 정보 불러오기
  useEffect(() => {
    const loadMedicationData = async () => {
      try {
        const patientIdFromStorage = sessionStorage.getItem('patient_id')
        if (!patientIdFromStorage) {
          setDataLoading(false)
          return
        }

        setPatientId(Number(patientIdFromStorage))

        const response = await apiGet<any>(`/api/patients/${patientIdFromStorage}/medications`)
        console.log('[PatientCondition3] Medications loaded:', response)

        if (response?.medicine_names && response.medicine_names.length > 0) {
          // 기존 약물 정보 로드
          setMedicineNames(response.medicine_names)
        }
      } catch (err) {
        // 404는 정상 (첫 번째 방문)
        console.log('[PatientCondition3] No existing medication data:', err)
      } finally {
        setDataLoading(false)
      }
    }

    loadMedicationData()
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

      // 🔧 모든 환자 정보 저장 완료
      console.log('[PatientCondition3] 환자 정보 저장 완료 (조건1+조건2+조건3)')
      console.log('[PatientCondition3] Patient ID:', patientId)

      // 다음 페이지로 이동 (모든 데이터가 저장됨)
      router.push('/caregiver-finder')
    } catch (err) {
      console.error('[PatientCondition3] 약물 정보 저장 실패:', err)
      setError(err as Error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex flex-col min-h-screen bg-[#f9f7f2] overflow-hidden font-['Pretendard']">
      <ErrorAlert error={error} onClose={() => setError(null)} />

      <div className="flex items-center px-5 py-4 border-b border-gray-100 shrink-0">
        <button
          onClick={() => router.push('/patient-condition-2')}
          className="text-[#18D4C6] bg-transparent border-none cursor-pointer"
        >
          <ChevronLeft className="w-6 h-6" />
        </button>
        <div className="flex-1 mx-5">
          <div className="w-full h-1 bg-transparent rounded-sm flex gap-1">
            <div className="flex-1 h-full bg-[#18D4C6] rounded-sm"></div>
            <div className="flex-1 h-full bg-[#18D4C6] rounded-sm"></div>
            <div className="flex-1 h-full bg-[#18D4C6] rounded-sm"></div>
            <div className="flex-1 h-full bg-[#18D4C6] rounded-sm"></div>
            <div className="flex-1 h-full bg-gray-200 rounded-sm"></div>
          </div>
        </div>
        <div className="w-8"></div> {/* Spacer to balance the header since Skip is removed */}
      </div>

      <div className="flex-1 overflow-y-auto px-5 py-8">
        <div className="mb-8">
          <h2 className="text-[26px] text-gray-800 mb-2">복용 중인 약이 있나요?</h2>
          <p className="text-[14px] text-gray-600">정확한 복약 관리를 위해 필요합니다</p>
        </div>

        <form onSubmit={handleSubmit}>
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
                    return [...prev, ...newMedicines]
                  })
                }}
                onConfirmMedicines={(medicines) => {
                  console.log('[PatientCondition3] 사용자가 약물 선택 확정:', medicines)
                  // 약물 목록에 표시됨 (onMedicinesSelected에서 이미 추가됨)
                }}
              />
            </div>
          )}

          {/* 기존 옵션들 (OCR 아래) */}
          <div className="bg-gray-50 rounded-2xl p-5 mb-6">
            <div className="text-[12px] font-semibold text-gray-600 mb-3">또는 다음 방법을 사용하세요</div>
            <div className="flex items-start gap-4 p-4 bg-white rounded-xl cursor-pointer hover:bg-gray-50 transition-all">
              <div className="text-4xl shrink-0">✏️</div>
              <div className="flex-1">
                <div className="text-[15px] font-semibold text-gray-800 mb-1">약 이름 직접 입력</div>
                <div className="text-[12px] text-gray-600">자동완성 지원</div>
              </div>
            </div>
          </div>

          <div className="mb-6">
            <div className="text-[14px] font-semibold text-gray-800 mb-3">약물 목록</div>
            <input
              name="currentMed"
              type="text"
              className="w-full px-4 py-4 border-2 border-dashed border-gray-200 rounded-xl text-[15px] text-black bg-white"
              placeholder="약 이름을 입력하세요 (예: 아스피린, 메트포민...)"
              value={currentMed}
              onChange={(e) => setCurrentMed(e.target.value)}
              onKeyDown={handleAddMedication}
            />
          </div>

          <div className="flex flex-wrap gap-2 mb-6">
            {medicine_names.map((med, index) => (
              <div key={index} className="inline-flex items-center gap-2 bg-purple-100 text-purple-900 px-3 py-2 rounded-full text-[14px]">
                <span>{med}</span>
                <span
                  className="cursor-pointer font-bold text-lg leading-none"
                  onClick={() => handleRemoveMedication(index)}
                >
                  ×
                </span>
              </div>
            ))}
          </div>

          <div className="mt-8 pb-3">
            <button
              type="submit"
              disabled={loading}
              className="w-full px-5 py-[18px] bg-[#18D4C6] text-white border-none rounded-xl text-[17px] font-semibold cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? '저장 중...' : '다음'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
