'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Plus, RefreshCw, ArrowLeft, Wrench } from 'lucide-react';
import { listProductionCampaigns, createProductionCampaign } from '@/lib/api';
import type { ProductionCampaign } from '@/lib/types';

export default function ProductionCampaignsPage() {
  const [campaigns, setCampaigns] = useState<ProductionCampaign[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [name, setName] = useState('');

  async function loadData() {
    setLoading(true);
    try { setCampaigns(await listProductionCampaigns()); } catch { /* */ }
    finally { setLoading(false); }
  }

  useEffect(() => { loadData(); }, []);

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    if (!name.trim()) return;
    await createProductionCampaign({ name });
    setName('');
    setShowCreate(false);
    loadData();
  }

  if (loading) {
    return <div className="flex items-center justify-center h-64"><RefreshCw className="w-6 h-6 animate-spin text-indigo-400" /></div>;
  }

  return (
    <div className="p-6 space-y-6 max-w-[1400px]">
      <div className="flex items-center gap-4">
        <Link href="/production" className="text-zinc-400 hover:text-white"><ArrowLeft className="w-5 h-5" /></Link>
        <h1 className="text-2xl font-bold text-white">Production Campaigns</h1>
        <button onClick={() => setShowCreate(!showCreate)} className="ml-auto flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium rounded-lg transition-colors">
          <Plus className="w-4 h-4" /> New Campaign
        </button>
      </div>

      {showCreate && (
        <form onSubmit={handleCreate} className="bg-zinc-900 border border-zinc-800 rounded-xl p-5 flex gap-4 items-end">
          <label className="flex-1">
            <div className="mb-1 text-xs uppercase tracking-[0.16em] text-zinc-500">Campaign Name</div>
            <input value={name} onChange={(e) => setName(e.target.value)} className="w-full rounded-xl border border-zinc-800 bg-zinc-950/80 px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500/50" />
          </label>
          <button type="submit" className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium rounded-lg">Create</button>
        </form>
      )}

      {campaigns.length === 0 ? (
        <div className="text-center py-12 text-zinc-500">No production campaigns yet</div>
      ) : (
        <div className="space-y-3">
          {campaigns.map((c) => (
            <Link key={c.id} href={`/production/campaigns/${c.id}`} className="block bg-zinc-900 border border-zinc-800 rounded-xl p-4 hover:border-zinc-700 transition-colors">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-medium text-white">{c.name}</h3>
                  {c.goal && <p className="text-zinc-400 text-sm mt-1">{c.goal}</p>}
                </div>
                <div className="flex items-center gap-4 text-xs text-zinc-500">
                  <span className="flex items-center gap-1"><Wrench className="w-3 h-3" /> {c.machine_count}</span>
                  <span>{c.status}</span>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
