/**
 * 애플리케이션 모니터링 유틸리티
 * 에러, API 성능, 사용자 인터랙션 추적
 */

import { logger } from './logger';

export interface ErrorMetrics {
    total: number;
    byType: Record<string, number>;
    recentErrors: Array<{
        timestamp: string;
        type: string;
        message: string;
        stack?: string;
    }>;
}

export interface ApiMetrics {
    totalRequests: number;
    successCount: number;
    errorCount: number;
    avgResponseTime: number;
    slowestRequests: Array<{
        url: string;
        method: string;
        duration: number;
        timestamp: string;
    }>;
}

export interface AppHealth {
    status: 'healthy' | 'degraded' | 'error';
    errorRate: number;
    avgApiResponseTime: number;
    lastError?: string;
}

/**
 * 모니터링 클래스
 */
class Monitoring {
    private errorMetrics: ErrorMetrics = {
        total: 0,
        byType: {},
        recentErrors: [],
    };

    private apiMetrics: ApiMetrics = {
        totalRequests: 0,
        successCount: 0,
        errorCount: 0,
        avgResponseTime: 0,
        slowestRequests: [],
    };

    private maxRecentErrors: number = 50;
    private maxSlowestRequests: number = 20;

    constructor() {
        this.setupErrorHandlers();
    }

    /**
     * 전역 에러 핸들러 설정
     */
    private setupErrorHandlers(): void {
        if (typeof window === 'undefined') return;

        // Unhandled promise rejection 감시
        window.addEventListener('unhandledrejection', (event: PromiseRejectionEvent) => {
            this.recordError('UnhandledRejection', event.reason);
        });

        // JavaScript 에러 감시
        window.addEventListener('error', (event: ErrorEvent) => {
            this.recordError('JSError', event.error || event.message);
        });
    }

    /**
     * API 요청 시작 기록
     */
    startApiRequest(method: string, url: string): () => void {
        const startTime = performance.now();

        return (statusCode: number = 200) => {
            const duration = Math.round(performance.now() - startTime);
            this.recordApiCall(method, url, statusCode, duration);
        };
    }

    /**
     * API 호출 기록
     */
    private recordApiCall(method: string, url: string, statusCode: number, duration: number): void {
        this.apiMetrics.totalRequests++;

        if (statusCode >= 200 && statusCode < 300) {
            this.apiMetrics.successCount++;
        } else {
            this.apiMetrics.errorCount++;
        }

        // 평균 응답 시간 계산
        this.apiMetrics.avgResponseTime =
            (this.apiMetrics.avgResponseTime * (this.apiMetrics.totalRequests - 1) + duration) /
            this.apiMetrics.totalRequests;

        // 느린 요청 추적
        if (duration > 1000) {
            // 1초 이상
            this.apiMetrics.slowestRequests.push({
                url,
                method,
                duration,
                timestamp: new Date().toISOString(),
            });

            // 최대 개수 유지
            if (this.apiMetrics.slowestRequests.length > this.maxSlowestRequests) {
                this.apiMetrics.slowestRequests.shift();
            }

            logger.logApiCall(method, url, statusCode, duration, false);
        }
    }

    /**
     * 에러 기록
     */
    private recordError(type: string, error: any): void {
        this.errorMetrics.total++;
        this.errorMetrics.byType[type] = (this.errorMetrics.byType[type] || 0) + 1;

        const errorEntry = {
            timestamp: new Date().toISOString(),
            type,
            message: error instanceof Error ? error.message : String(error),
            stack: error instanceof Error ? error.stack : undefined,
        };

        this.errorMetrics.recentErrors.push(errorEntry);

        // 최대 개수 유지
        if (this.errorMetrics.recentErrors.length > this.maxRecentErrors) {
            this.errorMetrics.recentErrors.shift();
        }

        logger.error(`${type}: ${errorEntry.message}`, error, 'Monitoring');
    }

    /**
     * 수동 에러 기록
     */
    trackError(error: Error | string, type: string = 'AppError'): void {
        this.recordError(type, error);
    }

    /**
     * API 성능 수동 기록
     */
    trackApiCall(method: string, url: string, statusCode: number, duration: number): void {
        this.recordApiCall(method, url, statusCode, duration);
    }

    /**
     * 사용자 인터랙션 추적
     */
    trackInteraction(action: string, details?: Record<string, any>): void {
        logger.info(`User Interaction: ${action}`, details, 'UserInteraction');
    }

    /**
     * 페이지 뷰 추적
     */
    trackPageView(pageName: string): void {
        logger.info(`Page View: ${pageName}`, undefined, 'PageView');
    }

    /**
     * 에러 메트릭 조회
     */
    getErrorMetrics(): ErrorMetrics {
        return { ...this.errorMetrics };
    }

    /**
     * API 메트릭 조회
     */
    getApiMetrics(): ApiMetrics {
        return { ...this.apiMetrics };
    }

    /**
     * 애플리케이션 상태 조회
     */
    getAppHealth(): AppHealth {
        const errorRate =
            this.apiMetrics.totalRequests > 0
                ? (this.apiMetrics.errorCount / this.apiMetrics.totalRequests) * 100
                : 0;

        let status: 'healthy' | 'degraded' | 'error' = 'healthy';
        if (errorRate > 10) {
            status = 'degraded';
        } else if (errorRate > 25 || this.errorMetrics.total > 10) {
            status = 'error';
        }

        return {
            status,
            errorRate: Math.round(errorRate * 100) / 100,
            avgApiResponseTime: Math.round(this.apiMetrics.avgResponseTime),
            lastError: this.errorMetrics.recentErrors[this.errorMetrics.recentErrors.length - 1]?.message,
        };
    }

    /**
     * 전체 모니터링 대시보드 (개발자용)
     */
    getDashboard() {
        return {
            health: this.getAppHealth(),
            errors: this.getErrorMetrics(),
            api: this.getApiMetrics(),
            timestamp: new Date().toISOString(),
        };
    }

    /**
     * 모니터링 데이터 리셋
     */
    reset(): void {
        this.errorMetrics = {
            total: 0,
            byType: {},
            recentErrors: [],
        };

        this.apiMetrics = {
            totalRequests: 0,
            successCount: 0,
            errorCount: 0,
            avgResponseTime: 0,
            slowestRequests: [],
        };

        logger.info('Monitoring data reset', undefined, 'Monitoring');
    }
}

// 전역 모니터링 인스턴스
export const monitoring = new Monitoring();

// 개발자 도구에서 접근 가능하도록
if (typeof window !== 'undefined') {
    (window as any).__monitoring = monitoring;
}

/**
 * API 호출 시간 측정 헬퍼
 * @example
 * const end = monitoring.startApiRequest('GET', '/api/users');
 * try {
 *     const response = await fetch(...);
 *     end(response.status);
 * } catch (error) {
 *     end(500);
 * }
 */
export function createApiRequestTracker(method: string, url: string) {
    const startTime = performance.now();

    return {
        end: (statusCode: number = 200) => {
            const duration = Math.round(performance.now() - startTime);
            monitoring.trackApiCall(method, url, statusCode, duration);
            return duration;
        },
    };
}
