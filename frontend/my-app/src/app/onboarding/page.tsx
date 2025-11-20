"use client"

import Link from "next/link"
import { motion } from "framer-motion"
import { Button } from "@/components/ui/button"
import { ArrowRight, Sparkles } from "lucide-react"

export default function OnboardingPage() {
    return (
        <div className="flex flex-col min-h-screen bg-white relative overflow-hidden">
            {/* Background Gradients */}
            <div className="absolute top-0 left-0 w-full h-full overflow-hidden z-0 pointer-events-none">
                <div className="absolute top-[-10%] right-[-20%] w-[500px] h-[500px] bg-purple-200/40 rounded-full blur-3xl" />
                <div className="absolute bottom-[-10%] left-[-20%] w-[500px] h-[500px] bg-pink-200/40 rounded-full blur-3xl" />
            </div>

            <div className="relative z-10 flex flex-col items-center justify-center flex-1 px-6 text-center">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8, ease: "easeOut" }}
                    className="mb-8"
                >
                    <div className="inline-flex items-center justify-center w-16 h-16 mb-6 rounded-2xl bg-gradient-to-br from-primary/20 to-secondary/20 shadow-inner">
                        <Sparkles className="w-8 h-8 text-primary" />
                    </div>
                    <h1 className="text-3xl font-bold text-gray-900 mb-4 leading-tight">
                        나에게 딱 맞는 <br />
                        <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-secondary">
                            AI 간병인 매칭
                        </span>
                    </h1>
                    <p className="text-gray-500 leading-relaxed max-w-[280px] mx-auto">
                        몇 가지 간단한 질문으로 <br />
                        가장 잘 맞는 간병인을 찾아드릴게요.
                    </p>
                </motion.div>

                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8, delay: 0.2, ease: "easeOut" }}
                    className="w-full max-w-[300px] space-y-4"
                >
                    <Button asChild size="lg" className="w-full h-14 text-lg font-bold rounded-2xl shadow-lg shadow-primary/20 bg-gradient-to-r from-primary to-teal-400 hover:opacity-90 transition-opacity border-none">
                        <Link href="/personality-test">
                            시작하기 <ArrowRight className="ml-2 w-5 h-5" />
                        </Link>
                    </Button>

                    <Button asChild variant="ghost" className="w-full text-gray-400 hover:text-gray-600 hover:bg-transparent">
                        <Link href="/">
                            다음에 할게요
                        </Link>
                    </Button>
                </motion.div>
            </div>
        </div>
    )
}
