import React, { useState } from 'react';
import {
  Search,
  BookOpen,
  CheckCircle,
  XCircle,
  FileText,
  Bookmark,
  SlidersHorizontal,
  ShieldAlert,
  ExternalLink,
  Copy,
  Check,
  History,
  ShieldCheck,
  Scale,
} from 'lucide-react';
import { useChambers } from '../../context/ChambersContext';
import {
  ResearchSynthesisResponse,
  RetrievedAuthorityDTO,
  RetrievedStatuteDTO,
} from '../../types';
import { executeResearchApi, saveResearchApi } from '../../api/researchClient';
import { DemoDataBadge } from '../common/DemoDataBadge';
import { ApiErrorBanner } from '../common/ApiErrorBanner';
import { ResearchTrailViewer } from './ResearchTrailViewer';
import { CitationVerificationCard } from './CitationVerificationCard';
import { UncertaintyBanner } from './UncertaintyBanner';
import { SavedResearchDrawer } from './SavedResearchDrawer';
import { HistoricalPatternCard } from './HistoricalPatternCard';

export interface SihDemoScenario {
  id: string;
  label: string;
  badge: string;
  badgeColor?: string;
  query: string;
  context: string;
  jurisdiction: string;
  includeOverruled: boolean;
  language?: string;
}

const SIH_DEMO_SCENARIOS: SihDemoScenario[] = [
  {
    id: 'sih-1',
    label: 'Demo 1: Mandatory Mediation (Sec 12A)',
    badge: 'Commercial Courts Act',
    badgeColor: '#1e3a8a',
    query:
      'Whether pre-institution mediation under Section 12A Commercial Courts Act is mandatory and consequences of non-exhaustion under Order VII Rule 11 CPC',
    context:
      'Commercial suit for breach of software license agreement; defendant moved application for rejection of plaint on ground that no urgent interim relief was contemplated.',
    jurisdiction: 'Supreme Court of India',
    includeOverruled: false,
    language: 'en',
  },
  {
    id: 'sih-2',
    label: 'Demo 2: Legal Evolution & Overruled Law',
    badge: 'Stamping & Overruling',
    badgeColor: '#dc2626',
    query:
      'Arbitration clause unstamped document enforceability Section 11 Appointment of Arbitrator',
    context:
      'Commercial concession agreement containing arbitration clause not stamped in accordance with State Stamp Act; respondent objects to Section 11 appointment.',
    jurisdiction: 'ALL',
    includeOverruled: true,
    language: 'en',
  },
  {
    id: 'sih-3',
    label: 'Demo 3: Responsible AI & Boundary Refusal',
    badge: 'Guardrail / Out-of-Scope',
    badgeColor: '#b45309',
    query:
      'Anticipatory bail Section 438 CrPC criminal trial arrest protection',
    context:
      'Accused seeking pre-arrest bail in non-commercial criminal proceeding.',
    jurisdiction: 'ALL',
    includeOverruled: false,
    language: 'en',
  },
  {
    id: 'sih-4',
    label: 'Demo 4: Liquidated Damages vs Proof of Loss',
    badge: 'Sec 74 Interplay',
    badgeColor: '#047857',
    query:
      'Whether Section 74 Indian Contract Act requires proof of actual commercial loss for liquidated damages or forfeiture',
    context:
      'Dispute regarding forfeiture of earnest money deposit and recovery of pre-estimated liquidated damages under commercial supply agreement.',
    jurisdiction: 'Supreme Court of India',
    includeOverruled: false,
    language: 'en',
  },
  {
    id: 'sih-5',
    label: 'Demo 5: Non-Arbitrability 4-Fold Test',
    badge: 'Arbitrability Doctrine',
    badgeColor: '#4338ca',
    query:
      'Arbitrability of dispute four-fold test actions in rem sovereign functions Section 8 Section 11',
    context:
      'Commercial dispute where respondent contends the subject matter involves rights in rem and is excluded from arbitration.',
    jurisdiction: 'Supreme Court of India',
    includeOverruled: false,
    language: 'en',
  },
  {
    id: 'sih-6-te',
    label: 'Demo 6 (Telugu): సెక్షన్ 12A తప్పనిసరి మధ్యవర్తిత్వం',
    badge: 'తెలుగు (Telugu MVP)',
    badgeColor: '#0284c7',
    query:
      'వాణిజ్య న్యాయస్థానాల చట్టం సెక్షన్ 12A ప్రకారం ముందస్తు సంస్థాగత మధ్యవర్తిత్వం తప్పనిసరి కాదా మరియు పాటించకపోతే ఆర్డర్ 7 రూల్ 11 కింద దావా తిరస్కరణ పరిణామాలు',
    context:
      'సాఫ్ట్‌వేర్ లైసెన్స్ ఒప్పందం ఉల్లంఘనపై వాణిజ్య దావా; అత్యవసర మధ్యంతర ఉపశమనం కోరలేదు కాబట్టి దావాను తిరస్కరించాలని ప్రతివాది దరఖాస్తు దాఖలు చేశారు.',
    jurisdiction: 'Supreme Court of India',
    includeOverruled: false,
    language: 'te',
  },
  {
    id: 'sih-7-hi',
    label: 'Demo 7 (Hindi): धारा 12A अनिवार्य पूर्व-संस्थागत मध्यस्थता',
    badge: 'हिन्दी (Hindi MVP)',
    badgeColor: '#ea580c',
    query:
      'क्या वाणिज्यिक न्यायालय अधिनियम की धारा 12A के तहत पूर्व-संस्थागत मध्यस्थता अनिवार्य है और अनुपालन न करने पर आदेश VII नियम 11 सीपीसी के परिणाम',
    context:
      'सॉफ्टवेयर लाइसेंस समझौते के उल्लंघन के लिए वाणिज्यिक वाद; प्रतिवादी ने इस आधार पर वाद खारिज करने का आवेदन किया कि कोई तत्काल अंतरिम राहत नहीं मांगी गई थी।',
    jurisdiction: 'Supreme Court of India',
    includeOverruled: false,
    language: 'hi',
  },
];

