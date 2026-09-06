import React from 'react';
import { ChambersProvider, useChambers } from './context/ChambersContext';
import { GovHeader } from './components/layout/GovHeader';
import { ChambersNavbar } from './components/layout/ChambersNavbar';
import { ChambersStatusFooter } from './components/layout/ChambersStatusFooter';
import { LegalResearchWorkspace } from './components/research/LegalResearchWorkspace';
import { SplitPaneReader } from './components/research/SplitPaneReader';
import { StatuteNavigator } from './components/statutes/StatuteNavigator';
import { BenchMemoBuilder } from './components/dossiers/BenchMemoBuilder';
import { ChambersAuditLog } from './components/audit/ChambersAuditLog';
import { ChambersAuthScreen } from './components/auth/ChambersAuthScreen';

const MainContent: React.FC = () => {
  const { activeTab } = useChambers();

  return (
    <main className="gov-main-container">
      {activeTab === 'research' && <LegalResearchWorkspace />}
      {activeTab === 'precedents' && <SplitPaneReader />}
      {activeTab === 'statutes' && <StatuteNavigator />}
      {activeTab === 'dossiers' && <BenchMemoBuilder />}
      {activeTab === 'audit' && <ChambersAuditLog />}
    </main>
  );
};

const AppContent: React.FC = () => {
  const { isAuthenticated, isAuthLoading } = useChambers();

  if (isAuthLoading) {
    return (
      <div
        style={{
          minHeight: '100vh',
          backgroundColor: '#0f172a',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#ffffff',
          gap: '12px',
          fontFamily: 'var(--font-sans)',
        }}
      >
        <div style={{ fontSize: '1.25rem', fontWeight: 700, color: '#f59e0b' }}>
          न्याय एआई <span style={{ color: '#ffffff', fontWeight: 400 }}>|</span> NYAYA AI
        </div>
        <div style={{ fontSize: '0.8rem', color: '#94a3b8' }}>
          Verifying Authorized Chambers Session...
        </div>
      </div>
    );
  }

  // Deny-by-default access gate: Unauthenticated users only see the authentication screen
  if (!isAuthenticated) {
    return <ChambersAuthScreen />;
  }

  // Authenticated users access the full application
  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <GovHeader />
      <ChambersNavbar />
      <MainContent />
      <ChambersStatusFooter />
    </div>
  );
};

export function App() {
  return (
    <ChambersProvider>
      <AppContent />
    </ChambersProvider>
  );
}

export default App;
