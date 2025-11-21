import Link from "next/link"
import Image from "next/image"
import { Button } from "@/components/ui/button"

export default function LoginPage() {
    return (
        <div className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-br from-purple-50/30 via-pink-50/20 to-blue-50/30 max-w-[430px] mx-auto p-6">
            {/* Logo */}
            <div className="mb-12">
                <Image
                    src="/assets/logo.png"
                    alt="늘봄케어"
                    width={120}
                    height={40}
                    className="h-10 w-auto"
                />
            </div>

            {/* Welcome Text */}
            <div className="text-center mb-12">
                <h1 className="text-2xl font-bold text-gray-900 mb-2">
                    환영합니다!
                </h1>
                <p className="text-gray-600 text-sm">
                    간편하게 시작해보세요
                </p>
            </div>

            {/* KakaoTalk Login Button */}
            <div className="w-full max-w-sm">
                <Button
                    className="w-full h-14 bg-[#FEE500] hover:bg-[#FEE500]/90 text-[#000000] font-semibold rounded-xl flex items-center justify-center gap-3 shadow-lg"
                >
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                        <path d="M12 3C6.48 3 2 6.58 2 11C2 13.5 3.5 15.72 5.84 17.12L4.5 21.5L9.5 18.92C10.28 19.08 11.13 19.17 12 19.17C17.52 19.17 22 15.59 22 11.17C22 6.58 17.52 3 12 3Z" fill="currentColor" />
                    </svg>
                    카카오톡으로 시작하기
                </Button>

                <p className="text-xs text-gray-500 text-center mt-6">
                    로그인 시 <Link href="#" className="underline">이용약관</Link> 및{" "}
                    <Link href="#" className="underline">개인정보처리방침</Link>에 동의하게 됩니다.
                </p>
            </div>
        </div>
    )
}
