"use client"

import React from "react"
import { useRouter } from "next/navigation"
import { ChevronLeft, Bell, ChevronDown, ChevronRight, Check, Image as ImageIcon, Plus } from "lucide-react"
import { cn } from "@/utils/cn"

export default function SchedulePage() {
    const router = useRouter()

    return (
        <div className="min-h-screen bg-gray-50 pb-[80px]">
            {/* Header */}
            <header className="sticky top-0 z-10 bg-white px-4 h-[60px] flex items-center justify-between border-b border-gray-100">
                <button
                    onClick={() => router.back()}
                    className="p-2 -ml-2 text-gray-600"
                    aria-label="Go back"
                >
                    <ChevronLeft className="w-6 h-6" />
                </button>

                <h1 className="text-lg font-semibold text-gray-800">일정 관리</h1>

                <button
                    className="p-2 -mr-2 text-gray-600"
                    aria-label="Notifications"
                >
                    <Bell className="w-6 h-6" />
                </button>
            </header>

            <main className="px-4 py-6 space-y-6">
                {/* User Selector */}
                <button className="w-full bg-[#18d4c6] text-white rounded-xl p-4 flex items-center justify-center gap-2 shadow-sm">
                    <span className="text-lg font-bold">김철수님</span>
                    <ChevronDown className="w-5 h-5" />
                </button>

                {/* Calendar Section */}
                <div className="bg-white rounded-2xl p-5 shadow-sm">
                    <div className="flex items-center justify-between mb-4">
                        <h2 className="text-lg font-bold text-gray-900">2025년 12월</h2>
                        <div className="flex gap-4 text-gray-400">
                            <ChevronLeft className="w-5 h-5" />
                            <ChevronRight className="w-5 h-5" />
                        </div>
                    </div>

                    <div className="grid grid-cols-7 gap-1 text-center mb-2">
                        {["일", "월", "화", "수", "목", "금", "토"].map((day) => (
                            <div key={day} className="text-xs text-gray-500 font-medium">
                                {day}
                            </div>
                        ))}
                    </div>

                    <div className="grid grid-cols-7 gap-1 text-center">
                        {[30, 1, 2, 3, 4, 5, 6].map((date, i) => {
                            const isToday = date === 5;
                            const isSelected = date === 6; // Just mimicking the green dot on 6th too from image? Or maybe 5 is today.
                            // Image shows 5 and 6 have green dots. 5 is bold.

                            return (
                                <div key={i} className="flex flex-col items-center gap-1 py-1">
                                    <span className={cn(
                                        "text-sm font-medium",
                                        isToday ? "text-gray-900 font-bold" : "text-gray-500"
                                    )}>
                                        {date}
                                    </span>
                                    {(date === 5 || date === 6) && (
                                        <div className="w-1.5 h-1.5 rounded-full bg-[#18d4c6]" />
                                    )}
                                </div>
                            )
                        })}
                    </div>

                    {/* Drag handle */}
                    <div className="flex justify-center mt-2">
                        <div className="w-10 h-1 bg-gray-200 rounded-full" />
                    </div>
                </div>

                {/* Daily Plan Title */}
                <div>
                    <p className="text-sm text-gray-500 mb-1">12월 5일</p>
                    <h2 className="text-xl font-bold text-gray-900">오늘의 돌봄 계획</h2>
                </div>

                {/* Task List */}
                <div className="space-y-4">

                    {/* Completed Task */}
                    <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100 flex items-start gap-4">
                        <div className="w-6 h-6 rounded-full bg-[#18d4c6] flex items-center justify-center shrink-0 mt-0.5">
                            <Check className="w-4 h-4 text-white" />
                        </div>
                        <div>
                            <h3 className="text-base font-bold text-gray-600">아침 약 복용</h3>
                            <p className="text-sm text-gray-400 mt-0.5">08:00 / 식후 30분</p>
                        </div>
                    </div>

                    {/* Pending Task with Photo Button */}
                    <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100 flex gap-4 relative overflow-hidden">
                        <div className="absolute left-0 top-0 bottom-0 w-1.5 bg-[#18d4c6]" />
                        <div className="w-6 h-6 rounded-full border-2 border-gray-300 shrink-0 mt-0.5 ml-2" />
                        <div className="flex-1">
                            <h3 className="text-base font-bold text-gray-900">점심식사</h3>
                            <p className="text-sm text-gray-500 mt-0.5">12:30 / 일반식(저염)</p>

                            <button className="mt-3 w-full max-w-[160px] h-10 border border-gray-200 rounded-lg flex items-center justify-center gap-2 text-gray-500 hover:bg-gray-50 transition-colors">
                                <ImageIcon className="w-4 h-4" />
                                <span className="text-xs font-medium">사진보기</span>
                            </button>
                        </div>
                    </div>

                    {/* Pending Task with FAB */}
                    <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100 flex items-center justify-between">
                        <div className="flex items-start gap-4">
                            <div className="w-6 h-6 rounded-full border-2 border-gray-300 shrink-0 mt-0.5" />
                            <div>
                                <h3 className="text-base font-bold text-gray-900">산책 및 말벗</h3>
                                <p className="text-sm text-gray-500 mt-0.5">15:00 / 날씨 맑음</p>
                            </div>
                        </div>

                        <button className="w-10 h-10 bg-[#18d4c6] rounded-full flex items-center justify-center text-white shadow-md hover:bg-[#15bkb0] transition-colors">
                            <Plus className="w-6 h-6" />
                        </button>
                    </div>

                </div>
            </main>
        </div>
    )
}
