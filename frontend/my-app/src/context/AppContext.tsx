/**
 * 전역 애플리케이션 상태 Context
 * sessionStorage 의존도를 줄이고 페이지 새로고침 후에도 상태 유지
 */

'use client'

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import type { PatientResponse, CaregiverMatch, ScheduleResponse, CareLog } from '@/types/api'

// Context 상태 타입 정의
export interface AppContextType {
  // 환자 정보
  currentPatient: PatientResponse | null
  setCurrentPatient: (patient: PatientResponse | null) => void

  // 선택된 매칭 정보
  selectedMatching: {
    matching_id: number | null
    caregiver: CaregiverMatch | null
  }
  setSelectedMatching: (matching: { matching_id: number | null; caregiver: CaregiverMatch | null }) => void

  // 케어 플랜 정보
  carePlan: {
    patient_id: number | null
    status: 'pending_review' | 'under_review' | 'reviewed' | 'confirmed' | 'scheduled' | null
    schedules: CareLog[]
    lastUpdated: string | null
  }
  setCarePlan: (plan: AppContextType['carePlan']) => void

  // 케어 플랜 결정 사항
  carePlanDecisions: Record<string, string>
  setCarePlanDecisions: (decisions: Record<string, string>) => void

  // 페이지 새로고침 시 상태 복구 여부
  isHydrated: boolean
}

// Context 생성
const AppContext = createContext<AppContextType | undefined>(undefined)

// Provider 컴포넌트
export function AppProvider({ children }: { children: ReactNode }) {
  // 환자 정보
  const [currentPatient, setCurrentPatient] = useState<PatientResponse | null>(null)

  // 선택된 매칭 정보
  const [selectedMatching, setSelectedMatching] = useState<AppContextType['selectedMatching']>({
    matching_id: null,
    caregiver: null,
  })

  // 케어 플랜 정보
  const [carePlan, setCarePlan] = useState<AppContextType['carePlan']>({
    patient_id: null,
    status: null,
    schedules: [],
    lastUpdated: null,
  })

  // 케어 플랜 결정 사항
  const [carePlanDecisions, setCarePlanDecisions] = useState<Record<string, string>>({})

  // 페이지 새로고침 시 상태 복구
  const [isHydrated, setIsHydrated] = useState(false)

  // 초기화: localStorage/sessionStorage에서 상태 복구
  useEffect(() => {
    try {
      // 환자 정보 복구
      const savedPatient = sessionStorage.getItem('patient_info')
      if (savedPatient) {
        try {
          const parsedPatient = JSON.parse(savedPatient)
          setCurrentPatient(parsedPatient)
        } catch (e) {
          console.warn('[AppContext] Failed to parse patient_info:', e)
        }
      }

      // 매칭 정보 복구
      const savedMatching = sessionStorage.getItem('selectedCaregiver')
      const savedMatchingId = sessionStorage.getItem('matching_id')
      if (savedMatching || savedMatchingId) {
        try {
          const caregiver = savedMatching ? JSON.parse(savedMatching) : null
          setSelectedMatching({
            matching_id: savedMatchingId ? parseInt(savedMatchingId) : null,
            caregiver,
          })
        } catch (e) {
          console.warn('[AppContext] Failed to parse matching info:', e)
        }
      }

      // 케어 플랜 정보 복구
      const savedCarePlan = sessionStorage.getItem('care_plan_info')
      if (savedCarePlan) {
        try {
          const parsedPlan = JSON.parse(savedCarePlan)
          setCarePlan(parsedPlan)
        } catch (e) {
          console.warn('[AppContext] Failed to parse care_plan_info:', e)
        }
      }

      // 케어 플랜 결정 사항 복구
      const savedDecisions = sessionStorage.getItem('care_plan_decisions')
      if (savedDecisions) {
        try {
          const parsedDecisions = JSON.parse(savedDecisions)
          setCarePlanDecisions(parsedDecisions)
        } catch (e) {
          console.warn('[AppContext] Failed to parse care_plan_decisions:', e)
        }
      }

      setIsHydrated(true)
      console.log('[AppContext] State hydrated from storage')
    } catch (error) {
      console.error('[AppContext] Failed to hydrate state:', error)
      setIsHydrated(true)
    }
  }, [])

  // currentPatient 변경 시 sessionStorage 동기화
  useEffect(() => {
    if (isHydrated && currentPatient) {
      sessionStorage.setItem('patient_info', JSON.stringify(currentPatient))
      sessionStorage.setItem('patient_id', currentPatient.patient_id.toString())
      console.log('[AppContext] Patient info saved to storage:', currentPatient.name)
    }
  }, [currentPatient, isHydrated])

  // selectedMatching 변경 시 sessionStorage 동기화
  useEffect(() => {
    if (isHydrated && selectedMatching.matching_id) {
      if (selectedMatching.caregiver) {
        sessionStorage.setItem('selectedCaregiver', JSON.stringify(selectedMatching.caregiver))
      }
      sessionStorage.setItem('matching_id', selectedMatching.matching_id.toString())
      console.log('[AppContext] Matching info saved to storage')
    }
  }, [selectedMatching, isHydrated])

  // carePlan 변경 시 sessionStorage 동기화
  useEffect(() => {
    if (isHydrated && carePlan.patient_id) {
      sessionStorage.setItem('care_plan_info', JSON.stringify(carePlan))
      console.log('[AppContext] Care plan info saved to storage')
    }
  }, [carePlan, isHydrated])

  // carePlanDecisions 변경 시 sessionStorage 동기화
  useEffect(() => {
    if (isHydrated && Object.keys(carePlanDecisions).length > 0) {
      sessionStorage.setItem('care_plan_decisions', JSON.stringify(carePlanDecisions))
      console.log('[AppContext] Care plan decisions saved to storage')
    }
  }, [carePlanDecisions, isHydrated])

  const value: AppContextType = {
    currentPatient,
    setCurrentPatient,
    selectedMatching,
    setSelectedMatching,
    carePlan,
    setCarePlan,
    carePlanDecisions,
    setCarePlanDecisions,
    isHydrated,
  }

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>
}

/**
 * AppContext를 사용하는 커스텀 Hook
 */
export function useAppContext() {
  const context = useContext(AppContext)
  if (!context) {
    throw new Error('useAppContext must be used within AppProvider')
  }
  return context
}

/**
 * 특정 값만 사용하는 커스텀 Hook들
 */
export function useCurrentPatient() {
  const { currentPatient, setCurrentPatient } = useAppContext()
  return { currentPatient, setCurrentPatient }
}

export function useSelectedMatching() {
  const { selectedMatching, setSelectedMatching } = useAppContext()
  return { selectedMatching, setSelectedMatching }
}

export function useCarePlan() {
  const { carePlan, setCarePlan } = useAppContext()
  return { carePlan, setCarePlan }
}

export function useCarePlanDecisions() {
  const { carePlanDecisions, setCarePlanDecisions } = useAppContext()
  return { carePlanDecisions, setCarePlanDecisions }
}
