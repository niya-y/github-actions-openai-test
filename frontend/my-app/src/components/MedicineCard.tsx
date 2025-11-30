'use client'

import { useState } from 'react'
import { ChevronDown, ChevronUp } from 'lucide-react'
import type { MedicineDetail } from '@/types/api'

interface MedicineCardProps {
  medicine: MedicineDetail
  onRemove?: (itemName: string) => void
}

export default function MedicineCard({ medicine, onRemove }: MedicineCardProps) {
  const [isExpanded, setIsExpanded] = useState(false)

  return (
    <div className="medicine-card bg-white rounded-xl border border-gray-100 overflow-hidden shadow-sm mb-4">
      {/* 헤더 - 기본 정보 */}
      <div className="medicine-header p-5 border-b border-gray-100">
        <div className="flex gap-4 items-start">
          {/* 약품 이미지 */}
          {medicine.item_image && (
            <div className="flex-shrink-0">
              <img
                src={medicine.item_image}
                alt={medicine.item_name}
                className="w-20 h-20 object-contain bg-gray-50 rounded-lg p-2"
                onError={(e) => {
                  (e.target as HTMLImageElement).style.display = 'none'
                }}
              />
            </div>
          )}

          {/* 기본 정보 */}
          <div className="flex-1 min-w-0">
            <div className="flex items-start gap-2 mb-2">
              <h4 className="text-base font-bold text-black break-words">
                ✓ {medicine.item_name}
              </h4>
              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-semibold bg-gradient-to-r from-green-500 to-emerald-600 text-white flex-shrink-0 whitespace-nowrap">
                식약처 검증
              </span>
            </div>
            <p className="text-sm text-gray-600 mb-3">{medicine.entp_name}</p>

            {/* 간단한 정보 */}
            <div className="space-y-2 text-sm">
              <div className="flex gap-2 items-start">
                <span className="text-base">📋</span>
                <div className="flex-1 min-w-0">
                  <p className="font-semibold text-gray-700 text-xs mb-1">효능</p>
                  <p className="text-gray-600 line-clamp-2 text-xs">
                    {medicine.efficacy.substring(0, 80)}...
                  </p>
                </div>
              </div>
              <div className="flex gap-2 items-start">
                <span className="text-base">💊</span>
                <div className="flex-1 min-w-0">
                  <p className="font-semibold text-gray-700 text-xs mb-1">용법</p>
                  <p className="text-gray-600 line-clamp-2 text-xs">
                    {medicine.usage.substring(0, 80)}...
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* 제거 버튼 */}
          {onRemove && (
            <button
              onClick={() => onRemove(medicine.item_name)}
              className="flex-shrink-0 text-xl font-bold leading-none text-gray-400 hover:text-red-500 transition-colors"
            >
              ×
            </button>
          )}
        </div>
      </div>

      {/* 상세보기 버튼 */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full px-5 py-3 flex items-center justify-between gap-2 hover:bg-gray-50 transition-colors"
      >
        <span className="text-sm font-semibold text-gray-700">
          {isExpanded ? '접기 ▲' : '상세보기 ▼'}
        </span>
      </button>

      {/* 상세 정보 (확장 시) */}
      {isExpanded && (
        <div className="border-t border-gray-100 px-5 py-4 space-y-4 bg-gray-50">
          {/* 효능 */}
          <DetailSection
            icon="📋"
            title="효능"
            content={medicine.efficacy}
          />

          {/* 사용법 */}
          <DetailSection
            icon="💊"
            title="사용법"
            content={medicine.usage}
          />

          {/* 주의사항 (경고) */}
          <DetailSection
            icon="⚠️"
            title="주의사항"
            content={medicine.precaution}
            isWarning
          />

          {/* 부작용 */}
          <DetailSection
            icon="😵"
            title="부작용"
            content={medicine.side_effect}
          />

          {/* 상호작용 */}
          <DetailSection
            icon="🔄"
            title="상호작용"
            content={medicine.interaction}
          />

          {/* 보관법 */}
          <DetailSection
            icon="📦"
            title="보관법"
            content={medicine.storage}
          />
        </div>
      )}
    </div>
  )
}

interface DetailSectionProps {
  icon: string
  title: string
  content: string
  isWarning?: boolean
}

function DetailSection({ icon, title, content, isWarning = false }: DetailSectionProps) {
  return (
    <div
      className={`rounded-lg p-4 ${
        isWarning
          ? 'bg-yellow-50 border border-yellow-200'
          : 'bg-white border border-gray-200'
      }`}
    >
      <h5
        className={`text-sm font-semibold mb-2 flex items-center gap-2 ${
          isWarning ? 'text-yellow-900' : 'text-gray-900'
        }`}
      >
        <span className="text-lg">{icon}</span>
        {title}
      </h5>
      <p
        className={`text-sm leading-relaxed whitespace-pre-line ${
          isWarning ? 'text-yellow-800' : 'text-gray-700'
        }`}
      >
        {content || '정보 없음'}
      </p>
    </div>
  )
}
