import React from 'react';
import { Scale, BookOpen, Shield, BookmarkCheck, Search } from 'lucide-react';
import { useChambers, NavTab } from '../../context/ChambersContext';

export const ChambersNavbar: React.FC = () => {
  const { activeTab, setActiveTab, currentUser, selectedDossier } = useChambers();

  const navItems: { id: NavTab; label: string; icon: React.ReactNode; primary?: boolean }[] = [
    {
      id: 'research',
      label: 'Legal Research Engine',
      icon: <Search size={16} />,
      primary: true,
    },
    {
      id: 'precedents',
      label: 'Precedents & Ratio',
      icon: <Scale size={16} />,
    },
    {
      id: 'statutes',
      label: 'Commercial Statutes',
      icon: <BookOpen size={16} />,
    },
    {
      id: 'dossiers',
      label: 'Bench Dossiers',
      icon: <BookmarkCheck size={16} />,
    },
    {
      id: 'audit',
      label: 'Audit Trail',
      icon: <Shield size={16} />,
    },
  ];

  return (
    <nav className="gov-navbar">
      <div className="gov-navbar-inner">
        <ul className="gov-nav-links">
          {navItems.map((item) => (
            <li key={item.id} className="gov-nav-item">
              <button
                type="button"
                className={activeTab === item.id ? 'active' : ''}
                onClick={() => setActiveTab(item.id)}
                style={
                  item.primary && activeTab !== item.id
                    ? { fontWeight: 600, color: 'var(--gov-navy-800)' }
                    : undefined
                }
              >
                {item.icon}
                <span>{item.label}</span>
              </button>
            </li>
          ))}
        </ul>

        {/* Active Matter & Chambers indicator */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px', fontSize: '0.775rem' }}>
          <div style={{ color: 'var(--gov-slate-600)' }}>
            Active Matter:{' '}
            <strong style={{ color: 'var(--gov-slate-900)' }}>
              {selectedDossier?.suitNumber || 'No Active Matter'}
            </strong>
          </div>
          <div style={{ height: '14px', width: '1px', backgroundColor: 'var(--gov-slate-300)' }} />
          <div style={{ color: 'var(--gov-slate-600)' }}>
            <strong style={{ color: 'var(--gov-navy-800)' }}>{currentUser.chambersNumber}</strong>
          </div>
        </div>
      </div>
    </nav>
  );
};
