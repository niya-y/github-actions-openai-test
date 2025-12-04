"use client"

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { ChevronLeft, ChevronDown, Edit2, Plus, Calendar } from 'lucide-react'
import { apiPost, apiGet } from '@/utils/api'
import ErrorAlert from '@/components/ErrorAlert'
import { cn } from '@/utils/cn'
import type { PatientResponse } from '@/types/api'

interface PatientInfo {
  patient_id: number
  name: string
  age: number
  birth_date: string
  gender: string
}

export default function PatientCondition1Page() {
  const router = useRouter()

  // 데이터 로딩 상태
  const [dataLoading, setDataLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<Error | null>(null)

  // 현재 환자 상태
  const [currentPatient, setCurrentPatient] = useState<PatientInfo | null>(null)
  const [patients, setPatients] = useState<PatientInfo[]>([]) // 모든 환자 목록

  // UI 모드 상태
  const [mode, setMode] = useState<'view' | 'edit' | 'addNew'>('view') // view: 보기, edit: 수정, addNew: 새 환자 추가

  // 폼 데이터
  const [formData, setFormData] = useState({
    name: '',
    birthDate: '',
    gender: 'Female',
    relationship: '',
    isDirectInput: false
  })

  // 🔧 초기 로드: 최근 환자 정보 조회
  useEffect(() => {
    const loadPatientData = async () => {
      try {
        const token = localStorage.getItem('access_token')
        if (!token) {
          router.push('/login')
          return
        }

        // 현재 보호자의 모든 환자 조회
        const response = await apiGet<any>('/api/patients/me')
        console.log('[PatientCondition1] Patients loaded:', response)

        if (response?.latest_patient) {
          // 모든 환자 목록 저장
          const patientsList = (response.patients || []).map((p: any) => ({
            patient_id: p.patient_id,
            name: p.name,
            age: p.age,
            birth_date: p.birth_date,
            gender: p.gender
          }))
          setPatients(patientsList)

          // 🔧 sessionStorage에서 선택된 환자 ID 확인
          const selectedPatientId = sessionStorage.getItem('patient_id')
          let patientToDisplay: PatientInfo | null = null

          if (selectedPatientId) {
            // selectedPatientId가 있으면 그 환자 선택
            patientToDisplay = patientsList.find((p: any) => p.patient_id === parseInt(selectedPatientId)) || null
            console.log('[PatientCondition1] Selected patient from sessionStorage:', patientToDisplay)
          }

          // selectedPatientId가 없거나 해당 환자를 찾지 못하면 latest_patient 사용
          if (!patientToDisplay) {
            patientToDisplay = {
              patient_id: response.latest_patient.patient_id,
              name: response.latest_patient.name,
              age: response.latest_patient.age,
              birth_date: response.latest_patient.birth_date,
              gender: response.latest_patient.gender
            }
            console.log('[PatientCondition1] Using latest patient as default:', patientToDisplay)
          }

          setCurrentPatient(patientToDisplay)
          setMode('view') // 기존 환자가 있으면 보기 모드로 시작
        } else {
          setMode('addNew') // 환자가 없으면 새 환자 추가 모드로 시작
        }
      } catch (err) {
        console.error('[PatientCondition1] Error loading patients:', err)
        // 환자가 없는 경우 (404) → 새로운 환자 추가 모드
        setMode('addNew')
      } finally {
        setDataLoading(false)
      }
    }

    loadPatientData()
  }, [router])

  // 수정 모드 시작
  const handleEdit = () => {
    if (currentPatient) {
      // 현재 환자 정보로 폼 채우기
      const birthYear = parseInt(currentPatient.birth_date.split('-')[0])
      const birthMonth = parseInt(currentPatient.birth_date.split('-')[1])
      const birthDay = parseInt(currentPatient.birth_date.split('-')[2])

      setFormData({
        name: currentPatient.name,
        birthDate: `${birthYear}-${String(birthMonth).padStart(2, '0')}-${String(birthDay).padStart(2, '0')}`,
        gender: currentPatient.gender,
        relationship: '',
        isDirectInput: false
      })
      setMode('edit')
    }
  }

  // 새 환자 추가 모드 시작
  const handleAddNew = () => {
    setFormData({
      name: '',
      birthDate: '',
      gender: 'Female',
      relationship: '',
      isDirectInput: false
    })
    setMode('addNew')
  }

  // 환자 선택 (드롭다운)
  const handleSelectPatient = (patientId: number) => {
    const selected = patients.find(p => p.patient_id === patientId)
    if (selected) {
      setCurrentPatient(selected)
      console.log('[PatientCondition1] Selected patient:', selected)
    }
  }

  // 취소
  const handleCancel = () => {
    if (currentPatient) {
      setMode('view')
    } else {
      setMode('addNew')
    }
    setFormData({
      name: '',
      birthDate: '',
      gender: 'Female',
      relationship: '',
      isDirectInput: false
    })
  }

  // 저장 (생성 또는 수정)
  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!formData.name || !formData.birthDate || !formData.relationship) {
      alert('모든 필수 항목을 입력해주세요.')
      return
    }

    setSubmitting(true)
    setError(null)

    try {
      // 나이 계산
      const birthYear = parseInt(formData.birthDate.split('-')[0])
      const currentYear = new Date().getFullYear()
      const age = currentYear - birthYear

      const response = await apiPost<PatientResponse>(
        '/api/patients',
        {
          name: formData.name,
          age: age,
          gender: formData.gender.toLowerCase(),
          relationship: formData.relationship
        }
      )

      console.log('[PatientCondition1] 환자 정보 저장 성공:', response)
      console.log('[PatientCondition1] Patient ID:', response.patient_id)

      const newPatient = {
        patient_id: response.patient_id,
        name: response.name,
        age: age,
        birth_date: formData.birthDate,
        gender: formData.gender
      }

      // 저장된 환자 정보를 현재 환자로 설정
      setCurrentPatient(newPatient)

      // 환자 목록에 추가 (새 환자인 경우)
      if (mode === 'addNew') {
        setPatients(prev => [newPatient, ...prev])
        console.log('[PatientCondition1] 새 환자 추가됨')
      } else {
        // 수정인 경우 목록 업데이트
        setPatients(prev => prev.map(p => p.patient_id === newPatient.patient_id ? newPatient : p))
        console.log('[PatientCondition1] 환자 정보 수정됨')
      }

      // sessionStorage에 patient_id 저장
      sessionStorage.setItem('patient_id', response.patient_id.toString())
      console.log('[PatientCondition1] sessionStorage에 patient_id 저장됨:', response.patient_id)

      // 저장 후 보기 모드로 변경
      setMode('view')
    } catch (err) {
      console.error('[PatientCondition1] Error saving patient:', err)
      setError(err as Error)
    } finally {
      setSubmitting(false)
    }
  }

  // 다음 단계로 이동 (건강 상태 입력 페이지)
  const handleNext = () => {
    if (currentPatient) {
      sessionStorage.setItem('patient_id', currentPatient.patient_id.toString())
      console.log('[PatientCondition1] 환자 선택됨, condition-2로 이동')
      console.log('[PatientCondition1] Selected Patient:', {
        patient_id: currentPatient.patient_id,
        name: currentPatient.name,
        age: currentPatient.age
      })
      router.push('/patient-condition-2')
    } else {
      alert('환자 정보를 먼저 저장해주세요.')
    }
  }

  const toggleDirectInput = () => {
    setFormData(prev => ({ ...prev, isDirectInput: !prev.isDirectInput, relationship: '' }))
  }

  return (
    <div className="min-h-screen bg-white flex flex-col">
      <ErrorAlert error={error} onClose={() => setError(null)} />

      {/* Header */}
      <header className="sticky top-0 z-10 bg-white px-4 pt-4 pb-2">
        <div className="flex items-center mb-4">
          <button
            onClick={() => router.push('/home')}
            className="p-2 -ml-2 text-gray-600"
            aria-label="Go back"
          >
            <ChevronLeft className="w-6 h-6" />
          </button>

          {/* Progress Bar */}
          <div className="flex-1 flex gap-2 ml-4 mr-2">
            <div className="h-1 flex-1 bg-[#18d4c6] rounded-full" />
            <div className="h-1 flex-1 bg-[#18d4c6] rounded-full" />
            <div className="h-1 flex-1 bg-gray-200 rounded-full" />
            <div className="h-1 flex-1 bg-gray-200 rounded-full" />
            <div className="h-1 flex-1 bg-gray-200 rounded-full" />
          </div>
        </div>

        <div className="h-px bg-gray-100 -mx-4" />
      </header>

      <main className="flex-1 px-8 pt-6 pb-8 overflow-y-auto">
        {dataLoading ? (
          // 로딩 상태
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-[#18D4C6] border-t-transparent mb-4"></div>
              <p className="text-gray-600">환자 정보를 불러오는 중...</p>
            </div>
          </div>
        ) : mode === 'view' && currentPatient ? (
          // 보기 모드 (기존 환자 표시)
          <div>
            <div className="mb-10">
              <h2 className="text-[28px] font-bold text-[#353535] mb-2">도움이 필요해요</h2>
              <p className="text-base font-bold text-[#908d8d]">케어 대상자의 기본 정보</p>
            </div>

            {/* 환자 선택 드롭다운 (여러 환자가 있을 때만 표시) */}
            {patients.length > 1 && (
              <div className="mb-6">
                <label className="block text-sm font-semibold text-black mb-2">
                  케어 대상자 선택
                </label>
                <div className="relative">
                  <select
                    value={currentPatient?.patient_id || ''}
                    onChange={(e) => handleSelectPatient(Number(e.target.value))}
                    className="w-full px-4 py-4 border border-gray-200 rounded-xl text-base text-black bg-white appearance-none pr-10"
                  >
                    {patients.map((patient) => (
                      <option key={patient.patient_id} value={patient.patient_id}>
                        {patient.name} ({patient.age}세)
                      </option>
                    ))}
                  </select>
                  <div className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-gray-400">
                    <ChevronDown className="w-5 h-5" />
                  </div>
                </div>
              </div>
            )}

            {/* 환자 정보 표시 (읽기 전용) */}
            <div className="space-y-5 mb-8">
              <div className="p-5 bg-white rounded-xl border border-gray-100">
                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div>
                    <p className="text-xs text-gray-500 mb-1">이름</p>
                    <p className="text-lg font-bold text-black">{currentPatient.name}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500 mb-1">나이</p>
                    <p className="text-lg font-bold text-black">{currentPatient.age}세</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500 mb-1">성별</p>
                    <p className="text-lg font-bold text-black">{currentPatient.gender === 'Male' ? '남성' : '여성'}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500 mb-1">생년월일</p>
                    <p className="text-lg font-bold text-black">{currentPatient.birth_date}</p>
                  </div>
                </div>
              </div>

              {/* 수정 버튼 */}
              <button
                onClick={handleEdit}
                className="w-full flex items-center justify-center gap-2 px-5 py-4 bg-white text-[#18D4C6] border border-[#18D4C6] rounded-xl text-sm font-semibold hover:bg-[#18D4C6]/5 transition-colors"
              >
                <Edit2 className="w-4 h-4" />
                수정하기
              </button>

              {/* 다른 환자 추가 안내 */}
              <div className="text-center py-4">
                <p className="text-sm text-gray-600 mb-3">다른 환자를 추가하시겠어요?</p>
                <button
                  onClick={handleAddNew}
                  className="flex items-center justify-center gap-2 px-4 py-3 mx-auto bg-gray-100 text-gray-700 rounded-lg text-sm hover:bg-gray-200 transition-colors"
                >
                  <Plus className="w-4 h-4" />
                  새로운 환자 추가
                </button>
              </div>
            </div>

            {/* 다음 버튼 */}
            <div className="mt-8 pb-3">
              <button
                onClick={handleNext}
                disabled={submitting}
                className="w-full px-5 py-[18px] bg-[#18D4C6] text-white border-none rounded-xl text-[17px] font-semibold cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {submitting ? '처리 중...' : '다음'}
              </button>
            </div>
          </div>
        ) : mode === 'edit' || mode === 'addNew' ? (
          // 수정 모드 또는 새 환자 추가 모드 (입력 폼)
          <div>
            <div className="mb-10">
              <h2 className="text-[28px] font-bold text-[#353535] mb-2">도움이 필요해요</h2>
              <p className="text-base font-bold text-[#908d8d]">
                {mode === 'edit' ? '케어 대상자 정보를 수정해주세요' : '새로운 케어 대상자 정보를 입력해주세요'}
              </p>
            </div>

            <form onSubmit={handleSave} className="space-y-5">
              {/* Name */}
              <div className="space-y-2">
                <label className="text-sm font-bold text-black ml-1">
                  이름<span className="text-[#ff8e8e]">*</span>
                </label>
                <input
                  name="name"
                  type="text"
                  className="w-full h-12 px-5 rounded-[10px] border border-[#828282] text-sm placeholder:text-[#828282] focus:outline-none focus:border-[#18d4c6]"
                  placeholder="예: 김영희"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  required
                />
              </div>

              {/* Date of Birth */}
              <div className="space-y-2">
                <label className="text-sm font-bold text-black ml-1">
                  생년월일<span className="text-[#ff8e8e]">*</span>
                </label>
                <div className="relative">
                  <input
                    name="birthDate"
                    type="text"
                    placeholder="연도-월-일"
                    className="w-full h-12 px-5 rounded-[10px] border border-[#828282] text-sm placeholder:text-[#828282] focus:outline-none focus:border-[#18d4c6]"
                    value={formData.birthDate}
                    onChange={(e) => setFormData({ ...formData, birthDate: e.target.value })}
                    required
                  />
                  <Calendar className="absolute right-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-800 pointer-events-none" />
                </div>
              </div>

              {/* Gender */}
              <div className="space-y-2">
                <label className="text-sm font-bold text-black ml-1">
                  성별<span className="text-[#ff8e8e]">*</span>
                </label>
                <div className="flex gap-2">
                  <button
                    type="button"
                    onClick={() => setFormData({ ...formData, gender: 'Female' })}
                    className={cn(
                      "flex-1 h-12 rounded-[10px] border text-sm font-bold transition-colors",
                      formData.gender === 'Female'
                        ? 'bg-[#e8fffd] border-[#18d4c6] text-[#353535]'
                        : 'bg-white border-[#828282] text-[#646464]'
                    )}
                  >
                    여성
                  </button>
                  <button
                    type="button"
                    onClick={() => setFormData({ ...formData, gender: 'Male' })}
                    className={cn(
                      "flex-1 h-12 rounded-[10px] border text-sm font-bold transition-colors",
                      formData.gender === 'Male'
                        ? 'bg-[#e8fffd] border-[#18d4c6] text-[#353535]'
                        : 'bg-white border-[#828282] text-[#646464]'
                    )}
                  >
                    남성
                  </button>
                </div>
              </div>

              {/* Relationship */}
              <div className="space-y-2">
                <div className="flex items-center justify-between ml-1">
                  <label className="text-sm font-bold text-black">
                    보호자와의 관계<span className="text-[#ff8e8e]">*</span>
                  </label>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold text-[#828282]">직접 입력</span>
                    <button
                      type="button"
                      onClick={toggleDirectInput}
                      className={cn(
                        "w-[27px] h-[14px] rounded-full transition-colors relative",
                        formData.isDirectInput ? "bg-[#18d4c6]" : "bg-[#d9d9d9]"
                      )}
                    >
                      <div className={cn(
                        "absolute top-0.5 w-2.5 h-2.5 bg-white rounded-full transition-all shadow-sm",
                        formData.isDirectInput ? "left-[15px]" : "left-0.5"
                      )} />
                    </button>
                  </div>
                </div>

                <div className="relative">
                  {formData.isDirectInput ? (
                    <input
                      name="relationship"
                      type="text"
                      placeholder="관계를 입력해주세요"
                      className="w-full h-12 px-5 rounded-[10px] border border-[#828282] text-sm placeholder:text-[#828282] focus:outline-none focus:border-[#18d4c6]"
                      value={formData.relationship}
                      onChange={(e) => setFormData({ ...formData, relationship: e.target.value })}
                      required
                    />
                  ) : (
                    <>
                      <select
                        name="relationship"
                        className="w-full h-12 px-5 rounded-[10px] border border-[#828282] text-sm text-[#353535] appearance-none bg-white focus:outline-none focus:border-[#18d4c6]"
                        value={formData.relationship}
                        onChange={(e) => setFormData({ ...formData, relationship: e.target.value })}
                        required
                      >
                        <option value="" disabled>선택해주세요</option>
                        <option value="어머니">어머니</option>
                        <option value="아버지">아버지</option>
                        <option value="배우자">배우자</option>
                        <option value="조부모">조부모</option>
                        <option value="기타">기타</option>
                      </select>
                      <ChevronDown className="absolute right-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
                    </>
                  )}
                </div>
              </div>

              {/* Buttons */}
              <div className="mt-8">
                <button
                  type="submit"
                  disabled={submitting}
                  className="w-full h-14 bg-[#18d4c6] rounded-[10px] flex items-center justify-center shadow-[1px_1px_2px_rgba(125,140,139,0.5)] hover:bg-[#15b0a8] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <span className="text-lg font-bold text-white">{submitting ? '저장 중...' : '저장'}</span>
                </button>
              </div>
            </form>
          </div>
        ) : null}
      </main>
    </div>
  )
}
