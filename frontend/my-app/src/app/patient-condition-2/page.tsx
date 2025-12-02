"use client"

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Image from 'next/image'
import { ChevronLeft, ChevronRight, X } from 'lucide-react'
import { apiPut, apiGet } from '@/utils/api'
import ErrorAlert from '@/components/ErrorAlert'
import { cn } from '@/utils/cn'
import type { HealthStatusUpdateRequest, HealthConditionResponse, DiseaseItem } from '@/types/api'

const diseasesOptions = [
  { id: 'cancer', name: '암', icon: '/assets/ic_cancer.svg', activeIcon: '/assets/ic_cancer_fill.svg' },
  { id: 'diabetes', name: '당뇨병', icon: '/assets/ic_diabetes.svg', activeIcon: '/assets/ic_diabetes_fill.svg' },
  { id: 'hypertension', name: '고혈압', icon: '/assets/ic_hypertension.svg', activeIcon: '/assets/ic_hypertension_fill.svg' },
  { id: 'parkinsons', name: '파킨슨병', icon: '/assets/ic_parkinsons.svg', activeIcon: '/assets/ic_parkinsons_fill.svg' },
  { id: 'dementia', name: '치매/인지장애', icon: '/assets/ic_dementia.svg', activeIcon: '/assets/ic_dementia_fill.svg' },
  { id: 'stroke', name: '뇌졸중/중풍', icon: '/assets/ic_stroke.svg', activeIcon: '/assets/ic_stroke_fill.svg' }
]

const mobilityOptions = [
  { id: 'independent', icon: '🚶', label: '혼자 걸을 수 있음', desc: '보조 없이 독립 보행 가능' },
  { id: 'assistive-device', icon: '🦯', label: '보조 기구 필요', desc: '지팡이, 워커 등 사용' },
  { id: 'wheelchair', icon: '♿', label: '휠체어 사용', desc: '휠체어로 이동' },
  { id: 'bedridden', icon: '🛏️', label: '침상 생활', desc: '거동 불가, 침대에서만 생활' }
]

