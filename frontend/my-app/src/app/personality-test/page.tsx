"use client"

import { useState, useEffect, useRef } from "react"
import { useRouter } from "next/navigation"
import { motion, AnimatePresence } from "framer-motion"
import { ChatBubble } from "@/components/ui/chat-bubble"
import { Button } from "@/components/ui/button"
import { Send, Sparkles } from "lucide-react"
import { Input } from "@/components/ui/input"

interface Message {
    id: number
    text: string
    isAi: boolean
}

export default function PersonalityTestPage() {
    const router = useRouter()
    const [messages, setMessages] = useState<Message[]>([])
    const [step, setStep] = useState(0)
    const [inputText, setInputText] = useState("")
    const [isTyping, setIsTyping] = useState(false)
    const messagesEndRef = useRef<HTMLDivElement>(null)
    const initialized = useRef(false)

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
    }

    useEffect(() => {
        scrollToBottom()
    }, [messages, isTyping])

    const addMessage = (text: string, isAi: boolean) => {
        setIsTyping(false)
        setMessages((prev) => [...prev, { id: Date.now(), text, isAi }])
    }

    // Initial greeting
    useEffect(() => {
        if (!initialized.current) {
            initialized.current = true
            setTimeout(() => setIsTyping(true), 0)
            setTimeout(() => {
                addMessage("안녕하세요! 늘봄케어 AI 매니저 늘보미입니다. ✨", true)
                setIsTyping(true)
                setTimeout(() => {
                    addMessage("어떤 분을 위한 간병인을 찾고 계신가요?", true)
                    setStep(1)
                }, 1000)
            }, 800)
        }
    }, [])

    const handleOptionClick = (option: string) => {
        addMessage(option, false)
        processNextStep(option)
    }

    const handleInputSubmit = (e: React.FormEvent) => {
        e.preventDefault()
        if (!inputText.trim()) return
        addMessage(inputText, false)
        setInputText("")
        processNextStep(inputText)
    }

    const processNextStep = (userResponse: string) => {
        setIsTyping(true)

        setTimeout(() => {
            if (step === 1) {
                addMessage(`${userResponse}님을 위한 케어시군요. 알겠습니다.`, true)
                setIsTyping(true)
                setTimeout(() => {
                    addMessage("가장 중요하게 생각하시는 부분은 무엇인가요?", true)
                    setStep(2)
                }, 1000)
            } else if (step === 2) {
                addMessage(`${userResponse}을(를) 최우선으로 고려하겠습니다.`, true)
                setIsTyping(true)
                setTimeout(() => {
                    addMessage("마지막으로, 특별히 원하시는 성향이 있으신가요?", true)
                    setStep(3)
                }, 1000)
            } else if (step === 3) {
                addMessage("모든 정보를 확인했습니다! 분석을 시작할게요. 🔍", true)
                setTimeout(() => {
                    setStep(4) // Show result
                }, 2000)
            }
        }, 1000)
    }

    return (
        <div className="flex flex-col h-screen bg-gradient-to-br from-purple-50/30 via-pink-50/20 to-blue-50/30 max-w-[430px] mx-auto overflow-hidden">
            {/* Chat Area */}
            <div className="flex-1 overflow-y-auto px-6 pt-6 flex flex-col justify-start min-h-0">
                <div className="space-y-2">
                    <AnimatePresence>
                        {messages.map((msg) => (
                            <ChatBubble key={msg.id} message={msg.text} isAi={msg.isAi} />
                        ))}
                    </AnimatePresence>

                    {isTyping && (
                        <motion.div
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="flex items-end gap-2 mb-3"
                        >
                            <div className="bg-white px-6 py-4 rounded-[24px] shadow-sm flex gap-1.5">
                                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0s" }} />
                                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0.2s" }} />
                                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0.4s" }} />
                            </div>
                        </motion.div>
                    )}

                    {/* Result Card */}
                    {step === 4 && (
                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.5 }}
                            className="mt-4 p-6 bg-white rounded-3xl shadow-lg text-center"
                        >
                            <div className="w-16 h-16 bg-gradient-to-br from-purple-100 to-pink-100 rounded-full flex items-center justify-center mx-auto mb-4">
                                <Sparkles className="w-8 h-8 text-primary" />
                            </div>
                            <h3 className="text-xl font-bold text-gray-900 mb-2">
                                &quot;따뜻하고 꼼꼼한&quot; <br />
                                간병인이 어울리시네요!
                            </h3>
                            <p className="text-sm text-gray-500 mb-6">
                                늘봄케어에서 딱 맞는 간병인을 <br />
                                지금 바로 연결해드릴게요.
                            </p>
                            <Button
                                onClick={() => router.push("/login")}
                                className="w-full h-12 text-lg font-bold rounded-xl shadow-lg shadow-primary/20 bg-primary hover:bg-primary/90"
                            >
                                간병인 연결하기
                            </Button>
                        </motion.div>
                    )}

                    <div ref={messagesEndRef} />
                </div>
            </div>

            {/* Input Area */}
            {step !== 4 && (
                <div className="bg-white/95 backdrop-blur-md p-4 flex-shrink-0 border-t border-gray-100">
                    {/* Suggestion text */}
                    <p className="text-xs text-gray-500 mb-3">AI에게 물어볼 내용 제안</p>

                    {/* Options for Step 1 */}
                    {step === 1 && !isTyping && (
                        <div className="flex gap-2 mb-3 overflow-x-auto pb-2 scrollbar-hide">
                            {["부모님", "배우자", "본인", "조부모님"].map((opt) => (
                                <Button
                                    key={opt}
                                    variant="outline"
                                    className="rounded-full border-gray-200 bg-white text-gray-700 hover:bg-gray-50 hover:border-gray-300 whitespace-nowrap px-5 py-2 text-sm shadow-sm"
                                    onClick={() => handleOptionClick(opt)}
                                >
                                    {opt}
                                </Button>
                            ))}
                        </div>
                    )}

                    {/* Options for Step 2 */}
                    {step === 2 && !isTyping && (
                        <div className="flex gap-2 mb-3 overflow-x-auto pb-2 scrollbar-hide">
                            {["전문성 (자격증)", "따뜻한 성격", "가까운 거리", "저렴한 비용"].map((opt) => (
                                <Button
                                    key={opt}
                                    variant="outline"
                                    className="rounded-full border-gray-200 bg-white text-gray-700 hover:bg-gray-50 hover:border-gray-300 whitespace-nowrap px-5 py-2 text-sm shadow-sm"
                                    onClick={() => handleOptionClick(opt)}
                                >
                                    {opt}
                                </Button>
                            ))}
                        </div>
                    )}

                    {/* Options for Step 3 */}
                    {step === 3 && !isTyping && (
                        <div className="flex gap-2 mb-3 overflow-x-auto pb-2 scrollbar-hide">
                            {["조용한 분", "대화가 많은 분", "힘이 센 분", "꼼꼼한 분"].map((opt) => (
                                <Button
                                    key={opt}
                                    variant="outline"
                                    className="rounded-full border-gray-200 bg-white text-gray-700 hover:bg-gray-50 hover:border-gray-300 whitespace-nowrap px-5 py-2 text-sm shadow-sm"
                                    onClick={() => handleOptionClick(opt)}
                                >
                                    {opt}
                                </Button>
                            ))}
                        </div>
                    )}

                    <form onSubmit={handleInputSubmit} className="flex gap-2">
                        <Input
                            value={inputText}
                            onChange={(e) => setInputText(e.target.value)}
                            placeholder="프로젝트에 대해 무엇이든 물어보세요..."
                            className="rounded-full border-gray-200 bg-gray-50 focus:bg-white transition-colors text-sm"
                        />
                        <Button type="submit" size="icon" className="rounded-full bg-primary hover:bg-primary/90 shrink-0" disabled={!inputText.trim() || isTyping}>
                            <Send className="w-4 h-4" />
                        </Button>
                    </form>
                </div>
            )}
        </div>
    )
}
