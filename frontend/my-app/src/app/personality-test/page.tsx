"use client"

import { useState, useEffect, useRef } from "react"
import { useRouter } from "next/navigation"
import { motion, AnimatePresence } from "framer-motion"
import { ChatBubble } from "@/components/ui/chat-bubble"
import { Sparkles } from "lucide-react"
import { apiPost } from "@/utils/api"
import ErrorAlert from "@/components/ErrorAlert"
import { Button } from "@/components/ui/button"

// 상황 기반 질문 (6개) + 각 선택지별 4차원 점수
interface QuestionOption {
  text: string
  scores: {
    empathy: number
    activity: number
    patience: number
    independence: number
  }
}

interface Question {
  id: string
  text: string
  options: QuestionOption[]
}

const PERSONALITY_QUESTIONS: Question[] = [
  {
    id: "q1",
    text: "환자분이 우울해 보일 때, 당신은 주로 어떻게 하나요?",
    options: [
      {
        text: "먼저 어떤 기분인지 물어보고 이야기를 들어주기",
        scores: { empathy: 5, activity: 1, patience: 4, independence: 2 }
      },
      {
        text: "함께 있으면서 필요할 때만 도와주기",
        scores: { empathy: 3, activity: 1, patience: 5, independence: 3 }
      },
      {
        text: "산책이나 활동을 제안해서 기분 전환 유도하기",
        scores: { empathy: 2, activity: 5, patience: 2, independence: 4 }
      }
    ]
  },
  {
    id: "q2",
    text: "응급 상황이 발생했을 때, 당신은 주로 어떻게 하나요?",
    options: [
      {
        text: "침착함을 유지하며 상황을 정확히 파악한 후 조치하기",
        scores: { empathy: 2, activity: 4, patience: 5, independence: 4 }
      },
      {
        text: "가족이나 의료진에게 먼저 알린 후 지시를 받기",
        scores: { empathy: 3, activity: 2, patience: 3, independence: 1 }
      },
      {
        text: "빠르게 판단해서 즉시 필요한 조치 취하기",
        scores: { empathy: 1, activity: 5, patience: 2, independence: 5 }
      }
    ]
  },
  {
    id: "q3",
    text: "환자분이 자신의 감정을 표현하기 어려워할 때, 당신은 어떻게 하나요?",
    options: [
      {
        text: "작은 변화도 놓치지 않고 세심하게 관찰하기",
        scores: { empathy: 4, activity: 1, patience: 5, independence: 3 }
      },
      {
        text: "편안한 분위기를 만들어 표현할 수 있도록 기다리기",
        scores: { empathy: 5, activity: 1, patience: 5, independence: 2 }
      },
      {
        text: "직접 선택지를 제시해서 의사를 파악하기",
        scores: { empathy: 2, activity: 4, patience: 2, independence: 4 }
      }
    ]
  },
  {
    id: "q4",
    text: "매일 반복되는 일상 케어 업무를 수행할 때, 당신은 어떻게 하나요?",
    options: [
      {
        text: "정해진 방식을 그대로 따르되, 환자의 변화에 따라 조정하기",
        scores: { empathy: 3, activity: 2, patience: 5, independence: 3 }
      },
      {
        text: "환자분이 최대한 편하시도록 여러 방법을 시도해보기",
        scores: { empathy: 4, activity: 4, patience: 3, independence: 4 }
      },
      {
        text: "효율적으로 일을 처리하되, 표준화된 방식 유지하기",
        scores: { empathy: 1, activity: 5, patience: 3, independence: 5 }
      }
    ]
  },
  {
    id: "q5",
    text: "예상하지 못한 어려운 상황이 생겼을 때, 당신은 어떻게 하나요?",
    options: [
      {
        text: "침착함을 유지하고 가능한 모든 방법을 차분하게 시도하기",
        scores: { empathy: 2, activity: 3, patience: 5, independence: 5 }
      },
      {
        text: "환자분의 마음을 먼저 안정시킨 후 문제 해결하기",
        scores: { empathy: 5, activity: 1, patience: 4, independence: 2 }
      },
      {
        text: "빠르게 대응해서 상황을 신속하게 해결하기",
        scores: { empathy: 1, activity: 5, patience: 2, independence: 5 }
      }
    ]
  },
  {
    id: "q6",
    text: "환자분과의 관계에서 당신이 가장 중요하게 생각하는 것은?",
    options: [
      {
        text: "환자분과의 감정적 신뢰와 편안한 관계",
        scores: { empathy: 5, activity: 1, patience: 4, independence: 1 }
      },
      {
        text: "업무의 효율성과 질 높은 케어 제공",
        scores: { empathy: 1, activity: 5, patience: 3, independence: 5 }
      },
      {
        text: "환자분의 독립성을 존중하면서 필요한 것 챙기기",
        scores: { empathy: 3, activity: 2, patience: 4, independence: 4 }
      }
    ]
  }
]

