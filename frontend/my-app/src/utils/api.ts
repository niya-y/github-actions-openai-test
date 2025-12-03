const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function apiPost<T>(url: string, body: any, options?: { includeAuth?: boolean; headers?: Record<string, string> }): Promise<T> {
    const headers: any = {};

    // FormData 여부 확인
    const isFormData = body instanceof FormData;

    // FormData가 아닐 때만 Content-Type 설정
    if (!isFormData) {
        headers['Content-Type'] = 'application/json';
    }

    // 커스텀 헤더 추가 (FormData의 경우 Content-Type 헤더 제거)
    if (options?.headers) {
        Object.assign(headers, options.headers);
        if (isFormData && headers['Content-Type'] === 'multipart/form-data') {
            delete headers['Content-Type'];
        }
    }

    // JWT 토큰이 있으면 헤더에 추가 (기본값: true, 로그인 요청은 false)
    const shouldIncludeAuth = options?.includeAuth !== false;
    if (shouldIncludeAuth) {
        const token = localStorage.getItem('access_token');
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
    }

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 30000); // 30초 타임아웃

    try {
        const response = await fetch(`${BASE_URL}${url}`, {
            method: 'POST',
            headers,
            body: isFormData ? body : JSON.stringify(body),
            credentials: 'include',
            mode: 'cors',
            signal: controller.signal,
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
            const errorBody = await response.text();
            console.error(`API Error - Status: ${response.status}, Body:`, errorBody);
            console.error(`API Error - URL: ${BASE_URL}${url}`, `Headers:`, headers);

            // 401 Unauthorized - 토큰 만료, 로그인 페이지로 리다이렉트
            if (response.status === 401) {
                localStorage.removeItem('access_token');
                window.location.href = '/login';
                return Promise.reject(new Error('Session expired. Please login again.'));
            }

            throw new Error(`API call failed: ${response.status} ${response.statusText}`);
        }

        try {
            return await response.json();
        } catch (parseError) {
            console.error('Failed to parse JSON response:', parseError);
            throw new Error('Invalid JSON response from server');
        }
    } catch (error) {
        clearTimeout(timeoutId);

        if (error instanceof Error && error.name === 'AbortError') {
            console.error('API request timeout (30s):', url);
            throw new Error('요청 타임아웃 (30초) - 네트워크 연결을 확인해주세요');
        }

        console.error('API request failed:', error);
        throw error;
    }
}

export async function apiGet<T>(url: string): Promise<T> {
    const headers: any = {
        'Content-Type': 'application/json',
    };

    // JWT 토큰이 있으면 헤더에 추가
    const token = localStorage.getItem('access_token');
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 30000); // 30초 타임아웃

    try {
        const response = await fetch(`${BASE_URL}${url}`, {
            method: 'GET',
            headers,
            credentials: 'include',
            mode: 'cors',
            signal: controller.signal,
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
            const errorBody = await response.text();
            console.error(`API Error - Status: ${response.status}, Body:`, errorBody);
            console.error(`API Error - URL: ${BASE_URL}${url}`, `Headers:`, headers);

            // 401 Unauthorized - 토큰 만료, 로그인 페이지로 리다이렉트
            if (response.status === 401) {
                localStorage.removeItem('access_token');
                window.location.href = '/login';
                return Promise.reject(new Error('Session expired. Please login again.'));
            }

            throw new Error(`API call failed: ${response.status} ${response.statusText}`);
        }

        try {
            return await response.json();
        } catch (parseError) {
            console.error('Failed to parse JSON response:', parseError);
            throw new Error('Invalid JSON response from server');
        }
    } catch (error) {
        clearTimeout(timeoutId);

        if (error instanceof Error && error.name === 'AbortError') {
            console.error('API request timeout (30s):', url);
            throw new Error('요청 타임아웃 (30초) - 네트워크 연결을 확인해주세요');
        }

        console.error('API request failed:', error);
        throw error;
    }
}

