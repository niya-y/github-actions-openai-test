import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Activity, Calendar, Pill, User, ChevronRight } from "lucide-react"

export default function DashboardPage() {
    return (
        <div className="flex flex-col min-h-screen bg-gray-50 pb-20">
            {/* Header Section */}
            <div className="bg-white px-6 py-8 rounded-b-[2rem] shadow-sm mb-6">
                <div className="flex items-center justify-between mb-6">
                    <div>
                        <h1 className="text-2xl font-bold text-gray-900">안녕하세요, <br />보호자님</h1>
                        <p className="text-sm text-gray-500 mt-1">오늘도 평안한 하루 되세요.</p>
                    </div>
                    <div className="h-12 w-12 bg-gray-100 rounded-full flex items-center justify-center">
                        <User className="h-6 w-6 text-gray-400" />
                    </div>
                </div>

                {/* Main Status Card */}
                <Card className="bg-gradient-to-r from-primary to-teal-400 border-none text-white shadow-lg shadow-primary/30">
                    <CardContent className="p-6">
                        <div className="flex items-center justify-between mb-4">
                            <span className="text-white/80 text-sm font-medium">오늘의 컨디션</span>
                            <Activity className="h-5 w-5 text-white" />
                        </div>
                        <div className="flex items-end gap-2 mb-2">
                            <span className="text-4xl font-bold">좋음</span>
                            <span className="text-sm text-white/80 mb-1">안정적임</span>
                        </div>
                        <p className="text-xs text-white/70">
                            어제보다 혈압이 안정적입니다. (120/80)
                        </p>
                    </CardContent>
                </Card>
            </div>

            <div className="px-6 space-y-6">
                {/* Quick Actions */}
                <div className="grid grid-cols-2 gap-4">
                    <Card className="border-none shadow-sm bg-white hover:shadow-md transition-shadow">
                        <CardContent className="p-4 flex flex-col items-center justify-center py-6">
                            <div className="h-10 w-10 rounded-full bg-blue-50 flex items-center justify-center mb-3">
                                <Calendar className="h-5 w-5 text-blue-500" />
                            </div>
                            <span className="font-bold text-gray-900">일정 확인</span>
                            <span className="text-xs text-gray-500 mt-1">2개의 일정</span>
                        </CardContent>
                    </Card>
                    <Card className="border-none shadow-sm bg-white hover:shadow-md transition-shadow">
                        <CardContent className="p-4 flex flex-col items-center justify-center py-6">
                            <div className="h-10 w-10 rounded-full bg-orange-50 flex items-center justify-center mb-3">
                                <Pill className="h-5 w-5 text-orange-500" />
                            </div>
                            <span className="font-bold text-gray-900">복약 관리</span>
                            <span className="text-xs text-gray-500 mt-1">복용 완료</span>
                        </CardContent>
                    </Card>
                </div>

                {/* Caregiver Status */}
                <div>
                    <h2 className="text-lg font-bold text-gray-900 mb-4">담당 간병인</h2>
                    <Card className="border-none shadow-sm bg-white overflow-hidden">
                        <CardContent className="p-0">
                            <div className="p-4 flex items-center gap-4">
                                <div className="h-12 w-12 rounded-full bg-gray-200" />
                                <div className="flex-1">
                                    <h3 className="font-bold text-gray-900">김영희 간병인</h3>
                                    <p className="text-xs text-primary font-medium">근무 중 • 오후 6시 퇴근</p>
                                </div>
                                <Button size="icon" variant="ghost" className="rounded-full">
                                    <ChevronRight className="h-5 w-5 text-gray-400" />
                                </Button>
                            </div>
                            <div className="bg-gray-50 px-4 py-3 flex justify-between items-center text-xs text-gray-500">
                                <span>최근 업데이트: 10분 전</span>
                                <span className="text-primary font-medium">활동 기록 보기</span>
                            </div>
                        </CardContent>
                    </Card>
                </div>

                {/* Recent Notifications */}
                <div>
                    <h2 className="text-lg font-bold text-gray-900 mb-4">최근 알림</h2>
                    <div className="space-y-3">
                        <div className="flex items-start gap-3 bg-white p-4 rounded-2xl shadow-sm">
                            <div className="h-2 w-2 mt-2 rounded-full bg-red-500 shrink-0" />
                            <div>
                                <p className="text-sm font-medium text-gray-900">혈압 측정 완료</p>
                                <p className="text-xs text-gray-500 mt-1">오후 2:30 • 정상 범위입니다.</p>
                            </div>
                        </div>
                        <div className="flex items-start gap-3 bg-white p-4 rounded-2xl shadow-sm">
                            <div className="h-2 w-2 mt-2 rounded-full bg-gray-300 shrink-0" />
                            <div>
                                <p className="text-sm font-medium text-gray-900">점심 식사 완료</p>
                                <p className="text-xs text-gray-500 mt-1">오후 12:30 • 전량 섭취하셨습니다.</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}
