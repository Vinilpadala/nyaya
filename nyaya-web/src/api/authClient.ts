import { requestApi, setAuthToken, clearAuthToken, getAuthToken } from './httpClient';
import { ChambersUser, JudicialRole } from '../types';

export interface BackendUserDTO {
  id: string;
  email: string;
  full_name: string;
  role: string;
  court_division: string;
  chambers_number: string;
  is_active: boolean;
  created_at: string;
}

export interface TokenResponseDTO {
  access_token: string;
  token_type: string;
  expires_in_minutes: number;
  user: BackendUserDTO;
}

export interface DemoUserDTO {
  email: string;
  password: string;
  full_name: string;
  role: string;
  court_division: string;
  chambers_number: string;
  description: string;
}

export function mapBackendUserToChambersUser(dto: BackendUserDTO): ChambersUser {
  return {
    id: dto.id,
    fullName: dto.full_name,
    role: (dto.role as JudicialRole) || 'RESEARCH_CLERK',
    title: dto.court_division || 'Commercial Division',
    courtDivision: dto.court_division,
    chambersNumber: dto.chambers_number,
    email: dto.email,
  };
}

export async function loginApi(email: string, password: string): Promise<ChambersUser> {
  const result = await requestApi<TokenResponseDTO>('/api/v1/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });

  if (result?.access_token) {
    setAuthToken(result.access_token);
  }

  return mapBackendUserToChambersUser(result.user);
}

export async function fetchMeApi(): Promise<ChambersUser> {
  const result = await requestApi<BackendUserDTO>('/api/v1/auth/me', {
    method: 'GET',
  }, true);

  return mapBackendUserToChambersUser(result);
}

export async function fetchDemoUsersApi(): Promise<DemoUserDTO[]> {
  try {
    return await requestApi<DemoUserDTO[]>('/api/v1/auth/demo-users', {
      method: 'GET',
    });
  } catch (err) {
    console.warn('Could not fetch demo users from backend:', err);
    return [];
  }
}

export function logoutApi(): void {
  clearAuthToken();
}

export function hasActiveToken(): boolean {
  return !!getAuthToken();
}
