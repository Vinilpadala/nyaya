import { ShieldCheck, Lock } from 'lucide-react';
import { DemoDataBadge } from '../common/DemoDataBadge';

export const ChambersStatusFooter: React.FC = () => {
  return (
    <footer className="gov-footer">
      <div className="gov-footer-inner">
        <div>
          <div style={{ fontWeight: 600, color: '#ffffff', marginBottom: '4px' }}>
            न्याय एआई | Nyaya AI - Commercial Courts Research Platform
          </div>
          <div style={{ color: 'var(--gov-slate-400)', fontSize: '0.725rem', maxWidth: '600px' }}>
            Operated for Commercial Courts and Commercial Appellate Divisions under the Commercial Courts Act, 2015.
            Strict assistive mandate: Not determinative, strictly verified citation cross-referencing.
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '20px', fontSize: '0.725rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <Lock size={13} color="#22c55e" />
            <span>Court-Specific Data Localization: Chambers Isolation Architecture</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <ShieldCheck size={14} color="#f59e0b" />
            <span>Anti-Hallucination Guardrail: Determinative SCR Cross-Check</span>
          </div>
          <DemoDataBadge label="BENCHMARK CORPUS (14 CASES)" />
        </div>
      </div>
      <div
        style={{
          maxWidth: '1440px',
          margin: '12px auto 0',
          paddingTop: '10px',
          borderTop: '1px solid rgba(255,255,255,0.08)',
          display: 'flex',
          justifyContent: 'space-between',
          fontSize: '0.7rem',
          color: 'var(--gov-slate-500)',
        }}
      >
        <span>Designed in accordance with Government of India Web Guidelines (GIGW)</span>
        <span>Version 1.0.0 • SIH Judicial Decision-Support Demonstration • Indian Standard Time</span>
      </div>
    </footer>
  );
};
