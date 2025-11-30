"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import Image from "next/image"
import { motion } from "framer-motion"
import { Button } from "@/components/ui/button"
import { ArrowRight } from "lucide-react"
import { firstPrimary } from "@/app/colors"

export default function WelcomePage() {
    const router = useRouter()

    // 🔧 AUTH REDIRECT: Already logged-in users should go to /home
    useEffect(() => {
        const token = localStorage.getItem('access_token')
        if (token) {
            router.push('/home')
            console.log('[Welcome] Authenticated user → Redirecting to /home')
        }
    }, [router])

    return (
        <div className="flex flex-col min-h-screen bg-[#f9f7f2] relative overflow-hidden font-['Pretendard']">
            {/* Background Gradients */}
            <div className="absolute top-0 left-0 w-full h-full overflow-hidden z-0 pointer-events-none">
                <div className="absolute top-[-10%] right-[-20%] w-[500px] h-[500px] bg-[#f9f7f2] rounded-full blur-3xl" />
                <div className="absolute bottom-[-10%] left-[-20%] w-[500px] h-[500px] bg-[#f9f7f2] rounded-full blur-3xl" />
            </div>

            <div className="relative z-10 flex flex-col items-center justify-center flex-1 px-6 text-center">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8, ease: "easeOut" }}
                    className="mb-8"
                >
                    <div className="inline-flex items-center justify-center w-24 h-24 mb-8 rounded-[2rem] bg-gradient-to-br from-primary/10 to-secondary/10 shadow-sm">
                        <div className="relative w-20 h-20">
                            <Image
                                src="/assets/logo_color.png"
                                alt="Neulbom Care Logo"
                                fill
                                className="object-contain"
                            />
                        </div>
                    </div>
                    <h1 className="text-3xl font-bold text-gray-900 mb-4 leading-tight">
                        나에게 딱 맞는 <br />
                        <span className="text-black">
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
                    <Link
                        href="/personality-test"
                        className="inline-flex items-center justify-center w-full h-14 text-lg font-bold rounded-2xl shadow-lg hover:opacity-90 transition-opacity border-none text-white"
                        style={{ background: firstPrimary }}
                    >
                        시작하기 <ArrowRight className="ml-2 w-5 h-5" />
                    </Link>

                    <Button asChild variant="ghost" className="w-full text-gray-400 hover:text-gray-600 hover:bg-transparent">
                        <Link href="/home">
                            다음에 할게요
                        </Link>
                    </Button>
                </motion.div>
            </div>
        </div>
    )
}
