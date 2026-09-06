import React from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

interface ApiErrorBannerProps {
  message: string;
  onRetry?: () => void;
  title?: string;
}

export const ApiErrorBanner: React.FC<ApiErrorBannerProps> = ({
  message,
  onRetry,
  title = 'Chambers Backend Connection Error',
}) => {
  return (
    <div
      style={{
        backgroundColor: '#fff1f2',
        border: '1px solid #fecdd3',
        borderRadius: '4px',
        padding: '12px 16px',
        marginBottom: '16px',
        display: 'flex',
        alignItems: 'flex-start',
        justifyContent: 'space-between',
        gap: '12px',
      }}
    >
      <div style={{ display: 'flex', gap: '12px', alignItems: 'flex-start' }}>
        <AlertTriangle size={18} color="#e11d48" style={{ marginTop: '2px', flexShrink: 0 }} />
        <div>
          <div style={{ fontWeight: 600, fontSize: '0.85rem', color: '#9f1239' }}>{title}</div>
          <div style={{ fontSize: '0.775rem', color: '#be123c', marginTop: '2px' }}>{message}</div>
          <div style={{ fontSize: '0.7rem', color: '#881337', marginTop: '4px', opacity: 0.85 }}>
            Ensure the FastAPI backend is running at <code>http://127.0.0.1:8000</code>.
          </div>
        </div>
      </div>

      {onRetry && (
        <button
          type="button"
          onClick={onRetry}
          className="gov-btn"
          style={{
            padding: '4px 10px',
            fontSize: '0.75rem',
            backgroundColor: '#ffffff',
            border: '1px solid #fda4af',
            color: '#9f1239',
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            cursor: 'pointer',
            flexShrink: 0,
          }}
        >
          <RefreshCw size={12} /> Retry
        </button>
      )}
    </div>
  );
};
