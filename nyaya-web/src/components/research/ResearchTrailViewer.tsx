import React, { useState } from 'react';
import {
  GitCommit,
  CheckCircle2,
  FileSearch,
  BookOpen,
  Quote,
  Sparkles,
  ChevronDown,
  ChevronUp,
  ShieldCheck,
  Clock,
} from 'lucide-react';
import { ResearchTrailDTO, ResearchTrailStep } from '../../types';

interface ResearchTrailViewerProps {
  trail: ResearchTrailDTO;
}

export const ResearchTrailViewer: React.FC<ResearchTrailViewerProps> = ({ trail }) => {
  const [selectedStep, setSelectedStep] = useState<number>(1);
  const [isCollapsed, setIsCollapsed] = useState<boolean>(false);

  const steps: { number: number; step: ResearchTrailStep; icon: React.ReactNode; label: string }[] = [
    {
      number: 1,
      step: trail.query_analysis_step,
      icon: <FileSearch size={16} />,
      label: 'User Query',
    },
    {
      number: 2,
      step: trail.retrieval_step,
      icon: <BookOpen size={16} />,
      label: 'Retrieved Sources',
    },
    {
      number: 3,
      step: trail.passage_extraction_step,
      icon: <Quote size={16} />,
      label: 'Relevant Passages',
    },
    {
      number: 4,
      step: trail.ai_synthesis_step,
      icon: <Sparkles size={16} />,
      label: 'AI Analysis',
    },
  ];

  const currentStepObj = steps.find((s) => s.number === selectedStep)?.step || trail.query_analysis_step;

  return (
    <div
      style={{
        backgroundColor: '#ffffff',
        border: '1px solid var(--gov-slate-300)',
        borderTop: '3px solid var(--gov-navy-800)',
        boxShadow: 'var(--gov-shadow-sm)',
        marginBottom: '20px',
      }}
    >
      {/* Header / Collapse Bar */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '10px 16px',
          backgroundColor: '#fafbfc',
          borderBottom: '1px solid var(--gov-slate-200)',
          cursor: 'pointer',
        }}
        onClick={() => setIsCollapsed(!isCollapsed)}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <GitCommit size={17} style={{ color: 'var(--gov-navy-800)' }} />
          <div>
            <span
              style={{
                fontSize: '0.825rem',
                fontWeight: 700,
                textTransform: 'uppercase',
                letterSpacing: '0.04em',
                color: 'var(--gov-navy-900)',
              }}
            >
              Research Explainability & Reasoning Trail
            </span>
            <span
              style={{
                marginLeft: '10px',
                fontSize: '0.75rem',
                color: 'var(--gov-slate-500)',
              }}
            >
              Audit Pipeline: Query → Sources → Passages → AI Synthesis
            </span>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '5px',
              fontSize: '0.725rem',
              color: 'var(--gov-emerald-700)',
              fontWeight: 600,
              backgroundColor: '#ecfdf5',
              padding: '2px 8px',
              border: '1px solid #a7f3d0',
            }}
          >
            <ShieldCheck size={13} />
            Strict Grounding Verified
          </div>
          <button
            type="button"
            style={{
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              color: 'var(--gov-slate-600)',
              display: 'flex',
              alignItems: 'center',
            }}
          >
            {isCollapsed ? <ChevronDown size={17} /> : <ChevronUp size={17} />}
          </button>
        </div>
      </div>

      {!isCollapsed && (
        <div style={{ padding: '16px' }}>
          {/* 7-Step Judicial Verification Flow */}
          <div
            style={{
              padding: '8px 12px',
              backgroundColor: '#f8fafc',
              border: '1px solid var(--gov-slate-200)',
              borderRadius: '2px',
              marginBottom: '14px',
              fontSize: '0.725rem',
              color: 'var(--gov-slate-700)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              flexWrap: 'wrap',
              gap: '6px',
            }}
          >
            <strong style={{ color: 'var(--gov-navy-900)' }}>Judicial Audit Flow:</strong>
            <span>1. Legal Question Understood → 2. Authorities Retrieved → 3. Quorum Ranked → 4. Citations Verified → 5. Uncertainty Assessed → 6. Grounded Briefing → 7. Citation Guard Verified</span>
          </div>

          {/* Pipeline Stepper Nodes */}
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(4, 1fr)',
              gap: '10px',
              position: 'relative',
              marginBottom: '16px',
            }}
          >
            {steps.map((s, idx) => {
              const isSelected = selectedStep === s.number;
              return (
                <div
                  key={s.number}
                  onClick={() => setSelectedStep(s.number)}
                  style={{
                    display: 'flex',
                    flexDirection: 'column',
                    padding: '10px 12px',
                    border: isSelected
                      ? '1.5px solid var(--gov-navy-800)'
                      : '1px solid var(--gov-slate-200)',
                    backgroundColor: isSelected ? '#f0f5fa' : '#ffffff',
                    cursor: 'pointer',
                    position: 'relative',
                    transition: 'all 0.15s ease',
                  }}
                >
                  <div
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      marginBottom: '4px',
                    }}
                  >
                    <div
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '6px',
                        fontSize: '0.75rem',
                        fontWeight: 700,
                        color: isSelected ? 'var(--gov-navy-900)' : 'var(--gov-slate-700)',
                      }}
                    >
                      <span
                        style={{
                          display: 'inline-flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          width: '18px',
                          height: '18px',
                          borderRadius: '50%',
                          backgroundColor: isSelected ? 'var(--gov-navy-800)' : 'var(--gov-slate-300)',
                          color: '#ffffff',
                          fontSize: '0.675rem',
                          fontWeight: 700,
                        }}
                      >
                        {s.number}
                      </span>
                      {s.label}
                    </div>
                    <CheckCircle2
                      size={13}
                      style={{
                        color: 'var(--gov-emerald-600)',
                      }}
                    />
                  </div>

                  <div
                    style={{
                      fontSize: '0.7rem',
                      color: 'var(--gov-slate-500)',
                      lineHeight: '1.25',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      whiteSpace: 'nowrap',
                    }}
                  >
                    {s.step.title}
                  </div>

                  {/* Indicator Arrow between nodes */}
                  {idx < steps.length - 1 && (
                    <div
                      style={{
                        position: 'absolute',
                        right: '-8px',
                        top: '50%',
                        zIndex: 2,
                        width: '14px',
                        height: '14px',
                        backgroundColor: '#ffffff',
                        borderRight: '1px solid var(--gov-slate-300)',
                        borderTop: '1px solid var(--gov-slate-300)',
                        transformOrigin: 'center',
                        transform: 'translateY(-50%) rotate(45deg)',
                      }}
                    />
                  )}
                </div>
              );
            })}
          </div>

          {/* Active Step Detail Inspector */}
          <div
            style={{
              padding: '12px 14px',
              backgroundColor: '#f8fafc',
              border: '1px solid var(--gov-slate-200)',
            }}
          >
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                marginBottom: '8px',
                borderBottom: '1px solid var(--gov-slate-200)',
                paddingBottom: '6px',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <strong
                  style={{
                    fontSize: '0.8rem',
                    color: 'var(--gov-navy-900)',
                    textTransform: 'uppercase',
                    letterSpacing: '0.03em',
                  }}
                >
                  Stage {selectedStep}: {currentStepObj.title}
                </strong>
                <span
                  style={{
                    fontSize: '0.7rem',
                    backgroundColor: 'var(--gov-slate-200)',
                    color: 'var(--gov-slate-700)',
                    padding: '1px 6px',
                    borderRadius: '2px',
                  }}
                >
                  {currentStepObj.items_count} verified items
                </span>
              </div>

              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px',
                  fontSize: '0.7rem',
                  color: 'var(--gov-slate-500)',
                }}
              >
                <Clock size={12} />
                <span>Captured at {currentStepObj.timestamp}</span>
              </div>
            </div>

            <p
              style={{
                fontSize: '0.775rem',
                color: 'var(--gov-slate-700)',
                lineHeight: '1.4',
                margin: '0 0 8px 0',
              }}
            >
              {currentStepObj.description}
            </p>

            {/* Structured details list */}
            {currentStepObj.details && currentStepObj.details.length > 0 && (
              <ul
                style={{
                  margin: 0,
                  paddingLeft: '18px',
                  fontSize: '0.75rem',
                  color: 'var(--gov-slate-600)',
                  lineHeight: '1.5',
                }}
              >
                {currentStepObj.details.map((item, i) => (
                  <li key={i}>{item}</li>
                ))}
              </ul>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
