/**
 * 타입 가드 함수 (Type Guard Functions)
 * API 응답의 타입 안전성을 검증합니다
 */

import type { CareLog, ScheduleResponse, ApiResponse, PatientResponse, CaregiverMatch } from './api'

/**
 * CareLog 타입 검증
 * 필수 필드: schedule_id, task_name, category, scheduled_time, is_completed
 */
export function validateCareLog(log: any): log is CareLog {
  if (!log || typeof log !== 'object') {
    return false
  }

  return (
    typeof log.schedule_id === 'number' &&
    typeof log.task_name === 'string' &&
    typeof log.category === 'string' &&
    (typeof log.scheduled_time === 'string' || log.scheduled_time === null) &&
    typeof log.is_completed === 'boolean'
  )
}

/**
 * ScheduleResponse 타입 검증
 * 필수 필드: patient_id, date, care_logs (배열)
 */
export function validateScheduleResponse(response: any): response is ScheduleResponse {
  if (!response || typeof response !== 'object') {
    return false
  }

  return (
    typeof response.patient_id === 'number' &&
    typeof response.date === 'string' &&
    Array.isArray(response.care_logs) &&
    response.care_logs.every((log: any) => validateCareLog(log))
  )
}

/**
 * CareLog 배열 검증
 * 배열의 모든 항목이 CareLog 타입인지 확인
 */
export function validateCareLogArray(logs: any): logs is CareLog[] {
  if (!Array.isArray(logs)) {
    return false
  }

  return logs.every((log: any) => validateCareLog(log))
}

/**
 * 일반 API 응답 검증
 * status 또는 success 필드 검증
 */
export function validateApiResponse(response: any): response is ApiResponse {
  if (!response || typeof response !== 'object') {
    return false
  }

  const hasStatus = response.status === 'success' || response.status === 'error'
  const hasSuccess = typeof response.success === 'boolean'

  return hasStatus || hasSuccess
}

/**
 * PatientResponse 타입 검증
 * 필수 필드: patient_id, name, age, gender
 */
export function validatePatientResponse(patient: any): patient is PatientResponse {
  if (!patient || typeof patient !== 'object') {
    return false
  }

  return (
    typeof patient.patient_id === 'number' &&
    typeof patient.name === 'string' &&
    typeof patient.age === 'number' &&
    (patient.gender === 'Male' || patient.gender === 'Female')
  )
}

/**
 * CaregiverMatch 타입 검증
 * 필수 필드: caregiver_id, caregiver_name, match_score, experience_years, hourly_rate
 */
export function validateCaregiverMatch(match: any): match is CaregiverMatch {
  if (!match || typeof match !== 'object') {
    return false
  }

  return (
    typeof match.caregiver_id === 'number' &&
    typeof match.caregiver_name === 'string' &&
    typeof match.match_score === 'number' &&
    typeof match.experience_years === 'number' &&
    typeof match.hourly_rate === 'number'
  )
}

/**
 * null/undefined 체크 헬퍼
 */
export function isValidData<T>(data: T | null | undefined): data is T {
  return data !== null && data !== undefined
}

/**
 * 배열이 비어있지 않은지 확인
 */
export function isNonEmptyArray<T>(arr: any): arr is T[] {
  return Array.isArray(arr) && arr.length > 0
}
