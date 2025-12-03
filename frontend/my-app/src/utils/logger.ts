/**
 * 에러 로깅 및 모니터링 유틸리티
 * 개발 환경과 프로덕션 환경에서 다른 로깅 전략 사용
 */

export enum LogLevel {
    DEBUG = 'DEBUG',
    INFO = 'INFO',
    WARN = 'WARN',
    ERROR = 'ERROR',
}

export interface LogEntry {
    timestamp: string;
    level: LogLevel;
    message: string;
    data?: any;
    stack?: string;
    context?: string; // 로그 출처 (페이지, 컴포넌트 등)
}

/**
 * 로거 클래스
 * 개발/프로덕션 환경별 로깅 전략 제공
 */
class Logger {
    private isDevelopment: boolean;
    private logHistory: LogEntry[] = [];
    private maxHistorySize: number = 1000; // 최대 로그 기록 수
    private logLevel: LogLevel = LogLevel.INFO;

    constructor() {
        this.isDevelopment = process.env.NODE_ENV === 'development';
        this.logLevel = (process.env.NEXT_PUBLIC_LOG_LEVEL as LogLevel) || LogLevel.INFO;
    }

    /**
     * 현재 로그 레벨 설정
     */
    setLogLevel(level: LogLevel): void {
        this.logLevel = level;
        console.debug(`[Logger] Log level changed to: ${level}`);
    }

    /**
     * 로그 기록 추가 (내부용)
     */
    private addToHistory(entry: LogEntry): void {
        this.logHistory.push(entry);

        // 최대 크기 초과 시 오래된 항목 제거
        if (this.logHistory.length > this.maxHistorySize) {
            this.logHistory.shift();
        }
    }

    /**
     * 로그 레벨 비교
     */
    private shouldLog(level: LogLevel): boolean {
        const levels = [LogLevel.DEBUG, LogLevel.INFO, LogLevel.WARN, LogLevel.ERROR];
        const currentIndex = levels.indexOf(this.logLevel);
        const messageIndex = levels.indexOf(level);
        return messageIndex >= currentIndex;
    }

    /**
     * DEBUG 레벨 로깅 (개발 환경에서만)
     */
    debug(message: string, data?: any, context?: string): void {
        if (!this.shouldLog(LogLevel.DEBUG)) return;

        const entry: LogEntry = {
            timestamp: new Date().toISOString(),
            level: LogLevel.DEBUG,
            message,
            data,
            context,
        };

        this.addToHistory(entry);

        if (this.isDevelopment) {
            console.debug(`[DEBUG] ${message}`, data || '');
        }
    }

    /**
     * INFO 레벨 로깅
     */
    info(message: string, data?: any, context?: string): void {
        if (!this.shouldLog(LogLevel.INFO)) return;

        const entry: LogEntry = {
            timestamp: new Date().toISOString(),
            level: LogLevel.INFO,
            message,
            data,
            context,
        };

        this.addToHistory(entry);

        if (this.isDevelopment) {
            console.info(`[INFO] ${message}`, data || '');
        } else {
            // 프로덕션: 중요한 정보만 기록
            if (context && (context.includes('auth') || context.includes('payment'))) {
                console.info(`[INFO] ${message}`);
            }
        }
    }

    /**
     * WARN 레벨 로깅
     */
    warn(message: string, data?: any, context?: string): void {
        if (!this.shouldLog(LogLevel.WARN)) return;

        const entry: LogEntry = {
            timestamp: new Date().toISOString(),
            level: LogLevel.WARN,
            message,
            data,
            context,
        };

        this.addToHistory(entry);

        console.warn(`[WARN] ${message}`, data || '');
    }

    /**
     * ERROR 레벨 로깅
     */
    error(message: string, error?: any, context?: string): void {
        if (!this.shouldLog(LogLevel.ERROR)) return;

        const stack = error instanceof Error ? error.stack : undefined;

        const entry: LogEntry = {
            timestamp: new Date().toISOString(),
            level: LogLevel.ERROR,
            message,
            data: error,
            stack,
            context,
        };

        this.addToHistory(entry);

        console.error(`[ERROR] ${message}`, error || '');

        // 프로덕션: 외부 에러 트래킹 서비스로 전송 가능
        if (!this.isDevelopment) {
            this.reportErrorToService(entry);
        }
    }

