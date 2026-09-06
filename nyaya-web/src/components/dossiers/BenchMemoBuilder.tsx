import React, { useState } from 'react';
import {
  FileText,
  Printer,
  Plus,
  Scale,
  X,
  Lock,
} from 'lucide-react';
import { useChambers } from '../../context/ChambersContext';
import { DemoDataBadge } from '../common/DemoDataBadge';
import { ApiErrorBanner } from '../common/ApiErrorBanner';

export const BenchMemoBuilder: React.FC = () => {
  const {
    dossiers,
    selectedDossier,
    setSelectedDossier,
    addDossierNote,
    removeDossierItem,
    currentUser,
    createNewDossier,
    dossiersLoading,
    dossiersError,
    reloadDossiers,
    isAuthenticated,
  } = useChambers();

  const [newNoteContent, setNewNoteContent] = useState('');
  const [newNoteSource, setNewNoteSource] = useState('');
  const [isAddingNote, setIsAddingNote] = useState(false);

  // New Dossier Modal State
  const [isNewDossierOpen, setIsNewDossierOpen] = useState(false);
  const [newSuitNumber, setNewSuitNumber] = useState('');
  const [newParties, setNewParties] = useState('');
  const [newJudicialNotes, setNewJudicialNotes] = useState('');
  const [isCreatingDossier, setIsCreatingDossier] = useState(false);
  const [createDossierError, setCreateDossierError] = useState<string | null>(null);

  const handleAddNote = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newNoteContent.trim() || !selectedDossier || isAddingNote) return;
    setIsAddingNote(true);
    try {
      await addDossierNote(
        selectedDossier.id,
        newNoteContent.trim(),
        newNoteSource.trim() || 'Chambers Oral Deliberation'
      );
      setNewNoteContent('');
      setNewNoteSource('');
    } finally {
      setIsAddingNote(false);
    }
  };

  const handleCreateDossierSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newSuitNumber.trim() || !newParties.trim()) return;

    setIsCreatingDossier(true);
    setCreateDossierError(null);
    try {
      await createNewDossier(newSuitNumber.trim(), newParties.trim(), newJudicialNotes.trim());
      setIsNewDossierOpen(false);
      setNewSuitNumber('');
      setNewParties('');
      setNewJudicialNotes('');
    } catch (err: any) {
      setCreateDossierError(err.message || 'Failed to create dossier on backend.');
    } finally {
      setIsCreatingDossier(false);
    }
  };

  const handlePrint = () => {
    window.print();
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      {dossiersError && (
        <ApiErrorBanner
          title="Chambers Dossier Service Offline"
          message={dossiersError}
          onRetry={reloadDossiers}
        />
      )}

      {!isAuthenticated && (
        <div
          style={{
            backgroundColor: '#eff6ff',
            border: '1px solid #bfdbfe',
            borderRadius: '4px',
            padding: '10px 14px',
            fontSize: '0.8rem',
            color: '#1e40af',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
          }}
        >
          <Lock size={14} color="#2563eb" />
          <span>
            <strong>Local Chambers Mode:</strong> Sign in to Chambers using the button in the header to synchronize dossiers and notes with the central court registry.
          </span>
        </div>
      )}

      {/* Top Docket Selector & Actions */}
      <div className="gov-panel" style={{ padding: '14px 18px' }}>
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            flexWrap: 'wrap',
            gap: '12px',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <FileText size={20} color="var(--gov-navy-800)" />
            <div>
              <div style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--gov-navy-900)' }}>
                Chambers Research Dossier & Bench Memorandum
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--gov-slate-500)' }}>
                Compilation of Authorities, Statutory Checklists, and Pre-Hearing Notes {dossiersLoading && <span style={{ color: '#2563eb' }}>(Syncing...)</span>}
              </div>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontSize: '0.8rem', color: 'var(--gov-slate-600)', fontWeight: 500 }}>
                Active Matter:
              </span>
              <select
                className="gov-select"
                style={{ width: 'auto', minWidth: '280px' }}
                value={selectedDossier?.id || ''}
                onChange={(e) => {
                  const d = dossiers.find((item) => item.id === e.target.value);
                  if (d) setSelectedDossier(d);
                }}
              >
                {dossiers.length === 0 && (
                  <option value="">No commercial dossiers created</option>
                )}
                {dossiers.map((d) => (
                  <option key={d.id} value={d.id}>
                    {d.suitNumber} - {d.parties.substring(0, 32)}...
                  </option>
                ))}
              </select>
            </div>

            <button
              type="button"
              className="gov-btn"
              onClick={() => setIsNewDossierOpen(true)}
              style={{
                padding: '6px 12px',
                fontSize: '0.775rem',
                backgroundColor: '#ffffff',
                border: '1px solid var(--gov-slate-300)',
                color: 'var(--gov-navy-900)',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                cursor: 'pointer',
              }}
              title="Create new commercial suit bench dossier"
            >
              <Plus size={14} />
              New Docket
            </button>

            <button
              type="button"
              className="gov-btn gov-btn-primary"
              onClick={handlePrint}
              title="Print formatted judicial bench memo"
            >
              <Printer size={14} />
              Print / Export Bench Memo
            </button>
          </div>
        </div>
      </div>

      {/* New Dossier Creation Modal */}
      {isNewDossierOpen && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            backgroundColor: 'rgba(15, 23, 42, 0.75)',
            backdropFilter: 'blur(3px)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 9999,
            padding: '16px',
          }}
        >
          <div
            style={{
              backgroundColor: '#ffffff',
              borderRadius: '6px',
              width: '100%',
              maxWidth: '520px',
              boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.2)',
              overflow: 'hidden',
              border: '1px solid var(--gov-slate-300)',
            }}
          >
            <div
              style={{
                backgroundColor: 'var(--gov-navy-900)',
                color: '#ffffff',
                padding: '14px 18px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
              }}
            >
              <div style={{ fontWeight: 700, fontSize: '0.95rem' }}>Create New Commercial Suit Dossier</div>
              <button
                type="button"
                onClick={() => setIsNewDossierOpen(false)}
                style={{ background: 'none', border: 'none', color: '#ffffff', cursor: 'pointer' }}
              >
                <X size={18} />
              </button>
            </div>

            <form onSubmit={handleCreateDossierSubmit} style={{ padding: '20px 22px', display: 'flex', flexDirection: 'column', gap: '14px' }}>
              {createDossierError && (
                <div style={{ backgroundColor: '#fff1f2', border: '1px solid #fecdd3', color: '#be123c', padding: '8px 12px', borderRadius: '4px', fontSize: '0.8rem' }}>
                  {createDossierError}
                </div>
              )}

              <div>
                <label style={{ display: 'block', fontSize: '0.775rem', fontWeight: 600, color: 'var(--gov-slate-700)', marginBottom: '4px' }}>
                  Commercial Suit Number *
                </label>
                <input
                  type="text"
                  className="gov-input"
                  placeholder="e.g. CS(COMM) 789/2026"
                  value={newSuitNumber}
                  onChange={(e) => setNewSuitNumber(e.target.value)}
                  required
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.775rem', fontWeight: 600, color: 'var(--gov-slate-700)', marginBottom: '4px' }}>
                  Parties / Title of Matter *
                </label>
                <input
                  type="text"
                  className="gov-input"
                  placeholder="e.g. Acme Logistics Ltd. v. Global Freight Corp."
                  value={newParties}
                  onChange={(e) => setNewParties(e.target.value)}
                  required
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.775rem', fontWeight: 600, color: 'var(--gov-slate-700)', marginBottom: '4px' }}>
                  Initial Chambers Notes / Cause of Action Summary
                </label>
                <textarea
                  className="gov-input"
                  rows={3}
                  placeholder="Brief summary of dispute, urgent relief prayed for, or procedural notes..."
                  value={newJudicialNotes}
                  onChange={(e) => setNewJudicialNotes(e.target.value)}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '6px' }}>
                <button
                  type="button"
                  className="gov-btn"
                  onClick={() => setIsNewDossierOpen(false)}
                  disabled={isCreatingDossier}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="gov-btn gov-btn-primary"
                  disabled={isCreatingDossier}
                >
                  {isCreatingDossier ? 'Persisting to Court Registry...' : 'Create Commercial Dossier'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Main Dossier Content */}
      {!selectedDossier ? (
        <div className="gov-panel" style={{ padding: '40px 20px', textAlign: 'center' }}>
          <Scale size={32} color="var(--gov-slate-400)" style={{ margin: '0 auto 12px' }} />
          <div style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--gov-navy-900)' }}>
            No Commercial Suit Dossier Active
          </div>
          <div style={{ fontSize: '0.825rem', color: 'var(--gov-slate-500)', marginTop: '4px', maxWidth: '440px', margin: '4px auto 16px' }}>
            Select an existing commercial docket from the selector above, or create a new bench memorandum to record judicial ratios and directions.
          </div>
          <button
            type="button"
            className="gov-btn gov-btn-primary"
            onClick={() => setIsNewDossierOpen(true)}
            style={{ margin: '0 auto' }}
          >
            <Plus size={14} /> Create Commercial Suit Dossier
          </button>
        </div>
      ) : (
        <div className="gov-split-layout">
          {/* Left Column: Matter Details & Compliance Status */}
          <div className="gov-pane-scroll" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div className="gov-panel">
              <div className="gov-panel-header">
                <span className="gov-panel-title">
                  <Scale size={16} /> Commercial Suit Information
                </span>
                <DemoDataBadge label="COMMERCIAL CAUSE LIST" />
              </div>

              <div className="gov-panel-body" style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
                <div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--gov-slate-500)', fontWeight: 600 }}>
                    SUIT NUMBER
                  </div>
                  <div style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--gov-navy-900)' }}>
                    {selectedDossier.suitNumber}
                  </div>
                </div>

                <div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--gov-slate-500)', fontWeight: 600 }}>
                    PARTIES
                  </div>
                  <div style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--gov-slate-800)' }}>
                    {selectedDossier.parties}
                  </div>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                  <div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--gov-slate-500)', fontWeight: 600 }}>
                      COMMERCIAL CATEGORY
                    </div>
                    <div style={{ fontSize: '0.8rem', color: 'var(--gov-slate-800)' }}>
                      {selectedDossier.commercialSubject}
                    </div>
                  </div>
                  <div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--gov-slate-500)', fontWeight: 600 }}>
                      NEXT HEARING
                    </div>
                    <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--gov-saffron-800)' }}>
                      {selectedDossier.nextHearingDate}
                    </div>
                  </div>
                </div>

                {/* Statutory Prerequisites Evaluation */}
                <div
                  style={{
                    padding: '12px',
                    backgroundColor: 'var(--gov-slate-50)',
                    border: '1px solid var(--gov-slate-200)',
                    borderRadius: 'var(--border-radius-sm)',
                  }}
                >
                  <div
                    style={{
                      fontSize: '0.75rem',
                      fontWeight: 700,
                      textTransform: 'uppercase',
                      color: 'var(--gov-slate-700)',
                      marginBottom: '8px',
                    }}
                  >
                    Commercial Statutory Prerequisite Checks
                  </div>

                  <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', fontSize: '0.8rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                      <span>Urgent Interim Relief Contemplated:</span>
                      <span
                        style={{
                          fontWeight: 600,
                          color: selectedDossier.isUrgentReliefContemplated ? '#15803d' : '#64748b',
                        }}
                      >
                        {selectedDossier.isUrgentReliefContemplated ? 'Yes (Ex-parte prayer)' : 'No'}
                      </span>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                      <span>Section 12A Pre-Institution Mediation:</span>
                      <span
                        style={{
                          fontWeight: 600,
                          color: selectedDossier.isSec12AExhausted ? '#15803d' : '#b91c1c',
                        }}
                      >
                        {selectedDossier.isSec12AExhausted ? 'Exhausted' : 'Not Exhausted (Patil Automation bar)'}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Judicial Background Notes */}
                <div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--gov-slate-500)', fontWeight: 600, marginBottom: '4px' }}>
                    CHAMBERS PRE-HEARING SYNOPSIS
                  </div>
                  <div
                    style={{
                      padding: '10px 12px',
                      backgroundColor: 'var(--gov-paper-warm)',
                      border: '1px solid var(--gov-slate-200)',
                      fontSize: '0.825rem',
                      lineHeight: '1.6',
                      color: 'var(--gov-slate-800)',
                    }}
                  >
                    {selectedDossier.judicialNotes || 'No synopsis recorded.'}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Right Column: Pinned Authorities, Bench Notes, and Add Note Form */}
          <div className="gov-pane-scroll" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {/* Printable Formal Memorandum Document */}
            <div className="judgment-paper" style={{ padding: '28px 32px' }}>
              <div style={{ textAlign: 'center', borderBottom: '2px solid var(--gov-slate-300)', paddingBottom: '16px', marginBottom: '20px' }}>
                <div style={{ fontFamily: 'var(--font-display)', fontSize: '1.1rem', fontWeight: 700, color: 'var(--gov-navy-900)' }}>
                  COMMERCIAL APPELLATE DIVISION, HIGH COURT OF DELHI
                </div>
                <div style={{ fontSize: '0.8rem', color: 'var(--gov-slate-600)', marginTop: '2px', fontWeight: 600 }}>
                  CHAMBERS BENCH MEMORANDUM • DEMONSTRATION DATA (SIH DEMO)
                </div>
                <div style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--gov-navy-800)', marginTop: '8px' }}>
                  IN RE: {selectedDossier.suitNumber.includes('DEMO') ? selectedDossier.suitNumber : `[DEMO MATTER] ${selectedDossier.suitNumber}`} ({selectedDossier.parties})
                </div>
                <div style={{ fontSize: '0.75rem', color: 'var(--gov-slate-500)' }}>
                  Compiled by: {currentUser.fullName} ({currentUser.title})
                </div>
              </div>

              {/* Pinned Precedents */}
              <div style={{ marginBottom: '20px' }}>
                <div
                  style={{
                    fontSize: '0.75rem',
                    fontWeight: 700,
                    textTransform: 'uppercase',
                    color: 'var(--gov-slate-600)',
                    marginBottom: '8px',
                    borderBottom: '1px solid var(--gov-slate-200)',
                    paddingBottom: '4px',
                  }}
                >
                  1. Authoritative Precedents to be Addressed by Counsel ({selectedDossier.pinnedCases.length})
                </div>
                <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginBottom: '12px' }}>
                  {selectedDossier.pinnedCases.length === 0 && (
                    <span style={{ fontSize: '0.8rem', color: 'var(--gov-slate-400)', fontStyle: 'italic' }}>
                      No authoritative precedents pinned yet. Pin precedents from Legal Research or Precedents reader.
                    </span>
                  )}
                  {selectedDossier.pinnedCases.map((c, idx) => {
                    const item = selectedDossier.items?.find((i) => i.item_type === 'CASE' && i.title === c);
                    return (
                      <span
                        key={idx}
                        style={{
                          padding: '4px 10px',
                          backgroundColor: 'var(--gov-navy-50)',
                          border: '1px solid var(--gov-navy-600)',
                          color: 'var(--gov-navy-900)',
                          fontSize: '0.8rem',
                          fontWeight: 600,
                          borderRadius: '2px',
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: '6px',
                        }}
                      >
                        ★ {c}
                        {item?.id && (
                          <button
                            type="button"
                            onClick={() => removeDossierItem(selectedDossier.id, item.id!)}
                            style={{ background: 'none', border: 'none', cursor: 'pointer', padding: 0, display: 'inline-flex', alignItems: 'center' }}
                            title="Remove pinned precedent from dossier"
                          >
                            <X size={12} color="#64748b" />
                          </button>
                        )}
                      </span>
                    );
                  })}
                </div>
              </div>

              {/* Pinned Statutory Provisions */}
              {selectedDossier.pinnedSections && selectedDossier.pinnedSections.length > 0 && (
                <div style={{ marginBottom: '20px' }}>
                  <div
                    style={{
                      fontSize: '0.75rem',
                      fontWeight: 700,
                      textTransform: 'uppercase',
                      color: 'var(--gov-slate-600)',
                      marginBottom: '8px',
                      borderBottom: '1px solid var(--gov-slate-200)',
                      paddingBottom: '4px',
                    }}
                  >
                    2. Statutory Provisions Pinned for Verification ({selectedDossier.pinnedSections.length})
                  </div>
                  <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginBottom: '12px' }}>
                    {selectedDossier.pinnedSections.map((s, idx) => {
                      const item = selectedDossier.items?.find((i) => i.item_type === 'SECTION' && i.title === s);
                      return (
                        <span
                          key={idx}
                          style={{
                            padding: '4px 10px',
                            backgroundColor: '#f8fafc',
                            border: '1px solid var(--gov-slate-300)',
                            color: 'var(--gov-slate-800)',
                            fontSize: '0.8rem',
                            fontWeight: 600,
                            borderRadius: '2px',
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: '6px',
                          }}
                        >
                          § {s}
                          {item?.id && (
                            <button
                              type="button"
                              onClick={() => removeDossierItem(selectedDossier.id, item.id!)}
                              style={{ background: 'none', border: 'none', cursor: 'pointer', padding: 0, display: 'inline-flex', alignItems: 'center' }}
                              title="Remove pinned statutory provision"
                            >
                              <X size={12} color="#64748b" />
                            </button>
                          )}
                        </span>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* Bench Notes & Queries List */}
              <div style={{ marginBottom: '24px' }}>
                <div
                  style={{
                    fontSize: '0.75rem',
                    fontWeight: 700,
                    textTransform: 'uppercase',
                    color: 'var(--gov-slate-600)',
                    marginBottom: '8px',
                    borderBottom: '1px solid var(--gov-slate-200)',
                    paddingBottom: '4px',
                  }}
                >
                  {selectedDossier.pinnedSections && selectedDossier.pinnedSections.length > 0 ? '3.' : '2.'} Chambers Research Notes & Bench Queries ({selectedDossier.dossierNotes.length})
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                  {selectedDossier.dossierNotes.length === 0 && (
                    <div style={{ fontSize: '0.8rem', color: 'var(--gov-slate-400)', fontStyle: 'italic', padding: '8px 0' }}>
                      No bench notes or oral queries recorded yet. Use the form below to append judicial notes.
                    </div>
                  )}
                  {selectedDossier.dossierNotes.map((note) => {
                    const item = selectedDossier.items?.find((i) => i.id === note.id);
                    return (
                      <div
                        key={note.id}
                        style={{
                          padding: '12px 14px',
                          backgroundColor: '#ffffff',
                          border: '1px solid var(--gov-slate-200)',
                          borderLeft: '4px solid var(--gov-navy-800)',
                        }}
                      >
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                          <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--gov-navy-800)' }}>
                            {note.sourceReference}
                          </span>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                            <span style={{ fontSize: '0.7rem', color: 'var(--gov-slate-400)' }}>
                              {note.timestamp}
                            </span>
                            {item?.id && (
                              <button
                                type="button"
                                onClick={() => removeDossierItem(selectedDossier.id, item.id!)}
                                style={{ background: 'none', border: 'none', cursor: 'pointer', padding: '2px', display: 'inline-flex', alignItems: 'center' }}
                                title="Delete this note"
                              >
                                <X size={13} color="#94a3b8" />
                              </button>
                            )}
                          </div>
                        </div>
                        <div style={{ fontSize: '0.85rem', lineHeight: '1.6', color: 'var(--gov-slate-800)' }}>
                          {note.content}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Add New Note Form (Hidden when printing) */}
              <div className="no-print" style={{ borderTop: '1px dashed var(--gov-slate-300)', paddingTop: '16px' }}>
                <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--gov-slate-700)', marginBottom: '8px' }}>
                  Add Note / Oral Query for this Matter
                </div>
                <form onSubmit={handleAddNote} style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                  <input
                    type="text"
                    className="gov-input"
                    placeholder="Reference (e.g., Para 91 Patil Automation or Plaint Page 14)"
                    value={newNoteSource}
                    onChange={(e) => setNewNoteSource(e.target.value)}
                  />
                  <textarea
                    className="gov-input"
                    rows={3}
                    placeholder="Enter judicial query, direction, or ratio extract to record for this docket..."
                    value={newNoteContent}
                    onChange={(e) => setNewNoteContent(e.target.value)}
                  />
                  <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
                    <button type="submit" className="gov-btn gov-btn-primary" disabled={isAddingNote}>
                      {isAddingNote ? 'Persisting...' : <><Plus size={14} /> Add to Dossier</>}
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

