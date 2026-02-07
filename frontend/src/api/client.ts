/**
 * API Client - バックエンドとの通信用クライアント
 * タスク6.1: フロントエンド・バックエンド統合
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

interface ApiResponse<T> {
  data: T | null;
  error: string | null;
  status?: number;
}

interface ApiError {
  detail: string;
  status: number;
}

// トークン管理
let authToken: string | null = null;

/**
 * 認証トークンを設定
 */
export function setAuthToken(token: string | null): void {
  authToken = token;
  if (token) {
    localStorage.setItem('auth_token', token);
  } else {
    localStorage.removeItem('auth_token');
  }
}

/**
 * 認証トークンを取得
 */
export function getAuthToken(): string | null {
  if (!authToken) {
    authToken = localStorage.getItem('auth_token');
  }
  return authToken;
}

/**
 * 認証トークンをクリア
 */
export function clearAuthToken(): void {
  authToken = null;
  localStorage.removeItem('auth_token');
}

/**
 * リクエストヘッダーを構築
 */
function buildHeaders(): HeadersInit {
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  };

  const token = getAuthToken();
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  return headers;
}

/**
 * エラーレスポンスをパース
 */
async function parseErrorResponse(response: Response): Promise<string> {
  try {
    const errorData = await response.json();
    if (errorData.detail) {
      if (typeof errorData.detail === 'string') {
        return errorData.detail;
      }
      // バリデーションエラーの場合
      if (Array.isArray(errorData.detail)) {
        return errorData.detail
          .map((err: { msg: string; loc: string[] }) => `${err.loc.join('.')}: ${err.msg}`)
          .join(', ');
      }
    }
    return `HTTP error! status: ${response.status}`;
  } catch {
    return `HTTP error! status: ${response.status}`;
  }
}

/**
 * 認証エラーをチェック
 */
function handleAuthError(status: number): void {
  if (status === 401) {
    clearAuthToken();
    // 必要に応じてログインページへリダイレクト
    window.dispatchEvent(new CustomEvent('auth-error', { detail: { status } }));
  }
}

export async function apiGet<T>(endpoint: string): Promise<ApiResponse<T>> {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'GET',
      headers: buildHeaders(),
      credentials: 'include',
    });

    if (!response.ok) {
      handleAuthError(response.status);
      const errorMessage = await parseErrorResponse(response);
      return { data: null, error: errorMessage, status: response.status };
    }

    const data = await response.json();
    return { data, error: null, status: response.status };
  } catch (error) {
    return {
      data: null,
      error: error instanceof Error ? error.message : 'ネットワークエラーが発生しました',
    };
  }
}

export async function apiPost<T, B>(endpoint: string, body: B): Promise<ApiResponse<T>> {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
      headers: buildHeaders(),
      credentials: 'include',
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      handleAuthError(response.status);
      const errorMessage = await parseErrorResponse(response);
      return { data: null, error: errorMessage, status: response.status };
    }

    const data = await response.json();
    return { data, error: null, status: response.status };
  } catch (error) {
    return {
      data: null,
      error: error instanceof Error ? error.message : 'ネットワークエラーが発生しました',
    };
  }
}

export async function apiPut<T, B>(endpoint: string, body: B): Promise<ApiResponse<T>> {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'PUT',
      headers: buildHeaders(),
      credentials: 'include',
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      handleAuthError(response.status);
      const errorMessage = await parseErrorResponse(response);
      return { data: null, error: errorMessage, status: response.status };
    }

    const data = await response.json();
    return { data, error: null, status: response.status };
  } catch (error) {
    return {
      data: null,
      error: error instanceof Error ? error.message : 'ネットワークエラーが発生しました',
    };
  }
}

export async function apiDelete<T>(endpoint: string): Promise<ApiResponse<T>> {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'DELETE',
      headers: buildHeaders(),
      credentials: 'include',
    });

    if (!response.ok) {
      handleAuthError(response.status);
      const errorMessage = await parseErrorResponse(response);
      return { data: null, error: errorMessage, status: response.status };
    }

    const data = await response.json();
    return { data, error: null, status: response.status };
  } catch (error) {
    return {
      data: null,
      error: error instanceof Error ? error.message : 'ネットワークエラーが発生しました',
    };
  }
}

export async function healthCheck(): Promise<{ status: string } | null> {
  const response = await apiGet<{ status: string }>('/health');
  return response.data;
}

/**
 * 認証エラーリスナーを登録
 */
export function onAuthError(callback: (status: number) => void): () => void {
  const handler = (event: CustomEvent<{ status: number }>) => {
    callback(event.detail.status);
  };
  window.addEventListener('auth-error', handler as EventListener);
  return () => window.removeEventListener('auth-error', handler as EventListener);
}