interface Message {
  id: number
  text: string
  isAi: boolean
  type?: "text" | "options"
  options?: QuestionOption[]
}

interface Answers {
  [key: string]: number
}

export default function PersonalityTestPage() {
  const router = useRouter()
  const [messages, setMessages] = useState<Message[]>([])
  const [currentQuestionIdx, setCurrentQuestionIdx] = useState(0)
  const [isTyping, setIsTyping] = useState(false)
  const [answers, setAnswers] = useState<Answers>({})
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<Error | null>(null)
  const [results, setResults] = useState<any>(null)
  const initialized = useRef(false)
  const chatContainerRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight
    }
  }

  useEffect(() => {
    setTimeout(() => scrollToBottom(), 100)
  }, [messages, isTyping, currentQuestionIdx])

  const addMessage = (text: string, isAi: boolean) => {
    setIsTyping(false)
    setMessages((prev) => [...prev, { id: Date.now(), text, isAi }])
  }

  // Initial greeting and first question
  useEffect(() => {
    if (!initialized.current) {
      initialized.current = true
      setTimeout(() => setIsTyping(true), 0)
      setTimeout(() => {
        addMessage("안녕하세요! 늘봄케어 AI 매니저 늘보미입니다.", true)
        setIsTyping(true)
        setTimeout(() => {
          addMessage("당신에게 맞는 간병인을 찾기 위해 몇 가지 질문을 드릴게요.", true)
          setIsTyping(true)
          setTimeout(() => {
            const firstQuestion = PERSONALITY_QUESTIONS[0]
            setMessages((prev) => [...prev, {
              id: Date.now(),
              text: firstQuestion.text,
              isAi: true,
              type: "options",
              options: firstQuestion.options
            }])
            setIsTyping(false)
            setCurrentQuestionIdx(0)
          }, 800)
        }, 1000)
      }, 800)
    }
  }, [])

  const handleOptionClick = (selectedOption: QuestionOption) => {
    const currentQuestion = PERSONALITY_QUESTIONS[currentQuestionIdx]

    // Add user's answer message
    addMessage(selectedOption.text, false)

    // Update answers with scores as JSON string
    setAnswers(prev => ({
      ...prev,
      [currentQuestion.id]: JSON.stringify(selectedOption.scores)
    }))

    // Move to next question or show results
    if (currentQuestionIdx < PERSONALITY_QUESTIONS.length - 1) {
      setIsTyping(true)
      setTimeout(() => {
        const nextQuestion = PERSONALITY_QUESTIONS[currentQuestionIdx + 1]
        setMessages((prev) => [...prev, {
          id: Date.now(),
          text: nextQuestion.text,
          isAi: true,
          type: "options",
          options: nextQuestion.options
        }])
        setIsTyping(false)
        setCurrentQuestionIdx(currentQuestionIdx + 1)
      }, 1000)
    } else {
      // All questions answered - submit
      setIsTyping(true)
      setTimeout(() => {
        addMessage("모든 정보를 확인했습니다! 분석을 시작할게요.", true)
        submitPersonalityTest()
      }, 1000)
    }
  }

  // 🔧 OPTION 1: 규칙 기반 성격 분석 함수
  const generateAnalysis = (scores: {
    empathy_score: number
    activity_score: number
    patience_score: number
    independence_score: number
  }): string => {
    const analyses: string[] = []

    // 공감 능력 분석
    if (scores.empathy_score > 75) {
      analyses.push("타인의 감정에 민감하고 공감 능력이 뛰어나 따뜻한 관계 형성이 가능합니다")
    } else if (scores.empathy_score > 50) {
      analyses.push("적절한 공감 능력으로 환자와 좋은 관계를 유지할 수 있습니다")
    } else {
      analyses.push("실무적이고 객관적인 접근으로 효율적인 업무 처리가 가능합니다")
    }

    // 활동성 분석
    if (scores.activity_score > 75) {
      analyses.push("활발하고 적극적인 성향으로 주도적이고 역동적인 돌봄을 제공할 수 있습니다")
    } else if (scores.activity_score > 50) {
      analyses.push("적절한 활동성으로 필요한 순간에 잘 대응할 수 있습니다")
    } else {
      analyses.push("차분하고 신중한 성향으로 안정적이고 집중력 있는 돌봄이 가능합니다")
    }

    // 인내심 분석
    if (scores.patience_score > 75) {
      analyses.push("높은 인내심과 관용으로 어려운 상황에서도 차분히 대처하며 오래 관계를 유지할 수 있습니다")
    } else if (scores.patience_score > 50) {
      analyses.push("적절한 인내심으로 환자의 다양한 요구에 대응할 수 있습니다")
    } else {
      analyses.push("빠른 판단과 행동력으로 효율적인 문제 해결이 가능합니다")
    }

    // 자립성 분석
    if (scores.independence_score > 75) {
      analyses.push("독립적이고 책임감 있는 성향으로 주어진 역할을 충실히 수행하고 자율적인 판단을 잘 합니다")
    } else if (scores.independence_score > 50) {
      analyses.push("적절한 독립성으로 지시를 잘 따르면서도 자율적으로 일할 수 있습니다")
    } else {
      analyses.push("협력적이고 팀 지향적 성향으로 다른 사람과의 조화를 잘 맞추며 함께 일할 수 있습니다")
    }

    return analyses.join(". ")
  }

  const generateRecommendation = (scores: {
    empathy_score: number
    activity_score: number
    patience_score: number
    independence_score: number
  }): string => {
    const traits: string[] = []

    if (scores.empathy_score > 70) traits.push("따뜻한")
    if (scores.activity_score > 70) traits.push("활발한")
    if (scores.patience_score > 70) traits.push("인내심 있는")
    if (scores.independence_score > 70) traits.push("책임감 있는")

    if (scores.empathy_score < 45) traits.push("실무적인")
    if (scores.activity_score < 45) traits.push("신중한")

    if (traits.length === 0) {
      traits.push("균형 잡힌")
    }

    return `${traits.join("하고 ")}하며 신뢰할 수 있는 간병인`
  }

  const submitPersonalityTest = async () => {
    setLoading(true)
    setError(null)

    try {
      // 모든 답변의 점수를 합산하여 최종 점수 계산
      const combinedScores = {
        empathy: 0,
        activity: 0,
        patience: 0,
        independence: 0
      }

      Object.values(answers).forEach((scoreStr: unknown) => {
        try {
          const scores = JSON.parse(String(scoreStr))
          combinedScores.empathy += scores.empathy || 0
          combinedScores.activity += scores.activity || 0
          combinedScores.patience += scores.patience || 0
          combinedScores.independence += scores.independence || 0
        } catch (e) {
          console.error("Failed to parse scores:", scoreStr)
        }
      })

      // 점수 정규화 (0-100 범위)
      const questionCount = PERSONALITY_QUESTIONS.length
      const normalizedScores = {
        empathy_score: Math.min(100, (combinedScores.empathy / (questionCount * 5)) * 100),
        activity_score: Math.min(100, (combinedScores.activity / (questionCount * 5)) * 100),
        patience_score: Math.min(100, (combinedScores.patience / (questionCount * 5)) * 100),
        independence_score: Math.min(100, (combinedScores.independence / (questionCount * 5)) * 100)
      }

      console.log("Calculated scores:", normalizedScores)
      console.log("Test answers:", answers)

      // sessionStorage에 저장 (로그인 후 API 호출 시 사용)
      sessionStorage.setItem("personality_scores", JSON.stringify(normalizedScores))
      sessionStorage.setItem("personality_answers", JSON.stringify(answers))

      // 🔧 결과 화면 표시 (OPTION 1: 규칙 기반 분석 사용)
      const analysis = generateAnalysis(normalizedScores)
      const recommendation = generateRecommendation(normalizedScores)

      setResults({
        ...normalizedScores,
        scores: normalizedScores,
        ai_analysis: analysis,
        recommendation: recommendation
      })

      console.log('[Personality Test] ✅ Analysis generated:', { analysis, recommendation })
    } catch (err) {
      console.error("성향 테스트 점수 계산 실패:", err)
      setError(err as Error)
      setIsTyping(false)
    } finally {
      setLoading(false)
    }
  }

  const progress = ((currentQuestionIdx + 1) / PERSONALITY_QUESTIONS.length) * 100

  // Results Screen
  if (results) {
    return (
      <div className="flex flex-col h-[100dvh] bg-[#E8FFFD] max-w-[430px] mx-auto overflow-hidden items-center justify-center p-6">
        <motion.div
          initial={{ scale: 0.9, opacity: 0, y: 20 }}
          animate={{ scale: 1, opacity: 1, y: 0 }}
          transition={{ type: "spring", duration: 0.5 }}
          className="w-full bg-white rounded-[30px] p-6 shadow-xl text-center"
        >
          <div className="w-16 h-16 bg-[#E8FFFD] rounded-full flex items-center justify-center mx-auto mb-5">
            <Sparkles className="w-8 h-8 text-[#18D4C6]" />
          </div>

          <h2 className="text-xl font-bold text-gray-900 mb-4">
            분석이 완료되었습니다!
          </h2>

          <div className="bg-[#E8FFFD] rounded-2xl p-5 mb-5">
            <p className="text-gray-600 font-medium mb-1 text-sm">추천 간병인 유형</p>
            <p className="text-lg text-[#18D4C6] font-bold">
              {results.recommendation || "따뜻하고 신뢰할 수 있는 간병인"}
            </p>
          </div>

          <div className="space-y-3 mb-6">
            <div className="flex justify-between items-center text-sm">
              <span className="text-gray-500 text-xs">공감 능력</span>
              <div className="flex items-center gap-2">
                <div className="w-24 h-1.5 bg-gray-100 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-blue-400 transition-all"
                    style={{ width: `${results.scores?.empathy_score || 0}%` }}
                  />
                </div>
                <span className="text-gray-600 font-medium w-6 text-xs text-right">
                  {results.scores?.empathy_score?.toFixed(0) || 0}
                </span>
              </div>
            </div>

            <div className="flex justify-between items-center text-sm">
              <span className="text-gray-500 text-xs">활동성</span>
              <div className="flex items-center gap-2">
                <div className="w-24 h-1.5 bg-gray-100 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-green-400 transition-all"
                    style={{ width: `${results.scores?.activity_score || 0}%` }}
                  />
                </div>
                <span className="text-gray-600 font-medium w-6 text-xs text-right">
                  {results.scores?.activity_score?.toFixed(0) || 0}
                </span>
              </div>
            </div>

            <div className="flex justify-between items-center text-sm">
              <span className="text-gray-500 text-xs">인내심</span>
              <div className="flex items-center gap-2">
                <div className="w-24 h-1.5 bg-gray-100 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-yellow-400 transition-all"
                    style={{ width: `${results.scores?.patience_score || 0}%` }}
                  />
                </div>
                <span className="text-gray-600 font-medium w-6 text-xs text-right">
                  {results.scores?.patience_score?.toFixed(0) || 0}
                </span>
              </div>
            </div>

            <div className="flex justify-between items-center text-sm">
              <span className="text-gray-500 text-xs">자립성</span>
              <div className="flex items-center gap-2">
                <div className="w-24 h-1.5 bg-gray-100 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-red-400 transition-all"
                    style={{ width: `${results.scores?.independence_score || 0}%` }}
                  />
                </div>
                <span className="text-gray-600 font-medium w-6 text-xs text-right">
                  {results.scores?.independence_score?.toFixed(0) || 0}
                </span>
              </div>
            </div>
          </div>

          <p className="text-xs text-gray-500 mb-6 leading-relaxed px-2">
            {results.ai_analysis || "분석이 준비 중입니다..."}
          </p>

          <div className="flex flex-col gap-3 w-full">
            <Button
              onClick={() => router.push("/login")}
              className="w-full h-11 bg-[#18D4C6] hover:bg-[#15b5a9] text-white font-semibold rounded-xl text-sm shadow-md shadow-[#18D4C6]/20 transition-all"
            >
              간병인 찾기
            </Button>
          </div>
        </motion.div>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-[100dvh] bg-white max-w-[430px] mx-auto overflow-hidden">
      <ErrorAlert error={error} onClose={() => setError(null)} />

      {/* Progress Bar Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-3 shrink-0">
        <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden mb-2">
          <motion.div
            className="h-full bg-[#18d4c6]"
            initial={{ width: 0 }}
            animate={{ width: `${progress}%` }}
            transition={{ duration: 0.3 }}
          />
        </div>
        <p className="text-xs text-gray-500 text-right">
          {currentQuestionIdx + 1} / {PERSONALITY_QUESTIONS.length}
        </p>
      </div>

      {/* Chat Area */}
      <div ref={chatContainerRef} className="flex-1 overflow-y-auto px-6 pb-4 flex flex-col justify-start min-h-0">
        <div className="h-12 shrink-0" /> {/* Top Spacer */}
        <div className="space-y-4">
          <AnimatePresence>
            {messages.map((msg, msgIndex) => (
              <motion.div key={msg.id} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}>
                {msg.type === "options" ? (
                  <div className="space-y-2">
                    {/* AI 질문 - 왼쪽 정렬, 회색 배경 */}
                    <div className="flex justify-start">
                      <div className="bg-[#f1f1f1] px-5 py-3 rounded-[20px] rounded-tl-none shadow-sm max-w-[85%]">
                        <p className="text-[#353535] text-sm leading-relaxed font-medium">{msg.text}</p>
                      </div>
                    </div>

                    {/* 답변 옵션 - 왼쪽 정렬, 민트색 배경 (현재 질문만 표시) */}
                    {msgIndex === messages.length - 1 && (
                      <motion.div className="flex flex-col gap-2 items-start w-full pl-2">
                        {msg.options?.map((option, idx) => (
                          <motion.button
                            key={idx}
                            onClick={() => handleOptionClick(option)}
                            whileHover={{ scale: 1.01 }}
                            whileTap={{ scale: 0.99 }}
                            disabled={isTyping || loading}
                            className="text-left px-5 py-3 rounded-[20px] bg-[#e7fffd] text-[#353535] text-sm font-medium transition-all disabled:opacity-50 hover:opacity-90 shadow-sm w-full max-w-[95%]"
                          >
                            {option.text}
                          </motion.button>
                        ))}
                      </motion.div>
                    )}
                  </div>
                ) : msg.isAi ? (
                  // AI 메시지 - 왼쪽 정렬, 회색 배경
                  <div className="flex justify-start">
                    <div className="bg-[#f1f1f1] px-5 py-3 rounded-[20px] rounded-tl-none shadow-sm max-w-[85%]">
                      <p className="text-[#353535] text-sm leading-relaxed font-medium">{msg.text}</p>
                    </div>
                  </div>
                ) : (
                  // 사용자 답변 - 오른쪽 정렬, 민트색 배경
                  <div className="flex justify-end">
                    <div className="bg-[#e7fffd] px-5 py-3 rounded-[20px] rounded-tr-none shadow-sm max-w-[85%]">
                      <p className="text-[#353535] text-sm leading-relaxed font-medium">{msg.text}</p>
                    </div>
                  </div>
                )}
              </motion.div>
            ))}
          </AnimatePresence>

          {(isTyping || loading) && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex justify-start"
            >
              <div className="bg-[#f1f1f1] px-5 py-3 rounded-[20px] rounded-tl-none flex gap-1.5 shadow-sm">
                <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0s" }} />
                <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0.2s" }} />
                <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0.4s" }} />
              </div>
            </motion.div>
          )}

          <div ref={chatContainerRef} />
        </div>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="bg-white/95 backdrop-blur-md pt-4 px-4 pb-4 shrink-0 border-t border-gray-100 flex items-center justify-center gap-3">
          <div className="animate-spin">
            <Sparkles className="w-5 h-5 text-primary" />
          </div>
          <p className="text-gray-600 font-medium">분석 중...</p>
        </div>
      )}
    </div>
  )
}
