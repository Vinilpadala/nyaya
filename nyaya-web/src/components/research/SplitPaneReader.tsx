import React, { useState } from 'react';
import {
  Search,
  CheckCircle,
  XCircle,
  FileText,
  Bookmark,
  Copy,
  Check,
} from 'lucide-react';
import { useChambers } from '../../context/ChambersContext';
import { JudicialCase } from '../../types';
import { DemoDataBadge } from '../common/DemoDataBadge';
import { ApiErrorBanner } from '../common/ApiErrorBanner';

export const SplitPaneReader: React.FC = () => {
  const {
    cases,
    selectedCase,
    setSelectedCase,
    selectedDossier,
    pinAuthorityToDossier,
    addAuditLog,
    casesLoading,
    casesError,
    reloadCases,
  } = useChambers();

  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCourt, setSelectedCourt] = useState('ALL');
  const [statusFilter, setStatusFilter] = useState<'ALL' | 'GOOD_LAW' | 'OVERRULED'>('ALL');
  const [highlightedPara, setHighlightedPara] = useState<number | null>(null);
  const [copiedCitation, setCopiedCitation] = useState<string | null>(null);
  const [pinSuccess, setPinSuccess] = useState(false);

  // Filter cases based on search and facets
  const filteredCases = cases.filter((c) => {
    const matchesSearch =
      c.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.standardCitation.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.neutralCitation.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.commercialCategory.toLowerCase().includes(searchQuery.toLowerCase());

    const matchesCourt =
      selectedCourt === 'ALL' || c.court.toLowerCase().includes(selectedCourt.toLowerCase());

    const matchesStatus =
      statusFilter === 'ALL' ||
      (statusFilter === 'GOOD_LAW' && c.isGoodLaw) ||
      (statusFilter === 'OVERRULED' && !c.isGoodLaw);

    return matchesSearch && matchesCourt && matchesStatus;
  });

  const handleSelectCase = (c: JudicialCase) => {
    setSelectedCase(c);
    setHighlightedPara(c.keyParagraphs[0]?.number || null);
    addAuditLog('VIEW_PRECEDENT', `${c.standardCitation} - ${c.title}`);
  };

  const handleCopyPinpoint = (citation: string, para: number) => {
    const text = `${citation} at paragraph ${para}`;
    navigator.clipboard.writeText(text);
    setCopiedCitation(text);
    setTimeout(() => setCopiedCitation(null), 2000);
  };

  const handlePinToDossier = (c: JudicialCase) => {
    if (!selectedDossier) return;
    pinAuthorityToDossier(selectedDossier.id, {
      type: 'CASE',
      title: c.title,
      referenceId: c.standardCitation,
      excerpt: c.ratioDecidendi,
    });
    setPinSuccess(true);
    setTimeout(() => setPinSuccess(false), 2500);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      {casesError && (
        <ApiErrorBanner
          title="Case Law Repository Offline"
          message={casesError}
          onRetry={() => reloadCases()}
        />
      )}

      {/* Search and Filters Header */}
      <div className="gov-panel" style={{ padding: '14px 18px' }}>
        <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap', alignItems: 'center' }}>
          <div style={{ flex: '1 1 350px', position: 'relative' }}>
            <Search
              size={17}
              color="var(--gov-slate-400)"
              style={{ position: 'absolute', left: '12px', top: '10px' }}
            />
            <input
              type="text"
              className="gov-input"
              style={{ paddingLeft: '38px' }}
              placeholder={casesLoading ? 'Updating precedents from Chambers API...' : 'Search commercial precedents by citation, case name, statutory section, or legal issue...'}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>

          <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
            <span style={{ fontSize: '0.8rem', color: 'var(--gov-slate-600)', fontWeight: 500 }}>
              Jurisdiction:
            </span>
            <select
              className="gov-select"
              style={{ width: 'auto' }}
              value={selectedCourt}
              onChange={(e) => setSelectedCourt(e.target.value)}
            >
              <option value="ALL">All Courts</option>
              <option value="Supreme Court">Supreme Court of India</option>
              <option value="High Court">High Courts Commercial Division</option>
            </select>
          </div>

          <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
            <span style={{ fontSize: '0.8rem', color: 'var(--gov-slate-600)', fontWeight: 500 }}>
              Precedent Status:
            </span>
            <select
              className="gov-select"
              style={{ width: 'auto' }}
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value as 'ALL' | 'GOOD_LAW' | 'OVERRULED')}
            >
              <option value="ALL">All Authorities</option>
              <option value="GOOD_LAW">Verified Good Law Only (Curated Corpus)</option>
              <option value="OVERRULED">Overruled Only</option>
            </select>
          </div>
        </div>
      </div>

      {/* Split-Pane Judicial Research Workspace */}
      <div className="gov-split-layout">
        {/* Left Pane: Precedents Catalog & Structured Ratio Decidendi */}
        <div className="gov-pane-scroll" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {/* Case List Selector */}
          <div className="gov-panel">
            <div className="gov-panel-header">
              <span className="gov-panel-title">
                <FileText size={16} /> Commercial Precedents Corpus ({filteredCases.length})
              </span>
              <DemoDataBadge label="BENCHMARK REPOSITORY" />
            </div>
            <div style={{ maxHeight: '230px', overflowY: 'auto' }}>
              {filteredCases.length === 0 ? (
                <div style={{ padding: '24px 16px', textAlign: 'center', color: 'var(--gov-slate-500)', fontSize: '0.8rem' }}>
                  No commercial precedents found matching the current search criteria or filters.
                </div>
              ) : (
                filteredCases.map((c) => {
                  const isSelected = selectedCase.id === c.id;
                  return (
                    <div
                      key={c.id}
                      onClick={() => handleSelectCase(c)}
                      style={{
                        padding: '10px 14px',
                        borderBottom: '1px solid var(--gov-slate-200)',
                        backgroundColor: isSelected ? 'var(--gov-navy-50)' : '#ffffff',
                        borderLeft: isSelected ? '4px solid var(--gov-navy-800)' : '4px solid transparent',
                        cursor: 'pointer',
                        transition: 'background-color 0.15s',
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                        <span style={{ fontSize: '0.825rem', fontWeight: 600, color: 'var(--gov-navy-800)' }}>
                          {c.standardCitation}
                        </span>
                        {c.isGoodLaw ? (
                          <span className="badge-good-law">
                            <CheckCircle size={10} /> Verified Good Law (Curated Corpus)
                          </span>
                        ) : (
                          <span className="badge-overruled">
                            <XCircle size={10} /> Overruled
                          </span>
                        )}
                      </div>
                      <div
                        style={{
                          fontSize: '0.825rem',
                          fontWeight: 600,
                          color: 'var(--gov-slate-900)',
                          margin: '3px 0',
                        }}
                      >
                        {c.title}
                      </div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--gov-slate-500)' }}>
                        {c.court} • {c.benchQuorum}
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </div>

          {/* Detailed Ratio Decidendi & Legal Brief for Active Case */}
          <div className="gov-panel">
            <div className="gov-panel-header">
              <span className="gov-panel-title">
                <Bookmark size={16} /> Authoritative Ratio Decidendi & Legal Analysis
              </span>
              <button
                type="button"
                className="gov-btn gov-btn-secondary"
                style={{ fontSize: '0.75rem', padding: '4px 8px' }}
                onClick={() => handlePinToDossier(selectedCase)}
              >
                {pinSuccess ? <Check size={13} color="#15803d" /> : <Bookmark size={13} />}
                {pinSuccess ? 'Pinned to Matter!' : 'Pin to Active Dossier'}
              </button>
            </div>

            <div className="gov-panel-body" style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <div>
                <div
                  style={{
                    fontSize: '0.725rem',
                    textTransform: 'uppercase',
                    letterSpacing: '0.04em',
                    color: 'var(--gov-slate-500)',
                    fontWeight: 600,
                    marginBottom: '4px',
                  }}
                >
                  Binding Legal Ratio (Ratio Decidendi)
                </div>
                <div
                  style={{
                    padding: '12px 14px',
                    backgroundColor: 'var(--gov-paper-warm)',
                    borderLeft: '4px solid var(--gov-saffron-700)',
                    border: '1px solid var(--gov-slate-200)',
                    borderLeftWidth: '4px',
                    fontFamily: 'var(--font-serif)',
                    fontSize: '0.875rem',
                    lineHeight: '1.7',
                    color: '#1a202c',
                  }}
                >
                  "{selectedCase.ratioDecidendi}"
                </div>
              </div>

              <div>
                <div
                  style={{
                    fontSize: '0.725rem',
                    textTransform: 'uppercase',
                    letterSpacing: '0.04em',
                    color: 'var(--gov-slate-500)',
                    fontWeight: 600,
                    marginBottom: '4px',
                  }}
                >
                  Commercial Controversy Summary
                </div>
                <p style={{ fontSize: '0.825rem', lineHeight: '1.6', color: 'var(--gov-slate-700)' }}>
                  {selectedCase.factsSummary}
                </p>
              </div>

              {/* Treatment of Cited Authorities */}
              {selectedCase.citationsMade.length > 0 && (
                <div>
                  <div
                    style={{
                      fontSize: '0.725rem',
                      textTransform: 'uppercase',
                      letterSpacing: '0.04em',
                      color: 'var(--gov-slate-500)',
                      fontWeight: 600,
                      marginBottom: '6px',
                    }}
                  >
                    Judicial Treatment of Prior Citations ({selectedCase.citationsMade.length})
                  </div>
                  <table className="gov-table" style={{ fontSize: '0.775rem' }}>
                    <thead>
                      <tr>
                        <th>Authority Cited</th>
                        <th>Citation</th>
                        <th>Treatment</th>
                        <th>Pinpoint</th>
                      </tr>
                    </thead>
                    <tbody>
                      {selectedCase.citationsMade.map((cit) => (
                        <tr key={cit.id}>
                          <td style={{ fontWeight: 600 }}>{cit.caseName}</td>
                          <td>{cit.citation}</td>
                          <td>
                            <span
                              style={{
                                display: 'inline-block',
                                padding: '1px 6px',
                                borderRadius: '2px',
                                fontSize: '0.7rem',
                                fontWeight: 700,
                                backgroundColor:
                                  cit.treatment === 'AFFIRMED'
                                    ? '#dcfce7'
                                    : cit.treatment === 'OVERRULED'
                                    ? '#fee2e2'
                                    : '#f1f5f9',
                                color:
                                  cit.treatment === 'AFFIRMED'
                                    ? '#15803d'
                                    : cit.treatment === 'OVERRULED'
                                    ? '#b91c1c'
                                    : '#334155',
                              }}
                            >
                              {cit.treatment}
                            </span>
                          </td>
                          <td style={{ color: 'var(--gov-slate-600)' }}>{cit.pinpointPara}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}

              {/* Landmark Key Paragraph Quick Navigator */}
              <div>
                <div
                  style={{
                    fontSize: '0.725rem',
                    textTransform: 'uppercase',
                    letterSpacing: '0.04em',
                    color: 'var(--gov-slate-500)',
                    fontWeight: 600,
                    marginBottom: '6px',
                  }}
                >
                  Landmark Pinpoint Paragraphs
                </div>
                <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                  {selectedCase.keyParagraphs.map((kp) => (
                    <button
                      key={kp.number}
                      type="button"
                      className="gov-btn gov-btn-secondary"
                      style={{
                        fontSize: '0.75rem',
                        padding: '4px 10px',
                        backgroundColor:
                          highlightedPara === kp.number ? 'var(--gov-navy-800)' : '#ffffff',
                        color: highlightedPara === kp.number ? '#ffffff' : 'var(--gov-slate-700)',
                      }}
                      onClick={() => setHighlightedPara(kp.number)}
                    >
                      Para {kp.number}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Right Pane: Full Judgment Reader & Official SCR Inspector */}
        <div className="gov-pane-scroll">
          <div className="judgment-paper">
            {/* Judicial Header */}
            <div className="judgment-header">
              <div className="judgment-court">{selectedCase.court}</div>
              <div style={{ fontSize: '0.8rem', color: 'var(--gov-slate-500)', letterSpacing: '0.03em' }}>
                COMMERCIAL APPELLATE JURISDICTION
              </div>
              <div className="judgment-parties">{selectedCase.title}</div>
              <div style={{ fontSize: '0.85rem', color: 'var(--gov-slate-600)', fontStyle: 'italic' }}>
                Judgment delivered on: {selectedCase.judgmentDate}
              </div>

              {/* Metadata Table */}
              <table className="judgment-meta-table">
                <tbody>
                  <tr>
                    <td className="label">Standard Citation:</td>
                    <td style={{ fontWeight: 700, color: 'var(--gov-navy-900)' }}>
                      {selectedCase.standardCitation}
                    </td>
                    <td className="label">Neutral Citation:</td>
                    <td>{selectedCase.neutralCitation || 'N/A'}</td>
                  </tr>
                  <tr>
                    <td className="label">Coram / Bench:</td>
                    <td colSpan={3}>{selectedCase.benchQuorum}</td>
                  </tr>
                  <tr>
                    <td className="label">Bench Strength:</td>
                    <td>{selectedCase.benchStrength} Judges ({selectedCase.benchStrength >= 5 ? 'Constitution Bench' : 'Division Bench'})</td>
                    <td className="label">Authority Status:</td>
                    <td>
                      <span style={{ fontWeight: 600, color: selectedCase.isGoodLaw ? '#15803d' : '#b91c1c' }}>
                        {selectedCase.statusSummary}
                      </span>
                    </td>
                  </tr>
                  <tr>
                    <td className="label">Relevant Acts:</td>
                    <td colSpan={3} style={{ fontFamily: 'var(--font-sans)', fontSize: '0.75rem' }}>
                      {selectedCase.relevantStatute}
                    </td>
                  </tr>
                </tbody>
              </table>

              <div
                style={{
                  display: 'flex',
                  justifyContent: 'flex-end',
                  gap: '8px',
                  marginTop: '12px',
                }}
              >
                <button
                  type="button"
                  className="gov-btn gov-btn-secondary no-print"
                  style={{ fontSize: '0.725rem', padding: '4px 8px' }}
                  onClick={() =>
                    handleCopyPinpoint(
                      selectedCase.standardCitation,
                      highlightedPara || selectedCase.keyParagraphs[0]?.number || 1
                    )
                  }
                >
                  {copiedCitation ? <Check size={12} color="#15803d" /> : <Copy size={12} />}
                  {copiedCitation ? 'Pinpoint Copied!' : 'Copy SCR Pinpoint Reference'}
                </button>
              </div>
            </div>

            {/* Official Judgment Paragraphs */}
            <div className="judgment-content">
              {selectedCase.fullJudgmentText.map((para, idx) => {
                // Match paragraph number [N]
                const match = para.match(/^\[(\d+)\]/);
                const paraNum = match ? parseInt(match[1], 10) : idx + 1;
                const isTargetHighlighted = highlightedPara === paraNum;

                return (
                  <div
                    key={idx}
                    id={`judgment-para-${paraNum}`}
                    className={`judgment-para ${isTargetHighlighted ? 'highlighted' : ''}`}
                  >
                    <span className="judgment-para-num">[{paraNum}]</span>
                    {para.replace(/^\[\d+\]\s*/, '')}
                    {isTargetHighlighted && (
                      <div
                        style={{
                          marginTop: '6px',
                          fontSize: '0.725rem',
                          fontFamily: 'var(--font-sans)',
                          color: 'var(--gov-saffron-800)',
                          fontWeight: 600,
                        }}
                      >
                        ★ Key Judicial Pinpoint: {selectedCase.keyParagraphs.find((k) => k.number === paraNum)?.highlightReason || 'Holding examined by Commercial Bench'}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
