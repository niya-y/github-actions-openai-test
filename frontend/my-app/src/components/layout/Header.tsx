"use client"

import Link from "next/link"
import Image from "next/image"
import { usePathname } from "next/navigation"
import { Bell } from "lucide-react"
import { Button } from "@/components/ui/button"

export function Header() {
    const pathname = usePathname()

    if (pathname === "/onboarding" || pathname === "/personality-test" || pathname === "/login" || pathname === "/welcome" || pathname === "/schedule") {
        return null
    }

    // Home uses the transparent header style
    const isTransparentHeader = pathname === "/home"

    return (
        <header className={`z-50 w-full transition-colors duration-300 ${isTransparentHeader
            ? "fixed top-0 bg-transparent border-none"
            : "sticky top-0 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60"
            }`}>
            <div className="flex h-14 items-center justify-between px-4">
                <Link href="/home" className="flex items-center space-x-2">
                    {/* Logo Image */}
                    <Image
                        src={isTransparentHeader ? "/assets/logo_black.png" : "/assets/logo_color.png"}
                        alt="Neulbom Care"
                        width={32}
                        height={32}
                        className="h-8 w-auto object-contain"
                    />
                </Link>

                <div className="flex items-center gap-2">
                    <Button variant="ghost" size="icon" className={`rounded-full ${isTransparentHeader ? "hover:bg-white/20 text-white" : "hover:bg-gray-100/50 text-gray-600"}`}>
                        <Bell className="h-5 w-5" />
                    </Button>
                </div>
            </div>
        </header>
    )
}
