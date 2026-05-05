'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import {
  Package,
  ShieldAlert,
  Eye,
  FlaskConical,
  ShoppingCart,
  Tag,
  ArrowRight,
  RefreshCw,
  CheckCircle2,
  Clock,
  AlertCircle,
  TrendingUp,
  BarChart3,
  Brain,
} from 'lucide-react';
import { StatusBadge } from '@/components/shared/status-badge';
import { RiskBadge } from '@/components/shared/risk-badge';
import { getDashboardStats } from '@/lib/api';
import type { DashboardStats, AgentResult } from '@/lib/types';

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getDashboardStats().then((data) => {
      setStats(data);
      setLoading(false);
    });
  }, []);

  if (loading || !stats) {
    return (
      <div className="flex items-center justify-center h-screen">
        <RefreshCw className="w-6 h-6 animate-spin text-indigo-400" />
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6 max-w-[1400px]">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-white">
            ResellOS Command Center
          </h1>
          <p className="text-sm text-zinc-400 mt-1">
            AI-powered product research and reselling dashboard
          </p>
        </div>
        <Link
          href="/products/new"
          className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium rounded-lg transition-colors"
        >
          <Package className="w-4 h-4" />
          New Product
        </Link>
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-6 gap-4">
        <StatCard icon={Package} label="Total Products" value={stats.total_products} color="text-blue-400" bgColor="bg-blue-500/10" href="/products" />
        <StatCard icon={ShieldAlert} label="Blocked" value={stats.blocked_count} color="text-red-400" bgColor="bg-red-500/10" href="/products?status=BLOCKED" />
        <StatCard icon={Eye} label="Watchlist" value={stats.watchlist_count} color="text-yellow-400" bgColor="bg-yellow-500/10" href="/products?status=WATCHLIST" />
        <StatCard icon={FlaskConical} label="BUY_SAMPLE" value={stats.buy_sample_candidates} color="text-purple-400" bgColor="bg-purple-500/10" href="/products?status=BUY_SAMPLE" />
        <StatCard icon={ShoppingCart} label="Ordered" value={stats.products_ordered} color="text-cyan-400" bgColor="bg-cyan-500/10" href="/inventory" />
        <StatCard icon={Tag} label="Listed" value={stats.products_listed} color="text-green-400" bgColor="bg-green-500/10" href="/listings" />
      </div>

      {/* Two-column layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Products */}
        <div className="lg:col-span-2 bg-zinc-900 border border-zinc-800 rounded-xl p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-semibold text-white flex items-center gap-2">
              <Clock className="w-4 h-4 text-zinc-500" />
              Recent Products
            </h2>
            <Link href="/products" className="text-xs text-indigo-400 hover:text-indigo-300 flex items-center gap-1">
              View all <ArrowRight className="w-3 h-3" />
            </Link>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-zinc-800">
                  <th className="text-left pb-3 text-zinc-500 font-medium text-xs uppercase tracking-wider">Product</th>
                  <th className="text-left pb-3 text-zinc-500 font-medium text-xs uppercase tracking-wider">Status</th>
                  <th className="text-left pb-3 text-zinc-500 font-medium text-xs uppercase tracking-wider">Risk</th>
                  <th className="text-right pb-3 text-zinc-500 font-medium text-xs uppercase tracking-wider">Score</th>
                  <th className="text-right pb-3 text-zinc-500 font-medium text-xs uppercase tracking-wider">Profit</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-800">
                {stats.recent_products.map((product) => (
                  <tr key={product.id} className="hover:bg-zinc-800/50">
                    <td className="py-3">
                      <Link href={`/products/${product.id}`} className="text-white hover:text-indigo-400 font-medium">
                        {product.name}
                      </Link>
                      <div className="text-xs text-zinc-500">{product.sku}</div>
                    </td>
                    <td className="py-3"><StatusBadge status={product.status} /></td>
                    <td className="py-3">{product.risk_level && <RiskBadge risk={product.risk_level} />}</td>
                    <td className="py-3 text-right"><ScoreBar score={product.final_score} /></td>
                    <td className="py-3 text-right text-green-400 font-mono text-xs">
                      {product.expected_profit ? `+$${product.expected_profit.toFixed(2)}` : '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Agent Activity */}
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-semibold text-white flex items-center gap-2">
              <Brain className="w-4 h-4 text-purple-400" />
              Agent Activity
            </h2>
          </div>
          <div className="space-y-3">
            {stats.agent_activity.map((agent, i) => (
              <AgentActivityCard key={i} agent={agent} />
            ))}
          </div>
        </div>
      </div>

      {/* Bottom row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Categories */}
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-5">
          <h2 className="text-sm font-semibold text-white flex items-center gap-2 mb-4">
            <BarChart3 className="w-4 h-4 text-zinc-500" />
            Top Categories
          </h2>
          <div className="space-y-3">
            {stats.top_categories.map((cat, i) => (
              <div key={cat.category} className="flex items-center gap-3">
                <span className="text-xs text-zinc-500 w-4">{i + 1}</span>
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm text-white">{cat.category}</span>
                    <span className="text-xs text-zinc-500">{cat.count}</span>
                  </div>
                  <div className="h-1.5 bg-zinc-800 rounded-full overflow-hidden">
                    <div className="h-full bg-indigo-500/60 rounded-full" style={{ width: `${(cat.count / stats.top_categories[0].count) * 100}%` }} />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Reorder Recommendations */}
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-semibold text-white flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-cyan-400" />
              Reorder Recommendations
            </h2>
            <Link href="/products?status=REORDER_CANDIDATE" className="text-xs text-indigo-400 hover:text-indigo-300 flex items-center gap-1">
              View all <ArrowRight className="w-3 h-3" />
            </Link>
          </div>
          <div className="space-y-2">
            {stats.reorder_recommendations.map((product) => (
              <Link key={product.id} href={`/products/${product.id}`} className="flex items-center justify-between p-3 rounded-lg bg-zinc-800/30 hover:bg-zinc-800/60 transition-colors">
                <div>
                  <div className="text-sm text-white font-medium">{product.name}</div>
                  <div className="text-xs text-zinc-500">{product.category} · {product.sku}</div>
                </div>
                <div className="text-right">
                  <div className="text-sm text-green-400 font-mono">+${product.expected_profit?.toFixed(2)}</div>
                  <div className="text-xs text-zinc-500">est. profit</div>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function StatCard({ icon: Icon, label, value, color, bgColor, href }: { icon: React.ElementType; label: string; value: number; color: string; bgColor: string; href: string }) {
  return (
    <Link href={href} className="bg-zinc-900 border border-zinc-800 rounded-xl p-4 hover:border-zinc-700 transition-colors group">
      <div className="flex items-center gap-3">
        <div className={`w-10 h-10 rounded-lg ${bgColor} flex items-center justify-center`}>
          <Icon className={`w-5 h-5 ${color}`} />
        </div>
        <div>
          <div className="text-2xl font-semibold text-white">{value}</div>
          <div className="text-xs text-zinc-500">{label}</div>
        </div>
      </div>
    </Link>
  );
}

function ScoreBar({ score }: { score?: number }) {
  if (!score) return <span className="text-zinc-500">—</span>;
  return (
    <div className="flex items-center gap-2 justify-end">
      <div className="w-16 h-1.5 bg-zinc-800 rounded-full overflow-hidden">
        <div className={`h-full rounded-full ${score >= 70 ? 'bg-green-500' : score >= 50 ? 'bg-yellow-500' : 'bg-red-500'}`} style={{ width: `${score}%` }} />
      </div>
      <span className={`text-xs font-mono ${score >= 70 ? 'text-green-400' : score >= 50 ? 'text-yellow-400' : 'text-red-400'}`}>{score}</span>
    </div>
  );
}

function AgentActivityCard({ agent }: { agent: AgentResult }) {
  const iconMap: Record<string, { icon: React.ElementType; color: string; bgColor: string }> = {
    market: { icon: BarChart3, color: 'text-blue-400', bgColor: 'bg-blue-500/10' },
    profit: { icon: TrendingUp, color: 'text-green-400', bgColor: 'bg-green-500/10' },
    risk: { icon: ShieldAlert, color: 'text-red-400', bgColor: 'bg-red-500/10' },
    decision: { icon: Brain, color: 'text-purple-400', bgColor: 'bg-purple-500/10' },
    supplier: { icon: Package, color: 'text-cyan-400', bgColor: 'bg-cyan-500/10' },
    competition: { icon: Eye, color: 'text-yellow-400', bgColor: 'bg-yellow-500/10' },
    listing: { icon: Tag, color: 'text-indigo-400', bgColor: 'bg-indigo-500/10' },
    overall: { icon: CheckCircle2, color: 'text-green-400', bgColor: 'bg-green-500/10' },
  };
  const { icon: Icon, color, bgColor } = iconMap[agent.agent_type] || { icon: Brain, color: 'text-zinc-400', bgColor: 'bg-zinc-500/10' };
  const statusIcon = {
    completed: <CheckCircle2 className="w-3.5 h-3.5 text-green-400" />,
    running: <RefreshCw className="w-3.5 h-3.5 text-blue-400 animate-spin" />,
    pending: <Clock className="w-3.5 h-3.5 text-yellow-400" />,
    failed: <AlertCircle className="w-3.5 h-3.5 text-red-400" />,
  }[agent.status] || <Clock className="w-3.5 h-3.5 text-zinc-400" />;

  return (
    <div className="flex items-start gap-3 p-3 rounded-lg bg-zinc-800/30">
      <div className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 ${bgColor}`}>
        <Icon className={`w-4 h-4 ${color}`} />
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between gap-2">
          <span className="text-xs font-medium text-white capitalize">{agent.agent_type} Agent</span>
          {statusIcon}
        </div>
        {agent.output && <p className="text-xs text-zinc-500 mt-1 line-clamp-2">{agent.output}</p>}
        {agent.confidence && <div className="text-xs text-zinc-500 mt-1">Confidence: {(agent.confidence * 100).toFixed(0)}%</div>}
      </div>
    </div>
  );
}
