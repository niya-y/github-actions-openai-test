import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { CheckCircle, AlertCircle, Clock, Pill } from "lucide-react"

export default function MedicationPage() {
    return (
        <div className="flex flex-col min-h-screen bg-gray-50 pb-20">
            <div className="px-6 py-8">
                <h1 className="text-2xl font-bold text-gray-900 mb-6">복약 관리</h1>

                {/* Alert Section */}
                <div className="bg-red-50 border border-red-100 rounded-2xl p-4 mb-6 flex gap-3">
                    <AlertCircle className="h-5 w-5 text-red-500 shrink-0 mt-0.5" />
                    <div>
                        <h3 className="text-sm font-bold text-red-700">주의사항</h3>
                        <p className="text-xs text-red-600 mt-1 leading-relaxed">
                            혈압약과 자몽 주스를 함께 복용하지 마세요. 약효에 영향을 줄 수 있습니다.
                        </p>
                    </div>
                </div>

                {/* Today's Status */}
                <div className="mb-8">
                    <div className="flex justify-between items-end mb-4">
                        <h2 className="text-lg font-bold text-gray-900">오늘의 복약</h2>
                        <span className="text-xs text-gray-500">2/3 완료</span>
                    </div>

                    <div className="space-y-3">
                        <Card className="border-none shadow-sm bg-white opacity-60">
                            <CardContent className="p-4 flex items-center justify-between">
                                <div className="flex items-center gap-4">
                                    <div className="h-10 w-10 rounded-full bg-green-100 flex items-center justify-center">
                                        <CheckCircle className="h-5 w-5 text-green-600" />
                                    </div>
                                    <div>
                                        <h3 className="font-bold text-gray-900 line-through">아침 식후 30분</h3>
                                        <p className="text-xs text-gray-500">혈압약, 비타민</p>
                                    </div>
                                </div>
                                <span className="text-xs font-medium text-gray-400">08:30 완료</span>
                            </CardContent>
                        </Card>

                        <Card className="border-none shadow-sm bg-white opacity-60">
                            <CardContent className="p-4 flex items-center justify-between">
                                <div className="flex items-center gap-4">
                                    <div className="h-10 w-10 rounded-full bg-green-100 flex items-center justify-center">
                                        <CheckCircle className="h-5 w-5 text-green-600" />
                                    </div>
                                    <div>
                                        <h3 className="font-bold text-gray-900 line-through">점심 식후 30분</h3>
                                        <p className="text-xs text-gray-500">당뇨약</p>
                                    </div>
                                </div>
                                <span className="text-xs font-medium text-gray-400">13:00 완료</span>
                            </CardContent>
                        </Card>

                        <Card className="border-none shadow-md bg-white border-l-4 border-l-primary">
                            <CardContent className="p-4 flex items-center justify-between">
                                <div className="flex items-center gap-4">
                                    <div className="h-10 w-10 rounded-full bg-blue-50 flex items-center justify-center">
                                        <Clock className="h-5 w-5 text-primary" />
                                    </div>
                                    <div>
                                        <h3 className="font-bold text-gray-900">저녁 식후 30분</h3>
                                        <p className="text-xs text-gray-500">혈압약, 칼슘제</p>
                                    </div>
                                </div>
                                <Badge variant="secondary" className="bg-blue-50 text-primary hover:bg-blue-100">예정</Badge>
                            </CardContent>
                        </Card>
                    </div>
                </div>

                {/* Medication List */}
                <div>
                    <h2 className="text-lg font-bold text-gray-900 mb-4">복용 중인 약물</h2>
                    <div className="grid grid-cols-2 gap-3">
                        <Card className="border-none shadow-sm bg-white">
                            <CardContent className="p-4 flex flex-col items-center text-center">
                                <div className="h-12 w-12 rounded-2xl bg-pink-50 flex items-center justify-center mb-3">
                                    <Pill className="h-6 w-6 text-pink-500" />
                                </div>
                                <h3 className="font-bold text-gray-900 text-sm">암로디핀</h3>
                                <p className="text-xs text-gray-500 mt-1">혈압약 • 1일 2회</p>
                            </CardContent>
                        </Card>
                        <Card className="border-none shadow-sm bg-white">
                            <CardContent className="p-4 flex flex-col items-center text-center">
                                <div className="h-12 w-12 rounded-2xl bg-purple-50 flex items-center justify-center mb-3">
                                    <Pill className="h-6 w-6 text-purple-500" />
                                </div>
                                <h3 className="font-bold text-gray-900 text-sm">메트포르민</h3>
                                <p className="text-xs text-gray-500 mt-1">당뇨약 • 1일 1회</p>
                            </CardContent>
                        </Card>
                    </div>
                </div>
            </div>
        </div>
    )
}
