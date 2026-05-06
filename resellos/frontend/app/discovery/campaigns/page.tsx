'use client';

import { useEffect, useMemo, useState } from 'react';
import Link from 'next/link';
import { Loader2, Plus, RefreshCw, Sparkles } from 'lucide-react';
import { createDiscoveryCampaign, listDiscoveryCampaigns } from '@/lib/api';
import type { DiscoveryCampaign, DiscoveryCampaignInput } from '@/lib/types';

const DEFAULT_FORM: DiscoveryCampaignInput & { constraints_text: string } = {
  name: 'Pet accessories discovery',
  category: 'Pet accessories',
  goal: 'Find low-risk pet accessory ideas worth deeper research.',
  constraints_json: {},
  budget_limit_usd: 25,
  max_ideas: 10,
  max_products_to_promote: 3,
  status: 'DRAFT',
  created_by: 'codex',
  constraints_text: JSON.stringify(
    {
      avoid: ['medicine', 'supplements', 'ingestibles', 'flea/tick', 'electric/shock', 'health claims'],
      budget_policy: 'standard queue only, low cost',
    },
    null,
    2,
  ),
};

export default function DiscoveryCampaignsPage() {
  const [campaigns, setCampaigns] = useState<DiscoveryCampaign[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState(DEFAULT_FORM);

  async function loadCampaigns() {
    setLoading(true);
    setError(null);
    try {
      setCampaigns(await listDiscoveryCampaigns());
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load campaigns');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadCampaigns();
  }, []);

  async function handleCreate() {
    setSaving(true);
    setError(null);
    try {
      let constraints_json = form.constraints_json || {};
      if (form.constraints_text.trim()) {
        constraints_json = JSON.parse(form.constraints_text);
      }
      await createDiscoveryCampaign({
        name: form.name,
        category: form.category,
        goal: form.goal,
        constraints_json,
        budget_limit_usd: form.budget_limit_usd,
        max_ideas: form.max_ideas,
        max_products_to_promote: form.max_products_to_promote,
        status: form.status,
        created_by: form.created_by,
      });
      setForm(DEFAULT_FORM);
      await loadCampaigns();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not create campaign');
    } finally {
      setSaving(false);
    }
  }

  const totalBudget = useMemo(
    () => campaigns.reduce((sum, campaign) => sum + Number(campaign.dataforseo_spend_estimate || 0), 0),
    [campaigns],
  );

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <RefreshCw className="h-6 w-6 animate-spin text-indigo-400" />
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="mx-auto max-w-[1440px] space-y-6">
        <header className="rounded-[28px] border border-zinc-800 bg-zinc-950/80 p-6 shadow-2xl shadow-black/20">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div>
              <div className="flex items-center gap-2">
                <Sparkles className="h-5 w-5 text-indigo-400" />
                <h1 className="text-3xl font-semibold tracking-tight text-white">Discovery Campaigns</h1>
              </div>
              <p className="mt-2 text-sm text-zinc-400">
                Controlled discovery campaigns keep the founder in charge while Codex scouts, ranks, and reports on ideas.
              </p>
            </div>
            <div className="flex flex-wrap gap-3 text-xs text-zinc-300">
              <Pill label={`Campaigns: ${campaigns.length}`} />
              <Pill label={`Total spend: ${money(totalBudget)}`} />
            </div>
          </div>
        </header>

        {error ? (
          <div className="rounded-2xl border border-red-500/20 bg-red-500/10 p-4 text-sm text-red-100">
            {error}
          </div>
        ) : null}

        <div className="grid gap-6 xl:grid-cols-[1fr_1.2fr]">
          <section className="rounded-[24px] border border-zinc-800 bg-zinc-950/80 p-5 shadow-xl shadow-black/10">
            <div className="mb-4 flex items-center gap-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-xl border border-zinc-800 bg-zinc-900 text-zinc-300">
                <Plus className="h-4 w-4" />
              </div>
              <h2 className="text-sm font-semibold uppercase tracking-[0.18em] text-zinc-200">Create Campaign</h2>
            </div>

            <div className="space-y-3">
              <Field label="Name" value={form.name} onChange={(value) => setForm((current) => ({ ...current, name: value }))} />
              <Field label="Category" value={form.category || ''} onChange={(value) => setForm((current) => ({ ...current, category: value }))} />
              <Field label="Goal" value={form.goal || ''} onChange={(value) => setForm((current) => ({ ...current, goal: value }))} />
              <Field label="Budget limit USD" type="number" value={String(form.budget_limit_usd ?? '')} onChange={(value) => setForm((current) => ({ ...current, budget_limit_usd: value ? Number(value) : undefined }))} />
              <Field label="Max ideas" type="number" value={String(form.max_ideas ?? '')} onChange={(value) => setForm((current) => ({ ...current, max_ideas: value ? Number(value) : undefined }))} />
              <Field label="Max products to promote" type="number" value={String(form.max_products_to_promote ?? '')} onChange={(value) => setForm((current) => ({ ...current, max_products_to_promote: value ? Number(value) : undefined }))} />
              <Field label="Created by" value={form.created_by || ''} onChange={(value) => setForm((current) => ({ ...current, created_by: value }))} />
              <div>
                <label className="mb-1 block text-xs uppercase tracking-[0.16em] text-zinc-500">Constraints JSON</label>
                <textarea
                  value={form.constraints_text}
                  onChange={(event) => setForm((current) => ({ ...current, constraints_text: event.target.value }))}
                  rows={8}
                  className="w-full rounded-xl border border-zinc-800 bg-zinc-950/80 px-3 py-2 text-sm text-white outline-none transition focus:border-indigo-500/50"
                />
              </div>
            </div>

            <div className="mt-4 flex justify-end">
              <button
                type="button"
                onClick={handleCreate}
                disabled={saving || !form.name.trim()}
                className="inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-indigo-500 disabled:opacity-60"
              >
                {saving ? <Loader2 className="h-4 w-4 animate-spin" /> : <Plus className="h-4 w-4" />}
                Create Campaign
              </button>
            </div>
          </section>

          <section className="rounded-[24px] border border-zinc-800 bg-zinc-950/80 p-5 shadow-xl shadow-black/10">
            <div className="mb-4 flex items-center justify-between gap-3">
              <div className="flex items-center gap-2">
                <div className="flex h-8 w-8 items-center justify-center rounded-xl border border-zinc-800 bg-zinc-900 text-zinc-300">
                  <Sparkles className="h-4 w-4" />
                </div>
                <h2 className="text-sm font-semibold uppercase tracking-[0.18em] text-zinc-200">Campaign Queue</h2>
              </div>
              <button
                type="button"
                onClick={loadCampaigns}
                className="rounded-lg border border-zinc-700 bg-zinc-900 px-3 py-1.5 text-xs text-zinc-300 hover:border-zinc-600"
              >
                Refresh
              </button>
            </div>

            <div className="space-y-3">
              {campaigns.length ? (
                campaigns.map((campaign) => (
                  <Link
                    key={campaign.id}
                    href={`/discovery/campaigns/${campaign.id}`}
                    className="block rounded-2xl border border-zinc-800 bg-zinc-950/60 p-4 transition hover:border-zinc-700 hover:bg-zinc-900/40"
                  >
                    <div className="flex flex-wrap items-start justify-between gap-3">
                      <div>
                        <div className="text-base font-medium text-white">{campaign.name}</div>
                        <div className="text-xs text-zinc-500">
                          {campaign.category || 'Uncategorized'} · {campaign.status}
                        </div>
                        <div className="mt-2 text-sm text-zinc-300">{campaign.goal || 'No goal recorded.'}</div>
                      </div>
                      <div className="text-right text-xs text-zinc-400">
                        <div>Budget {money(campaign.budget_limit_usd)}</div>
                        <div>Spend {money(campaign.dataforseo_spend_estimate)}</div>
                      </div>
                    </div>
                    <div className="mt-3 grid grid-cols-4 gap-2 text-xs text-zinc-300">
                      <Stat label="Ideas" value={String(campaign.idea_count ?? 0)} />
                      <Stat label="Promising" value={String(campaign.promising_idea_count ?? 0)} />
                      <Stat label="Promoted" value={String(campaign.promoted_product_count ?? 0)} />
                      <Stat label="Rejected" value={String(campaign.rejected_idea_count ?? 0)} />
                    </div>
                  </Link>
                ))
              ) : (
                <EmptyState title="No campaigns yet" description="Create the first campaign to start a controlled discovery run." />
              )}
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}

function Field(props: { label: string; value: string; onChange: (value: string) => void; type?: string }) {
  return (
    <label className="block">
      <div className="mb-1 text-xs uppercase tracking-[0.16em] text-zinc-500">{props.label}</div>
      <input
        type={props.type || 'text'}
        value={props.value}
        onChange={(event) => props.onChange(event.target.value)}
        className="w-full rounded-xl border border-zinc-800 bg-zinc-950/80 px-3 py-2 text-sm text-white outline-none transition focus:border-indigo-500/50"
      />
    </label>
  );
}

function Pill({ label }: { label: string }) {
  return <span className="rounded-full border border-zinc-800 bg-zinc-900 px-3 py-1">{label}</span>;
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-zinc-800 bg-zinc-950/80 px-3 py-2">
      <div className="text-[10px] uppercase tracking-[0.14em] text-zinc-500">{label}</div>
      <div className="mt-1 font-medium text-white">{value}</div>
    </div>
  );
}

function EmptyState({ title, description }: { title: string; description: string }) {
  return (
    <div className="rounded-2xl border border-dashed border-zinc-800 bg-zinc-950/40 p-6 text-center">
      <div className="text-sm font-medium text-white">{title}</div>
      <div className="mt-1 text-sm text-zinc-500">{description}</div>
    </div>
  );
}

function money(value?: number | null) {
  if (value == null) return '—';
  return `$${Number(value).toFixed(2)}`;
}
