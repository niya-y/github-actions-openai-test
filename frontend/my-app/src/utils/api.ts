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

    try {
        const response = await fetch(`${BASE_URL}${url}`, {
            method: 'POST',
            headers,
            body: isFormData ? body : JSON.stringify(body),
            credentials: 'include',
            mode: 'cors',
        });

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

        return response.json();
    } catch (error) {
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

    const response = await fetch(`${BASE_URL}${url}`, {
        method: 'GET',
        headers,
        credentials: 'include',
        mode: 'cors',
    });

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

    return response.json();
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

    const response = await fetch(`${BASE_URL}${url}`, {
        method: 'PUT',
        headers,
        body: JSON.stringify(body),
        credentials: 'include',
        mode: 'cors',
    });

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

    return response.json();
}
