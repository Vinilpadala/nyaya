import { requestApi } from './httpClient';
import { CommercialSuitDossier, DossierNote } from '../types';

export interface BackendDossierItemDTO {
  id?: string;
  dossier_id?: string;
  item_type: string; // 'CASE' | 'SECTION' | 'NOTE'
  reference_id: string;
  title: string;
  excerpt?: string;
  pinpoint?: string;
}

export interface BackendDossierDTO {
  id: string;
  user_id: string;
  matter_title: string;
  suit_number: string;
  judicial_notes: string;
  created_at: string;
  updated_at: string;
  items?: BackendDossierItemDTO[];
}

export interface BackendDossierCreateDTO {
  matter_title: string;
  suit_number: string;
  judicial_notes: string;
  items: BackendDossierItemDTO[];
}

export function mapBackendDossierToFrontend(dto: BackendDossierDTO): CommercialSuitDossier {
  const items = dto.items || [];

  const pinnedCases = items
    .filter((i) => i.item_type.toUpperCase() === 'CASE')
    .map((i) => i.title);

  const pinnedSections = items
    .filter((i) => i.item_type.toUpperCase() === 'SECTION')
    .map((i) => i.title);

  const dossierNotes: DossierNote[] = items
    .filter((i) => i.item_type.toUpperCase() === 'NOTE')
    .map((i, idx) => ({
      id: i.id || `note-${idx}`,
      type: 'BENCH_DIRECTION',
      content: i.title + (i.excerpt ? `: ${i.excerpt}` : ''),
      sourceReference: i.reference_id || 'Chambers Note',
      timestamp: dto.updated_at ? new Date(dto.updated_at).toLocaleTimeString('en-IN') + ' IST' : 'Session',
    }));

  // If there are raw judicial notes but no note items, populate one initial note
  if (dto.judicial_notes && dossierNotes.length === 0) {
    dossierNotes.push({
      id: `initial-notes-${dto.id}`,
      type: 'HOLDING',
      content: dto.judicial_notes,
      sourceReference: 'Chambers Record',
      timestamp: dto.created_at ? new Date(dto.created_at).toLocaleDateString('en-IN') : 'Initial Memo',
    });
  }

  const filingDateStr = dto.created_at
    ? new Date(dto.created_at).toLocaleDateString('en-IN', {
        day: '2-digit',
        month: 'short',
        year: 'numeric',
      })
    : 'Recent';

  const notesLower = (dto.judicial_notes || '').toLowerCase();

  return {
    id: dto.id,
    suitNumber: dto.suit_number,
    parties: dto.matter_title,
    commercialSubject: 'Commercial Dispute (Commercial Courts Act, 2015)',
    filingDate: filingDateStr,
    nextHearingDate: 'Listed for Regular Hearing',
    stage: 'Judicial Deliberation / Bench Memorandum',
    judicialNotes: dto.judicial_notes || '',
    pinnedCases,
    pinnedSections,
    dossierNotes,
    items,
    isUrgentReliefContemplated: notesLower.includes('urgent') || notesLower.includes('interim relief'),
    isSec12AExhausted: notesLower.includes('12a') || notesLower.includes('mediation exhausted'),
  };
}

export async function fetchDossiersApi(): Promise<CommercialSuitDossier[]> {
  const dtos = await requestApi<BackendDossierDTO[]>('/api/v1/dossiers', { method: 'GET' }, true);
  return dtos.map(mapBackendDossierToFrontend);
}

export async function fetchDossierDetailApi(dossierId: string): Promise<CommercialSuitDossier> {
  const dto = await requestApi<BackendDossierDTO>(
    `/api/v1/dossiers/${encodeURIComponent(dossierId)}`,
    { method: 'GET' },
    true
  );
  return mapBackendDossierToFrontend(dto);
}

export async function createDossierApi(payload: {
  matter_title: string;
  suit_number: string;
  judicial_notes?: string;
  items?: BackendDossierItemDTO[];
}): Promise<CommercialSuitDossier> {
  const body: BackendDossierCreateDTO = {
    matter_title: payload.matter_title,
    suit_number: payload.suit_number,
    judicial_notes: payload.judicial_notes || '',
    items: payload.items || [],
  };

  const dto = await requestApi<BackendDossierDTO>(
    '/api/v1/dossiers',
    {
      method: 'POST',
      body: JSON.stringify(body),
    },
    true
  );

  return mapBackendDossierToFrontend(dto);
}

export async function addDossierItemApi(
  dossierId: string,
  item: BackendDossierItemDTO
): Promise<CommercialSuitDossier> {
  const dto = await requestApi<BackendDossierDTO>(
    `/api/v1/dossiers/${encodeURIComponent(dossierId)}/items`,
    {
      method: 'POST',
      body: JSON.stringify(item),
    },
    true
  );
  return mapBackendDossierToFrontend(dto);
}

export async function removeDossierItemApi(
  dossierId: string,
  itemId: string
): Promise<CommercialSuitDossier> {
  const dto = await requestApi<BackendDossierDTO>(
    `/api/v1/dossiers/${encodeURIComponent(dossierId)}/items/${encodeURIComponent(itemId)}`,
    {
      method: 'DELETE',
    },
    true
  );
  return mapBackendDossierToFrontend(dto);
}

export async function updateDossierNotesApi(
  dossierId: string,
  judicialNotes: string
): Promise<CommercialSuitDossier> {
  const dto = await requestApi<BackendDossierDTO>(
    `/api/v1/dossiers/${encodeURIComponent(dossierId)}`,
    {
      method: 'PATCH',
      body: JSON.stringify({ judicial_notes: judicialNotes }),
    },
    true
  );
  return mapBackendDossierToFrontend(dto);
}

export async function deleteDossierApi(dossierId: string): Promise<void> {
  await requestApi<any>(
    `/api/v1/dossiers/${encodeURIComponent(dossierId)}`,
    {
      method: 'DELETE',
    },
    true
  );
}
