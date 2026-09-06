import { requestApi } from './httpClient';
import { StatuteItem, StatuteSection } from '../types';

export interface BackendStatuteSectionDTO {
  id: string;
  statute_id: string;
  section_number: string;
  heading: string;
  content: string;
  is_amended: boolean;
  amendment_notes: string;
  is_demo_data: boolean;
}

export interface BackendStatuteDTO {
  id: string;
  short_title: string;
  act_number: string;
  enactment_year: number;
  jurisdiction: string;
  is_demo_data: boolean;
  sections?: BackendStatuteSectionDTO[];
}

export function mapBackendSectionToStatuteSection(sec: BackendStatuteSectionDTO): StatuteSection {
  return {
    id: sec.id,
    sectionNumber: sec.section_number,
    heading: sec.heading,
    content: sec.content,
    isAmended: sec.is_amended,
    amendmentNotes: sec.amendment_notes || undefined,
    practicalGuidelines: sec.amendment_notes
      ? [sec.amendment_notes]
      : ['Verify strict compliance with procedural rules before the Commercial Division.'],
    landmarkPrecedents: [],
    isDemoData: sec.is_demo_data ?? true,
  };
}

export function mapBackendStatuteToStatuteItem(dto: BackendStatuteDTO): StatuteItem {
  return {
    id: dto.id,
    shortTitle: dto.short_title,
    actNumber: dto.act_number,
    enactmentYear: dto.enactment_year,
    jurisdiction: dto.jurisdiction,
    overview: `${dto.short_title} (${dto.act_number}) applies to commercial causes in ${dto.jurisdiction}.`,
    sections: (dto.sections || []).map(mapBackendSectionToStatuteSection),
    isDemoData: dto.is_demo_data ?? true,
  };
}

export async function fetchStatutesApi(search?: string): Promise<StatuteItem[]> {
  const query = search ? `?search=${encodeURIComponent(search)}` : '';
  const dtos = await requestApi<BackendStatuteDTO[]>(`/api/v1/statutes${query}`, { method: 'GET' });
  return dtos.map(mapBackendStatuteToStatuteItem);
}

export async function fetchStatuteDetailApi(statuteId: string): Promise<StatuteItem> {
  const dto = await requestApi<BackendStatuteDTO>(`/api/v1/statutes/${encodeURIComponent(statuteId)}`, {
    method: 'GET',
  });
  return mapBackendStatuteToStatuteItem(dto);
}

export async function fetchStatuteSectionApi(sectionId: string): Promise<StatuteSection> {
  const dto = await requestApi<BackendStatuteSectionDTO>(
    `/api/v1/statutes/sections/${encodeURIComponent(sectionId)}`,
    { method: 'GET' }
  );
  return mapBackendSectionToStatuteSection(dto);
}
