import React, { useState, useEffect } from 'react';
import {
  Bookmark,
  History,
  X,
  Trash2,
  ExternalLink,
  Clock,
} from 'lucide-react';
import { SavedResearchItem, ResearchSessionHistoryItem } from '../../types';
import { fetchSavedResearchApi, deleteSavedResearchApi, fetchSessionHistoryApi } from '../../api/researchClient';
import { DemoDataBadge } from '../common/DemoDataBadge';
import { ApiErrorBanner } from '../common/ApiErrorBanner';

interface SavedResearchDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectSavedQuery: (query: string, context?: string, jurisdiction?: string) => void;
}

export const SavedResearchDrawer: React.FC<SavedResearchDrawerProps> = ({
  isOpen,
  onClose,
  onSelectSavedQuery,
}) => {
  const [activeSubTab, setActiveSubTab] = useState<'saved' | 'history'>('saved');
  const [savedList, setSavedList] = useState<SavedResearchItem[]>([]);
  const [historyList, setHistoryList] = useState<ResearchSessionHistoryItem[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [drawerError, setDrawerError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen) {
      loadData();
    }
  }, [isOpen]);

  const loadData = async () => {
    setLoading(true);
    setDrawerError(null);
    try {
      const [saved, history] = await Promise.all([
        fetchSavedResearchApi(),
        fetchSessionHistoryApi(),
      ]);
      setSavedList(saved);
      setHistoryList(history);
    } catch (err: any) {
      console.error('Error loading saved research data:', err);
      setDrawerError(err.message || 'Unable to connect to Chambers API for saved research.');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteSaved = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (window.confirm('Remove this research item from chambers bookmarks?')) {
      await deleteSavedResearchApi(id);
      setSavedList((prev) => prev.filter((item) => item.id !== id));
    }
  };

  if (!isOpen) return null;

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        right: 0,
        bottom: 0,
        width: '520px',
        maxWidth: '90vw',
        backgroundColor: '#ffffff',
        boxShadow: '-4px 0 20px rgba(0, 0, 0, 0.15)',
        zIndex: 1000,
        display: 'flex',
        flexDirection: 'column',
        borderLeft: '2px solid var(--gov-navy-800)',
      }}
    >
      {/* Drawer Header */}
      <div
        style={{
          padding: '16px 20px',
          backgroundColor: 'var(--gov-navy-900)',
          color: '#ffffff',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Bookmark size={18} style={{ color: 'var(--gov-gold-400)' }} />
          <div>
            <h3 style={{ margin: 0, fontSize: '0.95rem', fontWeight: 700, letterSpacing: '0.02em' }}>
              Chambers Research Archive & History
            </h3>
            <div style={{ fontSize: '0.725rem', color: 'var(--gov-slate-300)' }}>
              Commercial Division Docket Integration
            </div>
          </div>
        </div>

        <button
          type="button"
          onClick={onClose}
          style={{
            background: 'none',
            border: 'none',
            color: '#ffffff',
            cursor: 'pointer',
            padding: '4px',
          }}
        >
          <X size={20} />
        </button>
      </div>

      {/* Navigation Sub-Tabs */}
      <div
        style={{
          display: 'flex',
          borderBottom: '1px solid var(--gov-slate-300)',
          backgroundColor: '#f8fafc',
        }}
      >
        <button
          type="button"
          onClick={() => setActiveSubTab('saved')}
          style={{
            flex: 1,
            padding: '10px 14px',
            border: 'none',
            borderBottom: activeSubTab === 'saved' ? '2px solid var(--gov-navy-800)' : 'none',
            backgroundColor: activeSubTab === 'saved' ? '#ffffff' : 'transparent',
            fontWeight: activeSubTab === 'saved' ? 700 : 500,
            color: activeSubTab === 'saved' ? 'var(--gov-navy-900)' : 'var(--gov-slate-600)',
            fontSize: '0.8rem',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '6px',
          }}
        >
          <Bookmark size={14} />
          <span>Saved Research ({savedList.length})</span>
        </button>

        <button
          type="button"
          onClick={() => setActiveSubTab('history')}
          style={{
            flex: 1,
            padding: '10px 14px',
            border: 'none',
            borderBottom: activeSubTab === 'history' ? '2px solid var(--gov-navy-800)' : 'none',
            backgroundColor: activeSubTab === 'history' ? '#ffffff' : 'transparent',
            fontWeight: activeSubTab === 'history' ? 700 : 500,
            color: activeSubTab === 'history' ? 'var(--gov-navy-900)' : 'var(--gov-slate-600)',
            fontSize: '0.8rem',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '6px',
          }}
        >
          <History size={14} />
          <span>Session Audit History ({historyList.length})</span>
        </button>
      </div>

      {/* Drawer Content Area */}
      <div
        style={{
          flex: 1,
          overflowY: 'auto',
          padding: '16px',
          backgroundColor: '#fafbfc',
        }}
      >
        {drawerError && (
          <ApiErrorBanner
            title="Saved Research Unavailable"
            message={drawerError}
            onRetry={loadData}
          />
        )}

        {loading ? (
          <div style={{ textAlign: 'center', padding: '30px', color: 'var(--gov-slate-500)', fontSize: '0.825rem' }}>
            Retrieving judicial research records...
          </div>
        ) : activeSubTab === 'saved' ? (
          savedList.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '30px', color: 'var(--gov-slate-500)', fontSize: '0.825rem' }}>
              No saved research bookmarks. Click <strong>"Bookmark Research"</strong> on any research result to save it here.
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {savedList.map((item) => (
                <div
                  key={item.id}
                  style={{
                    backgroundColor: '#ffffff',
                    border: '1px solid var(--gov-slate-300)',
                    padding: '12px 14px',
                    boxShadow: '0 1px 3px rgba(0, 0, 0, 0.04)',
                    cursor: 'pointer',
                    transition: 'border-color 0.15s ease',
                  }}
                  onClick={() => {
                    onSelectSavedQuery(item.query_text, item.case_context, item.jurisdiction);
                    onClose();
                  }}
                >
                  <div
                    style={{
                      display: 'flex',
                      alignItems: 'flex-start',
                      justifyContent: 'space-between',
                      marginBottom: '6px',
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      {item.matter_id && (
                        <span
                          style={{
                            fontSize: '0.675rem',
                            fontWeight: 700,
                            color: 'var(--gov-navy-900)',
                            backgroundColor: '#eff6ff',
                            padding: '2px 6px',
                            border: '1px solid #bfdbfe',
                          }}
                        >
                          {item.matter_id}
                        </span>
                      )}
                      <span
                        style={{
                          fontSize: '0.675rem',
                          fontWeight: 700,
                          padding: '2px 6px',
                          backgroundColor:
                            item.uncertainty_level === 'LOW'
                              ? '#ecfdf5'
                              : item.uncertainty_level === 'MEDIUM'
                              ? '#fffbeb'
                              : '#fef2f2',
                          color:
                            item.uncertainty_level === 'LOW'
                              ? 'var(--gov-emerald-800)'
                              : item.uncertainty_level === 'MEDIUM'
                              ? '#92400e'
                              : '#b91c1c',
                        }}
                      >
                        {item.uncertainty_level} UNCERTAINTY
                      </span>
                      {item.is_demo_data && <DemoDataBadge size="small" />}
                    </div>

                    <button
                      type="button"
                      onClick={(e) => handleDeleteSaved(item.id, e)}
                      style={{
                        background: 'none',
                        border: 'none',
                        color: 'var(--gov-slate-400)',
                        cursor: 'pointer',
                        padding: '2px',
                      }}
                      title="Remove bookmark"
                    >
                      <Trash2 size={14} />
                    </button>
                  </div>

                  <h5
                    style={{
                      margin: '0 0 4px 0',
                      fontSize: '0.825rem',
                      fontWeight: 700,
                      color: 'var(--gov-navy-900)',
                      lineHeight: '1.3',
                    }}
                  >
                    {item.query_text}
                  </h5>

                  <div style={{ fontSize: '0.725rem', color: 'var(--gov-slate-600)', marginBottom: '6px' }}>
                    Lead Citation:{' '}
                    <strong style={{ color: 'var(--gov-slate-900)' }}>
                      {item.lead_title} [{item.lead_citation}]
                    </strong>
                  </div>

                  {item.notes && (
                    <div
                      style={{
                        fontSize: '0.725rem',
                        backgroundColor: '#f8fafc',
                        borderLeft: '3px solid var(--gov-gold-500)',
                        padding: '6px 8px',
                        color: 'var(--gov-slate-800)',
                        marginBottom: '6px',
                        lineHeight: '1.35',
                      }}
                    >
                      <strong>Chambers Note: </strong>
                      {item.notes}
                    </div>
                  )}

                  <div
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      fontSize: '0.675rem',
                      color: 'var(--gov-slate-500)',
                      borderTop: '1px solid var(--gov-slate-100)',
                      paddingTop: '6px',
                    }}
                  >
                    <span>Jurisdiction: {item.jurisdiction}</span>
                    <span style={{ color: 'var(--gov-navy-800)', fontWeight: 600 }}>
                      Click to Reload Query →
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )
        ) : historyList.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '30px', color: 'var(--gov-slate-500)', fontSize: '0.825rem' }}>
            No research queries recorded in this session.
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {historyList.map((hist) => (
              <div
                key={hist.id}
                style={{
                  backgroundColor: '#ffffff',
                  border: '1px solid var(--gov-slate-200)',
                  padding: '10px 12px',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'flex-start',
                  justifyContent: 'space-between',
                  gap: '8px',
                }}
                onClick={() => {
                  onSelectSavedQuery(hist.query, undefined, hist.jurisdiction);
                  onClose();
                }}
              >
                <div>
                  <div
                    style={{
                      fontSize: '0.775rem',
                      fontWeight: 600,
                      color: 'var(--gov-slate-900)',
                      lineHeight: '1.3',
                      marginBottom: '3px',
                    }}
                  >
                    {hist.query}
                  </div>
                  <div
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px',
                      fontSize: '0.7rem',
                      color: 'var(--gov-slate-500)',
                    }}
                  >
                    <Clock size={11} />
                    <span>{hist.timestamp}</span>
                    <span>•</span>
                    <span>{hist.jurisdiction}</span>
                    <span>•</span>
                    <span>{hist.results_count} authorities</span>
                  </div>
                </div>

                <ExternalLink size={13} style={{ color: 'var(--gov-navy-800)', flexShrink: 0, marginTop: '2px' }} />
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Drawer Footer */}
      <div
        style={{
          padding: '12px 20px',
          borderTop: '1px solid var(--gov-slate-200)',
          backgroundColor: '#f8fafc',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          fontSize: '0.725rem',
          color: 'var(--gov-slate-500)',
        }}
      >
        <span>NIC Secure Court Registry Sync</span>
        <button
          type="button"
          onClick={onClose}
          style={{
            padding: '4px 12px',
            backgroundColor: 'var(--gov-navy-800)',
            color: '#ffffff',
            border: 'none',
            fontSize: '0.75rem',
            cursor: 'pointer',
          }}
        >
          Close Drawer
        </button>
      </div>
    </div>
  );
};
