"use client"

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { ChevronLeft, ChevronDown } from 'lucide-react'
import { apiPost, apiGet } from '@/utils/api'
import ErrorAlert from '@/components/ErrorAlert'
import type { GuardianResponse } from '@/types/api'

export default function GuardiansPage() {
  const router = useRouter()
  const [formData, setFormData] = useState({
    name: '',
    phone: '',
    address: '',
    relationship: ''
  })
  const [loading, setLoading] = useState(false)
  const [dataLoading, setDataLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  // 🔧 FETCH EXISTING GUARDIAN DATA
  useEffect(() => {
    const fetchGuardianData = async () => {
      try {
        const token = localStorage.getItem('access_token')
        if (!token) {
          router.push('/login')
          return
        }

        // Try to fetch existing guardian info
        const guardianData = await apiGet<any>('/api/guardians/me')
        console.log('[Guardians] Existing data loaded:', guardianData)

        // Pre-fill form with existing data
        if (guardianData) {
          setFormData({
            name: guardianData.name || '',
            phone: guardianData.phone || '',
            address: guardianData.address || '',
            relationship: guardianData.relationship || ''
          })
        }
      } catch (err) {
        // 404 means no existing guardian data (first time)
        console.log('[Guardians] No existing guardian data:', err)
        // Don't show error, just keep form empty for new entry
      } finally {
        setDataLoading(false)
      }
    }

    fetchGuardianData()
  }, [router])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!formData.name || !formData.phone || !formData.address || !formData.relationship) {
      alert('모든 필수 항목을 입력해주세요.')
      return
    }

    setLoading(true)
    setError(null)

    try {
      const response = await apiPost<GuardianResponse>(
        '/api/guardians',
        formData
      )

      console.log('보호자 정보 등록 성공:', response)

      // guardian_id를 세션 스토리지에 저장
      sessionStorage.setItem('guardian_id', response.guardian_id.toString())

      router.push('/patient-condition-1')
    } catch (err) {
      console.error('보호자 정보 등록 실패:', err)
      setError(err as Error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-screen bg-[#f9f7f2] overflow-hidden font-['Pretendard']">
      <ErrorAlert error={error} onClose={() => setError(null)} />

      {/* Navigation Bar with Progress */}
      <div className="flex items-center px-5 py-4 border-b border-gray-100 flex-shrink-0">
        <button
          onClick={() => router.push('/')}
          className="text-xl text-[#18D4C6] bg-transparent border-none cursor-pointer"
        >
          <ChevronLeft className="w-6 h-6" />
        </button>
        <div className="flex-1 mx-5">
          <div className="w-full h-1 bg-transparent rounded-sm flex gap-1">
            <div className="flex-1 h-full bg-[#18D4C6] rounded-sm"></div>
            <div className="flex-1 h-full bg-gray-200 rounded-sm"></div>
            <div className="flex-1 h-full bg-gray-200 rounded-sm"></div>
            <div className="flex-1 h-full bg-gray-200 rounded-sm"></div>
            <div className="flex-1 h-full bg-gray-200 rounded-sm"></div>
          </div>
        </div>
        <div className="w-8"></div> {/* Spacer to balance the header since Skip is removed */}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto px-5 py-8">
        <div className="mb-10">
          <h2 className="text-[28px] text-black mb-2">케어 대상자의 버팀목</h2>
          <p className="text-[15px] text-black">보호자분의 기본 정보를 입력해주세요</p>
        </div>

        {/* Avatar Upload */}
        <div className="flex flex-col items-center mb-8">
          <div className="w-[100px] h-[100px] rounded-full bg-[#f9f7f2] flex items-center justify-center text-5xl mb-4 cursor-pointer border-[3px] border-dashed border-[#18D4C6]">
            👤
          </div>
          <div className="text-[13px] text-black cursor-pointer">프로필 사진 추가 (선택)</div>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-5">
          {/* Name */}
          <div>
            <label className="block text-sm font-semibold text-black mb-2">
              이름 <span className="text-[#F2643B]">*</span>
            </label>
            <input
              name="name"
              type="text"
              className="w-full px-4 py-4 border border-gray-200 rounded-xl text-base text-black bg-white"
              placeholder="예: 김영희"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              required
            />
          </div>

          {/* Phone */}
          <div>
            <label className="block text-sm font-semibold text-black mb-2">
              연락처 <span className="text-[#F2643B]">*</span>
            </label>
            <input
              name="phone"
              type="tel"
              className="w-full px-4 py-4 border border-gray-200 rounded-xl text-base text-black bg-white"
              placeholder="예: 010-1234-5678"
              value={formData.phone}
              onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
              required
            />
          </div>

          {/* Relationship */}
          <div>
            <label className="block text-sm font-semibold text-black mb-2">
              환자와의 관계 <span className="text-[#F2643B]">*</span>
            </label>
            <div className="relative">
              <select
                name="relationship"
                className="w-full px-4 py-4 border border-gray-200 rounded-xl text-base text-black bg-white appearance-none pr-10"
                value={formData.relationship}
                onChange={(e) => setFormData({ ...formData, relationship: e.target.value })}
                required
              >
                <option value="">선택해주세요</option>
                <option value="배우자">배우자</option>
                <option value="자녀">자녀</option>
                <option value="부모">부모</option>
                <option value="형제자매">형제자매</option>
                <option value="손자/손녀">손자/손녀</option>
                <option value="기타">기타</option>
              </select>
              <div className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-gray-400">
                <ChevronDown className="w-5 h-5" />
              </div>
            </div>
          </div>

          {/* Address */}
          <div>
            <label className="block text-sm font-semibold text-black mb-2">
              주소 <span className="text-[#F2643B]">*</span>
            </label>
            <input
              name="address"
              type="text"
              className="w-full px-4 py-4 border border-gray-200 rounded-xl text-base text-black bg-white"
              placeholder="예: 서울특별시 서초구 반포대로 222"
              value={formData.address}
              onChange={(e) => setFormData({ ...formData, address: e.target.value })}
              required
            />
          </div>

          {/* Next Button */}
          <div className="mt-8 pb-3">
            <button
              type="submit"
              disabled={loading || dataLoading}
              className="w-full px-5 py-[18px] bg-[#18D4C6] text-white border-none rounded-xl text-[17px] font-semibold cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {dataLoading ? '정보 불러오는 중...' : loading ? '저장 중...' : '다음'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
