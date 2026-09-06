import React, { useState } from 'react';
import {
  TrendingUp,
  Scale,
  ShieldAlert,
  ChevronDown,
  ChevronUp,
  Building2,
  Calendar,
  Layers,
  FileCheck,
  AlertTriangle,
} from 'lucide-react';
import { HistoricalPatternAnalysisDTO } from '../../types';

interface HistoricalPatternCardProps {
  analysis: HistoricalPatternAnalysisDTO;
}

export const HistoricalPatternCard: React.FC<HistoricalPatternCardProps> = ({ analysis }) => {
  const [isExpanded, setIsExpanded] = useState<boolean>(true);

  return (
    <div
      style={{
        backgroundColor: '#ffffff',
        border: '1px solid var(--gov-slate-300)',
        borderTop: '3px solid #1e3a8a',
        borderRadius: 'var(--border-radius-sm)',
        boxShadow: 'var(--gov-shadow-sm)',
        overflow: 'hidden',
        marginBottom: '16px',
      }}
    >
      {/* Card Header */}
      <div
        style={{
          padding: '12px 18px',
          backgroundColor: '#fafbfc',
          borderBottom: '1px solid var(--gov-slate-200)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          cursor: 'pointer',
          flexWrap: 'wrap',
          gap: '10px',
        }}
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <TrendingUp size={18} style={{ color: '#1e3a8a' }} />
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
              <span
                style={{
                  fontSize: '0.85rem',
                  fontWeight: 700,
                  color: 'var(--gov-navy-900)',
                  letterSpacing: '0.02em',
                }}
              >
                Historical Precedent Pattern Analysis
              </span>
              <span
                style={{
                  fontSize: '0.675rem',
                  fontWeight: 600,
                  padding: '2px 8px',
                  backgroundColor: '#e0f2fe',
                  color: '#0369a1',
                  border: '1px solid #bae6fd',
                  borderRadius: '2px',
                }}
              >
                Assistive Benchmark • Non-ML Empirical Observation
              </span>
            </div>
            <div style={{ fontSize: '0.725rem', color: 'var(--gov-slate-600)', marginTop: '2px' }}>
              Observed procedural postures & substantive dispositions across {analysis.comparable_authorities_count} authentic precedent(s)
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontSize: '0.75rem', color: 'var(--gov-slate-500)' }}>
            {isExpanded ? 'Collapse' : 'Expand'}
          </span>
          {isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
        </div>
      </div>

      {isExpanded && (
        <div style={{ padding: '16px 20px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {/* Strict Non-Predictive Legal Invariant Banner */}
          <div
            style={{
              padding: '8px 14px',
              backgroundColor: '#eff6ff',
              borderLeft: '4px solid #1e40af',
              borderRadius: '2px',
              fontSize: '0.75rem',
              color: '#1e3a8a',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              fontWeight: 600,
            }}
          >
            <Scale size={14} style={{ color: '#1e40af', flexShrink: 0 }} />
            <span>Historical observation only — not a prediction of the present case outcome.</span>
          </div>

          {/* Summary Metadata Grid */}
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
              gap: '12px',
              padding: '12px 16px',
              backgroundColor: '#f8fafc',
              border: '1px solid var(--gov-slate-200)',
              borderRadius: 'var(--border-radius-sm)',
            }}
          >
            <div>
              <div style={{ fontSize: '0.7rem', color: 'var(--gov-slate-500)', display: 'flex', alignItems: 'center', gap: '4px' }}>
                <Calendar size={12} /> Temporal Benchmark Span
              </div>
              <div style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--gov-navy-900)' }}>
                {analysis.temporal_span}
              </div>
            </div>

            <div>
              <div style={{ fontSize: '0.7rem', color: 'var(--gov-slate-500)', display: 'flex', alignItems: 'center', gap: '4px' }}>
                <Building2 size={12} /> Jurisdiction & Courts
              </div>
              <div style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--gov-navy-900)' }}>
                {analysis.courts_represented.join(' • ')}
              </div>
            </div>

            <div>
              <div style={{ fontSize: '0.7rem', color: 'var(--gov-slate-500)', display: 'flex', alignItems: 'center', gap: '4px' }}>
                <Layers size={12} /> Legal Regime Era
              </div>
              <div style={{ fontSize: '0.825rem', fontWeight: 600, color: 'var(--gov-navy-900)' }}>
                {analysis.legal_regime_period}
              </div>
            </div>

            <div>
              <div style={{ fontSize: '0.7rem', color: 'var(--gov-slate-500)', display: 'flex', alignItems: 'center', gap: '4px' }}>
                <Scale size={12} /> Bench Quorum Breakdown
              </div>
              <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--gov-slate-700)' }}>
                {Object.entries(analysis.bench_strength_breakdown)
                  .map(([quorum, count]) => `${quorum}: ${count}`)
                  .join(' | ')}
              </div>
            </div>
          </div>

          {/* Active Precedent Postures & Dispositions Table */}
          <div>
            <div style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--gov-slate-900)', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <FileCheck size={14} style={{ color: '#059669' }} /> Observed Procedural Postures & Dispositions in Controlling Precedents
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {analysis.active_precedent_patterns.map((item, idx) => (
                <div
                  key={idx}
                  style={{
                    border: '1px solid #e2e8f0',
                    borderLeft: '4px solid #059669',
                    borderRadius: 'var(--border-radius-sm)',
                    padding: '10px 14px',
                    backgroundColor: '#ffffff',
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '8px', marginBottom: '4px' }}>
                    <div>
                      <strong style={{ fontSize: '0.825rem', color: 'var(--gov-navy-900)' }}>{item.case_title}</strong>{' '}
                      <span style={{ fontSize: '0.75rem', color: 'var(--gov-slate-600)' }}>({item.standard_citation})</span>
                    </div>
                    <span
                      style={{
                        fontSize: '0.65rem',
                        fontWeight: 700,
                        padding: '2px 6px',
                        backgroundColor: '#dcfce7',
                        color: '#15803d',
                        border: '1px solid #86efac',
                        borderRadius: '2px',
                      }}
                    >
                      {item.legal_status}
                    </span>
                  </div>

                  <div style={{ fontSize: '0.75rem', color: 'var(--gov-slate-700)', marginBottom: '4px' }}>
                    <strong>Procedural Posture:</strong> {item.procedural_posture}
                  </div>

                  <div style={{ fontSize: '0.75rem', color: '#0f172a', marginBottom: '4px', backgroundColor: '#f0fdf4', padding: '6px 10px', borderRadius: '2px', border: '1px solid #bbf7d0' }}>
                    <strong style={{ color: '#166534' }}>Observed Substantive Disposition:</strong> {item.actual_disposition}
                  </div>

                  <div style={{ fontSize: '0.675rem', color: 'var(--gov-slate-500)', fontStyle: 'italic' }}>
                    Provenance: {item.disposition_provenance} • Citator Treatment: {item.treatment_summary}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Overruled Precedents Panel (Regime Guard Isolation) */}
          {analysis.overruled_precedent_patterns.length > 0 && (
            <div
              style={{
                border: '1px solid #fecaca',
                borderLeft: '4px solid #dc2626',
                borderRadius: 'var(--border-radius-sm)',
                padding: '12px 14px',
                backgroundColor: '#fef2f2',
              }}
            >
              <div style={{ fontSize: '0.8rem', fontWeight: 700, color: '#991b1b', marginBottom: '6px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <AlertTriangle size={14} style={{ color: '#dc2626' }} /> Historical / Overruled Precedent Posture (Regime Guard Active)
              </div>
              <div style={{ fontSize: '0.725rem', color: '#7f1d1d', marginBottom: '8px' }}>
                The following precedent disposition is superseded by larger Constitution Bench jurisprudence and is isolated from active law:
              </div>
              {analysis.overruled_precedent_patterns.map((item, idx) => (
                <div key={idx} style={{ backgroundColor: '#ffffff', border: '1px solid #fca5a5', padding: '8px 12px', borderRadius: '2px' }}>
                  <div style={{ fontSize: '0.8rem', fontWeight: 700, color: '#991b1b' }}>
                    {item.case_title} ({item.standard_citation})
                  </div>
                  <div style={{ fontSize: '0.725rem', color: '#334155', marginTop: '2px' }}>
                    <strong>Historical Posture:</strong> {item.procedural_posture}
                  </div>
                  <div style={{ fontSize: '0.725rem', color: '#991b1b', marginTop: '2px' }}>
                    <strong>Historical Disposition:</strong> {item.actual_disposition}
                  </div>
                  <div style={{ fontSize: '0.675rem', color: 'var(--gov-slate-500)', marginTop: '2px', fontStyle: 'italic' }}>
                    Provenance: {item.disposition_provenance}
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Scientific Data-Readiness Notice */}
          <div
            style={{
              padding: '10px 14px',
              backgroundColor: '#fffbeb',
              border: '1px solid #fde68a',
              borderRadius: 'var(--border-radius-sm)',
              fontSize: '0.725rem',
              color: '#92400e',
              lineHeight: '1.45',
            }}
          >
            <div style={{ fontWeight: 700, marginBottom: '2px', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <ShieldAlert size={13} style={{ color: '#b45309' }} /> Scientific Data-Readiness Criterion:
            </div>
            {analysis.data_readiness_notice}
          </div>

          {/* Judicial Independence Disclaimer */}
          <div
            style={{
              fontSize: '0.7rem',
              color: 'var(--gov-slate-500)',
              borderTop: '1px solid var(--gov-slate-200)',
              paddingTop: '8px',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
            }}
          >
            <Scale size={13} style={{ flexShrink: 0 }} />
            <span>{analysis.judicial_disclaimer}</span>
          </div>
        </div>
      )}
    </div>
  );
};
