export type JudicialRole = 'JUDGE' | 'RESEARCH_CLERK' | 'REGISTRAR' | 'ADMIN';

export interface ChambersUser {
  id: string;
  fullName: string;
  role: JudicialRole;
  title: string;
  courtDivision: string;
  chambersNumber: string;
  email: string;
}

export type CitationTreatment = 'AFFIRMED' | 'OVERRULED' | 'DISTINGUISHED' | 'CONSIDERED' | 'APPLIED';

export interface CitationItem {
  id: string;
  caseName: string;
  citation: string;
  treatment: CitationTreatment;
  pinpointPara: string;
  benchStrength: number;
  court: string;
  year: number;
}

export interface JudicialCase {
  id: string;
  title: string;
  neutralCitation: string;
  standardCitation: string;
  court: string;
  judgmentDate: string;
  benchQuorum: string;
  benchStrength: number;
  commercialCategory: string;
  relevantStatute: string;
  ratioDecidendi: string;
  isGoodLaw: boolean;
  statusSummary: string;
  factsSummary: string;
  fullJudgmentText: string[];
  keyParagraphs: { number: number; text: string; highlightReason?: string }[];
  citationsMade: CitationItem[];
  isDemoData: boolean;
}

export interface StatuteSection {
  id: string;
  sectionNumber: string;
  heading: string;
  content: string;
  isAmended: boolean;
  amendmentNotes?: string;
  practicalGuidelines?: string[];
  landmarkPrecedents?: string[];
  isDemoData: boolean;
}

export interface StatuteItem {
  id: string;
  shortTitle: string;
  actNumber: string;
  enactmentYear: number;
  jurisdiction: string;
  overview: string;
  sections: StatuteSection[];
  isDemoData: boolean;
}

export interface DossierNote {
  id: string;
  type: 'HOLDING' | 'STATUTE_CHECK' | 'CHAMBERS_QUERY' | 'BENCH_DIRECTION';
  content: string;
  sourceReference: string;
  timestamp: string;
}

export interface CommercialSuitDossier {
  id: string;
  suitNumber: string;
  parties: string;
  commercialSubject: string;
  filingDate: string;
  nextHearingDate: string;
  stage: string;
  judicialNotes: string;
  pinnedCases: string[];
  pinnedSections: string[];
  dossierNotes: DossierNote[];
  items?: {
    id?: string;
    item_type: string;
    reference_id: string;
    title: string;
    excerpt?: string;
    pinpoint?: string;
  }[];
  isUrgentReliefContemplated: boolean;
  isSec12AExhausted: boolean;
}

export interface AuditLogEntry {
  id: string;
  timestamp: string;
  chambersUser: string;
  action: string;
  target: string;
  division: string;
  ipAddress: string;
}

export interface PinpointPassageDTO {
  paragraph_number: number;
  text: string;
  significance: string;
}

export interface CitationTreatmentRecord {
  treatment: 'AFFIRMED' | 'OVERRULED' | 'DISTINGUISHED' | 'CONSIDERED' | 'APPLIED' | 'MODIFIED' | string;
  citing_case: string;
  citation: string;
  year: number;
  court: string;
  bench_strength: number;
}

export interface CitationVerificationDTO {
  case_id: string;
  case_title: string;
  standard_citation: string;
  neutral_citation: string;
  court: string;
  judgment_date: string;
  bench_quorum: string;
  bench_strength: number;
  law_reporter_verified: boolean;
  official_reporter: string;
  good_law_status: string;
  is_good_law: boolean;
  treatment_history: CitationTreatmentRecord[];
  verification_notes: string;
  corpus_coverage_status?: 'VERIFIED_IN_CORPUS' | 'NO_TREATMENT_FOUND' | 'NEGATIVE_TREATMENT_FOUND' | 'INSUFFICIENT_CORPUS';
  is_demo_data?: boolean;
}

