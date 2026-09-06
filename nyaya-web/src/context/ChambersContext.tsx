import React, { createContext, useContext, useState, useEffect, ReactNode, useCallback } from 'react';
import {
  ChambersUser,
  JudicialCase,
  StatuteItem,
  CommercialSuitDossier,
  AuditLogEntry,
} from '../types';
import {
  DEMO_USERS,
  DEMO_CASES,
  DEMO_STATUTES,
  DEMO_DOSSIERS,
} from '../data/demoData';
import { loginApi, logoutApi, fetchMeApi, hasActiveToken } from '../api/authClient';
import { fetchCasesApi, CaseFilterParams } from '../api/casesClient';
import { fetchStatutesApi } from '../api/statutesClient';
import {
  fetchDossiersApi,
  createDossierApi,
  addDossierItemApi,
  removeDossierItemApi,
  updateDossierNotesApi,
} from '../api/dossiersClient';
import { fetchAuditLogsApi, recordAuditLogApi } from '../api/auditClient';
import { SupportedLanguage, TRANSLATIONS, UiTranslations } from '../i18n/translations';

export type NavTab = 'research' | 'precedents' | 'statutes' | 'dossiers' | 'audit';
export type FontSizeScale = 'standard' | 'large' | 'extra-large';

export interface PinItemPayload {
  type: 'CASE' | 'SECTION' | 'NOTE';
  title: string;
  referenceId?: string;
  excerpt?: string;
  pinpoint?: string;
}

interface ChambersContextType {
  // Authentication state & methods
  currentUser: ChambersUser;
  isAuthenticated: boolean;
  isAuthLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  switchUser: (userId: string) => void;
  users: ChambersUser[];

  // Navigation & Accessibility
  activeTab: NavTab;
  setActiveTab: (tab: NavTab) => void;
  fontSize: FontSizeScale;
  setFontSize: (size: FontSizeScale) => void;
  currentLanguage: SupportedLanguage;
  setCurrentLanguage: (lang: SupportedLanguage) => void;
  uiText: UiTranslations;

  // Case Law & Precedents
  cases: JudicialCase[];
  selectedCase: JudicialCase;
  setSelectedCase: (c: JudicialCase) => void;
  casesLoading: boolean;
  casesError: string | null;
  reloadCases: (filters?: CaseFilterParams) => Promise<void>;

  // Statutes
  statutes: StatuteItem[];
  selectedStatute: StatuteItem;
  setSelectedStatute: (s: StatuteItem) => void;
  statutesLoading: boolean;
  statutesError: string | null;
  reloadStatutes: (search?: string) => Promise<void>;

  // Dossiers
  dossiers: CommercialSuitDossier[];
  selectedDossier: CommercialSuitDossier | null;
  setSelectedDossier: (d: CommercialSuitDossier) => void;
  dossiersLoading: boolean;
  dossiersError: string | null;
  reloadDossiers: () => Promise<void>;
  createNewDossier: (suitNumber: string, parties: string, judicialNotes?: string) => Promise<CommercialSuitDossier>;
  addDossierNote: (dossierId: string, content: string, sourceRef: string) => Promise<void>;
  pinAuthorityToDossier: (dossierId: string, item: PinItemPayload) => Promise<void>;
  removeDossierItem: (dossierId: string, itemId: string) => Promise<void>;
  updateDossierNotes: (dossierId: string, notes: string) => Promise<void>;

  // Audit Logs
  auditLogs: AuditLogEntry[];
  auditLogsLoading: boolean;
  auditLogsError: string | null;
  reloadAuditLogs: (action?: string) => Promise<void>;
  addAuditLog: (action: string, target: string, endpoint?: string) => void;
}

const ChambersContext = createContext<ChambersContextType | undefined>(undefined);

