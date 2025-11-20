"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Loader2, Star, MapPin, Clock, CheckCircle, User, Search } from "lucide-react"

interface MatchResult {
    name: string
    age: number
    experience: string
    rating: number
    location: string
    specialties: string[]
    matchScore: number
    tags: string[]
}

export default function MatchingPage() {
    const [step, setStep] = useState(1)
    const [loading, setLoading] = useState(false)
    const [result, setResult] = useState<MatchResult | null>(null)

    const handleSearch = (e: React.FormEvent) => {
        e.preventDefault()
        setLoading(true)
        // Simulate AI processing
        setTimeout(() => {
            setLoading(false)
            setStep(2)
            setResult({
                name: "김영희",
                age: 54,
                experience: "10년",
                rating: 4.9,
                location: "서울시 강남구",
                specialties: ["치매 케어", "재활 운동", "식사 보조"],
                matchScore: 98,
                tags: ["자격증 보유", "비흡연", "차량 소지"],
            })
        }, 2000)
    }

    return (
        <div className="flex flex-col min-h-screen bg-gray-50 pb-20">
            <div className="px-6 py-8">
                <div className="space-y-2 mb-8">
                    <h1 className="text-2xl font-bold text-gray-900">
                        {step === 1 ? "간병인 찾기" : "매칭 결과"}
                    </h1>
                    <p className="text-sm text-gray-500">
                        {step === 1
                            ? "AI가 환자분에게 딱 맞는 간병인을 찾아드립니다."
                            : "AI 분석 결과, 가장 적합한 간병인입니다."}
                    </p>
                </div>

                {step === 1 && (
                    <Card className="border-none shadow-lg bg-white rounded-2xl overflow-hidden">
                        <div className="h-2 bg-primary w-full" />
                        <CardContent className="p-6">
                            <form onSubmit={handleSearch} className="space-y-6">
                                <div className="space-y-4">
                                    <div className="space-y-2">
                                        <label className="text-sm font-semibold text-gray-700">환자 성함</label>
                                        <div className="relative">
                                            <User className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                                            <Input placeholder="홍길동" required className="pl-10 bg-gray-50 border-gray-200 focus:bg-white transition-colors h-12 rounded-xl" />
                                        </div>
                                    </div>
                                    <div className="space-y-2">
                                        <label className="text-sm font-semibold text-gray-700">나이</label>
                                        <Input type="number" placeholder="75" required className="bg-gray-50 border-gray-200 focus:bg-white transition-colors h-12 rounded-xl" />
                                    </div>
                                    <div className="space-y-2">
                                        <label className="text-sm font-semibold text-gray-700">거주 지역</label>
                                        <div className="relative">
                                            <MapPin className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                                            <Input placeholder="서울시 강남구" required className="pl-10 bg-gray-50 border-gray-200 focus:bg-white transition-colors h-12 rounded-xl" />
                                        </div>
                                    </div>
                                    <div className="space-y-2">
                                        <label className="text-sm font-semibold text-gray-700">필요한 케어</label>
                                        <Input placeholder="예: 치매, 거동 불편" required className="bg-gray-50 border-gray-200 focus:bg-white transition-colors h-12 rounded-xl" />
                                    </div>
                                </div>

                                <Button type="submit" className="w-full h-14 text-lg font-bold rounded-xl shadow-lg shadow-primary/20" disabled={loading}>
                                    {loading ? (
                                        <>
                                            <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                                            분석 중...
                                        </>
                                    ) : (
                                        <>
                                            <Search className="mr-2 h-5 w-5" />
                                            AI 매칭 시작하기
                                        </>
                                    )}
                                </Button>
                            </form>
                        </CardContent>
                    </Card>
                )}

                {step === 2 && result && (
                    <div className="space-y-6">
                        <Card className="border-none shadow-xl bg-white rounded-3xl overflow-hidden relative">
                            <div className="absolute top-0 right-0 p-6">
                                <div className="flex flex-col items-center">
                                    <span className="text-xs font-bold text-primary uppercase tracking-wider">Match Score</span>
                                    <span className="text-4xl font-black text-primary">{result.matchScore}%</span>
                                </div>
                            </div>

                            <CardHeader className="pt-8 pb-4">
                                <Badge className="w-fit mb-4 bg-primary/10 text-primary hover:bg-primary/20 border-none px-3 py-1">
                                    AI 추천 1위
                                </Badge>
                                <CardTitle className="text-3xl font-bold text-gray-900">{result.name} <span className="text-lg font-normal text-gray-500">간병인</span></CardTitle>
                                <div className="flex items-center space-x-1 text-yellow-400 mt-2">
                                    <Star className="h-5 w-5 fill-current" />
                                    <span className="text-lg font-bold text-gray-900 ml-1">{result.rating}</span>
                                    <span className="text-sm text-gray-400 ml-2">경력 {result.experience}</span>
                                </div>
                            </CardHeader>

                            <CardContent className="space-y-6">
                                <div className="flex gap-4 text-sm text-gray-600 bg-gray-50 p-4 rounded-2xl">
                                    <div className="flex items-center">
                                        <MapPin className="mr-2 h-4 w-4 text-primary" />
                                        {result.location}
                                    </div>
                                    <div className="flex items-center">
                                        <Clock className="mr-2 h-4 w-4 text-primary" />
                                        즉시 가능
                                    </div>
                                </div>

                                <div>
                                    <h4 className="mb-3 text-sm font-bold text-gray-900">전문 분야</h4>
                                    <div className="flex flex-wrap gap-2">
                                        {result.specialties.map((s: string) => (
                                            <Badge key={s} variant="secondary" className="bg-secondary/10 text-secondary-foreground hover:bg-secondary/20 border-none px-3 py-1.5 text-sm">
                                                {s}
                                            </Badge>
                                        ))}
                                    </div>
                                </div>

                                <div>
                                    <h4 className="mb-3 text-sm font-bold text-gray-900">특이 사항</h4>
                                    <div className="space-y-2">
                                        {result.tags.map((t: string) => (
                                            <div key={t} className="flex items-center text-sm text-gray-600">
                                                <div className="h-6 w-6 rounded-full bg-green-50 flex items-center justify-center mr-3">
                                                    <CheckCircle className="h-4 w-4 text-green-500" />
                                                </div>
                                                {t}
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </CardContent>

                            <CardFooter className="pb-8 pt-4">
                                <div className="grid grid-cols-2 gap-4 w-full">
                                    <Button variant="outline" className="h-12 rounded-xl border-gray-200" onClick={() => setStep(1)}>
                                        다시 찾기
                                    </Button>
                                    <Button className="h-12 rounded-xl shadow-lg shadow-primary/20">
                                        매칭 신청
                                    </Button>
                                </div>
                            </CardFooter>
                        </Card>
                    </div>
                )}
            </div>
        </div>
    )
}
