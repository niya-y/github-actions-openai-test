"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { Home, Search, Calendar, User } from "lucide-react"
import { cn } from "@/utils/cn"

export function BottomNav() {
    const pathname = usePathname()

    if (pathname === "/onboarding" || pathname === "/personality-test" || pathname === "/login") {
        return null
    }

    const navItems = [
        { href: "/onboarding", label: "홈", icon: Home },
        { href: "/matching", label: "매칭", icon: Search },
        { href: "/schedule", label: "일정", icon: Calendar },
        { href: "/dashboard", label: "내 정보", icon: User },
    ]

    return (
        <nav className="fixed bottom-0 left-0 right-0 z-50 border-t bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 md:hidden">
            <div className="flex h-16 items-center justify-around px-4">
                {navItems.map((item) => {
                    const isActive = pathname === item.href
                    return (
                        <Link
                            key={item.href}
                            href={item.href}
                            className={cn(
                                "flex flex-col items-center justify-center space-y-1",
                                isActive ? "text-primary" : "text-muted-foreground hover:text-primary/50"
                            )}
                        >
                            <item.icon className={cn("h-6 w-6", isActive && "fill-current")} />
                            <span className="text-[10px] font-medium">{item.label}</span>
                        </Link>
                    )
                })}
            </div>
        </nav>
    )
}
