'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { background, firstPrimary, secondPrimary } from '../colors'
import { apiPost, apiPut } from '@/utils/api'
import ErrorAlert from '@/components/ErrorAlert'
import type { ApiResponse } from '@/types/api'
import { validateApiResponse } from '@/types/guards'
import { useAppContext, useCarePlanDecisions } from '@/context/AppContext'

export default function Screen11AIValidation() {
  const router = useRouter()
  const appContext = useAppContext()
  const { carePlanDecisions, setCarePlanDecisions } = useCarePlanDecisions()

  const [decisions, setDecisions] = useState<{
    [key: string]: string
  }>({
    'accept-0': undefined,
    'partial-0': undefined,
    'reject-0': undefined
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<Error | null>(null)

  // 사용자 결정 저장
  const handleDecision = (feedbackId: string, decision: string) => {
    setDecisions(prev => ({
      ...prev,
      [feedbackId]: decision
    }))
  }

  // 모든 결정이 완료되었는지 확인
  const areAllDecisionsMade = () => {
    return Object.values(decisions).every(v => v !== undefined)
  }

  // 최종 결정 저장 및 페이지 이동
  const handleSubmitDecisions = async () => {
    if (!areAllDecisionsMade()) {
      setError(new Error('모든 일정에 대해 결정을 내려주세요.'))
      return
    }

    setLoading(true)
    setError(null)

    try {
      // Context 또는 sessionStorage에서 환자 ID 조회
      const patientId = appContext.currentPatient?.patient_id?.toString() ||
                        sessionStorage.getItem('patient_id')
      const matchingId = appContext.selectedMatching?.matching_id?.toString() ||
                         sessionStorage.getItem('matching_id')

      if (!patientId) {
        throw new Error('환자 정보를 찾을 수 없습니다.')
      }

      // 결정 사항을 API에 전송
      const payload = {
        patient_id: parseInt(patientId),
        matching_id: matchingId,
        feedback_decisions: decisions,
        approved_at: new Date().toISOString()
      }

      console.log('[Care Plans Validation] Submitting decisions:', payload)

      // Context와 sessionStorage에 결정 사항 저장
      setCarePlanDecisions(decisions)
      sessionStorage.setItem('care_plan_decisions', JSON.stringify(decisions))
      sessionStorage.setItem('care_plan_approved_at', new Date().toISOString())

      // 스케줄 상태를 confirmed로 업데이트
      const response = await apiPut<ApiResponse>('/api/care-plans/schedules/status', {
        patient_id: parseInt(patientId),
        status: 'confirmed'
      })

      // API 응답 검증 - 타입 가드 함수 사용
      if (!response) {
        throw new Error('서버에서 응답을 받지 못했습니다')
      }

      if (!validateApiResponse(response)) {
        console.error('[Care Plans Validation] Invalid response structure:', response)
        throw new Error('스케줄 상태 업데이트 실패')
      }

      // 성공 여부 확인
      if (response.status === 'error' || response.success === false) {
        throw new Error(response.message || '스케줄 상태 업데이트 실패')
      }

      console.log('[Care Plans Validation] Decisions saved and status updated to confirmed')

      // 성공 시에만 페이지 이동
      router.push('/schedule')
    } catch (err) {
      console.error('[Care Plans Validation] Error submitting decisions:', err)
      setError(err as Error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex flex-col bg-white min-h-screen">
      {/* Header with Navigation */}
      <div className="flex flex-col items-start self-stretch bg-white" style={{ boxShadow: "0px 4px 4px #00000040" }}>
        {/* Navigation Bar */}
        <div className="relative flex items-center justify-between self-stretch bg-white py-[22px] px-[34px] mt-[54px] mb-[1px]">
          <button
            className="w-[5px] h-2.5 cursor-pointer z-10"
            onClick={() => router.back()}
          >
            ‹
          </button>
          <span className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 text-[#646464] text-lg font-bold">
            검증 결과
          </span>
          <div className="w-[18px] h-5 z-10"></div>
        </div>

        {/* Divider */}
        <img
          src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 1'%3E%3Cline x1='0' y1='0' x2='100' y2='0' stroke='%23E0E0E0' stroke-width='1'/%3E%3C/svg%3E"
          className="self-stretch h-[1px] mb-[27px] object-fill"
        />

        {/* Title Section */}
        <div className="flex flex-col items-start mb-12 ml-9 gap-1">
          <span className="text-[#353535] text-[28px] font-bold">간병인 의견이 도착했어요</span>
          <span className="text-[#828282] text-base font-bold mr-[82px]">AI가 검증한 결과를 확인하세요.</span>
        </div>

        {/* Summary Card */}
        <div className="flex flex-col items-start self-stretch bg-white py-[18px] mb-9 mx-[34px] rounded-lg border border-solid border-[#18D4C6]" style={{ boxShadow: "0px 1px 4px #00000040" }}>
          <span className="text-[#353535] text-base font-bold mb-3 ml-5">검토 결과 요약</span>

          {/* Summary Stats */}
          <div className="flex items-start self-stretch mb-3 mx-[42px] gap-4">
            <div className="flex flex-1 flex-col items-center gap-0.5">
              <button
                className="flex flex-col items-center self-stretch text-left py-[18px] rounded-[50px] border-0"
                style={{ background: "linear-gradient(180deg, #F2FFFE, #FFF4F4)" }}
              >
                <span className="text-[#18D4C6] font-bold">9건</span>
              </button>
              <span className="text-[#828282] text-xs font-bold">수용 권장</span>
            </div>

            <div className="flex flex-1 flex-col items-center gap-0.5">
              <button
                className="flex flex-col items-center self-stretch text-left py-[18px] rounded-[50px] border-0"
                style={{ background: "linear-gradient(180deg, #F2FFFE, #FFF4F4)" }}
              >
                <span className="text-[#18D4C6] font-bold">2건</span>
              </button>
              <span className="text-[#828282] text-xs font-bold">부분 수용</span>
            </div>

            <div className="flex flex-1 flex-col items-center gap-0.5">
              <button
                className="flex flex-col items-center self-stretch text-left py-[18px] rounded-[50px] border-0"
                style={{ background: "linear-gradient(180deg, #F2FFFE, #FFF4F4)" }}
              >
                <span className="text-[#18D4C6] font-bold">1건</span>
              </button>
              <span className="text-[#828282] text-xs font-bold">거부 권장</span>
            </div>
          </div>

          {/* Divider */}
          <img
            src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 1'%3E%3Cline x1='0' y1='0' x2='100' y2='0' stroke='%23E0E0E0' stroke-width='1'/%3E%3C/svg%3E"
            className="self-stretch h-[1px] mb-3 mx-[19px] object-fill"
          />

          {/* Trust Score */}
          <div className="flex flex-col items-center self-stretch mb-1">
            <span className="text-[#353535] text-2xl font-bold">92/100</span>
          </div>
          <div className="flex flex-col items-center self-stretch">
            <span className="text-[#828282] text-xs">검토 결과 요약</span>
          </div>
        </div>

        {/* Content Section - Accept Recommendations */}
        <div className={`flex flex-col items-start self-stretch py-[18px] pr-[19px] mb-6 mx-[34px] gap-3 rounded-lg relative transition-all ${
          decisions['accept-0'] === 'accept'
            ? 'bg-[#F0FFFD] border-2 border-[#18D4C6]'
            : decisions['accept-0'] === 'reject'
            ? 'bg-gray-100 opacity-50 border-2 border-gray-300'
            : 'bg-white border border-transparent'
        }`} style={decisions['accept-0'] === 'accept' || decisions['accept-0'] === 'reject' ? {} : { boxShadow: "0px 1px 4px #00000040" }}>
          {/* Status Badge */}
          {decisions['accept-0'] && (
            <div className={`absolute top-4 right-4 px-3 py-1 rounded-full text-xs font-bold ${
              decisions['accept-0'] === 'accept'
                ? 'bg-[#18D4C6] text-white'
                : 'bg-gray-400 text-white'
            }`}>
              {decisions['accept-0'] === 'accept' ? '✓ 확정' : '✗ 거절됨'}
            </div>
          )}
          <div className="flex items-center ml-[19px] gap-[7px]">
            <div className="w-2.5 h-2.5 bg-green-500 rounded-full"></div>
            <span className="text-[#353535] text-base font-bold">수용 권장</span>
          </div>

          {/* Divider */}
          <img
            src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 1'%3E%3Cline x1='0' y1='0' x2='100' y2='0' stroke='%23E0E0E0' stroke-width='1'/%3E%3C/svg%3E"
            className="self-stretch h-[1px] ml-[19px] object-fill"
          />

          {/* Existing Schedule */}
          <div className="flex flex-col items-start self-stretch bg-[#F8F8F8] py-3 ml-[19px] rounded-[5px]">
            <span className="text-[#353535] text-sm font-bold ml-[17px]">기존 일정</span>
            <div className="flex flex-col items-start ml-[17px]">
              <span className="text-[#828282] text-xs mr-[79px]">08:00 약 복용 확인</span>
              <span className="text-[#828282] text-xs">아스피린 100g, 메트포르민 500mg</span>
            </div>
          </div>

          {/* Caregiver Opinion */}
          <div className="flex flex-col items-start self-stretch bg-[#F2FFFE] py-[13px] pr-[17px] ml-[19px] rounded-[5px] border border-solid border-[#18D4C6]">
            <span className="text-[#353535] text-sm font-bold mb-1 ml-[17px]">간병인 의견</span>
            <span className="text-[#828282] text-xs w-[247px] mb-3 ml-[17px] whitespace-pre-line">약 복용은 식사 후 30분 뒤에 하는 것이 더 좋습니다.
메트포르민은 공복에 먹으면 속이 불편할 수 있습니다.</span>

            {/* Divider */}
            <img
              src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 1'%3E%3Cline x1='0' y1='0' x2='100' y2='0' stroke='%23E0E0E0' stroke-width='1'/%3E%3C/svg%3E"
              className="self-stretch h-[1px] mb-3 ml-[17px] object-fill"
            />

            {/* Validation */}
            <div className="flex flex-col items-start self-stretch ml-[17px] gap-[5px]">
              <div className="flex items-center gap-1.5">
                <div className="w-[9px] h-3 bg-red-400 rounded-full"></div>
                <span className="text-[#FF7E7E] text-xs font-bold">의학적으로 타당한 의견</span>
              </div>
              <span className="text-[#FF7E7E] text-xs w-[247px]">MSD 매뉴얼에 따르면, 메트포르민은 위장 부작용을
줄이기 위해 식사 중이나 직후에 복용하는 것이 권장됩
니다.</span>
            </div>
          </div>

          {/* AI Suggestion */}
          <div className="flex flex-col items-start self-stretch bg-[#F2FFFE] py-[11px] ml-[19px] gap-1 rounded-[5px] border border-solid border-[#18D4C6]">
            <span className="text-[#353535] text-sm font-bold ml-[17px]">조정 제안</span>
            <span className="text-[#828282] text-xs ml-[17px]">08:30으로 시간 변경 제안</span>
          </div>

          {/* Action Buttons */}
          <div className="flex items-start self-stretch ml-5 gap-2">
            <button
              onClick={() => {
                handleDecision('accept-0', 'accept')
                console.log('[Care Plans] Accept recommendation clicked')
              }}
              className="flex flex-1 flex-col items-center bg-[#18D4C6] text-left py-[11px] rounded-lg border border-solid border-[#18D4C6]"
            >
              <span className="text-white text-base font-bold">수용하기</span>
            </button>
            <button
              onClick={() => {
                handleDecision('accept-0', 'reject')
                console.log('[Care Plans] Reject recommendation clicked')
              }}
              className="flex flex-1 flex-col items-center bg-[#F2F2F2] text-left py-[11px] rounded-lg border border-solid border-[#828282]"
            >
              <span className="text-[#828282] text-base font-bold">거부하기</span>
            </button>
          </div>
        </div>

        {/* Content Section - Partial Accept */}
        <div className={`flex flex-col items-start self-stretch py-[17px] pr-[19px] mb-6 mx-[34px] gap-3 rounded-lg relative transition-all ${
          decisions['partial-0'] === 'ai_suggestion' || decisions['partial-0'] === 'caregiver_suggestion' || decisions['partial-0'] === 'manual_edit'
            ? 'bg-[#F0FFFD] border-2 border-[#18D4C6]'
            : 'bg-white border border-transparent'
        }`} style={decisions['partial-0'] ? {} : { boxShadow: "0px 1px 4px #00000040" }}>
          {/* Status Badge */}
          {decisions['partial-0'] && (
            <div className="absolute top-4 right-4 px-3 py-1 rounded-full text-xs font-bold bg-[#18D4C6] text-white">
              ✓ 확정
            </div>
          )}
          <div className="flex items-center ml-5 gap-1.5">
            <div className="w-2.5 h-2.5 bg-yellow-500 rounded-full"></div>
            <span className="text-[#353535] text-base font-bold">부분 수용 권장</span>
          </div>

          {/* Divider */}
          <img
            src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 1'%3E%3Cline x1='0' y1='0' x2='100' y2='0' stroke='%23E0E0E0' stroke-width='1'/%3E%3C/svg%3E"
            className="self-stretch h-[1px] ml-[19px] object-fill"
          />

          {/* Caregiver Opinion */}
          <div className="flex flex-col items-start self-stretch bg-[#F2FFFE] py-3 ml-[19px] rounded-[5px] border border-solid border-[#18D4C6]">
            <span className="text-[#353535] text-sm font-bold mb-1 ml-[17px]">간병인 의견</span>
            <span className="text-[#828282] text-xs mb-3 ml-[17px] mr-[34px] whitespace-pre-line">오전에 활동이 너무 집중되어 있어요. 환자분이 쉽게
피로해하실 수 있으니 휴식 시간을 2시간 늘리세요.</span>

            {/* Divider */}
            <img
              src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 1'%3E%3Cline x1='0' y1='0' x2='100' y2='0' stroke='%23E0E0E0' stroke-width='1'/%3E%3C/svg%3E"
              className="self-stretch h-[1px] mb-3 mx-[17px] object-fill"
            />

            {/* Validation */}
            <div className="flex flex-col items-start self-stretch mx-[17px] gap-[5px]">
              <div className="flex items-center gap-1.5">
                <div className="w-[9px] h-3 bg-yellow-500 rounded-full"></div>
                <span className="text-[#FF7E7E] text-xs font-bold">휴식 필요성은 타당한 의견</span>
              </div>
              <span className="text-[#FF7E7E] text-xs">!! 2시간은 과도함.</span>
              <span className="text-[#FF7E7E] text-xs w-[244px] whitespace-pre-line">78세 경도 치매 환자의 경우, 적절한 인지자극은 필요
합니다. 과도한 휴식은 오히려 인지 기능 저하를 유발
할 수 있습니다.</span>
            </div>
          </div>

          {/* AI Alternative Suggestion */}
          <div className="flex flex-col items-start self-stretch bg-[#F2FFFE] py-[11px] ml-[19px] gap-1 rounded-[5px] border border-solid border-[#18D4C6]">
            <span className="text-[#353535] text-sm font-bold ml-[17px]">AI 대안 제안</span>
            <span className="text-[#828282] text-xs w-[250px] ml-[17px] whitespace-pre-line">휴식 시간 1시간 + 가벼운 인지 활동(퍼즐, 이야기 나누
기 등) 30분 추가</span>
          </div>

          {/* Action Buttons */}
          <div className="flex items-start self-stretch ml-[19px] gap-2">
            <button
              onClick={() => {
                handleDecision('partial-0', 'ai_suggestion')
                console.log('[Care Plans] AI suggestion accepted')
              }}
              className="flex flex-1 flex-col items-center bg-[#18D4C6] text-left py-[11px] mr-2 rounded-lg border border-solid border-[#18D4C6]"
            >
              <span className="text-white text-sm font-bold">AI 제안 수용</span>
            </button>
            <button
              onClick={() => {
                handleDecision('partial-0', 'caregiver_suggestion')
                console.log('[Care Plans] Caregiver suggestion accepted')
              }}
              className="flex flex-1 flex-col items-center bg-[#F2F2F2] text-left py-[11px] mr-[9px] rounded-lg border border-solid border-[#828282]"
            >
              <span className="text-[#828282] text-sm font-bold">제안 수용</span>
            </button>
            <button
              onClick={() => {
                handleDecision('partial-0', 'manual_edit')
                console.log('[Care Plans] Manual edit selected')
              }}
              className="flex flex-1 flex-col items-center bg-[#F2F2F2] text-left py-[11px] rounded-lg border border-solid border-[#828282]"
            >
              <span className="text-[#828282] text-sm font-bold">직접 수정</span>
            </button>
          </div>
        </div>

        {/* Content Section - Reject Recommendations */}
        <div className={`flex flex-col items-start self-stretch py-4 pr-[19px] mb-[95px] mx-[34px] gap-3 rounded-lg relative transition-all ${
          decisions['reject-0'] === 'keep_original'
            ? 'bg-[#F0FFFD] border-2 border-[#18D4C6]'
            : decisions['reject-0'] === 'force_change'
            ? 'bg-gray-100 opacity-50 border-2 border-gray-300'
            : 'bg-white border border-transparent'
        }`} style={decisions['reject-0'] === 'keep_original' || decisions['reject-0'] === 'force_change' ? {} : { boxShadow: "0px 1px 4px #00000040" }}>
          {/* Status Badge */}
          {decisions['reject-0'] && (
            <div className={`absolute top-4 right-4 px-3 py-1 rounded-full text-xs font-bold ${
              decisions['reject-0'] === 'keep_original'
                ? 'bg-[#18D4C6] text-white'
                : 'bg-gray-400 text-white'
            }`}>
              {decisions['reject-0'] === 'keep_original' ? '✓ 확정' : '✗ 변경됨'}
            </div>
          )}
          <div className="flex items-center ml-5 gap-1.5">
            <div className="w-2.5 h-2.5 bg-red-500 rounded-full"></div>
            <span className="text-[#353535] text-base font-bold">거부 권장</span>
          </div>

          {/* Divider */}
          <img
            src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 1'%3E%3Cline x1='0' y1='0' x2='100' y2='0' stroke='%23E0E0E0' stroke-width='1'/%3E%3C/svg%3E"
            className="self-stretch h-[1px] ml-[19px] object-fill"
          />

          {/* Caregiver Opinion */}
          <div className="flex flex-col items-start self-stretch bg-[#F2FFFE] py-[13px] ml-[19px] rounded-[5px] border border-solid border-[#18D4C6]">
            <span className="text-[#353535] text-sm font-bold mb-1 ml-[17px]">간병인 의견</span>
            <span className="text-[#828282] text-xs mb-3 ml-[17px]">혈압약은 저녁에 복용하는 게 더 효과적입니다.</span>

            {/* Divider */}
            <img
              src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 1'%3E%3Cline x1='0' y1='0' x2='100' y2='0' stroke='%23E0E0E0' stroke-width='1'/%3E%3C/svg%3E"
              className="self-stretch h-[1px] mb-3 mx-[17px] object-fill"
            />

            {/* Validation */}
            <div className="flex flex-col items-start self-stretch ml-[17px] mr-[31px] gap-[5px]">
              <div className="flex items-center gap-1.5">
                <div className="w-[9px] h-3 bg-red-500 rounded-full"></div>
                <span className="text-[#FF7E7E] text-xs font-bold">의학적 근거 불충분</span>
              </div>
              <span className="text-[#FF7E7E] text-xs w-60 whitespace-pre-line">환자가 복용 중인 암로디핀은 하루 한 번 아침 복용이
표준입니다. 야간 저혈압 위험을 피하기 위해 저녁 복
용은 권장되지 않습니다.</span>
              <span className="text-[#D53D42] text-sm font-bold">의사와 상담 후 변경을 권장합니다.</span>
            </div>
          </div>

          {/* AI Alternative Suggestion */}
          <div className="flex flex-col items-start self-stretch bg-[#F2FFFE] py-[11px] ml-[19px] gap-1 rounded-[5px] border border-solid border-[#18D4C6]">
            <span className="text-[#353535] text-sm font-bold ml-[17px]">AI 대안 제안</span>
            <span className="text-[#828282] text-xs w-[250px] ml-[17px] whitespace-pre-line">휴식 시간 1시간 + 가벼운 인지 활동(퍼즐, 이야기 나누
기 등) 30분 추가</span>
          </div>

          {/* Action Buttons */}
          <div className="flex items-start self-stretch ml-[19px] gap-2.5">
            <button
              onClick={() => {
                handleDecision('reject-0', 'keep_original')
                console.log('[Care Plans] Keep original plan selected')
              }}
              className="flex flex-1 flex-col items-center bg-[#18D4C6] text-left py-[11px] rounded-lg border border-solid border-[#18D4C6]"
            >
              <span className="text-white text-base font-bold">원안 유지하기</span>
            </button>
            <button
              onClick={() => {
                handleDecision('reject-0', 'force_change')
                console.log('[Care Plans] Force change selected')
              }}
              className="flex flex-1 flex-col items-center bg-[#F2F2F2] text-left py-[11px] rounded-lg border border-solid border-[#828282]"
            >
              <span className="text-[#828282] text-base font-bold">그래도 변경</span>
            </button>
          </div>
        </div>

        {/* Error Alert */}
        <ErrorAlert error={error} onClose={() => setError(null)} />

        {/* Final Submit Button - Visible at bottom */}
        <div className="sticky bottom-0 flex items-center gap-2 px-[34px] py-6 bg-white border-t border-gray-200 w-full">
          <button
            onClick={handleSubmitDecisions}
            disabled={loading || !areAllDecisionsMade()}
            className={`w-full items-center justify-center py-3 rounded-lg font-bold text-base transition-all ${
              loading || !areAllDecisionsMade()
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-[#18D4C6] text-white hover:bg-[#15b0a8]'
            }`}
          >
            {loading ? '저장 중...' : '완료된 일정보기'}
          </button>
        </div>
      </div>
    </div>
  )
}