export default function PatientCondition2Page() {
  const router = useRouter()
  const [selectedDiseases, setSelectedDiseases] = useState<DiseaseItem[]>([])
  const [selectedMobility, setSelectedMobility] = useState<string>('')
  const [otherDisease, setOtherDisease] = useState('')
  const [loading, setLoading] = useState(false)
  const [dataLoading, setDataLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  const toggleDisease = (disease: any) => {
    setSelectedDiseases((prev) =>
      prev.some(d => d.id === disease.id)
        ? prev.filter((d) => d.id !== disease.id)
        : [...prev, { id: disease.id, name: disease.name }]
    )
  }

  const isDiseaseSelected = (id: string) => {
    return selectedDiseases.some(d => d.id === id)
  }

  // 🔧 기존 건강 상태 데이터 불러오기
  useEffect(() => {
    const loadHealthData = async () => {
      try {
        const patientId = sessionStorage.getItem('patient_id')
        if (!patientId) {
          setDataLoading(false)
          return
        }

        const response = await apiGet<any>(`/api/patients/${patientId}/health-status`)
        console.log('[PatientCondition2] Health status loaded:', response)

        if (response?.selected_diseases && response.selected_diseases.length > 0) {
          // 기존 질병 데이터 선택
          const diseases = response.selected_diseases.map((d: any) => ({
            id: d.id || d.name.toLowerCase().replace(" ", "-"),
            name: d.name
          }))
          setSelectedDiseases(diseases)
        }

        if (response?.mobility_status) {
          // 기존 거동 상태 데이터 선택
          setSelectedMobility(response.mobility_status)
        }
      } catch (err) {
        // 404는 정상 (첫 번째 방문)
        console.log('[PatientCondition2] No existing health data:', err)
      } finally {
        setDataLoading(false)
      }
    }

    loadHealthData()
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    const patientId = sessionStorage.getItem('patient_id')
    if (!patientId) {
      alert('환자 정보를 먼저 등록해주세요.')
      router.push('/patient-condition-1')
      return
    }

    if (selectedDiseases.length === 0 || !selectedMobility) {
      alert('질병 정보와 거동 상태를 모두 선택해주세요.')
      return
    }

    setLoading(true)
    setError(null)

    try {
      const payload: HealthStatusUpdateRequest = {
        selectedDiseases: selectedDiseases,
        mobility_status: selectedMobility
      }

      // 🔧 건강 상태 저장
      await apiPut<HealthConditionResponse>(`/api/patients/${patientId}/health-status`, payload)

      console.log('[PatientCondition2] 건강 상태 저장 성공')
      console.log('[PatientCondition2] 질병:', selectedDiseases)
      console.log('[PatientCondition2] 거동 상태:', selectedMobility)
      console.log('[PatientCondition2] Patient ID:', patientId)

      // condition-3으로 이동 (약물 정보 입력 페이지)
      router.push('/patient-condition-3')
    } catch (err) {
      console.error('[PatientCondition2] 건강 상태 저장 실패:', err)
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
            onClick={() => router.push('/patient-condition-1')}
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
            <div className="h-1 flex-1 bg-gray-200 rounded-full" />
            <div className="h-1 flex-1 bg-gray-200 rounded-full" />
          </div>
        </div>

        <div className="h-px bg-gray-100 -mx-4" />
      </header>

      <main className="flex-1 px-8 pt-6 pb-8 overflow-y-auto">
        {/* Title */}
        <div className="mb-8">
          <h1 className="text-[28px] font-bold text-[#353535] mb-2">건강 상태를 알려주세요</h1>
          <p className="text-base font-bold text-[#828282]">더 정확한 간병 계획을 위해 필요합니다.</p>
        </div>

        {/* Disease Selection Banner */}
        <div className="bg-[#18d4c6] rounded-[10px] py-3 px-4 mb-4 flex items-center justify-between">
          <span className="text-[17px] font-bold text-white">주요 질병을 선택해주세요.</span>
          <span className="text-xs font-bold text-[#f9f7f2]">중복 선택 가능</span>
        </div>

        <form onSubmit={handleSubmit}>
          {/* Disease Grid */}
          <div className="grid grid-cols-2 gap-2 mb-2">
            {diseasesOptions.map((disease) => {
              const isSelected = isDiseaseSelected(disease.id)
              const isStroke = disease.id === 'stroke'

              return (
                <button
                  key={disease.id}
                  type="button"
                  onClick={() => toggleDisease(disease)}
                  className={cn(
                    "flex flex-col items-center justify-center py-6 gap-3 rounded-[10px] border transition-all shadow-sm h-[120px]",
                    isSelected
                      ? "bg-[#e8fffd] border-[#18d4c6]"
                      : "bg-white border-[#828282]"
                  )}
                >
                  <div className="w-12 h-12 relative flex items-center justify-center">
                    <Image
                      src={isSelected ? disease.activeIcon : disease.icon}
                      alt={disease.name}
                      width={isStroke ? 36 : 40}
                      height={isStroke ? 36 : 40}
                      className={cn(
                        "object-contain",
                        isStroke ? "w-9 h-9" : "w-10 h-10"
                      )}
                    />
                  </div>
                  <span className={cn(
                    "text-sm font-bold",
                    isSelected ? "text-[#353535]" : "text-[#828282]"
                  )}>
                    {disease.name}
                  </span>
                </button>
              )
            })}
          </div>

          {/* Other Button / Input */}
          {isDiseaseSelected('other') ? (
            <div className="w-full mb-9 relative">
              <input
                type="text"
                value={otherDisease}
                onChange={(e) => setOtherDisease(e.target.value)}
                placeholder="질병명을 입력해주세요"
                className="w-full h-[54px] px-5 rounded-[10px] border border-[#18d4c6] text-sm font-bold text-[#353535] focus:outline-none bg-[#e8fffd]"
                autoFocus
              />
              <button
                type="button"
                onClick={() => {
                  const otherOption = diseasesOptions.find(d => d.id === 'other');
                  if (otherOption) toggleDisease(otherOption);
                }}
                className="absolute right-4 top-1/2 -translate-y-1/2 text-[#828282]"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          ) : (
            <button
              type="button"
              onClick={() => {
                const otherOption = diseasesOptions.find(d => d.id === 'other');
                if (otherOption) toggleDisease(otherOption);
              }}
              className="w-full bg-white border border-[#828282] rounded-[10px] py-4 mb-9 shadow-sm hover:bg-gray-50"
            >
              <span className="text-sm font-bold text-[#828282]">기타 (직접 입력)</span>
            </button>
          )}

          {/* Movement Question */}
          <div className="space-y-2 mb-8">
            <h2 className="text-lg font-bold text-[#353535]">스스로 움직이실 수 있나요?</h2>
            <div className="space-y-3">
              {mobilityOptions.map(option => (
                <div
                  key={option.id}
                  className={`p-4 border-2 rounded-xl cursor-pointer transition-all flex items-start gap-3 ${selectedMobility === option.id
                    ? 'border-[#18d4c6] bg-[#e8fffd]'
                    : 'border-[#828282]'
                    }`}
                  onClick={() => setSelectedMobility(option.id)}
                >
                  <div className="text-2xl shrink-0 mt-1">{option.icon}</div>
                  <div className="flex-1">
                    <div className={`text-[15px] font-semibold mb-1 ${selectedMobility === option.id ? 'text-[#353535]' : 'text-[#828282]'}`}>{option.label}</div>
                    <div className="text-[12px] text-[#828282]">{option.desc}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="mt-8">
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
