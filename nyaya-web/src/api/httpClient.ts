export class ApiError extends Error {
  status: number;
  code?: string;
  details?: any;

  constructor(message: string, status: number = 500, code?: string, details?: any) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

const TOKEN_STORAGE_KEY = 'nyaya_chambers_token';

export function getAuthToken(): string | null {
  try {
    return localStorage.getItem(TOKEN_STORAGE_KEY);
  } catch {
    return null;
  }
}

export function setAuthToken(token: string): void {
  try {
    localStorage.setItem(TOKEN_STORAGE_KEY, token);
  } catch (err) {
    console.error('Failed to store session token:', err);
  }
}

export function clearAuthToken(): void {
  try {
    localStorage.removeItem(TOKEN_STORAGE_KEY);
  } catch (err) {
    console.error('Failed to clear session token:', err);
  }
}

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://nyaya-api.onrender.com';


export async function requestApi<T>(
  endpoint: string,
  options: RequestInit = {},
  requiresAuth: boolean = false
): Promise<T> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> || {}),
  };

  const token = getAuthToken();
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  } else if (requiresAuth) {
    throw new ApiError('Authentication credentials missing. Please sign in to Chambers.', 401, 'UNAUTHORIZED');
  }

  const url = endpoint.startsWith('http') ? endpoint : `${API_BASE_URL}${endpoint}`;

  let response: Response;
  try {
    response = await fetch(url, {
      ...options,
      headers,
    });
  } catch (netErr: any) {
    throw new ApiError(
      `Unable to reach Nyaya AI Chambers Backend (API offline at ${API_BASE_URL || 'http://127.0.0.1:8000'}).`,
      0,
      'NETWORK_ERROR',
      netErr.message
    );
  }


  let json: any = null;
  const text = await response.text();
  try {
    json = text ? JSON.parse(text) : null;
  } catch {
    // If not JSON
  }

  if (!response.ok) {
    const errorDetail = json?.error || json?.detail;
    const message =
      (typeof errorDetail === 'object' ? errorDetail.message : errorDetail) ||
      `Chambers API error: HTTP ${response.status} ${response.statusText}`;
    const code = typeof errorDetail === 'object' ? errorDetail.code : 'HTTP_ERROR';
    throw new ApiError(message, response.status, code, json?.error?.details);
  }

  if (json && typeof json === 'object' && 'data' in json) {
    return json.data as T;
  }

  return json as T;
}
