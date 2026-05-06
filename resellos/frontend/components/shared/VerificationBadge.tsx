import type { VerificationStatus } from '@/lib/types';
import { VERIFICATION_LABELS, VERIFICATION_COLORS } from '@/lib/types';

interface VerificationBadgeProps {
  status?: string | null;
  className?: string;
}

export function VerificationBadge({ status, className = '' }: VerificationBadgeProps) {
  if (!status) return null;

  const colorClass = VERIFICATION_COLORS[status as VerificationStatus] || 'bg-slate-500/20 text-slate-400 border-slate-500/30';
  const label = VERIFICATION_LABELS[status as VerificationStatus] || status;

  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 text-xs font-medium border rounded-full ${colorClass} ${className}`}
    >
      {label}
    </span>
  );
}
