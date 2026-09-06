import { requestApi } from './httpClient';
import { AuditLogEntry } from '../types';

export interface BackendAuditLogDTO {
  id: string;
  timestamp: string;
  chambers_user: string;
  action: string;
  target: string;
  court_division: string;
  endpoint: string;
  ip_address: string;
  metadata_payload?: Record<string, any>;
}

export function mapBackendAuditToFrontend(dto: BackendAuditLogDTO): AuditLogEntry {
  const dateObj = new Date(dto.timestamp);
  const formattedTime = !isNaN(dateObj.getTime())
    ? dateObj.toLocaleString('en-IN', { timeZone: 'Asia/Kolkata' }) + ' IST'
    : dto.timestamp;

  return {
    id: dto.id,
    timestamp: formattedTime,
    chambersUser: dto.chambers_user,
    action: dto.action,
    target: dto.target,
    division: dto.court_division,
    ipAddress: dto.ip_address,
  };
}

export async function fetchAuditLogsApi(limit = 50, action?: string): Promise<AuditLogEntry[]> {
  let url = `/api/v1/audit-logs?limit=${limit}`;
  if (action) {
    url += `&action=${encodeURIComponent(action)}`;
  }
  const dtos = await requestApi<BackendAuditLogDTO[]>(url, { method: 'GET' }, true);
  return dtos.map(mapBackendAuditToFrontend);
}

export async function recordAuditLogApi(
  action: string,
  target: string,
  endpoint?: string,
  metadata?: Record<string, any>
): Promise<AuditLogEntry> {
  const body = {
    action,
    target,
    endpoint: endpoint || '/api/v1/client-session',
    metadata_payload: metadata || {},
  };
  const dto = await requestApi<BackendAuditLogDTO>(
    '/api/v1/audit-logs',
    {
      method: 'POST',
      body: JSON.stringify(body),
    },
    true
  );
  return mapBackendAuditToFrontend(dto);
}