export interface RetrievedAuthorityDTO {
  id: string;
  title: string;
  standard_citation: string;
  neutral_citation: string;
  court: string;
  judgment_date: string;
  bench_quorum: string;
  bench_strength?: number;
  benchStrength?: number;
  is_good_law: boolean;
  status_summary: string;
  relevance_score: number;
  why_relevant: string;
  ratio_extract: string;
  pinpoint_passages: PinpointPassageDTO[];
  citation_verification?: CitationVerificationDTO;
  is_demo_data?: boolean;
}

export interface RetrievedStatuteDTO {
  id: string;
  statute_title: string;
  section_number: string;
  heading: string;
  content: string;
  amendment_notes?: string;
  why_relevant: string;
  is_demo_data?: boolean;
}

export interface ResearchTrailStep {
  step_number: number;
  stage: 'QUERY_ANALYSIS' | 'SOURCE_RETRIEVAL' | 'PASSAGE_EXTRACTION' | 'AI_SYNTHESIS';
  title: string;
  description: string;
  items_count: number;
  timestamp: string;
  details: string[];
}

export interface ResearchTrailDTO {
  query_analysis_step: ResearchTrailStep;
  retrieval_step: ResearchTrailStep;
  passage_extraction_step: ResearchTrailStep;
  ai_synthesis_step: ResearchTrailStep;
}

export interface UncertaintyAssessmentDTO {
  confidence_score: number;
  uncertainty_level: 'LOW' | 'MEDIUM' | 'HIGH';
  is_ambiguous: boolean;
  has_conflicting_authorities: boolean;
  reason: string;
  cautionary_guidance: string;
  corpus_limitation_note?: string;
  retrieval_quality_score?: number;
  score_margin?: number;
}

export interface ResearchSynthesisResponse {
  query: string;
  case_context?: string;
  jurisdiction: string;
  retrieved_authorities: RetrievedAuthorityDTO[];
  retrieved_statutes: RetrievedStatuteDTO[];
  citation_verifications?: CitationVerificationDTO[];
  research_trail?: ResearchTrailDTO;
  uncertainty_assessment?: UncertaintyAssessmentDTO;
  ai_generated_summary: string;
  ai_legal_analysis: string;
  cautious_inferences: string[];
  bench_action_points: string[];
  has_overruled_authorities: boolean;
  synthesis_engine?: string;
  fallback_notice?: string | null;
  historical_pattern_analysis?: HistoricalPatternAnalysisDTO | null;
  language?: string;
  original_query?: string | null;
  translated_query?: string | null;
  translated_summary?: string | null;
  translated_analysis?: string | null;
  translation_engine?: string | null;
  translation_notice?: string | null;
  is_demo_data?: boolean;
}

export interface PrecedentDispositionItem {
  case_title: string;
  standard_citation: string;
  court: string;
  year: number;
  bench_strength: number;
  legal_status: string;
  treatment_summary: string;
  procedural_posture: string;
  actual_disposition: string;
  disposition_provenance: string;
  ratio_summary: string;
  is_active_law: boolean;
}

export interface HistoricalPatternAnalysisDTO {
  query_issue: string;
  comparable_authorities_count: number;
  temporal_span: string;
  courts_represented: string[];
  bench_strength_breakdown: Record<string, number>;
  active_precedent_patterns: PrecedentDispositionItem[];
  overruled_precedent_patterns: PrecedentDispositionItem[];
  controlling_doctrine_summary: string;
  legal_regime_period: string;
  active_regime_status: string;
  methodology_note: string;
  data_readiness_notice: string;
  judicial_disclaimer: string;
}

export interface SavedResearchItem {
  id: string;
  user_id: string;
  matter_id?: string;
  query_text: string;
  case_context?: string;
  jurisdiction: string;
  lead_citation: string;
  lead_title: string;
  summary_extract: string;
  confidence_score: number;
  uncertainty_level: 'LOW' | 'MEDIUM' | 'HIGH';
  notes: string;
  tags: string;
  full_payload?: any;
  is_demo_data?: boolean;
  created_at: string;
}

export interface ResearchSessionHistoryItem {
  id: string;
  timestamp: string;
  query: string;
  jurisdiction: string;
  results_count: number;
  action: string;
}

