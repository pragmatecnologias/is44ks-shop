'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import {
  ArrowRight,
  Brain,
  CheckCircle2,
  Loader2,
  Plus,
  RefreshCw,
  Sparkles,
  Target,
} from 'lucide-react';
import {
  archiveDiscoveryIdea,
  createDiscoveryIdea,
  deleteDiscoveryIdea,
  getOpportunityBoard,
  generateDiscoveryTasks,
  listDiscoveryIdeas,
  promoteDiscoveryIdea,
  quickScanDiscoveryIdea,
} from '@/lib/api';
import type { DiscoveryIdea, DiscoveryQuickScanInput, OpportunityBoardRow } from '@/lib/types';

const emptyQuickScan: DiscoveryQuickScanInput = {
  idea_name: '',
  category: 'Car accessories',
  source_platform: 'Alibaba',
  marketplace_observation: '',
};

const CATEGORY_HINTS = [
  'Car accessories',
  'Desk accessories',
  'Home organization',
  'Pet accessories',
  'Travel accessories',
  'Creator tools',
  'Small tools',
];

export default function DiscoveryPage() {
  const [ideas, setIdeas] = useState<DiscoveryIdea[]>([]);
  const [board, setBoard] = useState<OpportunityBoardRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [scanning, setScanning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState<DiscoveryQuickScanInput>(emptyQuickScan);

  async function loadIdeas() {
    setLoading(true);
    setError(null);
    try {
      setIdeas(await listDiscoveryIdeas());
      setBoard(await getOpportunityBoard());
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load discovery ideas');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadIdeas();
  }, []);

  async function handleQuickScan() {
    setScanning(true);
    setError(null);
    try {
      await quickScanDiscoveryIdea(form);
      setForm(emptyQuickScan);
      await loadIdeas();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Quick scan failed');
    } finally {
      setScanning(false);
    }
  }

  async function handleCreateIdea() {
    if (!form.idea_name.trim()) return;
    setSaving(true);
    setError(null);
    try {
      await createDiscoveryIdea(form);
      setForm(emptyQuickScan);
      await loadIdeas();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not save idea');
    } finally {
      setSaving(false);
    }
  }

  async function handlePromoteIdea(ideaId: string) {
    setError(null);
    try {
      await promoteDiscoveryIdea(ideaId);
      await loadIdeas();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not promote idea');
    }
  }

  async function handleDeleteIdea(ideaId: string) {
    setError(null);
    try {
      await deleteDiscoveryIdea(ideaId);
      await loadIdeas();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not delete idea');
    }
  }

  async function handleGenerateTasks(ideaId: string) {
    setError(null);
    try {
      await generateDiscoveryTasks(ideaId);
      await loadIdeas();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not generate tasks');
    }
  }

  async function handleArchiveIdea(ideaId: string) {
    setError(null);
    try {
      await archiveDiscoveryIdea(ideaId);
      await loadIdeas();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not archive idea');
    }
  }

  const readyCount = ideas.filter((idea) => idea.quick_scan_verdict === 'PROMISING').length;
  const marketCheckCount = ideas.filter((idea) => idea.quick_scan_verdict === 'NEEDS_MARKET_CHECK').length;
  const promotedCount = ideas.filter((idea) => idea.status === 'PROMOTED_TO_PRODUCT').length;

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
        <header className="rounded-[28px] border border-zinc-800 bg-[radial-gradient(circle_at_top_left,_rgba(79,70,229,0.22),_transparent_28%),linear-gradient(180deg,rgba(9,9,11,0.96),rgba(17,17,17,0.96))] p-6 shadow-2xl shadow-black/20">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div>
              <h1 className="text-3xl font-semibold tracking-tight text-white">Product Discovery</h1>
              <p className="mt-2 text-sm text-zinc-400">
                Product discovery starts here. Quick-scan rough ideas, then promote only the strongest ones into full research.
              </p>
            </div>
            <div className="flex gap-3 text-xs text-zinc-300">
              <Pill label={`Ideas: ${ideas.length}`} />
              <Pill label={`Promising: ${readyCount}`} />
              <Pill label={`Need market check: ${marketCheckCount}`} />
              <Pill label={`Promoted: ${promotedCount}`} />
            </div>
          </div>
        </header>

        {error ? (
          <div className="rounded-2xl border border-red-500/20 bg-red-500/10 p-4 text-sm text-red-100">
            {error}
          </div>
        ) : null}

        <div className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
          <section className="rounded-[24px] border border-zinc-800 bg-zinc-950/80 p-5 shadow-xl shadow-black/10">
            <div className="mb-4 flex items-center gap-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-xl border border-zinc-800 bg-zinc-900 text-zinc-300">
                <Sparkles className="h-4 w-4" />
              </div>
              <h2 className="text-sm font-semibold uppercase tracking-[0.18em] text-zinc-200">Quick Scan</h2>
            </div>

            <div className="grid gap-3 md:grid-cols-2">
              <Input label="Idea name" value={form.idea_name || ''} onChange={(value) => setForm((s) => ({ ...s, idea_name: value }))} />
              <Input label="Category" value={form.category || ''} onChange={(value) => setForm((s) => ({ ...s, category: value }))} list="category-hints" />
              <Input label="Source platform" value={form.source_platform || ''} onChange={(value) => setForm((s) => ({ ...s, source_platform: value }))} />
              <Input label="Source URL" value={form.source_url || ''} onChange={(value) => setForm((s) => ({ ...s, source_url: value }))} />
              <Input label="Rough supplier cost" type="number" step="0.01" value={form.rough_supplier_cost?.toString() ?? ''} onChange={(value) => setForm((s) => ({ ...s, rough_supplier_cost: value ? Number(value) : undefined }))} />
              <Input label="Estimated landed cost" type="number" step="0.01" value={form.estimated_landed_cost?.toString() ?? ''} onChange={(value) => setForm((s) => ({ ...s, estimated_landed_cost: value ? Number(value) : undefined }))} />
            </div>

              <Textarea label="Why interesting" value={form.why_interesting || ''} onChange={(value) => setForm((s) => ({ ...s, why_interesting: value }))} />
              <Textarea label="Marketplace observation" value={(form as DiscoveryQuickScanInput & { marketplace_observation?: string }).marketplace_observation || ''} onChange={(value) => setForm((s) => ({ ...s, marketplace_observation: value }))} />
              <Textarea label="Notes" value={form.notes || ''} onChange={(value) => setForm((s) => ({ ...s, notes: value }))} />

            <datalist id="category-hints">
              {CATEGORY_HINTS.map((hint) => (
                <option key={hint} value={hint} />
              ))}
            </datalist>

            <div className="mt-4 flex flex-wrap justify-end gap-3">
              <button
                type="button"
                onClick={handleCreateIdea}
                disabled={saving || !form.idea_name}
                className="inline-flex items-center gap-2 rounded-xl border border-zinc-700 bg-zinc-900 px-4 py-2 text-sm font-medium text-zinc-100 transition hover:border-zinc-600 disabled:opacity-60"
              >
                {saving ? <Loader2 className="h-4 w-4 animate-spin" /> : <Plus className="h-4 w-4" />}
                Save Idea
              </button>
              <button
                type="button"
                onClick={handleQuickScan}
                disabled={scanning || !form.idea_name}
                className="inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-indigo-500 disabled:opacity-60"
              >
                {scanning ? <Loader2 className="h-4 w-4 animate-spin" /> : <Brain className="h-4 w-4" />}
                Quick Scan
              </button>
            </div>
          </section>

          <section className="rounded-[24px] border border-zinc-800 bg-zinc-950/80 p-5 shadow-xl shadow-black/10">
            <div className="mb-4 flex items-center gap-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-xl border border-zinc-800 bg-zinc-900 text-zinc-300">
                <Target className="h-4 w-4" />
              </div>
              <h2 className="text-sm font-semibold uppercase tracking-[0.18em] text-zinc-200">Workflow</h2>
            </div>

            <div className="space-y-3 text-sm text-zinc-300">
              <Step title="1. Enter an idea" detail="Use a name, category, rough costs, and one marketplace observation." />
              <Step title="2. Quick scan" detail="Get a first-pass verdict, risk flags, and research priority." />
              <Step title="3. Collect evidence" detail="Add sold listings, active listings, suppliers, and competitors." />
              <Step title="4. Promote" detail="Move promising ideas into full product research when the gates are clear." />
            </div>
          </section>
        </div>

        <section className="rounded-[24px] border border-zinc-800 bg-zinc-950/80 p-5 shadow-xl shadow-black/10">
          <div className="mb-4 flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-xl border border-zinc-800 bg-zinc-900 text-zinc-300">
              <CheckCircle2 className="h-4 w-4" />
            </div>
            <h2 className="text-sm font-semibold uppercase tracking-[0.18em] text-zinc-200">Discovery Queue</h2>
          </div>

          <div className="grid gap-4 xl:grid-cols-2">
            {ideas.length === 0 ? (
              <EmptyState title="No ideas yet" description="Quick-scan a product idea to populate this queue." />
            ) : (
              ideas.map((idea) => (
                <IdeaCard
                  key={idea.id}
                  idea={idea}
                  onPromote={() => handlePromoteIdea(idea.id)}
                  onDelete={() => handleDeleteIdea(idea.id)}
                  onGenerateTasks={() => handleGenerateTasks(idea.id)}
                  onArchive={() => handleArchiveIdea(idea.id)}
                />
              ))
            )}
          </div>
        </section>

        <section className="rounded-[24px] border border-zinc-800 bg-zinc-950/80 p-5 shadow-xl shadow-black/10">
          <div className="mb-4 flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-xl border border-zinc-800 bg-zinc-900 text-zinc-300">
              <Sparkles className="h-4 w-4" />
            </div>
            <h2 className="text-sm font-semibold uppercase tracking-[0.18em] text-zinc-200">Opportunity Board</h2>
          </div>
          <div className="overflow-hidden rounded-2xl border border-zinc-800">
            <table className="w-full text-left text-sm">
              <thead className="bg-zinc-950/90 text-xs uppercase tracking-[0.14em] text-zinc-500">
                <tr>
                  <th className="px-4 py-3">Idea / Product</th>
                  <th className="px-4 py-3">Type</th>
                  <th className="px-4 py-3">Readiness</th>
                  <th className="px-4 py-3">Evidence</th>
                  <th className="px-4 py-3">Market</th>
                  <th className="px-4 py-3">Best Cost</th>
                  <th className="px-4 py-3">Verdict</th>
                  <th className="px-4 py-3">Next Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-800">
                {board.map((row) => (
                  <tr key={row.id} className="bg-zinc-950/40">
                    <td className="px-4 py-3 text-white">
                      <div className="font-medium">{row.title}</div>
                      <div className="text-xs text-zinc-500">{row.category || 'Uncategorized'}</div>
                    </td>
                    <td className="px-4 py-3 text-zinc-300">{row.entity_type}</td>
                    <td className="px-4 py-3 text-zinc-300">{row.research_completeness_score}%</td>
                    <td className="px-4 py-3 text-zinc-300">
                      {row.sold_evidence_count} sold / {row.active_evidence_count} active
                    </td>
                    <td className="px-4 py-3 text-zinc-300">
                      {row.median_sold_price != null ? money(row.median_sold_price) : '—'}
                    </td>
                    <td className="px-4 py-3 text-zinc-300">
                      {money(row.best_landed_cost)}
                    </td>
                    <td className="px-4 py-3 text-zinc-300">{row.research_verdict || row.status || '—'}</td>
                    <td className="px-4 py-3 text-zinc-400">{row.next_action || '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </div>
  );
}

function IdeaCard({
  idea,
  onPromote,
  onDelete,
  onGenerateTasks,
  onArchive,
}: {
  idea: DiscoveryIdea;
  onPromote: () => void;
  onDelete: () => void;
  onGenerateTasks: () => void;
  onArchive: () => void;
}) {
  return (
    <div className="rounded-2xl border border-zinc-800 bg-zinc-950/60 p-4">
      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-base font-semibold text-white">{idea.idea_name}</h3>
            <span className="rounded-full border border-zinc-800 bg-zinc-900 px-2 py-0.5 text-[10px] uppercase tracking-[0.16em] text-zinc-300">
              {idea.status}
            </span>
          </div>
          <div className="mt-1 text-xs text-zinc-500">
            {idea.category || 'Uncategorized'} {idea.source_platform ? `· ${idea.source_platform}` : ''}
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button onClick={onGenerateTasks} className="text-xs text-zinc-500 hover:text-indigo-400">
            Tasks
          </button>
          <button onClick={onArchive} className="text-xs text-zinc-500 hover:text-yellow-400">
            Archive
          </button>
          <button onClick={onDelete} className="text-xs text-zinc-500 hover:text-red-400">
            Delete
          </button>
          {idea.status !== 'PROMOTED_TO_PRODUCT' ? (
            <button onClick={onPromote} className="inline-flex items-center gap-1 rounded-lg border border-indigo-500/20 bg-indigo-500/10 px-2 py-1 text-xs text-indigo-300 hover:bg-indigo-500/20">
              Promote <ArrowRight className="h-3 w-3" />
            </button>
          ) : null}
        </div>
      </div>

      <div className="mt-3 grid gap-2 text-sm text-zinc-300 md:grid-cols-2">
        <StatRow label="Verdict" value={idea.quick_scan_verdict || 'IDEA'} />
        <StatRow label="Priority" value={idea.research_priority || '—'} />
        <StatRow label="Readiness" value={idea.buy_readiness_status || 'NOT_READY'} />
        <StatRow label="Research" value={`${idea.research_completeness_score ?? 0}%`} />
        <StatRow label="Supplier cost" value={money(idea.rough_supplier_cost)} />
        <StatRow label="Landed cost" value={money(idea.estimated_landed_cost)} />
      </div>

      <div className="mt-3 rounded-xl border border-zinc-800 bg-zinc-950/70 p-3">
        <div className="text-xs uppercase tracking-[0.16em] text-zinc-500">Why interesting</div>
        <div className="mt-1 text-sm text-zinc-200">{idea.why_interesting || 'No note yet.'}</div>
      </div>

      <div className="mt-3 rounded-xl border border-zinc-800 bg-zinc-950/70 p-3">
        <div className="text-xs uppercase tracking-[0.16em] text-zinc-500">Next evidence</div>
        <div className="mt-2 space-y-2">
          {(idea.required_next_evidence || []).length ? (
            (idea.required_next_evidence as string[]).map((item) => (
              <div key={item} className="flex items-start gap-2 text-sm text-zinc-300">
                <span className="mt-1 h-2 w-2 rounded-full bg-indigo-400" />
                <span>{item}</span>
              </div>
            ))
          ) : (
            <div className="text-sm text-zinc-500">No next evidence recorded.</div>
          )}
        </div>
      </div>

      <div className="mt-3 text-xs text-zinc-500">
        Keywords: {(idea.suggested_keywords as string[] | undefined)?.join(', ') || '—'}
      </div>
      <div className="mt-1 text-xs text-zinc-500">
        Risk: {(idea.risk_flags as string[] | undefined)?.join(', ') || 'None'}
      </div>
    </div>
  );
}

function Step({ title, detail }: { title: string; detail: string }) {
  return (
    <div className="rounded-2xl border border-zinc-800 bg-zinc-950/60 p-4">
      <div className="font-medium text-white">{title}</div>
      <div className="mt-1 text-xs text-zinc-400">{detail}</div>
    </div>
  );
}

function Input({
  label,
  value,
  onChange,
  type = 'text',
  step,
  list,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  type?: string;
  step?: string;
  list?: string;
}) {
  return (
    <label className="space-y-1">
      <div className="text-xs uppercase tracking-[0.16em] text-zinc-500">{label}</div>
      <input
        type={type}
        step={step}
        list={list}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full rounded-xl border border-zinc-800 bg-zinc-950/80 px-3 py-2 text-sm text-white outline-none transition focus:border-indigo-500/50"
      />
    </label>
  );
}

function Textarea({
  label,
  value,
  onChange,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
}) {
  return (
    <label className="mt-3 block space-y-1">
      <div className="text-xs uppercase tracking-[0.16em] text-zinc-500">{label}</div>
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        rows={3}
        className="w-full rounded-xl border border-zinc-800 bg-zinc-950/80 px-3 py-2 text-sm text-white outline-none transition focus:border-indigo-500/50"
      />
    </label>
  );
}

function EmptyState({ title, description }: { title: string; description: string }) {
  return (
    <div className="rounded-2xl border border-dashed border-zinc-800 bg-zinc-950/40 p-5 text-sm text-zinc-400">
      <div className="font-medium text-white">{title}</div>
      <div className="mt-1 text-sm text-zinc-500">{description}</div>
    </div>
  );
}

function StatRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between gap-3 rounded-xl border border-zinc-800 bg-zinc-950/60 px-3 py-2">
      <div className="text-xs uppercase tracking-[0.14em] text-zinc-500">{label}</div>
      <div className="text-sm text-white">{value}</div>
    </div>
  );
}

function Pill({ label }: { label: string }) {
  return <span className="inline-flex items-center rounded-full border border-zinc-800 bg-zinc-950/60 px-3 py-1.5 text-xs text-zinc-300">{label}</span>;
}

function money(value?: number | null) {
  if (value == null) return '—';
  return `$${Number(value).toFixed(2)}`;
}
