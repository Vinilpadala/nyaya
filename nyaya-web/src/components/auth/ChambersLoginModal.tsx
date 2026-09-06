import React, { useState, useEffect } from 'react';
import { Scale, Lock, UserCheck, AlertCircle, X, Shield } from 'lucide-react';
import { useChambers } from '../../context/ChambersContext';
import { fetchDemoUsersApi, DemoUserDTO } from '../../api/authClient';

const FALLBACK_DEMO_ACCOUNTS: DemoUserDTO[] = [
  {
    email: 'justice.sharma@commercialcourt.gov.in',
    password: 'Chambers@2026',
    full_name: "Hon'ble Justice A. K. Sharma — DEMO ACCOUNT",
    role: 'JUDGE',
    court_division: 'Commercial Appellate Division, High Court of Delhi',
    chambers_number: 'Courtroom 14 / Chambers 402',
    description: 'Presiding Commercial Division Judge (SIH Demo Account)',
  },
  {
    email: 'clerk.verma@commercialcourt.gov.in',
    password: 'Chambers@2026',
    full_name: 'R. K. Verma, Law Clerk (DEMO ACCOUNT)',
    role: 'RESEARCH_CLERK',
    court_division: 'Commercial Appellate Division, High Court of Delhi',
    chambers_number: 'Chambers 402 Library Desk',
    description: 'Judicial Research Assistant authorized to prepare case dossiers (SIH Demo Account)',
  },
  {
    email: 'registrar.commercial@delhihighcourt.nic.in',
    password: 'Chambers@2026',
    full_name: 'P. N. Gupta, Registrar (DEMO ACCOUNT)',
    role: 'REGISTRAR',
    court_division: 'Commercial Registry & Case Management',
    chambers_number: 'Registry Wing Room 108',
    description: 'Court Registry Administrator supervising commercial dockets (SIH Demo Account)',
  },
];

interface ChambersLoginModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const ChambersLoginModal: React.FC<ChambersLoginModalProps> = ({ isOpen, onClose }) => {
  const { login } = useChambers();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [demoAccounts, setDemoAccounts] = useState<DemoUserDTO[]>(FALLBACK_DEMO_ACCOUNTS);

  useEffect(() => {
    if (isOpen) {
      setError(null);
      fetchDemoUsersApi().then((users) => {
        if (users && users.length > 0) {
          setDemoAccounts(users);
        }
      });
    }
  }, [isOpen]);


  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim() || !password.trim()) {
      setError('Please provide both Chambers email and password.');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      await login(email.trim(), password.trim());
      onClose();
    } catch (err: any) {
      setError(err.message || 'Authentication failed. Please verify your credentials.');
    } finally {
      setLoading(false);
    }
  };

  const handleQuickLogin = (acc: DemoUserDTO) => {
    setEmail(acc.email);
    setPassword(acc.password);
  };

  return (
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
          boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.2), 0 10px 10px -5px rgba(0, 0, 0, 0.1)',
          overflow: 'hidden',
          border: '1px solid var(--gov-slate-300)',
        }}
      >
        {/* Modal Header */}
        <div
          style={{
            backgroundColor: 'var(--gov-navy-900)',
            color: '#ffffff',
            padding: '16px 20px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            borderBottom: '2px solid #f59e0b',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div
              style={{
                width: '32px',
                height: '32px',
                borderRadius: '4px',
                backgroundColor: 'rgba(245, 158, 11, 0.15)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <Scale size={18} color="#f59e0b" />
            </div>
            <div>
              <div style={{ fontWeight: 700, fontSize: '1rem', letterSpacing: '0.02em' }}>
                Chambers Authentication
              </div>
              <div style={{ fontSize: '0.7rem', color: 'var(--gov-slate-300)' }}>
                Commercial Courts & Appellate Division • Judicial Demonstration Session
              </div>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            style={{
              background: 'none',
              border: 'none',
              color: 'var(--gov-slate-300)',
              cursor: 'pointer',
              padding: '4px',
            }}
          >
            <X size={18} />
          </button>
        </div>

        {/* Modal Body */}
        <div style={{ padding: '20px 24px' }}>
          {error && (
            <div
              style={{
                backgroundColor: '#fff1f2',
                border: '1px solid #fecdd3',
                color: '#be123c',
                padding: '10px 12px',
                borderRadius: '4px',
                fontSize: '0.8rem',
                marginBottom: '16px',
                display: 'flex',
                gap: '8px',
                alignItems: 'center',
              }}
            >
              <AlertCircle size={16} color="#e11d48" style={{ flexShrink: 0 }} />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            <div>
              <label
                style={{
                  display: 'block',
                  fontSize: '0.8rem',
                  fontWeight: 600,
                  color: 'var(--gov-slate-700)',
                  marginBottom: '4px',
                }}
              >
                Chambers Official Email:
              </label>
              <input
                type="email"
                className="gov-input"
                placeholder="e.g. justice.sharma@commercialcourt.gov.in"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                disabled={loading}
              />
            </div>

            <div>
              <label
                style={{
                  display: 'block',
                  fontSize: '0.8rem',
                  fontWeight: 600,
                  color: 'var(--gov-slate-700)',
                  marginBottom: '4px',
                }}
              >
                Access Password:
              </label>
              <input
                type="password"
                className="gov-input"
                placeholder="Enter password (e.g. Chambers@2026)"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                disabled={loading}
              />
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '6px' }}>
              <button
                type="button"
                className="gov-btn"
                onClick={onClose}
                disabled={loading}
                style={{ padding: '8px 16px' }}
              >
                Cancel
              </button>
              <button
                type="submit"
                className="gov-btn gov-btn-primary"
                disabled={loading}
                style={{
                  padding: '8px 20px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                }}
              >
                <Lock size={14} />
                {loading ? 'Authenticating...' : 'Sign In to Chambers'}
              </button>
            </div>
          </form>

          {/* Quick Login Chips for Demo Accounts */}
          {demoAccounts.length > 0 && (
            <div
              style={{
                marginTop: '20px',
                paddingTop: '16px',
                borderTop: '1px solid var(--gov-slate-200)',
              }}
            >
              <div
                style={{
                  fontSize: '0.75rem',
                  fontWeight: 600,
                  color: 'var(--gov-slate-600)',
                  marginBottom: '8px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                }}
              >
                <Shield size={13} color="var(--gov-navy-800)" />
                <span>Pre-Configured Judicial Demo Credentials (Click to load):</span>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                {demoAccounts.map((acc) => (
                  <button
                    key={acc.email}
                    type="button"
                    onClick={() => handleQuickLogin(acc)}
                    style={{
                      textAlign: 'left',
                      padding: '8px 12px',
                      backgroundColor: '#f8fafc',
                      border: '1px solid var(--gov-slate-200)',
                      borderRadius: '4px',
                      cursor: 'pointer',
                      fontSize: '0.75rem',
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                    }}
                  >
                    <div>
                      <div style={{ fontWeight: 600, color: 'var(--gov-navy-900)' }}>
                        {acc.full_name} ({acc.role})
                      </div>
                      <div style={{ color: 'var(--gov-slate-500)', fontSize: '0.7rem' }}>
                        {acc.email}
                      </div>
                    </div>
                    <UserCheck size={14} color="#059669" />
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
