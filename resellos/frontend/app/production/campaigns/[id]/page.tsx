'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeft, Plus, RefreshCw, Wrench, DollarSign, AlertTriangle } from 'lucide-react';
import {
  getProductionCampaign,
  createMachineCandidate,
} from '@/lib/api';
import type { ProductionCampaignDetail, MachineCandidate } from '@/lib/types';
import { MACHINE_STATUS_COLORS, MACHINE_STATUS_LABELS, MACHINE_DECISION_COLORS, MACHINE_DECISION_LABELS } from '@/lib/types';

export default function ProductionCampaignDetailPage() {
  const params = useParams<{ id: string }>();
  const [detail, setDetail] = useState<ProductionCampaignDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [showAddMachine, setShowAddMachine] = useState(false);
  const [machineName, setMachineName] = useState('');

  async function loadData() {
    setLoading(true);
    try { setDetail(await getProductionCampaign(params.id)); } catch { /* */ }
    finally { setLoading(false); }
  }

  useEffect(() => { loadData(); }, [params.id]);

  async function handleAddMachine(e: React.FormEvent) {
    e.preventDefault();
    if (!machineName.trim()) return;
    await createMachineCandidate({ campaign_id: params.id, name: machineName });
    setMachineName('');
    setShowAddMachine(false);
    loadData();
  }

  if (loading) {
    return <div className="flex items-center justify-center h-64"><RefreshCw className="w-6 h-6 animate-spin text-indigo-400" /></div>;
  }

  if (!detail) {
    return <div className="p-6 text-zinc-400">Campaign not found</div>;
  }

  const { campaign, capabilities, machines } = detail;

  return (
    <div className="p-6 space-y-6 max-w-[1400px]">
      <div className="flex items-center gap-4">
        <Link href="/production" className="text-zinc-400 hover:text-white"><ArrowLeft className="w-5 h-5" /></Link>
        <div>
          <h1 className="text-2xl font-bold text-white">{campaign.name}</h1>
          {campaign.goal && <p className="text-zinc-400 text-sm mt-1">{campaign.goal}</p>}
        </div>
        <span className={`ml-auto inline-flex items-center px-2.5 py-1 text-xs font-medium border rounded-full ${
          campaign.status === 'RUNNING' ? 'bg-green-500/20 text-green-400 border-green-500/30' : 'bg-zinc-500/20 text-zinc-400 border-zinc-500/30'
        }`}>{campaign.status}</span>
      </div>

      {/* Campaign stats */}
      <div className="grid gap-3 md:grid-cols-4">
        <StatCard icon={<DollarSign className="w-4 h-4" />} label="Budget" value={campaign.budget_limit_usd ? `$${Number(campaign.budget_limit_usd).toLocaleString()}` : 'Not set'} />
        <StatCard icon={<Wrench className="w-4 h-4" />} label="Machines" value={String(campaign.machine_count)} />
        <StatCard icon={<AlertTriangle className="w-4 h-4" />} label="Shortlisted" value={String(campaign.shortlisted_count)} />
        <StatCard label="Decided" value={String(campaign.decided_count)} />
      </div>

      {/* Capabilities */}
      {capabilities.length > 0 && (
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-5">
          <h2 className="text-sm uppercase tracking-[0.18em] text-zinc-500 mb-3">Capabilities</h2>
          <div className="flex flex-wrap gap-2">
            {capabilities.map((cap) => (
              <span key={cap.id} className="inline-flex items-center px-3 py-1.5 text-xs font-medium bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 rounded-lg">
                {cap.name}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Machines */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-sm uppercase tracking-[0.18em] text-zinc-500">Machine Candidates</h2>
          <button onClick={() => setShowAddMachine(!showAddMachine)} className="flex items-center gap-1.5 px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium rounded-lg">
            <Plus className="w-3 h-3" /> Add Machine
          </button>
        </div>

        {showAddMachine && (
          <form onSubmit={handleAddMachine} className="mb-4 bg-zinc-900 border border-zinc-800 rounded-xl p-4 flex gap-3 items-end">
            <label className="flex-1">
              <div className="mb-1 text-xs uppercase tracking-[0.16em] text-zinc-500">Machine Name *</div>
              <input value={machineName} onChange={(e) => setMachineName(e.target.value)} className="w-full rounded-xl border border-zinc-800 bg-zinc-950/80 px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500/50" placeholder="e.g. 50W Fiber Laser Marker" />
            </label>
            <button type="submit" className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-sm rounded-lg">Add</button>
          </form>
        )}

        {machines.length === 0 ? (
          <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-8 text-center text-zinc-500">
            No machines added yet. Add one above.
          </div>
        ) : (
          <div className="space-y-3">
            {machines.map((m) => (
              <Link key={m.id} href={`/production/machines/${m.id}`} className="block bg-zinc-900 border border-zinc-800 rounded-xl p-4 hover:border-zinc-700 transition-colors">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-medium text-white">{m.name}</h3>
                    {m.brand && <span className="text-zinc-500 text-xs">{m.brand} {m.model}</span>}
                  </div>
                  <div className="flex items-center gap-3">
                    {m.price_new && <span className="text-sm text-zinc-300">${Number(m.price_new).toLocaleString()}</span>}
                    <span className={`inline-flex items-center px-2 py-0.5 text-xs font-medium border rounded-full ${MACHINE_STATUS_COLORS[m.status] || MACHINE_STATUS_COLORS.SUGGESTED}`}>
                      {MACHINE_STATUS_LABELS[m.status] || m.status}
                    </span>
                    {m.decision_recommendation && (
                      <span className={`inline-flex items-center px-2 py-0.5 text-xs font-medium border rounded-full ${MACHINE_DECISION_COLORS[m.decision_recommendation] || ''}`}>
                        {MACHINE_DECISION_LABELS[m.decision_recommendation] || m.decision_recommendation}
                      </span>
                    )}
                  </div>
                </div>
                <div className="flex gap-4 mt-2 text-xs text-zinc-500">
                  <span>{m.evidence_count} evidence</span>
                  <span>{m.product_family_count} families</span>
                  <span>{m.cost_scenario_count} scenarios</span>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function StatCard({ icon, label, value }: { icon?: React.ReactNode; label: string; value: string }) {
  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-4">
      <div className="flex items-center gap-2 text-zinc-500 text-xs mb-1">{icon}{label}</div>
      <div className="text-white font-medium">{value}</div>
    </div>
  );
}
