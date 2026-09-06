import React, { useState } from 'react';
import { Shield, Lock, CheckCircle, RefreshCw } from 'lucide-react';
import { useChambers } from '../../context/ChambersContext';
import { ApiErrorBanner } from '../common/ApiErrorBanner';

export const ChambersAuditLog: React.FC = () => {
  const { auditLogs, auditLogsLoading, auditLogsError, reloadAuditLogs, currentUser } = useChambers();
  const [filterAction, setFilterAction] = useState<string>('');

  const handleFilterChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const val = e.target.value;
    setFilterAction(val);
    reloadAuditLogs(val || undefined);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      {auditLogsError && (
        <ApiErrorBanner
          title="Audit Trail Service Offline"
          message={auditLogsError}
          onRetry={() => reloadAuditLogs(filterAction || undefined)}
        />
      )}

      <div className="gov-panel" style={{ padding: '16px 20px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <Shield size={22} color="var(--gov-navy-800)" />
            <div>
              <div style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--gov-navy-900)' }}>
                Chambers Research Audit Trail & Integrity Log
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--gov-slate-500)' }}>
                Tamper-Evident Record of Precedent Lookups, Statutory Queries & Bench Memoranda
              </div>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span className="badge-good-law" style={{ padding: '4px 8px' }}>
              <CheckCircle size={12} /> Chambers Isolation: Active (Demo Session)
            </span>
            <button
              type="button"
              className="gov-btn"
              onClick={() => reloadAuditLogs(filterAction || undefined)}
              disabled={auditLogsLoading}
              style={{
                fontSize: '0.775rem',
                padding: '4px 10px',
                backgroundColor: '#ffffff',
                border: '1px solid var(--gov-slate-300)',
                color: 'var(--gov-navy-900)',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '6px',
                cursor: 'pointer',
              }}
              title="Refresh audit trail from chambers database"
            >
              <RefreshCw size={13} className={auditLogsLoading ? 'animate-spin' : ''} />
              {auditLogsLoading ? 'Syncing...' : 'Refresh Log'}
            </button>
          </div>
        </div>
      </div>

      <div className="gov-panel">
        <div className="gov-panel-header" style={{ flexWrap: 'wrap', gap: '10px' }}>
          <span className="gov-panel-title">
            <Lock size={15} /> Chambers Session Operations ({auditLogs.length} Events)
          </span>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.75rem', color: 'var(--gov-slate-600)' }}>
              <span>Action Filter:</span>
              <select
                className="gov-select"
                style={{ fontSize: '0.75rem', padding: '2px 8px', width: 'auto' }}
                value={filterAction}
                onChange={handleFilterChange}
              >
                <option value="">All Operation Types</option>
                <option value="LEGAL_RESEARCH_QUERY">Legal Research Queries</option>
                <option value="DOSSIER_CREATED">Dossiers Created</option>
                <option value="DOSSIER_ITEM_PINNED">Authorities Pinned</option>
                <option value="BENCH_NOTE_RECORDED">Bench Notes</option>
                <option value="AUTHORITY_ACCESSED">Precedent Access</option>
                <option value="CHAMBERS_LOGIN">Chambers Logins</option>
              </select>
            </div>
            <span style={{ fontSize: '0.75rem', color: 'var(--gov-slate-500)' }}>
              Session: {currentUser.fullName}
            </span>
          </div>
        </div>

        <div style={{ overflowX: 'auto' }}>
          <table className="gov-table">
            <thead>
              <tr>
                <th>Timestamp (IST)</th>
                <th>Chambers Officer</th>
                <th>Operation Type</th>
                <th>Authority / Target</th>
                <th>Court Division</th>
                <th>Gateway IP</th>
              </tr>
            </thead>
            <tbody>
              {auditLogs.length === 0 ? (
                <tr>
                  <td colSpan={6} style={{ textAlign: 'center', padding: '24px', color: 'var(--gov-slate-500)', fontSize: '0.85rem' }}>
                    {auditLogsLoading ? 'Fetching live audit records...' : 'No tamper-evident audit logs recorded for this session.'}
                  </td>
                </tr>
              ) : (
                auditLogs.map((log) => (
                  <tr key={log.id}>
                    <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem', color: 'var(--gov-slate-600)', whiteSpace: 'nowrap' }}>
                      {log.timestamp}
                    </td>
                    <td style={{ fontWeight: 600, color: 'var(--gov-navy-900)' }}>
                      {log.chambersUser}
                    </td>
                    <td>
                      <span
                        style={{
                          padding: '2px 6px',
                          borderRadius: '2px',
                          fontSize: '0.7rem',
                          fontWeight: 700,
                          backgroundColor: '#f1f5f9',
                          color: 'var(--gov-navy-800)',
                          border: '1px solid var(--gov-slate-300)',
                          whiteSpace: 'nowrap',
                        }}
                      >
                        {log.action}
                      </span>
                    </td>
                    <td style={{ fontSize: '0.8rem', color: 'var(--gov-slate-800)', maxWidth: '320px', wordBreak: 'break-word' }}>
                      {log.target}
                    </td>
                    <td style={{ fontSize: '0.75rem', color: 'var(--gov-slate-600)' }}>
                      {log.division}
                    </td>
                    <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.7rem', color: 'var(--gov-slate-500)', whiteSpace: 'nowrap' }}>
                      {log.ipAddress}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
