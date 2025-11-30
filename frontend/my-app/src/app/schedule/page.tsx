import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { MapPin, ChevronLeft, ChevronRight } from "lucide-react"

export default function SchedulePage() {
    return (
        <div className="flex flex-col min-h-screen bg-gray-50 pb-20">
            <div className="px-6 py-8">
                <h1 className="text-2xl font-bold text-gray-900 mb-6">일정 관리</h1>

                {/* Calendar View Placeholder */}
                <Card className="border-none shadow-sm bg-white mb-6 overflow-hidden">
                    <CardContent className="p-4">
                        <div className="flex items-center justify-between mb-4">
                            <span className="font-bold text-lg">2025년 11월</span>
                            <div className="flex gap-2">
                                <button className="p-1 hover:bg-gray-100 rounded-full"><ChevronLeft className="h-5 w-5" /></button>
                                <button className="p-1 hover:bg-gray-100 rounded-full"><ChevronRight className="h-5 w-5" /></button>
                            </div>
                        </div>
                        <div className="grid grid-cols-7 gap-2 text-center text-sm mb-2">
                            <span className="text-red-500">일</span>
                            <span>월</span>
                            <span>화</span>
                            <span>수</span>
                            <span>목</span>
                            <span>금</span>
                            <span className="text-blue-500">토</span>
                        </div>
                        <div className="grid grid-cols-7 gap-2 text-center text-sm">
                            {/* Mock Calendar Days */}
                            <span className="text-gray-300">29</span>
                            <span className="text-gray-300">30</span>
                            <span>1</span>
                            <span>2</span>
                            <span>3</span>
                            <span>4</span>
                            <span>5</span>
                            <span>6</span>
                            <span>7</span>
                            <span>8</span>
                            <span>9</span>
                            <span>10</span>
                            <span>11</span>
                            <span>12</span>
                            <span>13</span>
                            <span>14</span>
                            <span>15</span>
                            <span>16</span>
                            <span>17</span>
                            <span>18</span>
                            <span>19</span>
                            <span className="bg-primary text-white rounded-full w-8 h-8 flex items-center justify-center mx-auto">20</span>
                            <span>21</span>
                            <span>22</span>
                            <span>23</span>
                            <span>24</span>
                            <span>25</span>
                            <span>26</span>
                            <span>27</span>
                            <span>28</span>
                            <span>29</span>
                            <span>30</span>
                        </div>
                    </CardContent>
                </Card>

                <div className="space-y-4">
                    <h2 className="text-lg font-bold text-gray-900">오늘의 일정</h2>

                    {/* Schedule Item: Completed */}
                    <div className="flex gap-4">
                        <div className="flex flex-col items-center">
                            <div className="w-2 h-2 rounded-full bg-primary mt-2" />
                            <div className="w-0.5 h-full bg-gray-200 my-1" />
                        </div>
                        <Card className="flex-1 border-none shadow-sm bg-white opacity-60">
                            <CardContent className="p-4">
                                <div className="flex justify-between items-start mb-2">
                                    <Badge variant="outline" className="text-gray-500 border-gray-200">완료</Badge>
                                    <span className="text-xs text-gray-400">08:00 AM</span>
                                </div>
                                <h3 className="font-bold text-gray-900 line-through">아침 식사 및 복약</h3>
                                <p className="text-xs text-gray-500 mt-1">담당: 김영희 간병인</p>
                            </CardContent>
                        </Card>
                    </div>

                    {/* Schedule Item: In Progress */}
                    <div className="flex gap-4">
                        <div className="flex flex-col items-center">
                            <div className="w-2 h-2 rounded-full bg-primary mt-2 ring-4 ring-primary/20" />
                            <div className="w-0.5 h-full bg-gray-200 my-1" />
                        </div>
                        <Card className="flex-1 border-none shadow-md bg-white border-l-4 border-l-primary">
                            <CardContent className="p-4">
                                <div className="flex justify-between items-start mb-2">
                                    <Badge className="bg-primary hover:bg-primary/90">진행 중</Badge>
                                    <span className="text-xs text-primary font-bold">02:00 PM</span>
                                </div>
                                <h3 className="font-bold text-gray-900">재활 운동 치료</h3>
                                <div className="flex items-center gap-2 mt-2 text-xs text-gray-500">
                                    <MapPin className="h-3 w-3" />
                                    <span>서울재활병원</span>
                                </div>
                            </CardContent>
                        </Card>
                    </div>

                    {/* Schedule Item: Upcoming */}
                    <div className="flex gap-4">
                        <div className="flex flex-col items-center">
                            <div className="w-2 h-2 rounded-full bg-gray-300 mt-2" />
                        </div>
                        <Card className="flex-1 border-none shadow-sm bg-white">
                            <CardContent className="p-4">
                                <div className="flex justify-between items-start mb-2">
                                    <Badge variant="secondary" className="bg-gray-100 text-gray-500 hover:bg-gray-200">예정</Badge>
                                    <span className="text-xs text-gray-500">06:00 PM</span>
                                </div>
                                <h3 className="font-bold text-gray-900">저녁 식사 준비</h3>
                                <p className="text-xs text-gray-500 mt-1">저염식 식단</p>
                            </CardContent>
                        </Card>
                    </div>
                </div>
            </div>
        </div>
    )
}
