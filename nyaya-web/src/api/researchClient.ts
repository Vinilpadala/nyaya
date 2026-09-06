import {
  ResearchSynthesisResponse,
  SavedResearchItem,
  ResearchSessionHistoryItem,
} from '../types';
import { requestApi } from './httpClient';

export interface ResearchQueryPayload {
  query: string;
  case_context?: string;
  jurisdiction?: string;
  statute_filter?: string;
  include_overruled?: boolean;
  min_bench_strength?: number;
  language?: string;
}

export async function executeResearchApi(
  payload: ResearchQueryPayload
): Promise<ResearchSynthesisResponse> {
  return await requestApi<ResearchSynthesisResponse>('/api/v1/research/query', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function saveResearchApi(payload: {
  matter_id?: string;
  query_text: string;
  case_context?: string;
  jurisdiction: string;
  lead_citation: string;
  lead_title: string;
  summary_extract: string;
  confidence_score: number;
  uncertainty_level: string;
  notes: string;
  tags: string;
  full_payload?: any;
}): Promise<SavedResearchItem> {
  return await requestApi<SavedResearchItem>('/api/v1/research/save', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function fetchSavedResearchApi(): Promise<SavedResearchItem[]> {
  return await requestApi<SavedResearchItem[]>('/api/v1/research/saved', {
    method: 'GET',
  });
}

export async function deleteSavedResearchApi(id: string): Promise<boolean> {
  return await requestApi<boolean>(`/api/v1/research/saved/${encodeURIComponent(id)}`, {
    method: 'DELETE',
  });
}

export async function fetchSessionHistoryApi(): Promise<ResearchSessionHistoryItem[]> {
  return await requestApi<ResearchSessionHistoryItem[]>('/api/v1/research/session-history', {
    method: 'GET',
  });
}
