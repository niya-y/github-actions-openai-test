'use client'

import { useState, useRef } from 'react'
import { Camera, AlertCircle, CheckCircle } from 'lucide-react'
import MedicineCard from './MedicineCard'
import { apiPost } from '@/utils/api'
import type { OCRResultResponse, MedicineDetail } from '@/types/api'

interface MedicationOCRProps {
  patientId: number
  onMedicinesSelected?: (medicines: string[]) => void
  onConfirmMedicines?: (medicines: string[]) => void
}

export default function MedicationOCR({
  patientId,
  onMedicinesSelected,
  onConfirmMedicines,
}: MedicationOCRProps) {
  const cameraInputRef = useRef<HTMLInputElement>(null)

  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [ocrResult, setOcrResult] = useState<OCRResultResponse | null>(null)
  const [selectedMedicines, setSelectedMedicines] = useState<MedicineDetail[]>([])

  // 이미지 업로드 처리
  const handleImageUpload = async (file: File) => {
    if (!file.type.startsWith('image/')) {
      setError('이미지 파일만 업로드 가능합니다.')
      return
    }

    setIsLoading(true)
    setError(null)

    try {
      const formData = new FormData()
      formData.append('file', file)

      console.log('[MedicationOCR] OCR 처리 시작:', {
        patientId,
        fileName: file.name,
        fileSize: file.size,
      })

      const response = await apiPost<OCRResultResponse>(
        `/api/patients/${patientId}/medications/ocr`,
        formData
      )

      console.log('[MedicationOCR] OCR 결과:', response)
      console.log('[MedicationOCR] response?.success:', response?.success)
      console.log('[MedicationOCR] response?.medicines:', response?.medicines)

      if (response?.success) {
        console.log('[MedicationOCR] ✅ OCR 성공!')
        setOcrResult(response)

        // 검증된 약 또는 미검증 약이 있는지 확인
        const verifiedMedicines = response.medicines || []
        const medicineNames = response.medicine_names || []

        console.log('[MedicationOCR] 검증된 약:', verifiedMedicines.length, '미검증 약:', medicineNames.length)

        if (medicineNames.length > 0) {
          // medicine_names에는 verified + unverified가 포함됨
          console.log('[MedicationOCR] 약물 목록:', medicineNames)

          // UI에 표시할 약물: 검증된 약이 있으면 그걸 쓰고, 없으면 OCR 추출 약을 씀
          if (verifiedMedicines.length > 0) {
            setSelectedMedicines(verifiedMedicines)
          } else {
            // MFDS API 검증 실패 시 OCR 추출 약을 MedicineDetail 형태로 변환
            const ocrExtractedMedicines = medicineNames.map(name => ({
              item_name: name,
              entp_name: '(검증 대기중)',
              item_seq: '',
              efficacy: '정보 없음',
              usage: '정보 없음',
              precaution: '정보 없음',
              side_effect: '정보 없음',
              storage: '정보 없음',
              interaction: '정보 없음',
              item_image: ''
            }))
            setSelectedMedicines(ocrExtractedMedicines)
          }

          onMedicinesSelected?.(medicineNames)
        } else {
          console.warn('[MedicationOCR] 인식된 약물이 없음')
          setError('인식된 약물이 없습니다. 다시 시도해주세요.')
        }
      } else {
        console.error('[MedicationOCR] ❌ OCR 실패:', response)
        setError(
          response?.message || '약봉지 인식에 실패했습니다. 다시 시도해주세요.'
        )
      }
    } catch (err) {
      console.error('[MedicationOCR] OCR 오류:', err)
      setError(
        err instanceof Error ? err.message : '약봉지 인식 중 오류가 발생했습니다.'
      )
    } finally {
      setIsLoading(false)
    }
  }

  // 카메라 촬영 후 처리
  const handleCameraCapture = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      handleImageUpload(file)
    }
    // input 초기화
    if (cameraInputRef.current) {
      cameraInputRef.current.value = ''
    }
  }

  // 약 제거
  const handleRemoveMedicine = (itemName: string) => {
    const updated = selectedMedicines.filter((m) => m.item_name !== itemName)
    setSelectedMedicines(updated)
    onMedicinesSelected?.(updated.map((m) => m.item_name))
  }

  // 다시 촬영
  const handleRetake = () => {
    setOcrResult(null)
    setSelectedMedicines([])
    setError(null)
    // 약물들은 부모 컴포넌트(patient-condition-3)의 medicine_names 상태에 저장되므로
    // 여기서는 초기화해도 됨
  }

  return (
    <div className="medication-ocr space-y-3">
      {/* 에러 메시지 */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-3 flex gap-2">
          <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-semibold text-red-900 text-sm">{error}</p>
          </div>
        </div>
      )}

      {/* 로딩 상태 */}
      {isLoading && (
        <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 text-center">
          <div className="inline-flex items-center justify-center w-8 h-8 mb-2 bg-blue-100 rounded-full">
            <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
          </div>
          <p className="font-semibold text-blue-900 text-sm">인식 중...</p>
        </div>
      )}

      {/* OCR 결과가 없을 때 - 촬영 옵션 표시 */}
      {!ocrResult && !isLoading && (
        <div className="space-y-4">
          {/* 카메라 촬영 옵션 */}
          <button
            type="button"
            onClick={() => cameraInputRef.current?.click()}
            disabled={isLoading}
            className="w-full p-6 bg-gradient-to-br from-blue-50 to-blue-100 border-2 border-blue-200 rounded-2xl hover:border-blue-300 hover:from-blue-100 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <input
              ref={cameraInputRef}
              type="file"
              accept="image/*"
              capture="environment"
              onChange={handleCameraCapture}
              className="hidden"
            />
            <div className="flex items-center justify-center gap-3 mb-2">
              <Camera className="w-6 h-6 text-blue-600" />
              <span className="text-lg font-bold text-blue-900">
                📸 처방전 사진 촬영
              </span>
            </div>
            <p className="text-sm text-blue-700">
              AI가 자동으로 약물 정보 인식
            </p>
            <div className="inline-block mt-2 px-3 py-1 bg-blue-600 text-white text-xs font-semibold rounded-full">
              추천
            </div>
          </button>
        </div>
      )}

      {/* OCR 결과 표시 - 약물 상세 정보 (팝업 없음, 내부에 표시) */}
      {ocrResult && !isLoading && (
        <div className="bg-white border border-gray-200 rounded-2xl p-4 space-y-3">
          {/* 헤더 */}
          <div className="flex items-center justify-between pb-3 border-b border-gray-200">
            <div>
              <h3 className="text-base font-bold text-gray-800">검색된 약물</h3>
              <p className="text-xs text-gray-600">{selectedMedicines.length}개 약품</p>
            </div>
            <button
              onClick={handleRetake}
              className="text-gray-400 hover:text-gray-600 text-2xl"
            >
              ×
            </button>
          </div>

          {/* 약물 목록 - 스크롤 가능 */}
          <div className="space-y-2 max-h-[300px] overflow-y-auto">
            {selectedMedicines.map((medicine, idx) => (
              <div key={idx} className="flex items-center justify-between gap-2 bg-gray-50 border border-gray-200 rounded-lg p-3">
                <h4 className="font-semibold text-gray-800 text-sm flex-1 truncate">{medicine.item_name}</h4>
                <button
                  onClick={() => handleRemoveMedicine(medicine.item_name)}
                  className="text-red-500 hover:text-red-700 font-bold text-lg shrink-0"
                >
                  ×
                </button>
              </div>
            ))}
          </div>

          {/* 하단 버튼 */}
          <div className="flex gap-2 pt-2 border-t border-gray-200">
            <button
              type="button"
              onClick={handleRetake}
              className="flex-1 px-3 py-2 bg-gray-200 text-gray-800 text-sm font-semibold rounded-lg hover:bg-gray-300 transition-colors"
            >
              다시 촬영
            </button>
            <button
              type="button"
              onClick={() => {
                const medicineNames = selectedMedicines.map((m) => m.item_name)
                console.log('[MedicationOCR] 약물 선택 확정:', medicineNames)
                onMedicinesSelected?.(medicineNames)
                onConfirmMedicines?.(medicineNames)
                setOcrResult(null)
                setSelectedMedicines([])
              }}
              className="flex-1 px-3 py-2 bg-green-600 text-white text-sm font-semibold rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              disabled={selectedMedicines.length === 0}
            >
              확인
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
