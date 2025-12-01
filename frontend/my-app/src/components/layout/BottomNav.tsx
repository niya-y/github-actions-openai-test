"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import Image from "next/image"
import { cn } from "@/utils/cn"

export function BottomNav() {
    const pathname = usePathname()

    // Hide on onboarding, login, welcome, and specific sub-pages where nav might distract
    // Show on main tabs: /home, /schedule, /mypage-message, /mypage-dashboard
    if (pathname === "/" || pathname === "/onboarding" || pathname === "/personality-test" || pathname === "/login" || pathname === "/welcome") {
        return null
    }

    const navItems = [
        { href: "/home", label: "홈", icon: "/assets/nav_home.svg" },
        { href: "/schedule", label: "일정 관리", icon: "/assets/nav_cal.svg" },
        { href: "/mypage-message", label: "대화", icon: "/assets/nav_talk.svg" },
        { href: "/mypage-dashboard", label: "내 정보", icon: "/assets/nav_my.svg" },
    ]

    return (
        <nav className="fixed bottom-0 left-0 right-0 z-50 bg-white border-t border-gray-100 pb-safe">
            <div className="flex h-[60px] items-center justify-around px-4">
                {navItems.map((item) => {
                    const isActive = pathname === item.href
                    return (
                        <Link
                            key={item.href}
                            href={item.href}
                            className={cn(
                                "flex flex-col items-center justify-center space-y-1 w-full h-full",
                                isActive ? "opacity-100" : "opacity-50 hover:opacity-75"
                            )}
                        >
                            <Image
                                src={item.icon}
                                alt={item.label}
                                width={24}
                                height={24}
                                className="w-6 h-6"
                            />
                            <span className={cn(
                                "text-[10px] font-medium",
                                isActive ? "text-[#353535]" : "text-[#828282]"
                            )}>
                                {item.label}
                            </span>
                        </Link>
                    )
                })}
            </div>
        </nav>
    )
}
