import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ArrowRight, Calendar, Pill, ShieldCheck, Star } from "lucide-react"

export default function Home() {
  return (
    <div className="flex flex-col min-h-screen bg-gray-50 pb-20">
      {/* Hero Section */}
      <section className="relative w-full py-12 px-6 bg-gradient-to-br from-primary/10 to-secondary/10 rounded-b-[2rem] overflow-hidden">
        <div className="absolute top-0 right-0 -mt-10 -mr-10 w-64 h-64 bg-primary/20 rounded-full blur-3xl" />
        <div className="absolute bottom-0 left-0 -mb-10 -ml-10 w-64 h-64 bg-secondary/20 rounded-full blur-3xl" />

        <div className="relative z-10 flex flex-col items-start space-y-4">
          <Badge variant="secondary" className="bg-white/80 text-primary backdrop-blur-sm shadow-sm">
            2025 새싹 해커톤 Blue Donut Lab
          </Badge>
          <h1 className="text-3xl font-bold tracking-tight text-gray-900 leading-tight">
            데이터로 선택하는 <br />
            <span className="text-primary">안심 간병, 늘봄케어</span>
          </h1>
          <p className="text-gray-600 text-sm leading-relaxed max-w-[300px]">
            AI가 분석한 최적의 간병인을 3분 만에 매칭해드립니다.
            가족은 안심하고, 환자는 편안한 케어를 경험하세요.
          </p>
          <div className="pt-4 w-full">
            <Button asChild size="lg" className="w-full rounded-xl shadow-lg shadow-primary/20 bg-primary hover:bg-primary/90 text-white font-bold h-12">
              <Link href="/matching">
                간병인 찾기 <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
          </div>
        </div>
      </section>

      {/* Quick Menu */}
      <section className="px-6 -mt-8 relative z-20">
        <div className="grid grid-cols-3 gap-4">
          <Link href="/matching" className="flex flex-col items-center p-4 bg-white rounded-2xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
            <div className="p-3 bg-blue-50 rounded-full mb-2">
              <ShieldCheck className="h-6 w-6 text-blue-500" />
            </div>
            <span className="text-xs font-medium text-gray-700">AI 매칭</span>
          </Link>
          <Link href="/schedule" className="flex flex-col items-center p-4 bg-white rounded-2xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
            <div className="p-3 bg-green-50 rounded-full mb-2">
              <Calendar className="h-6 w-6 text-green-500" />
            </div>
            <span className="text-xs font-medium text-gray-700">일정 관리</span>
          </Link>
          <Link href="/medication" className="flex flex-col items-center p-4 bg-white rounded-2xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
            <div className="p-3 bg-orange-50 rounded-full mb-2">
              <Pill className="h-6 w-6 text-orange-500" />
            </div>
            <span className="text-xs font-medium text-gray-700">복약 관리</span>
          </Link>
        </div>
      </section>

      {/* Stats Section */}
      <section className="px-6 mt-8">
        <h2 className="text-lg font-bold text-gray-900 mb-4">믿을 수 있는 늘봄케어</h2>
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
          <div className="grid grid-cols-2 gap-6 text-center">
            <div className="flex flex-col items-center space-y-1">
              <span className="text-2xl font-bold text-primary">88.6%</span>
              <span className="text-xs text-gray-500">매칭 정확도</span>
            </div>
            <div className="flex flex-col items-center space-y-1">
              <span className="text-2xl font-bold text-primary">3분</span>
              <span className="text-xs text-gray-500">평균 매칭 시간</span>
            </div>
            <div className="flex flex-col items-center space-y-1">
              <span className="text-2xl font-bold text-primary">50만+</span>
              <span className="text-xs text-gray-500">예상 사용자</span>
            </div>
            <div className="flex flex-col items-center space-y-1">
              <span className="text-2xl font-bold text-primary">2.5조</span>
              <span className="text-xs text-gray-500">비용 절감</span>
            </div>
          </div>
        </div>
      </section>

      {/* Review Section */}
      <section className="px-6 mt-8 mb-8">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-bold text-gray-900">생생한 이용 후기</h2>
          <Link href="#" className="text-xs text-gray-500 hover:text-primary">전체보기</Link>
        </div>
        <div className="space-y-4">
          <Card className="border-none shadow-sm bg-white">
            <CardContent className="p-4">
              <div className="flex items-center mb-2">
                <div className="flex text-yellow-400">
                  <Star className="h-3 w-3 fill-current" />
                  <Star className="h-3 w-3 fill-current" />
                  <Star className="h-3 w-3 fill-current" />
                  <Star className="h-3 w-3 fill-current" />
                  <Star className="h-3 w-3 fill-current" />
                </div>
                <span className="text-xs text-gray-400 ml-2">2일 전</span>
              </div>
              <p className="text-sm text-gray-700 line-clamp-2">
                &quot;급하게 간병인이 필요했는데 3분 만에 매칭되어서 놀랐습니다. 전문성도 뛰어나시고 아주 만족스럽습니다.&quot;
              </p>
              <div className="mt-2 flex items-center">
                <div className="w-6 h-6 rounded-full bg-gray-200 mr-2" />
                <span className="text-xs text-gray-500">이** 보호자님</span>
              </div>
            </CardContent>
          </Card>
        </div>
      </section >
    </div >
  )
}
