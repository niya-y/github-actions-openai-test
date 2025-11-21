"use client"

import Link from "next/link"
import Image from "next/image"
import { usePathname } from "next/navigation"
import { Bell } from "lucide-react"
import { Button } from "@/components/ui/button"

export function Header() {
    const pathname = usePathname()

    if (pathname === "/onboarding" || pathname === "/personality-test" || pathname === "/login") {
        return null
    }

    return (
        <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
            <div className="flex h-14 items-center justify-between px-4">
                <Link href="/onboarding" className="flex items-center space-x-2">
                    {/* Logo Image */}
                    <Image src="/assets/logo.png" alt="Neulbom Care" width={32} height={32} className="h-8 w-auto" />
                </Link>

                <div className="flex items-center gap-2">
                    <Button variant="ghost" size="icon" className="rounded-full">
                        <Bell className="h-5 w-5" />
                    </Button>
                </div>
            </div>
        </header>
    )
}
