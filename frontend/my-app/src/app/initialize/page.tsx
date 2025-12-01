'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Image from 'next/image'
import { motion } from 'framer-motion'

export default function InitializePage() {
    const router = useRouter()

    useEffect(() => {
        // Clear session storage to reset the flow
        sessionStorage.removeItem('guardian_id')
        sessionStorage.removeItem('patient_id')

        // Short delay for visual feedback, then redirect
        const timer = setTimeout(() => {
            router.push('/guardians')
        }, 2000) // Increased delay slightly to let animation play

        return () => clearTimeout(timer)
    }, [router])

    return (
        <div className="flex flex-col items-center justify-center h-screen bg-white font-['Pretendard']">
            <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5, ease: "easeOut" }}
                className="flex flex-col items-center"
            >
                <motion.div
                    animate={{
                        y: [0, -10, 0],
                        filter: ["drop-shadow(0px 4px 6px rgba(24, 212, 198, 0.2))", "drop-shadow(0px 8px 12px rgba(24, 212, 198, 0.3))", "drop-shadow(0px 4px 6px rgba(24, 212, 198, 0.2))"]
                    }}
                    transition={{
                        duration: 2,
                        repeat: Infinity,
                        ease: "easeInOut"
                    }}
                    className="w-64 h-64 relative mb-8"
                >
                    <Image
                        src="/assets/logo.png"
                        alt="Neulbom Care Logo"
                        fill
                        className="object-contain"
                        priority
                    />
                </motion.div>
                <motion.p
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.3, duration: 0.5 }}
                    className="text-[#555555] text-xl font-bold tracking-tight"
                >
                    새로운 매칭을 준비하고 있어요...
                </motion.p>
            </motion.div>
        </div>
    )
}