    /**
     * API 요청 로깅
     */
    logApiCall(
        method: string,
        url: string,
        status: number,
        duration: number,
        success: boolean
    ): void {
        const level = success ? LogLevel.DEBUG : LogLevel.WARN;

        if (!this.shouldLog(level)) return;

        const message = `API Call: ${method} ${url} [${status}] (${duration}ms)`;

        const entry: LogEntry = {
            timestamp: new Date().toISOString(),
            level,
            message,
            context: 'API',
        };

        this.addToHistory(entry);

        if (this.isDevelopment) {
            if (success) {
                console.debug(message);
            } else {
                console.warn(message);
            }
        }
    }

    /**
     * 성능 메트릭 로깅
     */
    logPerformance(metric: string, duration: number, threshold?: number): void {
        const isSlow = threshold && duration > threshold;
        const level = isSlow ? LogLevel.WARN : LogLevel.DEBUG;

        if (!this.shouldLog(level)) return;

        const message = `Performance: ${metric} took ${duration}ms${isSlow ? ' (SLOW)' : ''}`;

        const entry: LogEntry = {
            timestamp: new Date().toISOString(),
            level,
            message,
            context: 'Performance',
        };

        this.addToHistory(entry);

        if (this.isDevelopment) {
            if (isSlow) {
                console.warn(message);
            } else {
                console.debug(message);
            }
        }
    }

    /**
     * 프로덕션 환경에서 에러를 외부 서비스로 전송
     * 실제 구현에서는 Sentry, LogRocket, Bugsnag 등을 사용
     */
    private reportErrorToService(entry: LogEntry): void {
        try {
            // 예: Sentry 통합
            // if (typeof window !== 'undefined' && window.Sentry) {
            //     window.Sentry.captureException(entry.data, {
            //         extra: { context: entry.context }
            //     });
            // }

            // 예: 백엔드 에러 로깅 API
            // fetch('/api/logs', {
            //     method: 'POST',
            //     headers: { 'Content-Type': 'application/json' },
            //     body: JSON.stringify(entry)
            // }).catch(() => {
            //     // 로깅 실패 무시
            // });
        } catch (err) {
            // 에러 보고 실패는 조용히 처리
        }
    }

    /**
     * 로그 기록 조회
     */
    getHistory(filter?: { level?: LogLevel; context?: string; limit?: number }): LogEntry[] {
        let filtered = [...this.logHistory];

        if (filter?.level) {
            filtered = filtered.filter(entry => entry.level === filter.level);
        }

        if (filter?.context) {
            filtered = filtered.filter(entry => entry.context === filter.context);
        }

        const limit = filter?.limit || 100;
        return filtered.slice(-limit);
    }

    /**
     * 로그 기록 초기화
     */
    clearHistory(): void {
        this.logHistory = [];
    }

    /**
     * 로그 통계
     */
    getStats() {
        const stats = {
            total: this.logHistory.length,
            byLevel: {
                [LogLevel.DEBUG]: 0,
                [LogLevel.INFO]: 0,
                [LogLevel.WARN]: 0,
                [LogLevel.ERROR]: 0,
            },
            byContext: {} as Record<string, number>,
        };

        this.logHistory.forEach(entry => {
            stats.byLevel[entry.level]++;

            if (entry.context) {
                stats.byContext[entry.context] = (stats.byContext[entry.context] || 0) + 1;
            }
        });

        return stats;
    }

    /**
     * 로그를 JSON 형식으로 내보내기 (디버깅용)
     */
    export(): string {
        return JSON.stringify(this.logHistory, null, 2);
    }
}

// 전역 로거 인스턴스
export const logger = new Logger();

/**
 * 성능 측정을 위한 타이머 클래스
 */
export class PerformanceTimer {
    private startTime: number;
    private name: string;

    constructor(name: string) {
        this.name = name;
        this.startTime = performance.now();
    }

    /**
     * 경과 시간 반환 (밀리초)
     */
    elapsed(): number {
        return Math.round(performance.now() - this.startTime);
    }

    /**
     * 타이머 종료 및 로깅
     * @param threshold - 이 시간 이상 소요되면 경고 로깅
     */
    end(threshold?: number): number {
        const duration = this.elapsed();
        logger.logPerformance(this.name, duration, threshold);
        return duration;
    }
}

/**
 * 개발자 도구로 로그 조회
 * console에서 사용: window.__logger?.getHistory()
 */
if (typeof window !== 'undefined') {
    (window as any).__logger = logger;
}
