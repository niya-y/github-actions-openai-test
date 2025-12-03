/**
 * API 요청 재시도 유틸리티
 * Exponential backoff 전략을 사용하여 일시적 네트워크 오류 시 자동 재시도
 */

export interface RetryOptions {
    maxRetries?: number;           // 최대 재시도 횟수 (기본값: 3)
    baseDelay?: number;             // 기본 대기 시간(ms) (기본값: 1000)
    maxDelay?: number;              // 최대 대기 시간(ms) (기본값: 10000)
    backoffMultiplier?: number;     // 지수 증가 배수 (기본값: 2)
}

export interface RetryableError {
    isRetryable: boolean;
    reason: string;
}

/**
 * 에러가 재시도 가능한지 판단
 * - 네트워크 에러: 재시도 가능
 * - 타임아웃: 재시도 가능
 * - 5xx 서버 에러: 재시도 가능
 * - 4xx 클라이언트 에러: 재시도 불가
 * - 401 Unauthorized: 재시도 불가 (토큰 만료)
 */
function isRetryableError(error: any): RetryableError {
    if (error instanceof Error) {
        // 타임아웃 에러
        if (error.name === 'AbortError' || error.message.includes('타임아웃')) {
            return { isRetryable: true, reason: 'Timeout' };
        }

        // 네트워크 에러
        if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
            return { isRetryable: true, reason: 'Network error' };
        }
    }

    return { isRetryable: false, reason: 'Non-retryable error' };
}

/**
 * 재시도 가능한 상태 코드인지 확인
 * - 408: Request Timeout
 * - 429: Too Many Requests
 * - 500: Internal Server Error
 * - 502: Bad Gateway
 * - 503: Service Unavailable
 * - 504: Gateway Timeout
 */
function isRetryableStatusCode(statusCode: number): boolean {
    const retryableStatuses = [408, 429, 500, 502, 503, 504];
    return retryableStatuses.includes(statusCode);
}

/**
 * Exponential backoff를 적용하여 재시도 수행
 * @param fn - 실행할 비동기 함수
 * @param options - 재시도 옵션
 * @returns 함수 실행 결과
 */
export async function withRetry<T>(
    fn: () => Promise<T>,
    options: RetryOptions = {}
): Promise<T> {
    const {
        maxRetries = 3,
        baseDelay = 1000,
        maxDelay = 10000,
        backoffMultiplier = 2,
    } = options;

    let lastError: Error | null = null;

    for (let attempt = 1; attempt <= maxRetries; attempt++) {
        try {
            return await fn();
        } catch (error) {
            lastError = error as Error;

            // 마지막 시도이거나 재시도 불가능한 에러면 즉시 throw
            if (attempt === maxRetries) {
                console.error(`[Retry] All ${maxRetries} attempts failed for: ${lastError.message}`);
                throw lastError;
            }

            // 재시도 불가능한 에러 확인
            const retryableError = isRetryableError(lastError);
            if (!retryableError.isRetryable) {
                console.error(`[Retry] Non-retryable error (${retryableError.reason}):`, lastError.message);
                throw lastError;
            }

            // Exponential backoff 계산
            const delayMultiplier = Math.pow(backoffMultiplier, attempt - 1);
            const delay = Math.min(baseDelay * delayMultiplier, maxDelay);

            console.warn(
                `[Retry] Attempt ${attempt}/${maxRetries} failed, retrying in ${delay}ms...`,
                `Error: ${lastError.message}`
            );

            // 지정된 시간 대기 후 재시도
            await new Promise(resolve => setTimeout(resolve, delay));
        }
    }

    // 이 지점에 도달하지 않아야 함
    throw lastError;
}

/**
 * 재시도 기능이 포함된 API GET 요청
 * @param fetchFn - 실제 fetch 함수
 * @param url - 요청 URL
 * @param options - 재시도 옵션
 * @returns API 응답
 */
export async function apiGetWithRetry<T>(
    fetchFn: (url: string) => Promise<T>,
    url: string,
    retryOptions?: RetryOptions
): Promise<T> {
    return withRetry(() => fetchFn(url), retryOptions);
}

/**
 * 재시도 기능이 포함된 API POST 요청
 * @param fetchFn - 실제 fetch 함수
 * @param url - 요청 URL
 * @param body - 요청 바디
 * @param options - 재시도 옵션
 * @returns API 응답
 */
export async function apiPostWithRetry<T>(
    fetchFn: (url: string, body: any) => Promise<T>,
    url: string,
    body: any,
    retryOptions?: RetryOptions
): Promise<T> {
    return withRetry(() => fetchFn(url, body), retryOptions);
}

/**
 * 조건부 재시도: HTTP 상태 코드 기반
 * @param fn - 실행할 함수 (Response 반환 가정)
 * @param options - 재시도 옵션
 * @returns API 응답
 */
export async function withStatusCodeRetry(
    fn: () => Promise<Response>,
    options: RetryOptions = {}
): Promise<Response> {
    const {
        maxRetries = 3,
        baseDelay = 1000,
        maxDelay = 10000,
        backoffMultiplier = 2,
    } = options;

    let lastResponse: Response | null = null;
    let lastError: Error | null = null;

    for (let attempt = 1; attempt <= maxRetries; attempt++) {
        try {
            const response = await fn();
            lastResponse = response;

            // 재시도 불가능한 상태 코드이거나 성공하면 반환
            if (response.ok || !isRetryableStatusCode(response.status)) {
                return response;
            }

            // 마지막 시도이면 반환
            if (attempt === maxRetries) {
                console.error(`[Retry] All ${maxRetries} attempts failed with status ${response.status}`);
                return response;
            }

            // Exponential backoff 계산
            const delayMultiplier = Math.pow(backoffMultiplier, attempt - 1);
            const delay = Math.min(baseDelay * delayMultiplier, maxDelay);

            console.warn(
                `[Retry] Attempt ${attempt}/${maxRetries} failed with status ${response.status}, retrying in ${delay}ms...`
            );

            await new Promise(resolve => setTimeout(resolve, delay));
        } catch (error) {
            lastError = error as Error;

            // 마지막 시도이거나 재시도 불가능한 에러면 throw
            if (attempt === maxRetries) {
                console.error(`[Retry] All ${maxRetries} attempts failed with error:`, lastError.message);
                throw lastError;
            }

            // 재시도 불가능한 에러 확인
            const retryableError = isRetryableError(lastError);
            if (!retryableError.isRetryable) {
                console.error(`[Retry] Non-retryable error (${retryableError.reason}):`, lastError.message);
                throw lastError;
            }

            // Exponential backoff 계산
            const delayMultiplier = Math.pow(backoffMultiplier, attempt - 1);
            const delay = Math.min(baseDelay * delayMultiplier, maxDelay);

            console.warn(
                `[Retry] Attempt ${attempt}/${maxRetries} failed, retrying in ${delay}ms...`,
                `Error: ${lastError.message}`
            );

            await new Promise(resolve => setTimeout(resolve, delay));
        }
    }

    // 에러가 있으면 throw, 아니면 마지막 response 반환
    if (lastError) {
        throw lastError;
    }

    if (lastResponse) {
        return lastResponse;
    }

    throw new Error('Unexpected retry failure');
}
