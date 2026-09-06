import React from 'react';
import { AlertTriangle, CheckCircle, ShieldAlert } from 'lucide-react';
import { UncertaintyAssessmentDTO } from '../../types';

interface UncertaintyBannerProps {
  assessment: UncertaintyAssessmentDTO;
}

export const UncertaintyBanner: React.FC<UncertaintyBannerProps> = ({ assessment }) => {
  const isHigh = assessment.uncertainty_level === 'HIGH';
  const isMed = assessment.uncertainty_level === 'MEDIUM';


  const borderColor = isHigh ? '#dc2626' : isMed ? '#d97706' : 'var(--gov-emerald-700)';
  const bgColor = isHigh ? '#fef2f2' : isMed ? '#fffbeb' : '#f0fdf4';
  const iconColor = isHigh ? '#b91c1c' : isMed ? '#b45309' : 'var(--gov-emerald-700)';

  return (
    <div
      style={{
        backgroundColor: bgColor,
        border: `1px solid ${borderColor}`,
        borderLeft: `4px solid ${borderColor}`,
        padding: '12px 16px',
        marginBottom: '16px',
        boxShadow: 'var(--gov-shadow-sm)',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '12px' }}>
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: '10px' }}>
          <div style={{ color: iconColor, marginTop: '2px' }}>
            {isHigh ? (
              <ShieldAlert size={20} />
            ) : isMed ? (
              <AlertTriangle size={20} />
            ) : (
              <CheckCircle size={20} />
            )}
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
              <strong
                style={{
                  fontSize: '0.85rem',
                  color: isHigh ? '#991b1b' : isMed ? '#92400e' : 'var(--gov-emerald-900)',
                  textTransform: 'uppercase',
                  letterSpacing: '0.04em',
                }}
              >
                {isHigh
                  ? 'High Legal Uncertainty / Insufficient Evidence Notice'
                  : isMed
                  ? 'Judicial Ambiguity & Divergence Advisory'
                  : 'Settled Precedent / High Grounding Confidence'}
              </strong>
              <span
                style={{
                  fontSize: '0.725rem',
                  fontWeight: 700,
                  padding: '2px 8px',
                  backgroundColor: '#ffffff',
                  border: `1px solid ${borderColor}`,
                  borderRadius: '2px',
                  color: iconColor,
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '4px',
                }}
              >
                Research Grounding Confidence: {Math.round(assessment.confidence_score * 100)}%
              </span>
            </div>
            <div style={{ fontSize: '0.675rem', color: 'var(--gov-slate-600)', marginBottom: '6px', fontStyle: 'italic' }}>
              Indicates strength of available indexed research evidence; not a prediction of judicial outcome.
            </div>

            <p
              style={{
                margin: '0 0 6px 0',
                fontSize: '0.775rem',
                color: 'var(--gov-slate-800)',
                lineHeight: '1.4',
              }}
            >
              {assessment.reason}
            </p>

            <div
              style={{
                fontSize: '0.75rem',
                color: isHigh ? '#7f1d1d' : isMed ? '#78350f' : 'var(--gov-emerald-900)',
                backgroundColor: 'rgba(255, 255, 255, 0.7)',
                padding: '6px 10px',
                border: '1px solid rgba(0, 0, 0, 0.08)',
                lineHeight: '1.35',
              }}
            >
              <strong>Judicial Guidance: </strong>
              {assessment.cautionary_guidance}
            </div>

            {assessment.corpus_limitation_note && (
              <div
                style={{
                  marginTop: '6px',
                  fontSize: '0.7rem',
                  color: 'var(--gov-slate-600)',
                  fontStyle: 'italic',
                  lineHeight: '1.3',
                }}
              >
                {assessment.corpus_limitation_note}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
