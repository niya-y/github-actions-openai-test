'use client'

import { useState, useRef } from 'react'
import { Camera, Upload, AlertCircle, CheckCircle } from 'lucide-react'
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
  const fileInputRef = useRef<HTMLInputElement>(null)
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

      if (response?.success) {
        setOcrResult(response)
        // 검증된 약들을 선택된 약으로 추가
        if (response.medicines && response.medicines.length > 0) {
          setSelectedMedicines(response.medicines)
          onMedicinesSelected?.(response.medicine_names)
        }
      } else {
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

  // 파일 선택 후 처리
  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      handleImageUpload(file)
    }
    // input 초기화
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
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
  }

  return (
    <div className="medication-ocr space-y-6">
      {/* 에러 메시지 */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 flex gap-3">
          <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-semibold text-red-900">오류가 발생했습니다</p>
            <p className="text-sm text-red-700">{error}</p>
          </div>
        </div>
      )}

      {/* 로딩 상태 */}
      {isLoading && (
        <div className="bg-blue-50 border border-blue-200 rounded-xl p-8 text-center">
          <div className="inline-flex items-center justify-center w-12 h-12 mb-4 bg-blue-100 rounded-full">
            <div className="w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
          </div>
          <p className="font-semibold text-blue-900 mb-2">약 정보를 확인하는 중...</p>
          <p className="text-sm text-blue-700">식약처 데이터베이스 검증 중입니다</p>
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

          {/* 파일 업로드 옵션 */}
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            disabled={isLoading}
            className="w-full p-4 bg-white border border-gray-200 rounded-xl hover:bg-gray-50 hover:border-gray-300 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleFileSelect}
              className="hidden"
            />
            <div className="flex items-center justify-center gap-2">
              <Upload className="w-5 h-5 text-gray-600" />
              <span className="font-semibold text-gray-700">
                ✏️ 약 사진 업로드
              </span>
            </div>
          </button>
        </div>
      )}

      {/* OCR 결과 표시 */}
      {ocrResult && !isLoading && (
        <div className="space-y-4">
          {/* 결과 헤더 */}
          <div className="bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 rounded-xl p-4 flex items-start justify-between">
            <div className="flex gap-3 items-start flex-1">
              <CheckCircle className="w-6 h-6 text-green-600 flex-shrink-0 mt-0.5" />
              <div className="min-w-0">
                <p className="font-bold text-green-900">
                  {ocrResult.message}
                </p>
                <p className="text-sm text-green-700">
                  신뢰도: {(ocrResult.confidence * 100).toFixed(0)}%
                </p>
              </div>
            </div>
          </div>

          {/* 검증된 약 목록 */}
          {selectedMedicines.length > 0 && (
            <div>
              <p className="text-sm font-semibold text-gray-700 mb-3">
                검증된 약 ({selectedMedicines.length}개)
              </p>
              <div className="space-y-3">
                {selectedMedicines.map((medicine, idx) => (
                  <MedicineCard
                    key={idx}
                    medicine={medicine}
                    onRemove={handleRemoveMedicine}
                  />
                ))}
              </div>
            </div>
          )}

          {/* 미검증 약 경고 */}
          {ocrResult.unverified_names && ocrResult.unverified_names.length > 0 && (
            <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-4">
              <p className="font-bold text-yellow-900 mb-2 flex items-center gap-2">
                <AlertCircle className="w-5 h-5" />
                ⚠️ 확인이 필요한 약
              </p>
              <p className="text-sm text-yellow-700 mb-3">
                다음 약은 식약처 데이터베이스에서 찾을 수 없습니다:
              </p>
              <ul className="space-y-1 ml-4">
                {ocrResult.unverified_names.map((name, idx) => (
                  <li key={idx} className="text-sm text-yellow-800">
                    • {name}
                  </li>
                ))}
              </ul>
              <p className="text-xs text-gray-500 mt-3">
                * 일반의약품이거나 OCR이 잘못 인식했을 수 있습니다.
              </p>
            </div>
          )}

          {/* 액션 버튼 */}
          <div className="flex gap-3">
            <button
              type="button"
              onClick={handleRetake}
              className="flex-1 px-4 py-3 bg-gray-200 text-gray-800 font-semibold rounded-xl hover:bg-gray-300 transition-colors"
            >
              다시 촬영
            </button>
            <button
              type="button"
              onClick={() => {
                // 확인 버튼 - 선택된 약들을 확정하고 결과 리셋
                console.log('[MedicationOCR] 약물 선택 완료:', selectedMedicines)
                onConfirmMedicines?.(selectedMedicines.map((m) => m.item_name))
                // OCR 결과 초기화 (다시 촬영 가능하게)
                handleRetake()
              }}
              className="flex-1 px-4 py-3 bg-green-600 text-white font-semibold rounded-xl hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
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
