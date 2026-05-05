import type { ProductStatus } from '@/lib/types';
import { STATUS_COLORS, STATUS_LABELS } from '@/lib/types';

interface StatusBadgeProps {
  status: ProductStatus;
  className?: string;
}

export function StatusBadge({ status, className = '' }: StatusBadgeProps) {
  const colorClass = STATUS_COLORS[status] || 'bg-slate-500/20 text-slate-400 border-slate-500/30';
  const label = STATUS_LABELS[status] || status;

  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 text-xs font-medium border rounded-full ${colorClass} ${className}`}
    >
      {label}
    </span>
  );
}
