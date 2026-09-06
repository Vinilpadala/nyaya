import { requestApi } from './httpClient';
import { JudicialCase, CitationItem, CitationTreatment } from '../types';

export interface BackendCitationDTO {
  id: string;
  source_case_id: string;
  cited_case_name: string;
  cited_case_citation: string;
  treatment: string;
  pinpoint_paragraph: string;
}

export interface BackendCaseDTO {
  id: string;
  title: string;
  neutral_citation: string;
  standard_citation: string;
  court: string;
  judgment_date: string;
  bench_quorum: string;
  bench_strength: number;
  commercial_category: string;
  ratio_decidendi: string;
  is_good_law: boolean;
  status_summary: string;
  is_demo_data: boolean;
  full_text_snippet?: string;
  citations_made?: BackendCitationDTO[];
}

export function mapBackendCaseToJudicialCase(dto: BackendCaseDTO): JudicialCase {
  const citationsMade: CitationItem[] = (dto.citations_made || []).map((c) => ({
    id: c.id,
    caseName: c.cited_case_name,
    citation: c.cited_case_citation,
    treatment: (c.treatment as CitationTreatment) || 'CONSIDERED',
    pinpointPara: c.pinpoint_paragraph,
    benchStrength: 2,
    court: 'Supreme Court of India',
    year: 2022,
  }));

  // Create paragraph breakdown from snippet or ratio if explicit paragraphs are not separate
  const textSnippet = dto.full_text_snippet || dto.ratio_decidendi || '';
  const paragraphs = textSnippet
    .split(/\n\n+/)
    .map((p) => p.trim())
    .filter(Boolean);

  const keyParagraphs = paragraphs.map((p, idx) => {
    // Try to extract para number if starts with para X or numbers
    const paraMatch = p.match(/^para(?:graph)?\s*(\d+)|^\[?(\d+)\]?/i);
    const num = paraMatch ? parseInt(paraMatch[1] || paraMatch[2], 10) : idx + 1;
    return {
      number: num,
      text: p,
      highlightReason: idx === 0 ? 'Core Operative Holding / Ratio Decidendi' : 'Bench Observation',
    };
  });

  return {
    id: dto.id,
    title: dto.title,
    neutralCitation: dto.neutral_citation || 'Neutral Citation Pending',
    standardCitation: dto.standard_citation,
    court: dto.court,
    judgmentDate: dto.judgment_date,
    benchQuorum: dto.bench_quorum,
    benchStrength: dto.bench_strength || 2,
    commercialCategory: dto.commercial_category || 'Commercial Precedent',
    relevantStatute: dto.commercial_category,
    ratioDecidendi: dto.ratio_decidendi,
    isGoodLaw: dto.is_good_law,
    statusSummary: dto.status_summary || (dto.is_good_law ? 'Good Law' : 'Overruled / Questioned'),
    factsSummary: dto.ratio_decidendi,
    fullJudgmentText: paragraphs.length > 0 ? paragraphs : [dto.ratio_decidendi],
    keyParagraphs: keyParagraphs.length > 0 ? keyParagraphs : [
      {
        number: 1,
        text: dto.ratio_decidendi,
        highlightReason: 'Ratio Decidendi',
      },
    ],
    citationsMade,
    isDemoData: dto.is_demo_data ?? true,
  };
}

export interface CaseFilterParams {
  search?: string;
  court?: string;
  category?: string;
  good_law_only?: boolean;
}

export async function fetchCasesApi(filters?: CaseFilterParams): Promise<JudicialCase[]> {
  const queryParams = new URLSearchParams();
  if (filters?.search) queryParams.set('search', filters.search);
  if (filters?.court && filters.court !== 'ALL') queryParams.set('court', filters.court);
  if (filters?.category && filters.category !== 'ALL') queryParams.set('category', filters.category);
  if (filters?.good_law_only !== undefined) queryParams.set('good_law_only', String(filters.good_law_only));

  const url = `/api/v1/cases${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
  const dtos = await requestApi<BackendCaseDTO[]>(url, { method: 'GET' });
  return dtos.map(mapBackendCaseToJudicialCase);
}

export async function fetchCaseDetailApi(caseId: string): Promise<JudicialCase> {
  const dto = await requestApi<BackendCaseDTO>(`/api/v1/cases/${encodeURIComponent(caseId)}`, {
    method: 'GET',
  });
  return mapBackendCaseToJudicialCase(dto);
}
