import React from 'react';
import { AlertTriangle } from 'lucide-react';

interface DemoDataBadgeProps {
  label?: string;
  className?: string;
  size?: 'small' | 'medium' | 'large';
}

export const DemoDataBadge: React.FC<DemoDataBadgeProps> = ({
  label = 'DEMO DATA',
  className = '',
  size = 'medium',
}) => {
  const sizeStyle: React.CSSProperties =
    size === 'small'
      ? { fontSize: '0.625rem', padding: '1px 5px', gap: '3px' }
      : size === 'large'
      ? { fontSize: '0.8rem', padding: '4px 8px', gap: '6px' }
      : {};

  return (
    <span
      className={`badge-demo ${className}`}
      style={sizeStyle}
      title="This record is synthetic/demonstration legal data for system testing"
    >
      <AlertTriangle size={size === 'small' ? 10 : 11} strokeWidth={2.5} />
      {label}
    </span>
  );
};
