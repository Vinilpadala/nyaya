import React from 'react';
import { Scale, AlertCircle, LogOut, User, Languages } from 'lucide-react';
import { useChambers, FontSizeScale } from '../../context/ChambersContext';
import { DemoDataBadge } from '../common/DemoDataBadge';
import { SUPPORTED_LANGUAGES, SupportedLanguage } from '../../i18n/translations';

export const GovHeader: React.FC = () => {
  const { currentUser, logout, fontSize, setFontSize, currentLanguage, setCurrentLanguage, uiText } = useChambers();

  return (
    <header className="gov-header-wrapper">
      {/* Tricolor institutional border strip */}
      <div className="gov-tricolor-strip">
        <div className="stripe-saffron" />
        <div className="stripe-white" />
        <div className="stripe-green" />
      </div>

      {/* Main Official Header Bar */}
      <div className="gov-header">
        <div className="gov-header-inner">
          <div className="gov-brand">
            <div className="gov-seal-box" title="Scales of Justice - Commercial Courts of India">
              <Scale size={24} color="#f59e0b" strokeWidth={2} />
            </div>
            <div className="gov-title-group">
              <h1>
                {uiText.appTitle}
              </h1>
              <p>
                {uiText.appSubtitle}
              </p>
            </div>
          </div>

          <div className="gov-header-controls">
            {/* Official Judicial Language Selector */}
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                background: 'var(--gov-navy-800)',
                padding: '4px 10px',
                borderRadius: '4px',
                border: '1px solid var(--gov-navy-600)',
              }}
              title="Select Court Language (Currently supported: English, Hindi, Telugu • Tamil & Marathi in Future Expansion)"
            >
              <Languages size={14} color="#f59e0b" />
              <select
                id="sel-court-lang"
                value={currentLanguage}
                onChange={(e) => setCurrentLanguage(e.target.value as SupportedLanguage)}
                style={{
                  background: 'transparent',
                  color: '#ffffff',
                  border: 'none',
                  fontSize: '0.75rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                  outline: 'none',
                }}
              >
                {SUPPORTED_LANGUAGES.map((lang) => (
                  <option
                    key={lang.code}
                    value={lang.code}
                    style={{ background: '#0f172a', color: '#ffffff' }}
                  >
                    {lang.nativeLabel} ({lang.label})
                  </option>
                ))}
              </select>
            </div>

            {/* Font scaling controls for accessibility */}
            <div className="gov-font-controls" title="Text Resizing for Judicial Accessibility">
              <button
                type="button"
                className={`gov-font-btn ${fontSize === 'standard' ? 'active' : ''}`}
                onClick={() => setFontSize('standard' as FontSizeScale)}
              >
                A
              </button>
              <button
                type="button"
                className={`gov-font-btn ${fontSize === 'large' ? 'active' : ''}`}
                onClick={() => setFontSize('large' as FontSizeScale)}
              >
                A+
              </button>
              <button
                type="button"
                className={`gov-font-btn ${fontSize === 'extra-large' ? 'active' : ''}`}
                onClick={() => setFontSize('extra-large' as FontSizeScale)}
              >
                A++
              </button>
            </div>

            {/* Authenticated Judicial Profile & Sign Out */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '10px',
                  background: 'var(--gov-navy-800)',
                  padding: '5px 12px',
                  borderRadius: '4px',
                  border: '1px solid var(--gov-navy-600)',
                }}
              >
                <User size={15} color="#f59e0b" />
                <div style={{ textAlign: 'left' }}>
                  <div style={{ fontSize: '0.775rem', fontWeight: 600, color: '#ffffff' }}>
                    {currentUser.fullName}
                  </div>
                  <div style={{ fontSize: '0.675rem', color: 'var(--gov-slate-300)' }}>
                    {currentUser.role} • {currentUser.chambersNumber}
                  </div>
                </div>

                <div
                  style={{
                    height: '20px',
                    width: '1px',
                    backgroundColor: 'var(--gov-navy-600)',
                    margin: '0 4px',
                  }}
                />

                <button
                  type="button"
                  onClick={logout}
                  title="Sign Out of Authorized Chambers Session"
                  style={{
                    background: 'none',
                    border: 'none',
                    color: '#fca5a5',
                    cursor: 'pointer',
                    padding: '4px 6px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px',
                    fontSize: '0.725rem',
                    fontWeight: 500,
                  }}
                >
                  <LogOut size={13} />
                  <span>Sign Out</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Prominent Session Security Banner */}
      <div className="gov-demo-banner">
        <div className="gov-demo-banner-content">
          <AlertCircle size={15} color="#b45309" />
          <span>
            <strong>AUTHORIZED JUDICIAL RESEARCH SESSION:</strong> SIH Demonstration Environment with authenticated session credentials.
          </span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <span style={{ fontSize: '0.725rem', opacity: 0.85 }}>
            Security: <strong>Authenticated Bearer Token</strong>
          </span>
          <DemoDataBadge label="SESSION ACTIVE" />
        </div>
      </div>
    </header>
  );
};
