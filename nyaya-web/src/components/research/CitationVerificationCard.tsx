import React from 'react';
import {
  CheckCircle2,
  AlertTriangle,
  History,
  FileCheck,
} from 'lucide-react';
import { CitationVerificationDTO } from '../../types';
import { DemoDataBadge } from '../common/DemoDataBadge';

interface CitationVerificationCardProps {
  verification: CitationVerificationDTO;
}

export const CitationVerificationCard: React.FC<CitationVerificationCardProps> = ({
  verification,
}) => {
  const statusLower = (verification.good_law_status || '').toLowerCase();
  const isOverruled = !verification.is_good_law || statusLower.includes('overruled');
  const isCaution = statusLower.includes('caution') || statusLower.includes('distinguished') || statusLower.includes('modified');
  const isNoTreatment = verification.corpus_coverage_status === 'NO_TREATMENT_FOUND' || statusLower.includes('no treatment');
  const isInsufficient = verification.corpus_coverage_status === 'INSUFFICIENT_CORPUS' || statusLower.includes('insufficient');

  const cardBorderLeft = isOverruled ? '#dc2626' : isCaution ? '#d97706' : isNoTreatment ? 'var(--gov-slate-400)' : 'var(--gov-emerald-700)';
  const badgeBg = isOverruled ? '#fef2f2' : isCaution ? '#fffbeb' : isNoTreatment ? '#f8fafc' : isInsufficient ? '#fef2f2' : '#ecfdf5';
  const badgeColor = isOverruled ? '#b91c1c' : isCaution ? '#b45309' : isNoTreatment ? 'var(--gov-slate-700)' : isInsufficient ? '#b91c1c' : 'var(--gov-emerald-800)';
  const badgeBorder = isOverruled ? '#fecaca' : isCaution ? '#fde68a' : isNoTreatment ? 'var(--gov-slate-300)' : isInsufficient ? '#fecaca' : '#a7f3d0';

  return (
    <div
      style={{
        backgroundColor: '#ffffff',
        border: '1px solid var(--gov-slate-300)',
        borderLeft: `4px solid ${cardBorderLeft}`,
        padding: '14px 16px',
        marginBottom: '14px',
        boxShadow: 'var(--gov-shadow-sm)',
      }}
    >
      {/* Top Bar */}
      <div
        style={{
          display: 'flex',
          alignItems: 'flex-start',
          justifyContent: 'space-between',
          gap: '12px',
          marginBottom: '10px',
        }}
      >
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <span
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '4px',
                fontSize: '0.725rem',
                fontWeight: 700,
                padding: '2px 8px',
                backgroundColor: badgeBg,
                color: badgeColor,
                border: `1px solid ${badgeBorder}`,
                borderRadius: '2px',
                textTransform: 'uppercase',
                letterSpacing: '0.03em',
              }}
            >
              {isOverruled || isInsufficient ? (
                <AlertTriangle size={13} />
              ) : isCaution ? (
                <AlertTriangle size={13} />
              ) : (
                <CheckCircle2 size={13} />
              )}
              {verification.good_law_status}
            </span>

            <span
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '4px',
                fontSize: '0.725rem',
                fontWeight: 600,
                padding: '2px 8px',
                backgroundColor: '#eff6ff',
                color: 'var(--gov-navy-800)',
                border: '1px solid #bfdbfe',
                borderRadius: '2px',
              }}
            >
              <FileCheck size={12} />
              Reporter: {verification.official_reporter}
            </span>

            {verification.is_demo_data && <DemoDataBadge size="small" />}
          </div>

          <h4
            style={{
              margin: '0 0 4px 0',
              fontSize: '0.95rem',
              fontWeight: 700,
              color: 'var(--gov-slate-900)',
              lineHeight: '1.35',
            }}
          >
            {verification.case_title}
          </h4>

          <div
            style={{
              display: 'flex',
              flexWrap: 'wrap',
              gap: '12px',
              fontSize: '0.775rem',
              color: 'var(--gov-slate-600)',
            }}
          >
            <span>
              Standard Citation: <strong style={{ color: 'var(--gov-navy-900)' }}>{verification.standard_citation}</strong>
            </span>
            {verification.neutral_citation && (
              <span>
                Neutral Citation: <strong style={{ color: 'var(--gov-navy-900)' }}>{verification.neutral_citation}</strong>
              </span>
            )}
            <span>
              Date: <strong>{verification.judgment_date}</strong>
            </span>
          </div>
        </div>

        {/* Bench Quorum Box */}
        <div
          style={{
            textAlign: 'right',
            backgroundColor: '#f8fafc',
            border: '1px solid var(--gov-slate-200)',
            padding: '6px 10px',
            minWidth: '160px',
          }}
        >
          <div style={{ fontSize: '0.7rem', color: 'var(--gov-slate-500)', textTransform: 'uppercase' }}>
            Bench Quorum
          </div>
          <div
            style={{
              fontSize: '0.825rem',
              fontWeight: 700,
              color: 'var(--gov-navy-900)',
              marginTop: '2px',
            }}
          >
            {verification.bench_strength}-Judge Bench
          </div>
          <div
            style={{
              fontSize: '0.7rem',
              color: 'var(--gov-slate-600)',
              lineHeight: '1.2',
              marginTop: '2px',
            }}
          >
            {verification.bench_quorum}
          </div>
        </div>
      </div>

      {/* Verification Notes */}
      {verification.verification_notes && (
        <div
          style={{
            fontSize: '0.775rem',
            color: 'var(--gov-slate-700)',
            backgroundColor: '#f8fafc',
            padding: '8px 10px',
            border: '1px solid var(--gov-slate-200)',
            marginBottom: '10px',
            lineHeight: '1.4',
          }}
        >
          <strong style={{ color: 'var(--gov-navy-900)' }}>Verification Note: </strong>
          {verification.verification_notes}
        </div>
      )}

      {/* Treatment History (Shepardize Table) */}
      {verification.treatment_history && verification.treatment_history.length > 0 && (
        <div>
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              fontSize: '0.725rem',
              fontWeight: 700,
              textTransform: 'uppercase',
              letterSpacing: '0.04em',
              color: 'var(--gov-slate-600)',
              marginBottom: '6px',
            }}
          >
            <History size={13} />
            Subsequent Judicial Treatment & Citation Trail
          </div>

          <table
            style={{
              width: '100%',
              fontSize: '0.75rem',
              borderCollapse: 'collapse',
              border: '1px solid var(--gov-slate-200)',
            }}
          >
            <thead>
              <tr style={{ backgroundColor: '#f1f5f9', color: 'var(--gov-slate-700)' }}>
                <th style={{ padding: '4px 8px', textAlign: 'left', width: '100px' }}>Treatment</th>
                <th style={{ padding: '4px 8px', textAlign: 'left' }}>Subsequent Citing Case</th>
                <th style={{ padding: '4px 8px', textAlign: 'left', width: '150px' }}>Citation</th>
                <th style={{ padding: '4px 8px', textAlign: 'left', width: '130px' }}>Court & Quorum</th>
              </tr>
            </thead>
            <tbody>
              {verification.treatment_history.map((t, idx) => {
                const treatmentColor =
                  t.treatment === 'OVERRULED'
                    ? '#b91c1c'
                    : t.treatment === 'DISTINGUISHED' || t.treatment === 'MODIFIED'
                    ? '#b45309'
                    : 'var(--gov-emerald-700)';

                return (
                  <tr
                    key={idx}
                    style={{
                      borderTop: '1px solid var(--gov-slate-200)',
                      backgroundColor: idx % 2 === 0 ? '#ffffff' : '#fafbfc',
                    }}
                  >
                    <td style={{ padding: '5px 8px', fontWeight: 700, color: treatmentColor }}>
                      {t.treatment}
                    </td>
                    <td style={{ padding: '5px 8px', color: 'var(--gov-slate-800)', fontWeight: 500 }}>
                      {t.citing_case}
                    </td>
                    <td style={{ padding: '5px 8px', color: 'var(--gov-slate-600)', fontFamily: 'monospace' }}>
                      {t.citation}
                    </td>
                    <td style={{ padding: '5px 8px', color: 'var(--gov-slate-600)' }}>
                      {t.court} ({t.bench_strength}J)
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
