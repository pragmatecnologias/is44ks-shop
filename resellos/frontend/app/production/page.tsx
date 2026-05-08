'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Cog, Plus, RefreshCw, Factory, Wrench } from 'lucide-react';
import {
  listProductionCampaigns,
  createProductionCampaign,
} from '@/lib/api';
import type { ProductionCampaign } from '@/lib/types';
import { MACHINE_STATUS_COLORS, MACHINE_STATUS_LABELS } from '@/lib/types';

export default function ProductionPage() {
  const [campaigns, setCampaigns] = useState<ProductionCampaign[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [form, setForm] = useState({ name: '', goal: '', budget_limit_usd: '', workspace_type: '' });

  async function loadData() {
    setLoading(true);
    try {
      setCampaigns(await listProductionCampaigns());
    } catch {
      /* offline */
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { loadData(); }, []);

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    if (!form.name.trim()) return;
    try {
      await createProductionCampaign({
        name: form.name,
        goal: form.goal || undefined,
        budget_limit_usd: form.budget_limit_usd ? parseFloat(form.budget_limit_usd) : undefined,
        workspace_type: form.workspace_type || undefined,
      });
      setShowCreate(false);
      setForm({ name: '', goal: '', budget_limit_usd: '', workspace_type: '' });
      loadData();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to create campaign');
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="w-6 h-6 animate-spin text-indigo-400" />
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6 max-w-[1400px]">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-3">
            <Cog className="w-7 h-7 text-indigo-400" />
            Production Discovery
          </h1>
          <p className="text-zinc-400 text-sm mt-1">
            Evaluate machines and production capabilities as business investments
          </p>
        </div>
        <button
          onClick={() => setShowCreate(!showCreate)}
          className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium rounded-lg transition-colors"
        >
          <Plus className="w-4 h-4" />
          New Campaign
        </button>
      </div>

      {showCreate && (
        <form onSubmit={handleCreate} className="bg-zinc-900 border border-zinc-800 rounded-xl p-5 space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <label className="block">
              <div className="mb-1 text-xs uppercase tracking-[0.16em] text-zinc-500">Campaign Name *</div>
              <input
                value={form.name}
                onChange={(e) => setForm((s) => ({ ...s, name: e.target.value }))}
                className="w-full rounded-xl border border-zinc-800 bg-zinc-950/80 px-3 py-2 text-sm text-white placeholder:text-zinc-600 focus:outline-none focus:border-indigo-500/50"
                placeholder="e.g. Home Micro-Factory Machines"
              />
            </label>
            <label className="block">
              <div className="mb-1 text-xs uppercase tracking-[0.16em] text-zinc-500">Budget Limit ($)</div>
              <input
                type="number"
                value={form.budget_limit_usd}
                onChange={(e) => setForm((s) => ({ ...s, budget_limit_usd: e.target.value }))}
                className="w-full rounded-xl border border-zinc-800 bg-zinc-950/80 px-3 py-2 text-sm text-white placeholder:text-zinc-600 focus:outline-none focus:border-indigo-500/50"
                placeholder="10000"
              />
            </label>
            <label className="block">
              <div className="mb-1 text-xs uppercase tracking-[0.16em] text-zinc-500">Workspace Type</div>
              <input
                value={form.workspace_type}
                onChange={(e) => setForm((s) => ({ ...s, workspace_type: e.target.value }))}
                className="w-full rounded-xl border border-zinc-800 bg-zinc-950/80 px-3 py-2 text-sm text-white placeholder:text-zinc-600 focus:outline-none focus:border-indigo-500/50"
                placeholder="e.g. garage, basement, spare room"
              />
            </label>
            <label className="block">
              <div className="mb-1 text-xs uppercase tracking-[0.16em] text-zinc-500">Goal</div>
              <input
                value={form.goal}
                onChange={(e) => setForm((s) => ({ ...s, goal: e.target.value }))}
                className="w-full rounded-xl border border-zinc-800 bg-zinc-950/80 px-3 py-2 text-sm text-white placeholder:text-zinc-600 focus:outline-none focus:border-indigo-500/50"
                placeholder="e.g. Find a laser marker for metal tags under $5k"
              />
            </label>
          </div>
          <div className="flex justify-end gap-3">
            <button type="button" onClick={() => setShowCreate(false)} className="px-4 py-2 text-sm text-zinc-400 hover:text-white">Cancel</button>
            <button type="submit" className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium rounded-lg">Create Campaign</button>
          </div>
        </form>
      )}

      {campaigns.length === 0 ? (
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-12 text-center">
          <Factory className="w-12 h-12 text-zinc-600 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-zinc-300">No production campaigns yet</h3>
          <p className="text-zinc-500 text-sm mt-2">Create a campaign to start evaluating machines and production capabilities.</p>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {campaigns.map((c) => (
            <Link
              key={c.id}
              href={`/production/campaigns/${c.id}`}
              className="bg-zinc-900 border border-zinc-800 rounded-xl p-5 hover:border-zinc-700 transition-colors"
            >
              <div className="flex items-start justify-between mb-3">
                <h3 className="font-medium text-white">{c.name}</h3>
                <span className={`inline-flex items-center px-2 py-0.5 text-xs font-medium border rounded-full ${
                  c.status === 'DRAFT' ? 'bg-zinc-500/20 text-zinc-400 border-zinc-500/30' :
                  c.status === 'RUNNING' ? 'bg-green-500/20 text-green-400 border-green-500/30' :
                  'bg-blue-500/20 text-blue-400 border-blue-500/30'
                }`}>
                  {c.status}
                </span>
              </div>
              {c.goal && <p className="text-zinc-400 text-sm mb-3 line-clamp-2">{c.goal}</p>}
              <div className="flex gap-4 text-xs text-zinc-500">
                <span className="flex items-center gap-1"><Wrench className="w-3 h-3" /> {c.machine_count} machines</span>
                <span>${c.budget_limit_usd ? Number(c.budget_limit_usd).toLocaleString() : 'No budget'}</span>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
