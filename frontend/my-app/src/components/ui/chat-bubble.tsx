"use client"

import { motion } from "framer-motion"
import { cn } from "@/utils/cn"

interface ChatBubbleProps {
    message: string
    isAi?: boolean
    delay?: number
}

export function ChatBubble({ message, isAi = false, delay = 0 }: ChatBubbleProps) {
    return (
        <motion.div
            initial={{ opacity: 0, y: 10, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            transition={{ duration: 0.4, delay: delay, ease: "easeOut" }}
            className={cn(
                "flex w-full mb-3",
                isAi ? "justify-start" : "justify-end"
            )}
        >
            <div className={cn("flex max-w-[75%]", isAi ? "flex-row" : "flex-row-reverse")}>
                <div
                    className={cn(
                        "px-6 py-4 text-[15px] leading-relaxed",
                        isAi
                            ? "bg-white rounded-[24px] text-gray-800 shadow-sm"
                            : "bg-gradient-to-br from-blue-50 to-purple-50 rounded-[24px] text-gray-800 border border-blue-100"
                    )}
                >
                    {message}
                </div>
            </div>
        </motion.div>
    )
}
