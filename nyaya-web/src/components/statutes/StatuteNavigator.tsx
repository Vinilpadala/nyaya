import React, { useState } from 'react';
import { BookOpen, CheckSquare, FileText, Bookmark } from 'lucide-react';
import { useChambers } from '../../context/ChambersContext';
import { StatuteSection } from '../../types';
import { DemoDataBadge } from '../common/DemoDataBadge';
import { ApiErrorBanner } from '../common/ApiErrorBanner';

export const StatuteNavigator: React.FC = () => {
  const {
    statutes,
    selectedStatute,
    setSelectedStatute,
    selectedDossier,
    pinAuthorityToDossier,
    addAuditLog,
    statutesLoading,
    statutesError,
    reloadStatutes,
  } = useChambers();

  const [activeSection, setActiveSection] = useState<StatuteSection>(
    selectedStatute?.sections?.[0] || null
  );

  const handleSelectStatute = (statuteId: string) => {
    const s = statutes.find((item) => item.id === statuteId);
    if (s) {
      setSelectedStatute(s);
      setActiveSection(s.sections[0] || null);
      addAuditLog('VIEW_STATUTE', `${s.shortTitle}`);
    }
  };

  const handleSelectSection = (sec: StatuteSection) => {
    setActiveSection(sec);
    addAuditLog('VIEW_SECTION', `${selectedStatute.shortTitle} - ${sec.sectionNumber}`);
  };

  const handlePinSection = (sec: StatuteSection) => {
    if (!selectedDossier) return;
    pinAuthorityToDossier(selectedDossier.id, {
      type: 'SECTION',
      title: `${selectedStatute.shortTitle} - ${sec.sectionNumber} (${sec.heading})`,
      referenceId: `${selectedStatute.shortTitle} ${sec.sectionNumber}`,
      excerpt: sec.content,
    });
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      {statutesError && (
        <ApiErrorBanner
          title="Statutes Repository Offline"
          message={statutesError}
          onRetry={() => reloadStatutes()}
        />
      )}

      {/* Statute Header Selector */}
      <div className="gov-panel" style={{ padding: '14px 18px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <BookOpen size={20} color="var(--gov-navy-800)" />
            <div>
              <div style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--gov-navy-900)' }}>
                {selectedStatute.shortTitle} {statutesLoading && <span style={{ fontSize: '0.75rem', fontWeight: 400, color: 'var(--gov-slate-500)' }}>(Updating from API...)</span>}
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--gov-slate-500)' }}>
                {selectedStatute.actNumber} • Enacted {selectedStatute.enactmentYear} • Jurisdiction: {selectedStatute.jurisdiction}
              </div>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontSize: '0.8rem', color: 'var(--gov-slate-600)', fontWeight: 500 }}>
              Select Act:
            </span>
            <select
              className="gov-select"
              style={{ width: 'auto', minWidth: '260px' }}
              value={selectedStatute.id}
              onChange={(e) => handleSelectStatute(e.target.value)}
            >
              {statutes.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.shortTitle} ({s.enactmentYear})
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Split Section Layout */}
      <div className="gov-split-layout">
        {/* Left Column: Sections List */}
        <div className="gov-pane-scroll">
          <div className="gov-panel">
            <div className="gov-panel-header">
              <span className="gov-panel-title">
                <FileText size={16} /> Key Commercial Provisions ({selectedStatute.sections.length})
              </span>
              <DemoDataBadge label="CENTRAL ACTS" />
            </div>

            <div style={{ display: 'flex', flexDirection: 'column' }}>
              {selectedStatute.sections.map((sec) => {
                const isSelected = activeSection?.id === sec.id;
                return (
                  <div
                    key={sec.id}
                    onClick={() => handleSelectSection(sec)}
                    style={{
                      padding: '14px 16px',
                      borderBottom: '1px solid var(--gov-slate-200)',
                      backgroundColor: isSelected ? 'var(--gov-navy-50)' : '#ffffff',
                      borderLeft: isSelected ? '4px solid var(--gov-navy-800)' : '4px solid transparent',
                      cursor: 'pointer',
                      transition: 'background-color 0.15s',
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span style={{ fontSize: '0.875rem', fontWeight: 700, color: 'var(--gov-navy-900)' }}>
                        {sec.sectionNumber}
                      </span>
                      {sec.isAmended && (
                        <span
                          style={{
                            fontSize: '0.675rem',
                            fontWeight: 600,
                            padding: '1px 5px',
                            borderRadius: '2px',
                            backgroundColor: '#e0f2fe',
                            color: '#0369a1',
                            border: '1px solid #bae6fd',
                          }}
                        >
                          AMENDED
                        </span>
                      )}
                    </div>
                    <div
                      style={{
                        fontSize: '0.8rem',
                        color: 'var(--gov-slate-700)',
                        marginTop: '4px',
                        fontWeight: 500,
                      }}
                    >
                      {sec.heading}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Right Column: Statutory Text, Amendments, and Judicial Guidelines */}
        <div className="gov-pane-scroll">
          {activeSection ? (
            <div className="gov-panel" style={{ padding: '24px 28px' }}>
              <div
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'flex-start',
                  borderBottom: '2px solid var(--gov-slate-200)',
                  paddingBottom: '16px',
                  marginBottom: '20px',
                }}
              >
                <div>
                  <div style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--gov-navy-900)' }}>
                    {activeSection.sectionNumber}: {activeSection.heading}
                  </div>
                  <div style={{ fontSize: '0.775rem', color: 'var(--gov-slate-500)', marginTop: '4px' }}>
                    {selectedStatute.shortTitle}
                  </div>
                </div>

                <button
                  type="button"
                  className="gov-btn gov-btn-secondary"
                  onClick={() => handlePinSection(activeSection)}
                >
                  <Bookmark size={14} />
                  Pin to Active Dossier
                </button>
              </div>

              {/* Official Statutory Text */}
              <div style={{ marginBottom: '24px' }}>
                <div
                  style={{
                    fontSize: '0.725rem',
                    textTransform: 'uppercase',
                    letterSpacing: '0.04em',
                    color: 'var(--gov-slate-500)',
                    fontWeight: 600,
                    marginBottom: '8px',
                  }}
                >
                  Authoritative Statutory Text
                </div>
                <div
                  style={{
                    padding: '16px 20px',
                    backgroundColor: 'var(--gov-paper-warm)',
                    border: '1px solid var(--gov-slate-300)',
                    borderRadius: 'var(--border-radius-sm)',
                    fontFamily: 'var(--font-serif)',
                    fontSize: '0.925rem',
                    lineHeight: '1.8',
                    color: '#1a202c',
                    whiteSpace: 'pre-line',
                  }}
                >
                  {activeSection.content}
                </div>
              </div>

              {/* Amendment Notes */}
              {activeSection.isAmended && (
                <div style={{ marginBottom: '20px' }}>
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
                    Legislative History & Amendments
                  </div>
                  <div
                    style={{
                      padding: '10px 14px',
                      backgroundColor: '#f8fafc',
                      borderLeft: '3px solid var(--gov-navy-600)',
                      fontSize: '0.8rem',
                      color: 'var(--gov-slate-700)',
                    }}
                  >
                    {activeSection.amendmentNotes}
                  </div>
                </div>
              )}

              {/* Practical Guidelines for Commercial Judges */}
              {activeSection.practicalGuidelines && activeSection.practicalGuidelines.length > 0 && (
                <div style={{ marginBottom: '20px' }}>
                  <div
                    style={{
                      fontSize: '0.725rem',
                      textTransform: 'uppercase',
                      letterSpacing: '0.04em',
                      color: 'var(--gov-slate-500)',
                      fontWeight: 600,
                      marginBottom: '8px',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '6px',
                    }}
                  >
                    <CheckSquare size={13} color="var(--gov-navy-800)" />
                    Commercial Bench Compliance Checklist
                  </div>
                  <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    {activeSection.practicalGuidelines.map((g: string, idx: number) => (
                      <li
                        key={idx}
                        style={{
                          fontSize: '0.825rem',
                          color: 'var(--gov-slate-800)',
                          display: 'flex',
                          alignItems: 'flex-start',
                          gap: '10px',
                          padding: '6px 10px',
                          background: 'var(--gov-slate-50)',
                          borderRadius: '2px',
                        }}
                      >
                        <span style={{ color: 'var(--gov-navy-700)', fontWeight: 700 }}>•</span>
                        <span>{g}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Landmark Precedents Construing This Section */}
              {activeSection.landmarkPrecedents && activeSection.landmarkPrecedents.length > 0 && (
                <div>
                  <div
                    style={{
                      fontSize: '0.725rem',
                      textTransform: 'uppercase',
                      letterSpacing: '0.04em',
                      color: 'var(--gov-slate-500)',
                      fontWeight: 600,
                      marginBottom: '8px',
                    }}
                  >
                    Landmark Precedents Interpreting this Provision
                  </div>
                  <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                    {activeSection.landmarkPrecedents.map((p: string, idx: number) => (
                      <span
                        key={idx}
                        style={{
                          fontSize: '0.775rem',
                          fontWeight: 600,
                          padding: '4px 10px',
                          backgroundColor: '#f1f5f9',
                          border: '1px solid #cbd5e1',
                          borderRadius: '2px',
                          color: 'var(--gov-navy-900)',
                        }}
                      >
                        {p}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div style={{ padding: '40px', textAlign: 'center', color: 'var(--gov-slate-500)' }}>
              Select a statutory section from the left column to view statutory text and compliance checklists.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
