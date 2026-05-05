import type { RiskLevel } from '@/lib/types';
import { RISK_COLORS } from '@/lib/types';

interface RiskBadgeProps {
  risk: RiskLevel;
  className?: string;
}

export function RiskBadge({ risk, className = '' }: RiskBadgeProps) {
  const colorClass = RISK_COLORS[risk] || 'bg-slate-500/20 text-slate-400 border-slate-500/30';

  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 text-xs font-medium border rounded-full ${colorClass} ${className}`}
    >
      {risk}
    </span>
  );
}
