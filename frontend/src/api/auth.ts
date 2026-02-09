/**
 * 認証API
 */
import { apiPost, apiGet, apiPut, setAuthToken } from './client';
import { AuthResponse, User, ProfileUpdateRequest, ApiTokenResponse } from '../types';

interface RegisterRequest {
  email: string;
  password: string;
  display_name: string;
}

interface LoginRequest {
  email: string;
  password: string;
}

/**
 * ユーザー登録
 */
export async function register(
  request: RegisterRequest
): Promise<{ data: AuthResponse | null; error: string | null }> {
  const result = await apiPost<AuthResponse, RegisterRequest>('/auth/register', request);
  if (result.data) {
    setAuthToken(result.data.access_token);
  }
  return result;
}

/**
 * ログイン
 */
export async function login(
  request: LoginRequest
): Promise<{ data: AuthResponse | null; error: string | null }> {
  const result = await apiPost<AuthResponse, LoginRequest>('/auth/login', request);
  if (result.data) {
    setAuthToken(result.data.access_token);
  }
  return result;
}

/**
 * 現在のユーザー情報を取得
 */
export async function getMe(): Promise<{ data: User | null; error: string | null }> {
  return apiGet<User>('/auth/me');
}

/**
 * プロフィール更新
 */
export async function updateProfile(
  request: ProfileUpdateRequest
): Promise<{ data: User | null; error: string | null }> {
  return apiPut<User, ProfileUpdateRequest>('/auth/profile', request);
}

/**
 * MCP用長寿命APIトークンを発行
 */
export async function createApiToken(): Promise<{ data: ApiTokenResponse | null; error: string | null }> {
  return apiPost<ApiTokenResponse, Record<string, never>>('/auth/api-token', {});
}