export const ChambersProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  // Auth state
  const [currentUser, setCurrentUser] = useState<ChambersUser>(DEMO_USERS[0]);
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(hasActiveToken());
  const [isAuthLoading, setIsAuthLoading] = useState<boolean>(true);

  // App navigation
  const [activeTab, setActiveTab] = useState<NavTab>('research');
  const [fontSize, setFontSize] = useState<FontSizeScale>('standard');
  const [currentLanguage, setCurrentLanguage] = useState<SupportedLanguage>('en');
  const uiText = TRANSLATIONS[currentLanguage];

  // Cases state
  const [cases, setCases] = useState<JudicialCase[]>(DEMO_CASES);
  const [selectedCase, setSelectedCase] = useState<JudicialCase>(DEMO_CASES[0]);
  const [casesLoading, setCasesLoading] = useState<boolean>(false);
  const [casesError, setCasesError] = useState<string | null>(null);

  // Statutes state
  const [statutes, setStatutes] = useState<StatuteItem[]>(DEMO_STATUTES);
  const [selectedStatute, setSelectedStatute] = useState<StatuteItem>(DEMO_STATUTES[0]);
  const [statutesLoading, setStatutesLoading] = useState<boolean>(false);
  const [statutesError, setStatutesError] = useState<string | null>(null);

  // Dossiers state
  const [dossiers, setDossiers] = useState<CommercialSuitDossier[]>(DEMO_DOSSIERS);
  const [selectedDossier, setSelectedDossier] = useState<CommercialSuitDossier | null>(DEMO_DOSSIERS[0]);
  const [dossiersLoading, setDossiersLoading] = useState<boolean>(false);
  const [dossiersError, setDossiersError] = useState<string | null>(null);

  // Audit logs (persistent session activities)
  const [auditLogs, setAuditLogs] = useState<AuditLogEntry[]>([]);
  const [auditLogsLoading, setAuditLogsLoading] = useState<boolean>(false);
  const [auditLogsError, setAuditLogsError] = useState<string | null>(null);

  // Apply font size scale to root document
  useEffect(() => {
    document.documentElement.removeAttribute('data-font-size');
    if (fontSize === 'large') {
      document.documentElement.setAttribute('data-font-size', 'large');
    } else if (fontSize === 'extra-large') {
      document.documentElement.setAttribute('data-font-size', 'extra-large');
    }
  }, [fontSize]);

  // Load audit logs from backend
  const reloadAuditLogs = useCallback(async (actionFilter?: string) => {
    if (!hasActiveToken()) return;
    setAuditLogsLoading(true);
    setAuditLogsError(null);
    try {
      const liveLogs = await fetchAuditLogsApi(60, actionFilter);
      setAuditLogs(liveLogs);
    } catch (err: any) {
      console.warn('Backend audit logs fetch failed:', err);
      setAuditLogsError(err.message || 'Failed to fetch audit records from central repository.');
    } finally {
      setAuditLogsLoading(false);
    }
  }, []);

  const addAuditLog = useCallback(
    (action: string, target: string, endpoint?: string) => {
      const newEntry: AuditLogEntry = {
        id: `audit-${Date.now()}`,
        timestamp: new Date().toLocaleString('en-IN', { timeZone: 'Asia/Kolkata' }) + ' IST',
        chambersUser: `${currentUser.fullName} (${currentUser.role})`,
        action,
        target,
        division: currentUser.courtDivision,
        ipAddress: '10.24.112.4 (NIC Secure Court Gateway)',
      };
      setAuditLogs((prev) => [newEntry, ...prev]);

      // Asynchronously persist to backend audit_logs table
      if (hasActiveToken()) {
        recordAuditLogApi(action, target, endpoint).catch((err) => {
          console.warn('Background audit recording failed:', err);
        });
      }
    },
    [currentUser]
  );

  // Load cases from backend
  const reloadCases = useCallback(async (filters?: CaseFilterParams) => {
    setCasesLoading(true);
    setCasesError(null);
    try {
      const data = await fetchCasesApi(filters);
      if (data && data.length > 0) {
        setCases(data);
        setSelectedCase(data[0]);
      }
    } catch (err: any) {
      console.warn('Backend cases fetch failed:', err);
      setCasesError(err.message || 'Failed to fetch commercial precedents from backend.');
    } finally {
      setCasesLoading(false);
    }
  }, []);

  // Load statutes from backend
  const reloadStatutes = useCallback(async (search?: string) => {
    setStatutesLoading(true);
    setStatutesError(null);
    try {
      const data = await fetchStatutesApi(search);
      if (data && data.length > 0) {
        setStatutes(data);
        setSelectedStatute(data[0]);
      }
    } catch (err: any) {
      console.warn('Backend statutes fetch failed:', err);
      setStatutesError(err.message || 'Failed to fetch commercial statutes from backend.');
    } finally {
      setStatutesLoading(false);
    }
  }, []);

  // Load dossiers from backend
  const reloadDossiers = useCallback(async () => {
    if (!hasActiveToken()) return;
    setDossiersLoading(true);
    setDossiersError(null);
    try {
      const data = await fetchDossiersApi();
      if (data && data.length > 0) {
        setDossiers(data);
        setSelectedDossier((prev) => {
          if (prev) {
            const stillExists = data.find((d) => d.id === prev.id);
            if (stillExists) return stillExists;
          }
          return data[0];
        });
      } else {
        setDossiers([]);
        setSelectedDossier(null);
      }
    } catch (err: any) {
      console.warn('Backend dossiers fetch failed:', err);
      setDossiersError(err.message || 'Failed to fetch chambers dossiers from backend.');
    } finally {
      setDossiersLoading(false);
    }
  }, []);

  // Restore authenticated session on startup
  useEffect(() => {
    const initAuth = async () => {
      setIsAuthLoading(true);
      if (hasActiveToken()) {
        try {
          const user = await fetchMeApi();
          setCurrentUser(user);
          setIsAuthenticated(true);
        } catch {
          logoutApi();
          setIsAuthenticated(false);
        }
      } else {
        setIsAuthenticated(false);
      }
      setIsAuthLoading(false);
    };

    initAuth();
  }, []);

  // When authentication status changes to true, fetch protected judicial data
  useEffect(() => {
    if (isAuthenticated) {
      reloadCases();
      reloadStatutes();
      reloadDossiers();
      reloadAuditLogs();
    }
  }, [isAuthenticated, reloadCases, reloadStatutes, reloadDossiers, reloadAuditLogs]);

  const login = async (email: string, pass: string) => {
    const user = await loginApi(email, pass);
    setCurrentUser(user);
    setIsAuthenticated(true);
    addAuditLog('CHAMBERS_LOGIN', `User ${user.fullName} logged into ${user.chambersNumber}`);
  };

  const logout = () => {
    logoutApi();
    setIsAuthenticated(false);
    addAuditLog('CHAMBERS_LOGOUT', `Session terminated for ${currentUser.fullName}`);
  };

  const switchUser = (userId: string) => {
    const found = DEMO_USERS.find((u) => u.id === userId);
    if (found) {
      setCurrentUser(found);
      addAuditLog('SESSION_SWITCH', `Switched view context to ${found.fullName} (${found.role})`);
    }
  };

  const createNewDossier = async (
    suitNumber: string,
    parties: string,
    judicialNotes?: string
  ): Promise<CommercialSuitDossier> => {
    const newDossier = await createDossierApi({
      suit_number: suitNumber,
      matter_title: parties,
      judicial_notes: judicialNotes || '',
    });

    setDossiers((prev) => [newDossier, ...prev.filter((d) => d.id !== newDossier.id)]);
    setSelectedDossier(newDossier);
    addAuditLog('DOSSIER_CREATED', `New commercial bench dossier: ${suitNumber} (${parties})`);
    return newDossier;
  };

  const addDossierNote = async (dossierId: string, content: string, sourceRef: string): Promise<void> => {
    try {
      const updated = await addDossierItemApi(dossierId, {
        item_type: 'NOTE',
        title: content,
        reference_id: sourceRef,
        excerpt: '',
        pinpoint: '',
      });

      setDossiers((prev) => prev.map((d) => (d.id === updated.id ? updated : d)));
      setSelectedDossier((prev) => (prev && prev.id === updated.id ? updated : prev));
      addAuditLog('BENCH_NOTE_RECORDED', `Note added to dossier: ${sourceRef}`);
    } catch (err: any) {
      console.error('Failed to persist dossier note:', err);
      // Fallback local update if network is unavailable
      const newNote = {
        id: `note-${Date.now()}`,
        type: 'BENCH_DIRECTION' as const,
        content,
        sourceReference: sourceRef,
        timestamp: new Date().toLocaleString('en-IN', { timeZone: 'Asia/Kolkata' }),
      };
      setDossiers((prev) =>
        prev.map((d) => (d.id === dossierId ? { ...d, dossierNotes: [newNote, ...d.dossierNotes] } : d))
      );
      setSelectedDossier((prev) =>
        prev && prev.id === dossierId ? { ...prev, dossierNotes: [newNote, ...prev.dossierNotes] } : prev
      );
    }
  };

  const pinAuthorityToDossier = async (dossierId: string, item: PinItemPayload): Promise<void> => {
    try {
      const updated = await addDossierItemApi(dossierId, {
        item_type: item.type,
        reference_id: item.referenceId || '',
        title: item.title,
        excerpt: item.excerpt || '',
        pinpoint: item.pinpoint || '',
      });

      setDossiers((prev) => prev.map((d) => (d.id === updated.id ? updated : d)));
      setSelectedDossier((prev) => (prev && prev.id === updated.id ? updated : prev));
      addAuditLog('DOSSIER_ITEM_PINNED', `Pinned ${item.title} to dossier`);
    } catch (err: any) {
      console.error('Failed to pin authority to dossier:', err);
    }
  };

  const removeDossierItem = async (dossierId: string, itemId: string): Promise<void> => {
    try {
      const updated = await removeDossierItemApi(dossierId, itemId);
      setDossiers((prev) => prev.map((d) => (d.id === updated.id ? updated : d)));
      setSelectedDossier((prev) => (prev && prev.id === updated.id ? updated : prev));
      addAuditLog('DOSSIER_ITEM_REMOVED', `Removed item from dossier`);
    } catch (err: any) {
      console.error('Failed to remove dossier item:', err);
    }
  };

  const updateDossierNotes = async (dossierId: string, notes: string): Promise<void> => {
    try {
      const updated = await updateDossierNotesApi(dossierId, notes);
      setDossiers((prev) => prev.map((d) => (d.id === updated.id ? updated : d)));
      setSelectedDossier((prev) => (prev && prev.id === updated.id ? updated : prev));
      addAuditLog('DOSSIER_UPDATED', `Updated judicial notes for dossier`);
    } catch (err: any) {
      console.error('Failed to update dossier notes:', err);
    }
  };

  return (
    <ChambersContext.Provider
      value={{
        currentUser,
        isAuthenticated,
        isAuthLoading,
        login,
        logout,
        switchUser,
        users: DEMO_USERS,
        activeTab,
        setActiveTab,
        fontSize,
        setFontSize,
        currentLanguage,
        setCurrentLanguage,
        uiText,
        cases,
        selectedCase,
        setSelectedCase,
        casesLoading,
        casesError,
        reloadCases,
        statutes,
        selectedStatute,
        setSelectedStatute,
        statutesLoading,
        statutesError,
        reloadStatutes,
        dossiers,
        selectedDossier,
        setSelectedDossier,
        dossiersLoading,
        dossiersError,
        reloadDossiers,
        createNewDossier,
        addDossierNote,
        pinAuthorityToDossier,
        removeDossierItem,
        updateDossierNotes,
        auditLogs,
        auditLogsLoading,
        auditLogsError,
        reloadAuditLogs,
        addAuditLog,
      }}
    >
      {children}
    </ChambersContext.Provider>
  );
};

export const useChambers = () => {
  const context = useContext(ChambersContext);
  if (!context) {
    throw new Error('useChambers must be used within a ChambersProvider');
  }
  return context;
};
