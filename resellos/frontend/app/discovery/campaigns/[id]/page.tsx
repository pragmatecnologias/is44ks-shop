'use client';

import { useEffect, useMemo, useState } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { Plus, RefreshCw, Sparkles, Target } from 'lucide-react';
import {
  addIdeaToCampaign,
  createDiscoveryCampaignTask,
  generateDiscoveryCampaignNextTasks,
  getDiscoveryCampaign,
  getDiscoveryCampaignReport,
  updateDiscoveryCampaign,
  updateDiscoveryCampaignTask,
} from '@/lib/api';
import type {
  DiscoveryCampaignDetail,
  DiscoveryCampaignTaskInput,
  DiscoveryQuickScanInput,
} from '@/lib/types';

const DEFAULT_IDEA_FORM: DiscoveryQuickScanInput = {
  idea_name: '',
  category: 'Pet accessories',
  source_platform: 'Manual',
  marketplace_observation: '',
  why_interesting: '',
};

export default function DiscoveryCampaignDetailPage() {
  const params = useParams<{ id: string }>();
  const campaignId = params.id;
  const [detail, setDetail] = useState<DiscoveryCampaignDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [status, setStatus] = useState<string>('DRAFT');
  const [ideaForm, setIdeaForm] = useState<DiscoveryQuickScanInput>(DEFAULT_IDEA_FORM);
  const [taskForm, setTaskForm] = useState<DiscoveryCampaignTaskInput>({ task_type: 'SCOUTING', title: '' });

  async function loadDetail() {
    if (!campaignId) return;
    setLoading(true);
    setError(null);
    try {
      const data = await getDiscoveryCampaign(campaignId);
      setDetail(data);
      setStatus(data.campaign.status);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load campaign');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadDetail();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [campaignId]);

  async function refreshReport() {
    if (!campaignId) return;
    setSaving(true);
    setError(null);
    try {
      await getDiscoveryCampaignReport(campaignId);
      await loadDetail();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to refresh report');
    } finally {
      setSaving(false);
    }
  }

  async function generateTasks() {
    if (!campaignId) return;
    setSaving(true);
    setError(null);
    try {
      await generateDiscoveryCampaignNextTasks(campaignId);
      await loadDetail();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate campaign tasks');
    } finally {
      setSaving(false);
    }
  }

  async function saveStatus() {
    if (!campaignId || !detail) return;
    setSaving(true);
    setError(null);
    try {
      await updateDiscoveryCampaign(campaignId, { status });
      await loadDetail();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update campaign status');
    } finally {
      setSaving(false);
    }
  }

  async function handleAddIdea() {
    if (!campaignId || !ideaForm.idea_name.trim()) return;
    setSaving(true);
    setError(null);
    try {
      await addIdeaToCampaign(campaignId, {
        ...ideaForm,
        campaign_id: campaignId,
      });
      setIdeaForm(DEFAULT_IDEA_FORM);
      await loadDetail();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to add idea to campaign');
    } finally {
      setSaving(false);
    }
  }

  async function handleCreateTask() {
    if (!campaignId || !taskForm.title.trim()) return;
    setSaving(true);
    setError(null);
    try {
      await createDiscoveryCampaignTask(campaignId, taskForm);
      setTaskForm({ task_type: 'SCOUTING', title: '' });
      await loadDetail();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create task');
    } finally {
      setSaving(false);
    }
  }

  async function handleTaskStatus(taskId: string, nextStatus: string) {
    if (!campaignId) return;
    setError(null);
    try {
      await updateDiscoveryCampaignTask(campaignId, taskId, { status: nextStatus as any });
      await loadDetail();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update task');
    }
  }

  const sortedIdeas = useMemo(() => {
    return [...(detail?.ideas || [])].sort((a, b) => (b.opportunity_score || 0) - (a.opportunity_score || 0));
  }, [detail?.ideas]);

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <RefreshCw className="h-6 w-6 animate-spin text-indigo-400" />
      </div>
    );
  }

  if (!detail) {
    return (
      <div className="p-6 text-zinc-300">
        <div className="rounded-2xl border border-red-500/20 bg-red-500/10 p-4">Campaign not found.</div>
      </div>
    );
  }

  const { campaign, report } = detail;

  return (
    <div className="p-6">
      <div className="mx-auto max-w-[1440px] space-y-6">
        <header className="rounded-[28px] border border-zinc-800 bg-[radial-gradient(circle_at_top_left,_rgba(79,70,229,0.22),_transparent_28%),linear-gradient(180deg,rgba(9,9,11,0.96),rgba(17,17,17,0.96))] p-6 shadow-2xl shadow-black/20">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div>
              <div className="flex items-center gap-2">
                <Sparkles className="h-5 w-5 text-indigo-400" />
                <h1 className="text-3xl font-semibold tracking-tight text-white">{campaign.name}</h1>
              </div>
              <p className="mt-2 text-sm text-zinc-400">
                {campaign.category || 'Uncategorized'} · {campaign.status}
              </p>
              <p className="mt-2 max-w-4xl text-sm text-zinc-300">{campaign.goal || 'No goal recorded.'}</p>
            </div>
            <div className="flex flex-wrap gap-3 text-xs text-zinc-300">
              <Pill label={`Budget ${money(campaign.budget_limit_usd)}`} />
              <Pill label={`Spend ${money(campaign.dataforseo_spend_estimate)}`} />
              <Pill label={`Ideas ${campaign.idea_count ?? 0}`} />
              <Pill label={`Promoted ${campaign.promoted_product_count ?? 0}`} />
              <Pill label={`Report ${campaign.report_generated_at ? 'ready' : 'missing'}`} />
            </div>
          </div>
          <div className="mt-4 flex flex-wrap gap-3">
            <Link href="/discovery/campaigns" className="rounded-xl border border-zinc-700 bg-zinc-900 px-4 py-2 text-sm text-zinc-200 hover:border-zinc-600">
              Back to campaigns
            </Link>
            <button
              type="button"
              onClick={generateTasks}
              className="rounded-xl border border-zinc-700 bg-zinc-900 px-4 py-2 text-sm text-zinc-200 hover:border-zinc-600"
            >
              Generate next tasks
            </button>
            <button
              type="button"
              onClick={refreshReport}
              className="rounded-xl border border-indigo-500/30 bg-indigo-500/10 px-4 py-2 text-sm text-indigo-200 hover:bg-indigo-500/20"
            >
              Refresh report
            </button>
          </div>
        </header>

        {error ? (
          <div className="rounded-2xl border border-red-500/20 bg-red-500/10 p-4 text-sm text-red-100">
            {error}
          </div>
        ) : null}

        <section className="grid gap-3 md:grid-cols-4">
          <Metric label="Total ideas" value={String(report.total_ideas)} />
          <Metric label="Promising ideas" value={String(report.promising_ideas)} />
          <Metric label="Promoted products" value={String(report.promoted_products)} />
          <Metric label="DataForSEO spend" value={money(report.dataforseo_spend_estimate)} />
        </section>

        <div className="grid gap-6 xl:grid-cols-[1.05fr_0.95fr]">
          <section className="rounded-[24px] border border-zinc-800 bg-zinc-950/80 p-5 shadow-xl shadow-black/10">
            <div className="mb-4 flex items-center gap-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-xl border border-zinc-800 bg-zinc-900 text-zinc-300">
                <Target className="h-4 w-4" />
              </div>
              <h2 className="text-sm font-semibold uppercase tracking-[0.18em] text-zinc-200">Idea Funnel</h2>
            </div>
            <div className="overflow-hidden rounded-2xl border border-zinc-800">
              <table className="w-full text-left text-sm">
                <thead className="bg-zinc-950/90 text-xs uppercase tracking-[0.14em] text-zinc-500">
                  <tr>
                    <th className="px-4 py-3">Idea</th>
                    <th className="px-4 py-3">Verdict</th>
                    <th className="px-4 py-3">Opportunity</th>
                    <th className="px-4 py-3">Next Evidence</th>
                    <th className="px-4 py-3">Promoted</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-zinc-800">
                  {sortedIdeas.length ? (
                    sortedIdeas.map((idea) => (
                      <tr key={idea.id} className="bg-zinc-950/40">
                        <td className="px-4 py-3 text-white">
                          <div className="font-medium">{idea.idea_name}</div>
                          <div className="text-xs text-zinc-500">{idea.category || 'Uncategorized'}</div>
                        </td>
                        <td className="px-4 py-3 text-zinc-300">{idea.quick_scan_verdict || idea.status}</td>
                        <td className="px-4 py-3 text-zinc-300">{idea.opportunity_score || 0}</td>
                        <td className="px-4 py-3 text-zinc-400">
                          {Array.isArray(idea.required_next_evidence)
                            ? idea.required_next_evidence.join(', ')
                            : typeof idea.required_next_evidence === 'string'
                            ? idea.required_next_evidence
                            : '—'}
                        </td>
                        <td className="px-4 py-3 text-zinc-300">
                          {idea.promoted_product_id ? 'Yes' : '—'}
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td className="px-4 py-6 text-sm text-zinc-500" colSpan={5}>
                        No ideas in this campaign yet.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </section>

          <section className="rounded-[24px] border border-zinc-800 bg-zinc-950/80 p-5 shadow-xl shadow-black/10">
            <div className="mb-4 flex items-center gap-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-xl border border-zinc-800 bg-zinc-900 text-zinc-300">
                <Plus className="h-4 w-4" />
              </div>
              <h2 className="text-sm font-semibold uppercase tracking-[0.18em] text-zinc-200">Campaign Controls</h2>
            </div>

            <div className="space-y-4">
              <div className="rounded-2xl border border-zinc-800 bg-zinc-950/60 p-4">
                <label className="block space-y-1">
                  <div className="text-xs uppercase tracking-[0.16em] text-zinc-500">Status</div>
                  <select
                    value={status}
                    onChange={(event) => setStatus(event.target.value)}
                    className="w-full rounded-xl border border-zinc-800 bg-zinc-950/80 px-3 py-2 text-sm text-white outline-none transition focus:border-indigo-500/50"
                  >
                    <option value="DRAFT">DRAFT</option>
                    <option value="RUNNING">RUNNING</option>
                    <option value="PAUSED">PAUSED</option>
                    <option value="COMPLETED">COMPLETED</option>
                  </select>
                </label>
                <button
                  type="button"
                  onClick={saveStatus}
                  disabled={saving}
                  className="mt-3 rounded-xl border border-zinc-700 bg-zinc-900 px-4 py-2 text-sm text-zinc-200 hover:border-zinc-600 disabled:opacity-60"
                >
                  Save status
                </button>
              </div>

              <div className="rounded-2xl border border-zinc-800 bg-zinc-950/60 p-4">
                <div className="mb-2 text-sm font-medium text-white">Add idea to campaign</div>
                <div className="space-y-2">
                  <Field label="Idea name" value={ideaForm.idea_name} onChange={(value) => setIdeaForm((current) => ({ ...current, idea_name: value }))} />
                  <Field label="Category" value={ideaForm.category || ''} onChange={(value) => setIdeaForm((current) => ({ ...current, category: value }))} />
                  <Field label="Source platform" value={ideaForm.source_platform || ''} onChange={(value) => setIdeaForm((current) => ({ ...current, source_platform: value }))} />
                  <Textarea label="Why interesting" value={ideaForm.why_interesting || ''} onChange={(value) => setIdeaForm((current) => ({ ...current, why_interesting: value }))} />
                </div>
                <button
                  type="button"
                  onClick={handleAddIdea}
                  disabled={saving || !ideaForm.idea_name.trim()}
                  className="mt-3 rounded-xl border border-indigo-500/30 bg-indigo-500/10 px-4 py-2 text-sm text-indigo-200 hover:bg-indigo-500/20 disabled:opacity-60"
                >
                  Add idea
                </button>
              </div>

              <div className="rounded-2xl border border-zinc-800 bg-zinc-950/60 p-4">
                <div className="mb-2 text-sm font-medium text-white">Create campaign task</div>
                <div className="space-y-2">
                  <Field label="Task type" value={taskForm.task_type} onChange={(value) => setTaskForm((current) => ({ ...current, task_type: value }))} />
                  <Field label="Task title" value={taskForm.title} onChange={(value) => setTaskForm((current) => ({ ...current, title: value }))} />
                  <Textarea label="Description" value={taskForm.description || ''} onChange={(value) => setTaskForm((current) => ({ ...current, description: value }))} />
                </div>
                <button
                  type="button"
                  onClick={handleCreateTask}
                  disabled={saving || !taskForm.title.trim()}
                  className="mt-3 rounded-xl border border-zinc-700 bg-zinc-900 px-4 py-2 text-sm text-zinc-200 hover:border-zinc-600 disabled:opacity-60"
                >
                  Create task
                </button>
              </div>
            </div>
          </section>
        </div>

        <section className="rounded-[24px] border border-zinc-800 bg-zinc-950/80 p-5 shadow-xl shadow-black/10">
          <div className="mb-4 flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-xl border border-zinc-800 bg-zinc-900 text-zinc-300">
              <Sparkles className="h-4 w-4" />
            </div>
            <h2 className="text-sm font-semibold uppercase tracking-[0.18em] text-zinc-200">Task Queue</h2>
          </div>
          <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
            {detail.tasks.length ? (
              detail.tasks.map((task) => (
                <div key={task.id} className="rounded-2xl border border-zinc-800 bg-zinc-950/60 p-4">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <div className="text-sm font-medium text-white">{task.title}</div>
                      <div className="text-[11px] uppercase tracking-[0.14em] text-zinc-500">{task.task_type}</div>
                    </div>
                    <span className="rounded-full border border-zinc-800 bg-zinc-900 px-2 py-0.5 text-[10px] uppercase tracking-[0.16em] text-zinc-300">
                      {task.status}
                    </span>
                  </div>
                  <p className="mt-2 text-sm text-zinc-300">{task.description || 'No description.'}</p>
                  <div className="mt-3 flex flex-wrap gap-2">
                    {['TODO', 'IN_PROGRESS', 'DONE', 'BLOCKED', 'SKIPPED'].map((nextStatus) => (
                      <button
                        key={nextStatus}
                        type="button"
                        onClick={() => handleTaskStatus(task.id, nextStatus)}
                        className="rounded-lg border border-zinc-700 bg-zinc-900 px-2.5 py-1 text-xs text-zinc-300 hover:border-zinc-600"
                      >
                        {nextStatus}
                      </button>
                    ))}
                  </div>
                  {task.error_message ? (
                    <div className="mt-2 text-xs text-red-300">{task.error_message}</div>
                  ) : null}
                </div>
              ))
            ) : (
              <EmptyState title="No campaign tasks yet" description="Generate next tasks or create one manually." />
            )}
          </div>
        </section>

        <div className="grid gap-6 xl:grid-cols-2">
          <section className="rounded-[24px] border border-zinc-800 bg-zinc-950/80 p-5 shadow-xl shadow-black/10">
            <div className="mb-4 flex items-center gap-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-xl border border-zinc-800 bg-zinc-900 text-zinc-300">
                <Sparkles className="h-4 w-4" />
              </div>
              <h2 className="text-sm font-semibold uppercase tracking-[0.18em] text-zinc-200">Top Ideas</h2>
            </div>
            <div className="space-y-3">
              {report.top_ranked_ideas.length ? (
                report.top_ranked_ideas.map((idea) => (
                  <div key={String(idea.id)} className="rounded-2xl border border-zinc-800 bg-zinc-950/60 p-4">
                    <div className="flex flex-wrap items-start justify-between gap-3">
                      <div>
                        <div className="text-sm font-medium text-white">{idea.idea_name}</div>
                        <div className="text-xs text-zinc-500">{idea.category || 'Uncategorized'}</div>
                      </div>
                      <div className="text-xs text-zinc-400">
                        Score {idea.opportunity_score} · {idea.quick_scan_verdict || idea.status}
                      </div>
                    </div>
                    <div className="mt-2 text-sm text-zinc-300">
                      {Array.isArray(idea.required_next_evidence)
                        ? idea.required_next_evidence.join(', ')
                        : typeof idea.required_next_evidence === 'string'
                        ? idea.required_next_evidence
                        : 'No next evidence recorded.'}
                    </div>
                  </div>
                ))
              ) : (
                <EmptyState title="No ranked ideas yet" description="Generate the campaign report to populate rankings." />
              )}
            </div>
          </section>

          <section className="rounded-[24px] border border-zinc-800 bg-zinc-950/80 p-5 shadow-xl shadow-black/10">
            <div className="mb-4 flex items-center gap-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-xl border border-zinc-800 bg-zinc-900 text-zinc-300">
                <Target className="h-4 w-4" />
              </div>
              <h2 className="text-sm font-semibold uppercase tracking-[0.18em] text-zinc-200">Top Products</h2>
            </div>
            <div className="space-y-3">
              {report.top_products.length ? (
                report.top_products.map((product) => (
                  <Link
                    key={product.id}
                    href={`/products/${product.id}`}
                    className="block rounded-2xl border border-zinc-800 bg-zinc-950/60 p-4 transition hover:border-zinc-700 hover:bg-zinc-900/40"
                  >
                    <div className="flex flex-wrap items-start justify-between gap-3">
                      <div>
                        <div className="text-sm font-medium text-white">{product.name}</div>
                        <div className="text-xs text-zinc-500">{product.category || 'Uncategorized'} · {product.status}</div>
                      </div>
                      <div className="text-xs text-zinc-400">
                        {product.research_verdict || '—'} · {product.buy_readiness_status || 'NOT_READY'}
                      </div>
                    </div>
                    <div className="mt-2 text-sm text-zinc-300">{product.next_action || product.main_blocker || 'No next action recorded.'}</div>
                  </Link>
                ))
              ) : (
                <EmptyState title="No promoted products yet" description="Promote the strongest idea when it is ready." />
              )}
            </div>
          </section>
        </div>

        <section className="rounded-[24px] border border-zinc-800 bg-zinc-950/80 p-5 shadow-xl shadow-black/10">
          <div className="mb-4 flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-xl border border-zinc-800 bg-zinc-900 text-zinc-300">
              <Sparkles className="h-4 w-4" />
            </div>
            <h2 className="text-sm font-semibold uppercase tracking-[0.18em] text-zinc-200">Next Actions</h2>
          </div>
          <div className="space-y-2">
            {report.next_actions.length ? (
              report.next_actions.map((action) => (
                <div key={action} className="rounded-xl border border-zinc-800 bg-zinc-950/60 px-4 py-3 text-sm text-zinc-300">
                  {action}
                </div>
              ))
            ) : (
              <EmptyState title="No next actions" description="Generate a report to produce next steps." />
            )}
          </div>
        </section>

        <section className="rounded-[24px] border border-zinc-800 bg-zinc-950/80 p-5 shadow-xl shadow-black/10">
          <div className="mb-4 flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-xl border border-zinc-800 bg-zinc-900 text-zinc-300">
              <Sparkles className="h-4 w-4" />
            </div>
            <h2 className="text-sm font-semibold uppercase tracking-[0.18em] text-zinc-200">Evidence Candidates</h2>
          </div>
          <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
            {detail.evidence_candidates.length ? (
              detail.evidence_candidates.map((candidate) => (
                <div key={candidate.id} className="rounded-2xl border border-zinc-800 bg-zinc-950/60 p-4">
                  <div className="text-sm font-medium text-white">{candidate.title || 'Untitled candidate'}</div>
                  <div className="text-xs uppercase tracking-[0.14em] text-zinc-500">
                    {candidate.source} · {candidate.marketplace || 'Unknown'} · {candidate.review_status}
                  </div>
                  <div className="mt-2 text-sm text-zinc-300">
                    {candidate.evidence_type || '—'} · {candidate.price != null ? money(candidate.price) : 'No price'}
                  </div>
                </div>
              ))
            ) : (
              <EmptyState title="No evidence candidates" description="Use external research or capture to populate this queue." />
            )}
          </div>
        </section>
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

function Textarea(props: { label: string; value: string; onChange: (value: string) => void; rows?: number }) {
  return (
    <label className="block">
      <div className="mb-1 text-xs uppercase tracking-[0.16em] text-zinc-500">{props.label}</div>
      <textarea
        value={props.value}
        onChange={(event) => props.onChange(event.target.value)}
        rows={props.rows ?? 3}
        className="w-full rounded-xl border border-zinc-800 bg-zinc-950/80 px-3 py-2 text-sm text-white outline-none transition focus:border-indigo-500/50"
      />
    </label>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-zinc-800 bg-zinc-950/80 p-4">
      <div className="text-[10px] uppercase tracking-[0.14em] text-zinc-500">{label}</div>
      <div className="mt-2 text-2xl font-semibold text-white">{value}</div>
    </div>
  );
}

function Pill({ label }: { label: string }) {
  return <span className="rounded-full border border-zinc-800 bg-zinc-900 px-3 py-1">{label}</span>;
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