export const LegalResearchWorkspace: React.FC = () => {
  const {
    selectedDossier,
    addDossierNote,
    logout,
    addAuditLog,
    setSelectedCase,

    cases,
    setActiveTab,
    currentLanguage,
    setCurrentLanguage,
    uiText,
  } = useChambers();

  // Query & Facet States
  const [query, setQuery] = useState(SIH_DEMO_SCENARIOS[0].query);
  const [caseContext, setCaseContext] = useState(SIH_DEMO_SCENARIOS[0].context);
  const [jurisdiction, setJurisdiction] = useState(SIH_DEMO_SCENARIOS[0].jurisdiction);
  const [includeOverruled, setIncludeOverruled] = useState(false);
  const [minBenchStrength, setMinBenchStrength] = useState<number>(0);
  const [isSearching, setIsSearching] = useState(false);
  const [queryError, setQueryError] = useState<string | null>(null);

  // Results State
  const [synthesis, setSynthesis] = useState<ResearchSynthesisResponse | null>(null);
  const [selectedAuthorityModal, setSelectedAuthorityModal] =
    useState<RetrievedAuthorityDTO | null>(null);

  // Multilingual Dual-View Toggle State
  const [showAuthoritativeEnglish, setShowAuthoritativeEnglish] = useState(false);

  // Phase 4: Trust, Explainability, Drawer & Bookmark States
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const [isSaveModalOpen, setIsSaveModalOpen] = useState(false);
  const [saveNotes, setSaveNotes] = useState('');
  const [saveTags, setSaveTags] = useState('Commercial Courts Act, Mandatory Mediation');
  const [isSaving, setIsSaving] = useState(false);
  const [saveSuccessMsg, setSaveSuccessMsg] = useState<string | null>(null);

  // Copy feedback
  const [copiedCitation, setCopiedCitation] = useState<string | null>(null);
  const [pinnedItems, setPinnedItems] = useState<Set<string>>(new Set());

  const handleExecuteResearch = async (
    e?: React.FormEvent,
    customQuery?: string,
    customContext?: string,
    customJurisdiction?: string
  ) => {
    if (e) e.preventDefault();
    const qToRun = customQuery || query;
    if (!qToRun.trim()) return;

    setIsSearching(true);
    setQueryError(null);
    const targetJurisdiction = customJurisdiction || jurisdiction;
    addAuditLog('LEGAL_RESEARCH_QUERY', `Query: ${qToRun.substring(0, 50)}... [${targetJurisdiction}] [${currentLanguage}]`);

    try {
      const res = await executeResearchApi({
        query: qToRun.trim(),
        case_context: (customContext !== undefined ? customContext : caseContext).trim() || undefined,
        jurisdiction: targetJurisdiction,
        include_overruled: includeOverruled,
        min_bench_strength: minBenchStrength > 0 ? minBenchStrength : undefined,
        language: currentLanguage,
      });
      setSynthesis(res);
      // If result has translated summary, default to showing translated view
      if (res.translated_summary) {
        setShowAuthoritativeEnglish(false);
      }
    } catch (err: any) {
      console.error('Error executing legal research query:', err);
      if (err?.status === 401 || err?.message?.includes('User account not found') || err?.message?.includes('deactivated')) {
        logout();
      } else {
        setQueryError(err.message || 'Error executing legal research query against backend.');
      }
    }
 finally {
      setIsSearching(false);
    }
  };

  const handleApplyPreset = (item: SihDemoScenario) => {
    setQuery(item.query);
    setCaseContext(item.context);
    setJurisdiction(item.jurisdiction);
    setIncludeOverruled(Boolean(item.includeOverruled));
    setQueryError(null);
    if (item.language) {
      setCurrentLanguage(item.language as any);
    }
  };

  const handleSelectSavedQuery = (q: string, ctx?: string, jur?: string) => {
    setQuery(q);
    if (ctx !== undefined) setCaseContext(ctx);
    if (jur !== undefined) setJurisdiction(jur);
    handleExecuteResearch(undefined, q, ctx, jur);
  };

  const handleCopyCitation = (citation: string) => {
    navigator.clipboard.writeText(citation);
    setCopiedCitation(citation);
    setTimeout(() => setCopiedCitation(null), 2000);
  };

  const handlePinAuthority = (auth: RetrievedAuthorityDTO) => {
    if (!selectedDossier) return;
    addDossierNote(
      selectedDossier.id,
      `[Retrieved Authority] ${auth.title} (${auth.standard_citation}) - Ratio: ${auth.ratio_extract}`,
      auth.standard_citation
    );
    setPinnedItems((prev) => new Set(prev).add(auth.id));
  };

  const handlePinStatute = (statute: RetrievedStatuteDTO) => {
    if (!selectedDossier) return;
    addDossierNote(
      selectedDossier.id,
      `[Retrieved Statute] ${statute.statute_title} - ${statute.section_number}: ${statute.heading}`,
      `${statute.statute_title} ${statute.section_number}`
    );
    setPinnedItems((prev) => new Set(prev).add(statute.id));
  };

  const handleOpenInSplitPane = (auth: RetrievedAuthorityDTO) => {
    const fullCase = cases.find(
      (c) => c.standardCitation === auth.standard_citation || c.id === auth.id
    );
    if (fullCase) {
      setSelectedCase(fullCase);
      setActiveTab('precedents');
    }
  };

  const handleSaveResearchToPortfolio = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!synthesis) return;

    setIsSaving(true);
    try {
      const leadAuth = synthesis.retrieved_authorities[0];
      await saveResearchApi({
        matter_id: selectedDossier?.suitNumber || 'PORTFOLIO',
        query_text: synthesis.query,
        case_context: synthesis.case_context,
        jurisdiction: synthesis.jurisdiction,
        lead_citation: leadAuth?.standard_citation || 'Commercial Precedent',
        lead_title: leadAuth?.title || 'Commercial Synthesis',
        summary_extract: synthesis.ai_generated_summary,
        confidence_score: synthesis.uncertainty_assessment?.confidence_score || 0.95,
        uncertainty_level: synthesis.uncertainty_assessment?.uncertainty_level || 'LOW',
        notes: saveNotes,
        tags: saveTags,
        full_payload: synthesis,
      });

      addAuditLog('RESEARCH_BOOKMARKED', `Bookmarked query: ${synthesis.query.substring(0, 40)}...`);
      setSaveSuccessMsg('Research synthesis bookmarked to Chambers Portfolio successfully.');
      setTimeout(() => {
        setSaveSuccessMsg(null);
        setIsSaveModalOpen(false);
        setSaveNotes('');
      }, 1800);
    } catch (err) {
      console.error('Error saving research:', err);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Research Query & Context Panel */}
      <div className="gov-panel">
        <div className="gov-panel-header" style={{ justifyContent: 'space-between' }}>
          <span className="gov-panel-title">
            <Search size={16} /> {uiText.searchPanelTitle || 'Commercial Court Legal Research Engine & Precedent Synthesizer'}
          </span>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <button
              type="button"
              className="gov-btn gov-btn-secondary"
              onClick={() => setIsDrawerOpen(true)}
              style={{ fontSize: '0.75rem', padding: '4px 10px', gap: '5px' }}
            >
              <Bookmark size={13} style={{ color: 'var(--gov-gold-600)' }} />
              <History size={13} />
              <span>Chambers Archive & History</span>
            </button>
            <DemoDataBadge size="small" />
          </div>
        </div>

        <div className="gov-panel-body">
          {/* Smart India Hackathon Demonstration Scenarios */}
          <div style={{ marginBottom: '16px' }}>
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                marginBottom: '8px',
              }}
            >
              <div
                style={{
                  fontSize: '0.75rem',
                  fontWeight: 600,
                  color: 'var(--gov-slate-600)',
                  textTransform: 'uppercase',
                  letterSpacing: '0.04em',
                }}
              >
                Smart India Hackathon (SIH) Demonstration Scenarios:
              </div>
              <span style={{ fontSize: '0.7rem', color: 'var(--gov-slate-500)' }}>
                Click to load verified judicial benchmark scenario
              </span>
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
              {SIH_DEMO_SCENARIOS.map((item) => {
                const isSelected = query === item.query;
                return (
                  <button
                    key={item.id}
                    type="button"
                    onClick={() => handleApplyPreset(item)}
                    style={{
                      backgroundColor: isSelected ? '#f0f4f8' : '#ffffff',
                      border: isSelected ? '1.5px solid var(--gov-navy-800)' : '1px solid var(--gov-slate-300)',
                      padding: '6px 12px',
                      fontSize: '0.75rem',
                      color: 'var(--gov-navy-900)',
                      cursor: 'pointer',
                      borderRadius: 'var(--border-radius-sm)',
                      textAlign: 'left',
                      fontWeight: isSelected ? 600 : 500,
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px',
                      boxShadow: isSelected ? '0 1px 3px rgba(0,0,0,0.08)' : 'none',
                    }}
                    title={item.query}
                  >
                    <span>{item.label}</span>
                    <span
                      style={{
                        fontSize: '0.65rem',
                        padding: '1px 6px',
                        borderRadius: '3px',
                        backgroundColor: item.badgeColor ? `${item.badgeColor}15` : '#f1f5f9',
                        color: item.badgeColor || 'var(--gov-slate-700)',
                        border: `1px solid ${item.badgeColor || '#cbd5e1'}`,
                        fontWeight: 600,
                      }}
                    >
                      {item.badge}
                    </span>
                  </button>
                );
              })}
            </div>
          </div>

          {queryError && (
            <ApiErrorBanner
              title="Legal Research Engine Unavailable"
              message={queryError}
              onRetry={() => handleExecuteResearch()}
            />
          )}

          <form onSubmit={(e) => handleExecuteResearch(e)}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {/* Query Field */}
              <div>
                <label
                  htmlFor="txt-query"
                  style={{
                    display: 'block',
                    fontSize: '0.8rem',
                    fontWeight: 600,
                    color: 'var(--gov-slate-800)',
                    marginBottom: '4px',
                  }}
                >
                  Natural-Language Judicial Issue / Legal Proposition:
                </label>
                <input
                  id="txt-query"
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="e.g. Whether Section 12A Commercial Courts Act pre-institution mediation is mandatory before filing commercial suit..."
                  style={{
                    width: '100%',
                    padding: '9px 12px',
                    fontSize: '0.875rem',
                    border: '1px solid var(--gov-slate-300)',
                    borderRadius: 'var(--border-radius-sm)',
                    fontFamily: 'var(--font-sans)',
                  }}
                />
              </div>

              {/* Case Context Field */}
              <div>
                <label
                  htmlFor="txt-context"
                  style={{
                    display: 'block',
                    fontSize: '0.8rem',
                    fontWeight: 600,
                    color: 'var(--gov-slate-800)',
                    marginBottom: '4px',
                  }}
                >
                  Ongoing Matter Factual Context (Optional — for pinpointing commercial nexus):
                </label>
                <textarea
                  id="txt-context"
                  rows={2}
                  value={caseContext}
                  onChange={(e) => setCaseContext(e.target.value)}
                  placeholder="e.g. Commercial suit for recovery arising out of software supply contract; application moved under Order VII Rule 11 CPC on grounds of non-exhaustion of mediation..."
                  style={{
                    width: '100%',
                    padding: '8px 12px',
                    fontSize: '0.825rem',
                    border: '1px solid var(--gov-slate-300)',
                    borderRadius: 'var(--border-radius-sm)',
                    fontFamily: 'var(--font-sans)',
                    resize: 'vertical',
                  }}
                />
              </div>

              {/* Facets & Filters Row */}
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
                  gap: '14px',
                  paddingTop: '6px',
                }}
              >
                <div>
                  <label
                    htmlFor="sel-jurisdiction"
                    style={{
                      display: 'block',
                      fontSize: '0.75rem',
                      fontWeight: 600,
                      color: 'var(--gov-slate-700)',
                      marginBottom: '4px',
                    }}
                  >
                    Jurisdiction / Target Court:
                  </label>
                  <select
                    id="sel-jurisdiction"
                    value={jurisdiction}
                    onChange={(e) => setJurisdiction(e.target.value)}
                    style={{
                      width: '100%',
                      padding: '7px 10px',
                      fontSize: '0.8rem',
                      border: '1px solid var(--gov-slate-300)',
                      borderRadius: 'var(--border-radius-sm)',
                    }}
                  >
                    <option value="Supreme Court of India">Supreme Court of India</option>
                    <option value="High Court of Delhi">High Court of Delhi (Commercial Division)</option>
                    <option value="High Court of Bombay">High Court of Bombay (Commercial Division)</option>
                    <option value="ALL">All Indexed Benches (Curated Benchmark Corpus)</option>
                  </select>
                </div>

                <div>
                  <label
                    htmlFor="sel-bench"
                    style={{
                      display: 'block',
                      fontSize: '0.75rem',
                      fontWeight: 600,
                      color: 'var(--gov-slate-700)',
                      marginBottom: '4px',
                    }}
                  >
                    Minimum Bench Quorum Strength:
                  </label>
                  <select
                    id="sel-bench"
                    value={minBenchStrength}
                    onChange={(e) => setMinBenchStrength(Number(e.target.value))}
                    style={{
                      width: '100%',
                      padding: '7px 10px',
                      fontSize: '0.8rem',
                      border: '1px solid var(--gov-slate-300)',
                      borderRadius: 'var(--border-radius-sm)',
                    }}
                  >
                    <option value={0}>Any Bench Quorum</option>
                    <option value={2}>Division Bench (2+ Judges)</option>
                    <option value={3}>Full Bench (3+ Judges)</option>
                    <option value={5}>Constitution Bench (5+ Judges)</option>
                  </select>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '20px' }}>
                  <input
                    type="checkbox"
                    id="chk-overruled"
                    checked={includeOverruled}
                    onChange={(e) => setIncludeOverruled(e.target.checked)}
                    style={{ width: '16px', height: '16px', cursor: 'pointer' }}
                  />
                  <label
                    htmlFor="chk-overruled"
                    style={{ fontSize: '0.8rem', color: 'var(--gov-slate-700)', cursor: 'pointer' }}
                  >
                    Include Overruled Authorities (for historical tracing)
                  </label>
                </div>
              </div>

              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '12px', flexWrap: 'wrap', gap: '8px' }}>
                <div style={{ fontSize: '0.75rem', color: isSearching ? 'var(--gov-navy-800)' : 'var(--gov-slate-500)', fontStyle: isSearching ? 'italic' : 'normal', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  {isSearching ? (
                    <>
                      <span className="gov-spinner" style={{ width: '12px', height: '12px', display: 'inline-block' }} />
                      Consulting Commercial Precedents & Statutes • Evaluating Quorums • Grounding Judicial Synthesis...
                    </>
                  ) : (
                    'Verified against official law reporters and central statutory enactments'
                  )}
                </div>
                <button
                  type="submit"
                  className="gov-btn gov-btn-primary"
                  style={{ padding: '9px 20px', minWidth: '170px' }}
                  disabled={isSearching}
                >
                  <Search size={15} />
                  {isSearching ? (uiText.searchingButton || 'Grounding Synthesis...') : (uiText.searchButton || 'Search & Synthesize')}
                </button>
              </div>
            </div>
          </form>
        </div>
      </div>

      {/* Structured Research Synthesis Results */}
      {synthesis && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>
          {/* Overview & Action Toolbar */}
          <div
            style={{
              padding: '12px 18px',
              backgroundColor: '#ffffff',
              border: '1px solid var(--gov-slate-300)',
              borderRadius: 'var(--border-radius-sm)',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              flexWrap: 'wrap',
              gap: '12px',
            }}
          >
            <div>
              <span style={{ fontSize: '0.825rem', color: 'var(--gov-slate-600)' }}>
                Showing verified results for:{' '}
                <strong style={{ color: 'var(--gov-navy-900)' }}>"{synthesis.original_query || synthesis.query}"</strong>
              </span>
              {synthesis.translated_query && (
                <div style={{ fontSize: '0.725rem', color: 'var(--gov-slate-500)', marginTop: '2px' }}>
                  Normalized Legal Concepts (Supreme Court Index): <em style={{ color: 'var(--gov-navy-800)' }}>"{synthesis.translated_query}"</em>
                </div>
              )}
              <div style={{ fontSize: '0.725rem', color: 'var(--gov-slate-500)', marginTop: '2px' }}>
                Jurisdiction: <strong>{synthesis.jurisdiction}</strong> • {synthesis.retrieved_authorities.length} Precedents •{' '}
                {synthesis.retrieved_statutes.length} Statutory Sections
              </div>
            </div>

            <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
              <button
                type="button"
                className="gov-btn gov-btn-secondary"
                style={{ fontSize: '0.75rem', padding: '6px 12px' }}
                onClick={() => setIsSaveModalOpen(true)}
              >
                <Bookmark size={13} style={{ color: 'var(--gov-gold-600)' }} /> Bookmark This Research
              </button>

              <button
                type="button"
                className="gov-btn gov-btn-secondary"
                style={{ fontSize: '0.75rem', padding: '6px 12px' }}
                onClick={() => {
                  window.scrollTo({ top: 0, behavior: 'smooth' });
                }}
              >
                <SlidersHorizontal size={13} /> Refine Parameters
              </button>
            </div>
          </div>

          {/* Persistent Notice to Bench */}
          <div
            style={{
              padding: '10px 16px',
              backgroundColor: '#f8fafc',
              border: '1px solid var(--gov-slate-300)',
              borderLeft: '4px solid var(--gov-navy-800)',
              borderRadius: 'var(--border-radius-sm)',
              fontSize: '0.75rem',
              color: 'var(--gov-slate-700)',
              lineHeight: '1.45',
            }}
          >
            <strong style={{ color: 'var(--gov-navy-900)' }}>NOTICE TO BENCH: </strong>
            Legal grounding is confined to the curated commercial-court benchmark repository. It is not an exhaustive national legal database. Formal verification with authoritative law reports is required before reliance in judicial orders.
          </div>

          {/* Phase 4: Precedent Status Warning Alert for Overruled Authorities */}
          {synthesis.has_overruled_authorities && (
            <div
              style={{
                display: 'flex',
                alignItems: 'flex-start',
                gap: '12px',
                padding: '12px 16px',
                backgroundColor: '#fef2f2',
                border: '1px solid #fecaca',
                borderLeft: '5px solid #dc2626',
                borderRadius: 'var(--border-radius-sm)',
                boxShadow: 'var(--gov-shadow-sm)',
              }}
            >
              <ShieldAlert size={20} style={{ color: '#dc2626', flexShrink: 0, marginTop: '2px' }} />
              <div>
                <div style={{ fontSize: '0.85rem', fontWeight: 700, color: '#991b1b', marginBottom: '2px' }}>
                  Precedent Status Alert: Overruled / Historical Authority Present
                </div>
                <div style={{ fontSize: '0.775rem', color: '#7f1d1d', lineHeight: '1.45' }}>
                  This research retrieval includes one or more authorities that have received negative treatment or have been expressly overruled by a larger Constitution Bench (e.g., <em>In Re: Interplay</em> [7-Judge Bench] superseding <em>SMS Tea Estates</em>). Overruled precedents are preserved solely for historical lineage and must not be cited as current governing law.
                </div>
              </div>
            </div>
          )}

          {/* Phase 4: Uncertainty Banner (Communicating Insufficient Evidence or Ambiguity) */}
          {synthesis.uncertainty_assessment && (
            <UncertaintyBanner assessment={synthesis.uncertainty_assessment} />
          )}

          {/* Phase 4: 4-Step Explainability Research Trail */}
          {synthesis.research_trail && (
            <ResearchTrailViewer trail={synthesis.research_trail} />
          )}

          {/* Phase 5B: Historical Precedent Pattern Analysis (Non-ML Empirical Benchmark) */}
          {synthesis.historical_pattern_analysis && (
            <HistoricalPatternCard analysis={synthesis.historical_pattern_analysis} />
          )}

          {/* Strict Separation Callout */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              padding: '8px 14px',
              backgroundColor: '#f1f5f9',
              borderLeft: '4px solid var(--gov-navy-800)',
              fontSize: '0.725rem',
              color: 'var(--gov-slate-700)',
            }}
          >
            <div>
              <strong style={{ color: 'var(--gov-navy-900)' }}>Judicial Integrity Standard: </strong>
              Source Materials (Judgments & Statutes) are strictly separated from AI-Generated Analysis & Inferences.
            </div>
            <span style={{ color: 'var(--gov-slate-500)' }}>No hallucinated or fabricated citations</span>
          </div>

          {/* SECTION 1: Objective AI-Generated Summary (Settled Legal Principles) */}
          <div className="gov-panel">
            <div className="gov-panel-header" style={{ backgroundColor: '#fafbfc' }}>
              <span className="gov-panel-title">
                <FileText size={16} color="var(--gov-navy-800)" /> 1. AI-GENERATED RESEARCH BRIEFING: Objective Judicial Summary (Settled Law)
              </span>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
                {synthesis.language && synthesis.language !== 'en' && (
                  <span
                    style={{
                      fontSize: '0.675rem',
                      padding: '2px 8px',
                      backgroundColor: '#f5f3ff',
                      color: '#6d28d9',
                      border: '1px solid #ddd6fe',
                      fontWeight: 600,
                      borderRadius: '2px',
                    }}
                  >
                    🌐 {synthesis.language === 'te' ? 'తెలుగు (Telugu MVP)' : synthesis.language === 'hi' ? 'हिन्दी (Hindi MVP)' : synthesis.language.toUpperCase()}
                  </span>
                )}
                {synthesis.synthesis_engine && (
                  <span
                    style={{
                      fontSize: '0.675rem',
                      padding: '2px 8px',
                      backgroundColor: synthesis.synthesis_engine.includes('Gemini') ? '#f0fdf4' : '#fffbeb',
                      color: synthesis.synthesis_engine.includes('Gemini') ? '#166534' : '#92400e',
                      border: `1px solid ${synthesis.synthesis_engine.includes('Gemini') ? '#bbf7d0' : '#fde68a'}`,
                      fontWeight: 600,
                      borderRadius: '2px',
                    }}
                  >
                    {synthesis.synthesis_engine.includes('Gemini') ? '✨ ' : '🛡️ '}
                    {synthesis.synthesis_engine}
                  </span>
                )}
                <span
                  style={{
                    fontSize: '0.7rem',
                    padding: '2px 8px',
                    backgroundColor: '#e0f2fe',
                    color: 'var(--gov-navy-800)',
                    border: '1px solid #bae6fd',
                    fontWeight: 600,
                  }}
                >
                  Source-Grounded • Verbatim Backed
                </span>
              </div>
            </div>
            {synthesis.fallback_notice && (
              <div
                style={{
                  padding: '8px 16px',
                  backgroundColor: '#fffbeb',
                  borderBottom: '1px solid #fde68a',
                  fontSize: '0.75rem',
                  color: '#92400e',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                }}
              >
                <ShieldAlert size={14} style={{ color: '#d97706', flexShrink: 0 }} />
                <span>{synthesis.fallback_notice}</span>
              </div>
            )}
            {synthesis.translation_notice && (
              <div
                style={{
                  padding: '8px 16px',
                  backgroundColor: '#f0fdf4',
                  borderBottom: '1px solid #bbf7d0',
                  fontSize: '0.75rem',
                  color: '#166534',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  flexWrap: 'wrap',
                  gap: '8px',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <ShieldCheck size={14} style={{ color: '#16a34a', flexShrink: 0 }} />
                  <span>{synthesis.translation_notice}</span>
                </div>
                {synthesis.translation_engine && (
                  <span
                    style={{
                      fontSize: '0.675rem',
                      padding: '1px 6px',
                      backgroundColor: '#dcfce7',
                      color: '#14532d',
                      borderRadius: '3px',
                      fontWeight: 600,
                    }}
                  >
                    Translator: {synthesis.translation_engine}
                  </span>
                )}
              </div>
            )}
            <div className="gov-panel-body">
              {synthesis.translated_summary && (
                <div style={{ display: 'flex', gap: '8px', marginBottom: '12px' }}>
                  <button
                    type="button"
                    onClick={() => setShowAuthoritativeEnglish(false)}
                    style={{
                      padding: '4px 12px',
                      fontSize: '0.75rem',
                      fontWeight: !showAuthoritativeEnglish ? 700 : 500,
                      backgroundColor: !showAuthoritativeEnglish ? 'var(--gov-navy-800)' : '#f1f5f9',
                      color: !showAuthoritativeEnglish ? '#ffffff' : 'var(--gov-slate-700)',
                      border: '1px solid var(--gov-slate-300)',
                      borderRadius: '3px',
                      cursor: 'pointer',
                    }}
                  >
                    {synthesis.language === 'te'
                      ? '🇮🇳 తెలుగు వివరణ (Telugu)'
                      : synthesis.language === 'hi'
                      ? '🇮🇳 हिन्दी विवरण (Hindi)'
                      : '🇮🇳 Translated View'}
                  </button>
                  <button
                    type="button"
                    onClick={() => setShowAuthoritativeEnglish(true)}
                    style={{
                      padding: '4px 12px',
                      fontSize: '0.75rem',
                      fontWeight: showAuthoritativeEnglish ? 700 : 500,
                      backgroundColor: showAuthoritativeEnglish ? 'var(--gov-navy-800)' : '#f1f5f9',
                      color: showAuthoritativeEnglish ? '#ffffff' : 'var(--gov-slate-700)',
                      border: '1px solid var(--gov-slate-300)',
                      borderRadius: '3px',
                      cursor: 'pointer',
                    }}
                  >
                    ⚖️ Authoritative English Primary Source
                  </button>
                </div>
              )}
              <p
                style={{
                  fontSize: '0.85rem',
                  lineHeight: '1.6',
                  color: 'var(--gov-slate-800)',
                  margin: '0 0 12px 0',
                }}
              >
                {synthesis.translated_summary && !showAuthoritativeEnglish
                  ? synthesis.translated_summary
                  : synthesis.ai_generated_summary}
              </p>
              <div
                style={{
                  fontSize: '0.725rem',
                  color: 'var(--gov-slate-500)',
                  borderTop: '1px solid var(--gov-slate-200)',
                  paddingTop: '6px',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                }}
              >
                <span>Summary is purely declaratory of current legal standards; not an opinion or advocacy.</span>
                {synthesis.translated_summary && (
                  <span style={{ fontStyle: 'italic', color: 'var(--gov-navy-800)' }}>
                    {showAuthoritativeEnglish ? 'Viewing Authoritative English Source' : 'Viewing Machine-Assisted Vernacular Text'}
                  </span>
                )}
              </div>
            </div>
          </div>

          {/* SECTION 2: Retrieved Primary Authorities (Precedents with Verbatim Passages) */}
          <div className="gov-panel">
            <div className="gov-panel-header">
              <span className="gov-panel-title">
                <Scale size={16} /> 2. AUTHORITATIVE SOURCE: Retrieved Primary Judicial Authorities ({synthesis.retrieved_authorities.length})
              </span>
              <span style={{ fontSize: '0.725rem', color: 'var(--gov-slate-600)' }}>
                Grounded in Supreme Court Cases (SCC) / Official Law Reports
              </span>
            </div>

            <div className="gov-panel-body" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              {synthesis.retrieved_authorities.length === 0 ? (
                <div style={{ padding: '24px 16px', textAlign: 'center', color: 'var(--gov-slate-500)', fontSize: '0.825rem', backgroundColor: '#ffffff', border: '1px dashed var(--gov-slate-300)' }}>
                  No direct commercial judicial authorities matched the specific query and jurisdiction filter.
                </div>
              ) : (
                synthesis.retrieved_authorities.map((auth) => {
                const isPinned = pinnedItems.has(auth.id);
                return (
                  <div
                    key={auth.id}
                    style={{
                      border: auth.is_good_law ? '1px solid var(--gov-slate-300)' : '1px solid #fecaca',
                      borderLeft: auth.is_good_law ? '4px solid #059669' : '5px solid #dc2626',
                      borderRadius: 'var(--border-radius-sm)',
                      backgroundColor: auth.is_good_law ? '#ffffff' : '#fffbfa',
                      overflow: 'hidden',
                      boxShadow: 'var(--gov-shadow-sm)',
                    }}
                  >
                    {/* Precedent Header */}
                    <div
                      style={{
                        padding: '12px 16px',
                        backgroundColor: auth.is_good_law ? '#fafbfc' : '#fef2f2',
                        borderBottom: '1px solid var(--gov-slate-200)',
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'flex-start',
                        gap: '12px',
                        flexWrap: 'wrap',
                      }}
                    >
                      <div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px', flexWrap: 'wrap' }}>
                          <span
                            style={{
                              fontSize: '0.65rem',
                              fontWeight: 700,
                              padding: '2px 6px',
                              backgroundColor: auth.is_good_law ? '#dcfce7' : '#fee2e2',
                              color: auth.is_good_law ? '#15803d' : '#b91c1c',
                              border: `1px solid ${auth.is_good_law ? '#86efac' : '#fca5a5'}`,
                              borderRadius: '2px',
                              textTransform: 'uppercase',
                              letterSpacing: '0.03em',
                            }}
                          >
                            {auth.is_good_law ? 'Verified Good Law (Curated Corpus)' : 'OVERRULED / HISTORICAL PRECEDENT'}
                          </span>

                          <span
                            style={{
                              fontSize: '0.7rem',
                              fontWeight: 700,
                              padding: '2px 6px',
                              backgroundColor: auth.is_good_law ? '#ecfdf5' : '#fef2f2',
                              color: auth.is_good_law ? 'var(--gov-emerald-800)' : '#991b1b',
                              border: `1px solid ${auth.is_good_law ? '#a7f3d0' : '#fecaca'}`,
                              borderRadius: '2px',
                              display: 'inline-flex',
                              alignItems: 'center',
                              gap: '4px',
                            }}
                          >
                            {auth.is_good_law ? <CheckCircle size={12} /> : <XCircle size={12} />}
                            {auth.status_summary}
                          </span>

                          <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--gov-navy-900)' }}>
                            {auth.standard_citation}
                          </span>
                          {auth.neutral_citation && (
                            <span style={{ fontSize: '0.7rem', color: 'var(--gov-slate-500)' }}>
                              [{auth.neutral_citation}]
                            </span>
                          )}
                          {auth.is_demo_data && <DemoDataBadge size="small" />}
                        </div>
                        <div style={{ fontSize: '0.675rem', color: 'var(--gov-slate-500)', marginBottom: '4px', fontStyle: 'italic' }}>
                          External authoritative verification required before reliance in judicial orders.
                        </div>

                        <h4
                          style={{
                            margin: '0 0 4px 0',
                            fontSize: '0.925rem',
                            fontWeight: 700,
                            color: 'var(--gov-slate-900)',
                            lineHeight: '1.3',
                          }}
                        >
                          {auth.title}
                        </h4>

                        <div style={{ fontSize: '0.75rem', color: 'var(--gov-slate-600)' }}>
                          {auth.court} • Quorum: <strong>{auth.bench_quorum}</strong> ({auth.bench_strength || auth.benchStrength}-Judge Bench) • Judgment Date: {auth.judgment_date}
                        </div>
                      </div>

                      {/* Action buttons */}
                      <div style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
                        <button
                          type="button"
                          className="gov-btn gov-btn-secondary"
                          style={{ fontSize: '0.7rem', padding: '4px 8px' }}
                          onClick={() => handleCopyCitation(auth.standard_citation)}
                          title="Copy citation to clipboard"
                        >
                          {copiedCitation === auth.standard_citation ? (
                            <>
                              <Check size={12} color="var(--gov-emerald-700)" /> Copied
                            </>
                          ) : (
                            <>
                              <Copy size={12} /> Copy Citation
                            </>
                          )}
                        </button>

                        <button
                          type="button"
                          className="gov-btn gov-btn-secondary"
                          style={{
                            fontSize: '0.7rem',
                            padding: '4px 8px',
                            backgroundColor: isPinned ? 'var(--gov-gold-100)' : undefined,
                          }}
                          onClick={() => handlePinAuthority(auth)}
                          title="Pin authority to active Bench Dossier"
                        >
                          <Bookmark size={12} color={isPinned ? 'var(--gov-gold-600)' : undefined} />
                          {isPinned ? 'Pinned' : 'Pin to Dossier'}
                        </button>

                        <button
                          type="button"
                          className="gov-btn gov-btn-primary"
                          style={{ fontSize: '0.7rem', padding: '4px 8px' }}
                          onClick={() => setSelectedAuthorityModal(auth)}
                        >
                          <ExternalLink size={12} /> View Full Ratio & Passages
                        </button>
                      </div>
                    </div>

                    {/* Precedent Body */}
                    <div style={{ padding: '14px 16px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
                      {/* Why Relevant Badge */}
                      <div
                        style={{
                          backgroundColor: '#f0f9ff',
                          borderLeft: '3px solid var(--gov-navy-800)',
                          padding: '8px 12px',
                          fontSize: '0.775rem',
                          color: 'var(--gov-navy-900)',
                        }}
                      >
                        <strong>Nexus to Query: </strong>
                        {auth.why_relevant}
                      </div>

                      {/* Operative Ratio Decidendi */}
                      <div>
                        <div
                          style={{
                            fontSize: '0.725rem',
                            fontWeight: 700,
                            color: 'var(--gov-slate-600)',
                            textTransform: 'uppercase',
                            letterSpacing: '0.04em',
                            marginBottom: '4px',
                          }}
                        >
                          Operative Ratio Decidendi:
                        </div>
                        <div
                          style={{
                            fontFamily: 'var(--font-serif)',
                            fontSize: '0.85rem',
                            lineHeight: '1.6',
                            color: 'var(--gov-slate-900)',
                            backgroundColor: 'var(--gov-paper-warm)',
                            padding: '10px 12px',
                            border: '1px solid var(--gov-slate-200)',
                          }}
                        >
                          "{auth.ratio_extract}"
                        </div>
                      </div>

                      {/* Pinpoint Passages */}
                      {auth.pinpoint_passages && auth.pinpoint_passages.length > 0 && (
                        <div>
                          <div
                            style={{
                              fontSize: '0.725rem',
                              fontWeight: 700,
                              color: 'var(--gov-slate-600)',
                              textTransform: 'uppercase',
                              letterSpacing: '0.04em',
                              marginBottom: '6px',
                            }}
                          >
                            Key Pinpoint Paragraphs (Verbatim Law Report Text):
                          </div>

                          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                            {auth.pinpoint_passages.map((passage, pIdx) => (
                              <div
                                key={pIdx}
                                style={{
                                  borderLeft: '3px solid var(--gov-saffron-500)',
                                  backgroundColor: '#fafbfc',
                                  padding: '8px 12px',
                                  fontSize: '0.8rem',
                                  fontFamily: 'var(--font-serif)',
                                  lineHeight: '1.5',
                                }}
                              >
                                <div
                                  style={{
                                    display: 'flex',
                                    justifyContent: 'space-between',
                                    fontFamily: 'var(--font-sans)',
                                    fontSize: '0.7rem',
                                    fontWeight: 700,
                                    color: 'var(--gov-navy-900)',
                                    marginBottom: '4px',
                                  }}
                                >
                                  <span>Paragraph [{passage.paragraph_number}]</span>
                                  <span style={{ color: 'var(--gov-saffron-800)', fontWeight: 600 }}>
                                    {passage.significance}
                                  </span>
                                </div>
                                <div style={{ color: 'var(--gov-slate-800)' }}>
                                  "{passage.text}"
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Citation Verification Summary */}
                      {auth.citation_verification && (
                        <div
                          style={{
                            fontSize: '0.725rem',
                            color: 'var(--gov-slate-600)',
                            backgroundColor: '#f8fafc',
                            padding: '6px 10px',
                            border: '1px solid var(--gov-slate-200)',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'space-between',
                          }}
                        >
                          <span>
                            <ShieldCheck size={13} style={{ color: 'var(--gov-emerald-700)', verticalAlign: 'middle', marginRight: '4px' }} />
                            Reporter Verified: <strong>{auth.citation_verification.official_reporter}</strong> ({auth.citation_verification.treatment_history.length} Subsequent Treatments Verified)
                          </span>
                          <button
                            type="button"
                            onClick={() => setSelectedAuthorityModal(auth)}
                            style={{
                              background: 'none',
                              border: 'none',
                              color: 'var(--gov-navy-800)',
                              fontWeight: 600,
                              cursor: 'pointer',
                              padding: 0,
                            }}
                          >
                            Inspect Citation Trail →
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                );
              })
              )}
            </div>
          </div>

          {/* SECTION 3: Retrieved Statutes (Commercial Legislation Extracts) */}
          <div className="gov-panel">
            <div className="gov-panel-header">
              <span className="gov-panel-title">
                <BookOpen size={16} /> 3. AUTHORITATIVE SOURCE: Statutory Enactments & Legislative Provisions ({synthesis.retrieved_statutes.length})
              </span>
            </div>

            <div className="gov-panel-body" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))', gap: '14px' }}>
              {synthesis.retrieved_statutes.length === 0 ? (
                <div style={{ padding: '24px 16px', textAlign: 'center', color: 'var(--gov-slate-500)', fontSize: '0.825rem', backgroundColor: '#ffffff', border: '1px dashed var(--gov-slate-300)', gridColumn: '1 / -1' }}>
                  No specific statutory sections matched the active query terms.
                </div>
              ) : (
                synthesis.retrieved_statutes.map((statute) => {
                const isPinned = pinnedItems.has(statute.id);
                return (
                  <div
                    key={statute.id}
                    style={{
                      border: '1px solid var(--gov-slate-300)',
                      backgroundColor: '#ffffff',
                      padding: '12px 14px',
                      display: 'flex',
                      flexDirection: 'column',
                      justifyContent: 'space-between',
                    }}
                  >
                    <div>
                      <div
                        style={{
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center',
                          marginBottom: '6px',
                        }}
                      >
                        <span
                          style={{
                            fontSize: '0.75rem',
                            fontWeight: 700,
                            color: 'var(--gov-navy-900)',
                            backgroundColor: '#eff6ff',
                            padding: '2px 6px',
                            border: '1px solid #bfdbfe',
                          }}
                        >
                          {statute.section_number}
                        </span>
                        {statute.is_demo_data && <DemoDataBadge size="small" />}
                      </div>

                      <h5 style={{ margin: '0 0 2px 0', fontSize: '0.85rem', fontWeight: 700, color: 'var(--gov-slate-900)' }}>
                        {statute.heading}
                      </h5>
                      <div style={{ fontSize: '0.725rem', color: 'var(--gov-slate-600)', marginBottom: '8px' }}>
                        {statute.statute_title}
                      </div>

                      <div
                        style={{
                          fontSize: '0.75rem',
                          backgroundColor: '#f8fafc',
                          padding: '8px',
                          border: '1px solid var(--gov-slate-200)',
                          fontFamily: 'var(--font-serif)',
                          lineHeight: '1.5',
                          marginBottom: '8px',
                          color: 'var(--gov-slate-800)',
                        }}
                      >
                        "{statute.content}"
                      </div>

                      <div style={{ fontSize: '0.725rem', color: 'var(--gov-navy-800)', fontWeight: 500, marginBottom: '6px' }}>
                        <strong>Relevance: </strong>
                        {statute.why_relevant}
                      </div>

                      {statute.amendment_notes && (
                        <div style={{ fontSize: '0.7rem', color: 'var(--gov-slate-500)', fontStyle: 'italic' }}>
                          Note: {statute.amendment_notes}
                        </div>
                      )}
                    </div>

                    <div style={{ marginTop: '10px', display: 'flex', justifyContent: 'flex-end' }}>
                      <button
                        type="button"
                        className="gov-btn gov-btn-secondary"
                        style={{ fontSize: '0.7rem', padding: '3px 8px' }}
                        onClick={() => handlePinStatute(statute)}
                      >
                        <Bookmark size={11} color={isPinned ? 'var(--gov-gold-600)' : undefined} />
                        {isPinned ? 'Pinned to Dossier' : 'Pin to Active Docket'}
                      </button>
                    </div>
                  </div>
                );
              })
              )}
            </div>
          </div>

          {/* SECTION 4: Grounded AI Legal Analysis & Substantive Reasoning */}
          <div className="gov-panel">
            <div className="gov-panel-header" style={{ backgroundColor: '#fafbfc' }}>
              <span className="gov-panel-title">
                <FileText size={16} /> 4. AI-GENERATED RESEARCH BRIEFING: Synthesized Legal Principles & Reasoning
              </span>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                {synthesis.translated_analysis && (
                  <span
                    style={{
                      fontSize: '0.675rem',
                      padding: '2px 8px',
                      backgroundColor: '#f5f3ff',
                      color: '#6d28d9',
                      border: '1px solid #ddd6fe',
                      fontWeight: 600,
                      borderRadius: '2px',
                    }}
                  >
                    🌐 {synthesis.language === 'te' ? 'తెలుగు విశ్లేషణ' : synthesis.language === 'hi' ? 'हिन्दी विश्लेषण' : 'Vernacular Analysis'}
                  </span>
                )}
                <span
                  style={{
                    fontSize: '0.7rem',
                    padding: '2px 8px',
                    backgroundColor: '#fef3c7',
                    color: '#92400e',
                    border: '1px solid #fde68a',
                    fontWeight: 600,
                  }}
                >
                  Structured Analysis • Assistive Only
                </span>
              </div>
            </div>
            <div className="gov-panel-body">
              <div
                style={{
                  fontSize: '0.825rem',
                  lineHeight: '1.65',
                  color: 'var(--gov-slate-800)',
                  whiteSpace: 'pre-line',
                }}
              >
                {synthesis.translated_analysis && !showAuthoritativeEnglish
                  ? synthesis.translated_analysis
                  : synthesis.ai_legal_analysis}
              </div>
            </div>
          </div>

          {/* SECTION 5: Cautious Judicial Inferences & Bench Action Points */}
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))',
              gap: '16px',
            }}
          >
            {/* Cautious Inferences */}
            <div className="gov-panel">
              <div className="gov-panel-header" style={{ backgroundColor: '#fffbeb' }}>
                <span className="gov-panel-title" style={{ color: '#92400e' }}>
                  <ShieldAlert size={16} color="#d97706" /> 5. Cautious Inferences (Judicial Scrutiny)
                </span>
              </div>
              <div className="gov-panel-body">
                <div style={{ fontSize: '0.725rem', color: 'var(--gov-slate-600)', marginBottom: '8px' }}>
                  Inferences are deduced based on the specific facts provided; the Bench must independently verify:
                </div>
                <ul
                  style={{
                    margin: 0,
                    paddingLeft: '18px',
                    fontSize: '0.8rem',
                    color: 'var(--gov-slate-800)',
                    lineHeight: '1.6',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '6px',
                  }}
                >
                  {synthesis.cautious_inferences.map((inf, i) => (
                    <li key={i}>{inf}</li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Bench Action Points */}
            <div className="gov-panel">
              <div className="gov-panel-header" style={{ backgroundColor: '#f0fdf4' }}>
                <span className="gov-panel-title" style={{ color: 'var(--gov-emerald-900)' }}>
                  <CheckCircle size={16} color="var(--gov-emerald-700)" /> 6. Bench Action Points (For Admission Hearing)
                </span>
              </div>
              <div className="gov-panel-body">
                <div style={{ fontSize: '0.725rem', color: 'var(--gov-slate-600)', marginBottom: '8px' }}>
                  Immediate inquiries and directives for the Commercial Court hearing:
                </div>
                <ul
                  style={{
                    margin: 0,
                    paddingLeft: '18px',
                    fontSize: '0.8rem',
                    color: 'var(--gov-slate-800)',
                    lineHeight: '1.6',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '6px',
                  }}
                >
                  {synthesis.bench_action_points.map((action, aIdx) => (
                    <li key={aIdx}>{action}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* AUTHORITY INSPECTION MODAL */}
      {selectedAuthorityModal && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(15, 23, 42, 0.65)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1100,
            padding: '20px',
          }}
          onClick={() => setSelectedAuthorityModal(null)}
        >
          <div
            style={{
              backgroundColor: '#ffffff',
              maxWidth: '840px',
              width: '100%',
              maxHeight: '90vh',
              overflowY: 'auto',
              borderTop: '4px solid var(--gov-navy-800)',
              padding: '24px',
              boxShadow: 'var(--gov-shadow-lg)',
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'flex-start',
                marginBottom: '16px',
                borderBottom: '1px solid var(--gov-slate-200)',
                paddingBottom: '12px',
              }}
            >
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                  <span
                    style={{
                      fontSize: '0.725rem',
                      fontWeight: 700,
                      color: selectedAuthorityModal.is_good_law ? 'var(--gov-emerald-800)' : '#991b1b',
                    }}
                  >
                    {selectedAuthorityModal.is_good_law ? 'Verified Good Law (Curated Corpus)' : 'OVERRULED / HISTORICAL PRECEDENT'}
                  </span>
                  <span style={{ fontSize: '0.775rem', fontWeight: 600, color: 'var(--gov-navy-900)' }}>
                    {selectedAuthorityModal.standard_citation}
                  </span>
                  {selectedAuthorityModal.is_demo_data && <DemoDataBadge size="small" />}
                </div>
                <h3 style={{ margin: 0, fontSize: '1.05rem', color: 'var(--gov-slate-900)' }}>
                  {selectedAuthorityModal.title}
                </h3>
              </div>

              <button
                type="button"
                className="gov-btn gov-btn-secondary"
                style={{ fontSize: '0.75rem' }}
                onClick={() => setSelectedAuthorityModal(null)}
              >
                Close (ESC)
              </button>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              {/* Phase 4: Full Citation Verification Card in Modal */}
              {selectedAuthorityModal.citation_verification && (
                <CitationVerificationCard verification={selectedAuthorityModal.citation_verification} />
              )}

              <div
                style={{
                  padding: '10px 14px',
                  backgroundColor: 'var(--gov-navy-50)',
                  borderLeft: '4px solid var(--gov-navy-800)',
                  fontSize: '0.825rem',
                  color: 'var(--gov-navy-900)',
                }}
              >
                <strong>Relevance Determination:</strong> {selectedAuthorityModal.why_relevant}
              </div>

              <div>
                <div
                  style={{
                    fontSize: '0.75rem',
                    fontWeight: 700,
                    color: 'var(--gov-slate-600)',
                    textTransform: 'uppercase',
                    marginBottom: '4px',
                  }}
                >
                  Operative Ratio Decidendi:
                </div>
                <div
                  style={{
                    fontFamily: 'var(--font-serif)',
                    fontSize: '0.9rem',
                    lineHeight: '1.7',
                    backgroundColor: 'var(--gov-paper-warm)',
                    padding: '14px',
                    border: '1px solid var(--gov-slate-200)',
                  }}
                >
                  "{selectedAuthorityModal.ratio_extract}"
                </div>
              </div>

              {selectedAuthorityModal.pinpoint_passages.length > 0 && (
                <div>
                  <div
                    style={{
                      fontSize: '0.75rem',
                      fontWeight: 700,
                      color: 'var(--gov-slate-600)',
                      textTransform: 'uppercase',
                      marginBottom: '6px',
                    }}
                  >
                    Authoritative Pinpoint Paragraphs:
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                    {selectedAuthorityModal.pinpoint_passages.map((p) => (
                      <div
                        key={p.paragraph_number}
                        style={{
                          padding: '12px 14px',
                          border: '1px solid var(--gov-slate-200)',
                          backgroundColor: '#ffffff',
                          fontFamily: 'var(--font-serif)',
                          fontSize: '0.85rem',
                          lineHeight: '1.7',
                        }}
                      >
                        <div
                          style={{
                            fontWeight: 700,
                            color: 'var(--gov-navy-900)',
                            fontFamily: 'var(--font-sans)',
                            marginBottom: '4px',
                          }}
                        >
                          Paragraph [{p.paragraph_number}]
                        </div>
                        {p.text}
                        <div
                          style={{
                            marginTop: '6px',
                            fontSize: '0.75rem',
                            fontFamily: 'var(--font-sans)',
                            color: 'var(--gov-saffron-800)',
                            fontWeight: 600,
                          }}
                        >
                          Significance: {p.significance}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '10px' }}>
                <button
                  type="button"
                  className="gov-btn gov-btn-secondary"
                  onClick={() => handleCopyCitation(selectedAuthorityModal.standard_citation)}
                >
                  <Copy size={13} /> Copy Standard Citation
                </button>
                <button
                  type="button"
                  className="gov-btn gov-btn-primary"
                  onClick={() => {
                    handleOpenInSplitPane(selectedAuthorityModal);
                    setSelectedAuthorityModal(null);
                  }}
                >
                  <ExternalLink size={13} /> Open Full Judgment in Split-Pane Reader
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* PHASE 4: BOOKMARK / SAVE RESEARCH MODAL */}
      {isSaveModalOpen && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(15, 23, 42, 0.65)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1150,
            padding: '20px',
          }}
          onClick={() => setIsSaveModalOpen(false)}
        >
          <div
            style={{
              backgroundColor: '#ffffff',
              maxWidth: '560px',
              width: '100%',
              borderTop: '4px solid var(--gov-navy-800)',
              padding: '24px',
              boxShadow: 'var(--gov-shadow-lg)',
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                marginBottom: '16px',
                borderBottom: '1px solid var(--gov-slate-200)',
                paddingBottom: '10px',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Bookmark size={18} style={{ color: 'var(--gov-gold-600)' }} />
                <h4 style={{ margin: 0, fontSize: '0.95rem', color: 'var(--gov-navy-900)' }}>
                  Bookmark Research to Chambers Portfolio
                </h4>
              </div>
              <button
                type="button"
                onClick={() => setIsSaveModalOpen(false)}
                style={{ background: 'none', border: 'none', cursor: 'pointer' }}
              >
                ✕
              </button>
            </div>

            {saveSuccessMsg ? (
              <div
                style={{
                  padding: '20px',
                  backgroundColor: '#ecfdf5',
                  color: 'var(--gov-emerald-800)',
                  border: '1px solid #a7f3d0',
                  textAlign: 'center',
                  fontSize: '0.875rem',
                  fontWeight: 600,
                }}
              >
                ✓ {saveSuccessMsg}
              </div>
            ) : (
              <form onSubmit={handleSaveResearchToPortfolio}>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
                  <div>
                    <span style={{ fontSize: '0.75rem', color: 'var(--gov-slate-500)' }}>
                      Active Commercial Suit:
                    </span>
                    <div style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--gov-slate-900)' }}>
                      {selectedDossier ? `${selectedDossier.suitNumber} — ${selectedDossier.parties}` : 'General Research / No Active Matter'}
                    </div>
                  </div>

                  <div>
                    <label
                      htmlFor="txt-save-notes"
                      style={{
                        display: 'block',
                        fontSize: '0.775rem',
                        fontWeight: 600,
                        color: 'var(--gov-slate-700)',
                        marginBottom: '4px',
                      }}
                    >
                      Chambers Notes & Bench Instructions:
                    </label>
                    <textarea
                      id="txt-save-notes"
                      rows={3}
                      value={saveNotes}
                      onChange={(e) => setSaveNotes(e.target.value)}
                      placeholder="e.g. Essential authority for interim injunction hearing. Verify paragraph 93 urgency threshold..."
                      style={{
                        width: '100%',
                        padding: '8px 10px',
                        fontSize: '0.8rem',
                        border: '1px solid var(--gov-slate-300)',
                      }}
                    />
                  </div>

                  <div>
                    <label
                      htmlFor="txt-save-tags"
                      style={{
                        display: 'block',
                        fontSize: '0.775rem',
                        fontWeight: 600,
                        color: 'var(--gov-slate-700)',
                        marginBottom: '4px',
                      }}
                    >
                      Judicial Tags (Comma Separated):
                    </label>
                    <input
                      id="txt-save-tags"
                      type="text"
                      value={saveTags}
                      onChange={(e) => setSaveTags(e.target.value)}
                      style={{
                        width: '100%',
                        padding: '7px 10px',
                        fontSize: '0.8rem',
                        border: '1px solid var(--gov-slate-300)',
                      }}
                    />
                  </div>

                  <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '10px' }}>
                    <button
                      type="button"
                      className="gov-btn gov-btn-secondary"
                      onClick={() => setIsSaveModalOpen(false)}
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      className="gov-btn gov-btn-primary"
                      disabled={isSaving}
                    >
                      {isSaving ? 'Saving...' : 'Save to Portfolio'}
                    </button>
                  </div>
                </div>
              </form>
            )}
          </div>
        </div>
      )}

      {/* PHASE 4: SAVED RESEARCH & SESSION HISTORY SLIDE-OVER DRAWER */}
      <SavedResearchDrawer
        isOpen={isDrawerOpen}
        onClose={() => setIsDrawerOpen(false)}
        onSelectSavedQuery={handleSelectSavedQuery}
      />
    </div>
  );
};
