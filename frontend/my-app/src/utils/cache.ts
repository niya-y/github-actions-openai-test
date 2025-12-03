/**
 * 요청 캐싱 유틸리티
 * TTL (Time To Live)을 지원하는 간단한 메모리 캐시
 * GET 요청의 응답을 캐싱하여 성능 향상
 */

export interface CacheEntry<T> {
    data: T;
    timestamp: number;
    ttl: number; // Time To Live in milliseconds
}

/**
 * 요청 캐시 클래스
 * 일반 목적의 메모리 캐시로 사용 가능
 */
export class RequestCache<T = any> {
    private cache: Map<string, CacheEntry<T>> = new Map();
    private defaultTtl: number; // 기본 TTL (밀리초)

    /**
     * @param defaultTtlMs - 기본 TTL (밀리초). 기본값: 5분 (300000ms)
     */
    constructor(defaultTtlMs: number = 5 * 60 * 1000) {
        this.defaultTtl = defaultTtlMs;
    }

    /**
     * 캐시에서 값 가져오기
     * TTL이 만료되었으면 null 반환 및 캐시 제거
     * @param key - 캐시 키
     * @returns 캐시된 데이터 또는 null
     */
    get(key: string): T | null {
        const entry = this.cache.get(key);

        if (!entry) {
            return null;
        }

        // TTL 확인
        const now = Date.now();
        const age = now - entry.timestamp;

        if (age > entry.ttl) {
            // 만료된 항목 제거
            this.cache.delete(key);
            console.debug(`[Cache] Expired entry removed: ${key}`);
            return null;
        }

        console.debug(`[Cache] Hit: ${key} (age: ${age}ms, TTL: ${entry.ttl}ms)`);
        return entry.data;
    }

    /**
     * 캐시에 값 저장
     * @param key - 캐시 키
     * @param data - 저장할 데이터
     * @param ttlMs - TTL (밀리초). 지정하지 않으면 기본값 사용
     */
    set(key: string, data: T, ttlMs?: number): void {
        const ttl = ttlMs ?? this.defaultTtl;

        this.cache.set(key, {
            data,
            timestamp: Date.now(),
            ttl,
        });

        console.debug(`[Cache] Set: ${key} (TTL: ${ttl}ms)`);

        // TTL 후 자동 제거 스케줄
        setTimeout(() => {
            if (this.cache.get(key)?.timestamp === this.cache.get(key)?.timestamp) {
                this.cache.delete(key);
                console.debug(`[Cache] Auto-expired: ${key}`);
            }
        }, ttl);
    }

    /**
     * 특정 키의 캐시 제거
     * @param key - 제거할 캐시 키
     */
    delete(key: string): void {
        this.cache.delete(key);
        console.debug(`[Cache] Deleted: ${key}`);
    }

    /**
     * 모든 캐시 제거
     */
    clear(): void {
        const size = this.cache.size;
        this.cache.clear();
        console.debug(`[Cache] Cleared all ${size} entries`);
    }

    /**
     * 캐시 크기 반환
     * @returns 캐시된 항목 수
     */
    size(): number {
        return this.cache.size;
    }

    /**
     * 캐시 상태 확인
     * @returns 캐시에 저장된 모든 키와 남은 TTL
     */
    status(): { [key: string]: { remainingTtl: number; data: T } } {
        const status: { [key: string]: { remainingTtl: number; data: T } } = {};
        const now = Date.now();

        this.cache.forEach((entry, key) => {
            const age = now - entry.timestamp;
            const remainingTtl = Math.max(0, entry.ttl - age);

            status[key] = {
                remainingTtl,
                data: entry.data,
            };
        });

        return status;
    }

    /**
     * 패턴에 맞는 모든 키의 캐시 제거
     * 정규식 패턴을 지원 (예: /^api\/users\//)
     * @param pattern - 정규식 패턴
     */
    deleteByPattern(pattern: RegExp): number {
        let deletedCount = 0;

        this.cache.forEach((_, key) => {
            if (pattern.test(key)) {
                this.cache.delete(key);
                deletedCount++;
            }
        });

        if (deletedCount > 0) {
            console.debug(`[Cache] Deleted ${deletedCount} entries matching pattern: ${pattern}`);
        }

        return deletedCount;
    }
}

/**
 * 전역 API 캐시 인스턴스
 * GET 요청 결과를 캐싱하는데 사용
 */
export const apiCache = new RequestCache<any>(5 * 60 * 1000); // 5분 기본 TTL

/**
 * API 응답 캐싱을 위한 고차 함수
 * @param fetchFn - 실행할 fetch 함수
 * @param cacheKey - 캐시 키
 * @param cacheTtl - 캐시 TTL (밀리초)
 * @returns 캐시된 응답 또는 새 응답
 */
export async function withCache<T>(
    fetchFn: () => Promise<T>,
    cacheKey: string,
    cacheTtl?: number
): Promise<T> {
    // 캐시에서 먼저 확인
    const cached = apiCache.get(cacheKey);
    if (cached !== null) {
        return cached as T;
    }

    // 캐시 미스: 함수 실행
    const result = await fetchFn();

    // 캐시에 저장
    apiCache.set(cacheKey, result, cacheTtl);

    return result;
}

/**
 * 캐시 무효화: 패턴에 맞는 모든 캐시 제거
 * @param pattern - 정규식 패턴
 * @example
 * // GET /api/users/* 관련 캐시 모두 제거
 * invalidateCache(/^api\/users\//);
 */
export function invalidateCache(pattern: RegExp): number {
    return apiCache.deleteByPattern(pattern);
}

/**
 * 캐시 초기화
 */
export function clearCache(): void {
    apiCache.clear();
}

/**
 * 캐시 상태 조회
 */
export function getCacheStatus() {
    return apiCache.status();
}