export async function apiPut<T>(url: string, body: any): Promise<T> {
    const headers: any = {
        'Content-Type': 'application/json',
    };

    // JWT 토큰이 있으면 헤더에 추가
    const token = localStorage.getItem('access_token');
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 30000); // 30초 타임아웃

    try {
        const response = await fetch(`${BASE_URL}${url}`, {
            method: 'PUT',
            headers,
            body: JSON.stringify(body),
            credentials: 'include',
            mode: 'cors',
            signal: controller.signal,
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
            const errorBody = await response.text();
            console.error(`API Error - Status: ${response.status}, Body:`, errorBody);

            // 401 Unauthorized - 토큰 만료, 로그인 페이지로 리다이렉트
            if (response.status === 401) {
                localStorage.removeItem('access_token');
                window.location.href = '/login';
                return Promise.reject(new Error('Session expired. Please login again.'));
            }

            throw new Error(`API call failed: ${response.status} ${response.statusText}`);
        }

        try {
            return await response.json();
        } catch (parseError) {
            console.error('Failed to parse JSON response:', parseError);
            throw new Error('Invalid JSON response from server');
        }
    } catch (error) {
        clearTimeout(timeoutId);

        if (error instanceof Error && error.name === 'AbortError') {
            console.error('API request timeout (30s):', url);
            throw new Error('요청 타임아웃 (30초) - 네트워크 연결을 확인해주세요');
        }

        console.error('API request failed:', error);
        throw error;
    }
}

export async function apiDelete<T>(url: string): Promise<T> {
    const token = localStorage.getItem('access_token');
    const headers: Record<string, string> = {};

    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 30000); // 30초 타임아웃

    try {
        const response = await fetch(`${BASE_URL}${url}`, {
            method: 'DELETE',
            headers,
            credentials: 'include',
            mode: 'cors',
            signal: controller.signal,
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
            const errorBody = await response.text();
            console.error(`API Error - Status: ${response.status}, Body:`, errorBody);

            // 401 Unauthorized - 토큰 만료
            if (response.status === 401) {
                localStorage.removeItem('access_token');
                window.location.href = '/login';
                return Promise.reject(new Error('Session expired. Please login again.'));
            }

            throw new Error(`API call failed: ${response.status} ${response.statusText}`);
        }

        try {
            return await response.json();
        } catch (parseError) {
            console.error('Failed to parse JSON response:', parseError);
            throw new Error('Invalid JSON response from server');
        }
    } catch (error) {
        clearTimeout(timeoutId);

        if (error instanceof Error && error.name === 'AbortError') {
            console.error('API request timeout (30s):', url);
            throw new Error('요청 타임아웃 (30초) - 네트워크 연결을 확인해주세요');
        }

        console.error('API request failed:', error);
        throw error;
    }
}

/**
 * Retry-enabled API functions with exponential backoff
 * 재시도 기능이 포함된 API 함수들 (Exponential backoff)
 */

import { withRetry, RetryOptions } from './retry';

export async function apiGetWithRetry<T>(
    url: string,
    retryOptions?: RetryOptions
): Promise<T> {
    return withRetry(() => apiGet<T>(url), retryOptions);
}

export async function apiPostWithRetry<T>(
    url: string,
    body: any,
    options?: { includeAuth?: boolean; headers?: Record<string, string> },
    retryOptions?: RetryOptions
): Promise<T> {
    return withRetry(() => apiPost<T>(url, body, options), retryOptions);
}

export async function apiPutWithRetry<T>(
    url: string,
    body: any,
    retryOptions?: RetryOptions
): Promise<T> {
    return withRetry(() => apiPut<T>(url, body), retryOptions);
}

export async function apiDeleteWithRetry<T>(
    url: string,
    retryOptions?: RetryOptions
): Promise<T> {
    return withRetry(() => apiDelete<T>(url), retryOptions);
}
