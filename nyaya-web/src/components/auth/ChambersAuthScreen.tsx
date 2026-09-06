import React, { useState, useEffect } from 'react';
import { Scale, Lock, Shield, AlertCircle, ChevronDown, ChevronUp, UserCheck } from 'lucide-react';
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

export const ChambersAuthScreen: React.FC = () => {
  const { login } = useChambers();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [demoAccounts, setDemoAccounts] = useState<DemoUserDTO[]>(FALLBACK_DEMO_ACCOUNTS);
  const [showDemoCredentials, setShowDemoCredentials] = useState(true);

  useEffect(() => {
    fetchDemoUsersApi().then((users) => {
      if (users && users.length > 0) {
        setDemoAccounts(users);
      }
    });
  }, []);


  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim() || !password.trim()) {
      setError('Please provide both Chambers Official User ID (email) and Password.');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      await login(email.trim(), password.trim());
      // On success, ChambersContext updates isAuthenticated to true and App renders main application
    } catch (err: any) {
      setError(err.message || 'Authentication failed. Please verify your chambers credentials.');
    } finally {
      setLoading(false);
    }
  };

  const handleSelectDemoRole = (acc: DemoUserDTO) => {
    setEmail(acc.email);
    setPassword(acc.password);
    setError(null);
  };

  return (
    <div
      style={{
        minHeight: '100vh',
        backgroundColor: '#0f172a',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '24px 16px',
        position: 'relative',
        fontFamily: 'var(--font-sans)',
      }}
    >
      {/* Tricolor institutional border strip */}
      <div
        style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          height: '4px',
          display: 'flex',
          zIndex: 100,
        }}
      >
        <div style={{ flex: 1, backgroundColor: '#f97316' }} />
        <div style={{ flex: 1, backgroundColor: '#ffffff' }} />
        <div style={{ flex: 1, backgroundColor: '#16a34a' }} />
      </div>

      {/* Main Authentication Card */}
      <div
        style={{
          width: '100%',
          maxWidth: '480px',
          backgroundColor: '#ffffff',
          borderRadius: '6px',
          boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.4)',
          overflow: 'hidden',
          border: '1px solid var(--gov-slate-300)',
        }}
      >
        {/* Institutional Card Header */}
        <div
          style={{
            backgroundColor: 'var(--gov-navy-900)',
            color: '#ffffff',
            padding: '24px 28px 20px',
            textAlign: 'center',
            borderBottom: '2px solid #f59e0b',
          }}
        >
          <div
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              justifyContent: 'center',
              width: '48px',
              height: '48px',
              borderRadius: '6px',
              backgroundColor: 'rgba(245, 158, 11, 0.15)',
              border: '1px solid rgba(245, 158, 11, 0.4)',
              marginBottom: '12px',
            }}
          >
            <Scale size={26} color="#f59e0b" strokeWidth={2} />
          </div>
          <h1
            style={{
              fontSize: '1.25rem',
              fontWeight: 700,
              letterSpacing: '0.04em',
              margin: '0 0 4px 0',
              color: '#ffffff',
            }}
          >
            न्याय एआई <span style={{ color: '#f59e0b', fontWeight: 400 }}>|</span> NYAYA AI
          </h1>
          <div
            style={{
              fontSize: '0.75rem',
              color: 'var(--gov-slate-300)',
              fontWeight: 500,
              lineHeight: 1.4,
            }}
          >
            AI-Driven Research Engine for Commercial Courts
          </div>
          <div
            style={{
              fontSize: '0.675rem',
              color: '#f59e0b',
              marginTop: '4px',
              letterSpacing: '0.06em',
              textTransform: 'uppercase',
              fontWeight: 600,
            }}
          >
            Commercial Courts Act, 2015 • SIH Judicial Decision-Support Demonstration
          </div>
        </div>

        {/* Card Body */}
        <div style={{ padding: '24px 28px' }}>
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              marginBottom: '18px',
              paddingBottom: '12px',
              borderBottom: '1px solid var(--gov-slate-200)',
            }}
          >
            <div>
              <div
                style={{
                  fontSize: '0.95rem',
                  fontWeight: 700,
                  color: 'var(--gov-navy-900)',
                }}
              >
                Authorized Judicial Access
              </div>
              <div style={{ fontSize: '0.725rem', color: 'var(--gov-slate-500)' }}>
                Sign in with official court chambers credentials
              </div>
            </div>
            <Shield size={20} color="var(--gov-navy-800)" />
          </div>

          {error && (
            <div
              style={{
                backgroundColor: '#fff1f2',
                border: '1px solid #fecdd3',
                color: '#be123c',
                padding: '10px 14px',
                borderRadius: '4px',
                fontSize: '0.775rem',
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
                  fontSize: '0.775rem',
                  fontWeight: 600,
                  color: 'var(--gov-slate-700)',
                  marginBottom: '4px',
                }}
              >
                User ID / Official Chambers Email
              </label>
              <input
                type="email"
                className="gov-input"
                placeholder="e.g. justice.sharma@commercialcourt.gov.in"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                disabled={loading}
                autoFocus
              />
            </div>

            <div>
              <label
                style={{
                  display: 'block',
                  fontSize: '0.775rem',
                  fontWeight: 600,
                  color: 'var(--gov-slate-700)',
                  marginBottom: '4px',
                }}
              >
                Chambers Password
              </label>
              <input
                type="password"
                className="gov-input"
                placeholder="••••••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                disabled={loading}
              />
            </div>

            <button
              type="submit"
              className="gov-btn gov-btn-primary"
              disabled={loading}
              style={{
                marginTop: '6px',
                padding: '10px 20px',
                fontSize: '0.85rem',
                fontWeight: 600,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
                width: '100%',
              }}
            >
              <Lock size={15} />
              <span>{loading ? 'Verifying Judicial Credentials...' : 'Sign In to Chambers'}</span>
            </button>
          </form>

          {/* Statutory / Authorized Access Notice */}
          <div
            style={{
              marginTop: '20px',
              padding: '10px 12px',
              backgroundColor: '#f8fafc',
              border: '1px solid var(--gov-slate-200)',
              borderRadius: '4px',
              fontSize: '0.7rem',
              color: 'var(--gov-slate-600)',
              lineHeight: 1.45,
              textAlign: 'center',
            }}
          >
            <strong>Official Notice:</strong> Authorized access only. This system is intended for authorized judicial personnel of the Commercial Courts and Commercial Appellate Divisions. All sessions are logged for audit compliance.
          </div>

          {/* SIH / Evaluation Credentials Helper (Development convenience, strictly non-bypassing) */}
          {demoAccounts.length > 0 && (
            <div
              style={{
                marginTop: '16px',
                borderTop: '1px solid var(--gov-slate-200)',
                paddingTop: '12px',
              }}
            >
              <button
                type="button"
                onClick={() => setShowDemoCredentials(!showDemoCredentials)}
                style={{
                  background: 'none',
                  border: 'none',
                  width: '100%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '4px 0',
                  fontSize: '0.725rem',
                  fontWeight: 600,
                  color: 'var(--gov-navy-800)',
                  cursor: 'pointer',
                }}
              >
                <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <Shield size={12} color="var(--gov-navy-800)" />
                  <span>SIH Evaluation Credentials (Test Accounts)</span>
                </span>
                {showDemoCredentials ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
              </button>

              {showDemoCredentials && (
                <div style={{ marginTop: '8px', display: 'flex', flexDirection: 'column', gap: '6px' }}>
                  <div style={{ fontSize: '0.675rem', color: 'var(--gov-slate-500)', marginBottom: '2px' }}>
                    Click a role to load test credentials into the form, then submit to authenticate via backend:
                  </div>
                  {demoAccounts.map((acc) => (
                    <button
                      key={acc.email}
                      type="button"
                      onClick={() => handleSelectDemoRole(acc)}
                      style={{
                        textAlign: 'left',
                        padding: '6px 10px',
                        backgroundColor: '#f1f5f9',
                        border: '1px solid var(--gov-slate-300)',
                        borderRadius: '3px',
                        cursor: 'pointer',
                        fontSize: '0.7rem',
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                      }}
                    >
                      <div>
                        <span style={{ fontWeight: 600, color: 'var(--gov-navy-900)' }}>
                          {acc.full_name}
                        </span>{' '}
                        <span
                          style={{
                            fontSize: '0.625rem',
                            padding: '1px 5px',
                            backgroundColor: 'var(--gov-navy-800)',
                            color: '#ffffff',
                            borderRadius: '2px',
                            fontWeight: 600,
                          }}
                        >
                          {acc.role}
                        </span>
                        <div style={{ color: 'var(--gov-slate-500)', fontSize: '0.65rem' }}>
                          {acc.email}
                        </div>
                      </div>
                      <UserCheck size={13} color="#059669" />
                    </button>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Institutional Footer Strip */}
        <div
          style={{
            backgroundColor: '#f8fafc',
            borderTop: '1px solid var(--gov-slate-200)',
            padding: '10px 16px',
            textAlign: 'center',
            fontSize: '0.675rem',
            color: 'var(--gov-slate-500)',
          }}
        >
          Designed in accordance with Government of India Web Guidelines (GIGW)
        </div>
      </div>
    </div>
  );
};
