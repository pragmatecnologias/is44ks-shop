'use client';

import { useEffect, useState, type ReactNode } from 'react';
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
  Upload,
  Search,
} from 'lucide-react';
import {
  approveEvidenceCandidate,
  captureManualEvidence,
  archiveDiscoveryIdea,
  createDiscoveryIdea,
  deleteDiscoveryIdea,
  getOpportunityBoard,
  getProductCockpit,
  generateDiscoveryTasks,
  listDiscoveryIdeas,
  listEvidenceCandidates,
  listExternalResearchJobs,
  promoteDiscoveryIdea,
  runOpportunityScout,
  pollExternalResearchJob,
  quickScanDiscoveryIdea,
  rejectEvidenceCandidate,
  runExternalResearchGoogleShopping,
  updateDiscoveryTask,
} from '@/lib/api';
import type {
  CaptureType,
  DiscoveryIdea,
  DiscoveryQuickScanInput,
  EvidenceCandidate,
  ExternalResearchJob,
  ManualCaptureInput,
  OpportunityBoardRow,
  ResearchCockpit,
} from '@/lib/types';
import { SCOUT_STATUS_COLORS, SCOUT_STATUS_LABELS } from '@/lib/types';

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
  const [externalJobs, setExternalJobs] = useState<ExternalResearchJob[]>([]);
  const [evidenceCandidates, setEvidenceCandidates] = useState<EvidenceCandidate[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [scanning, setScanning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState<DiscoveryQuickScanInput>(emptyQuickScan);
  const [externalResearchIdea, setExternalResearchIdea] = useState<DiscoveryIdea | null>(null);
  const [externalQueryText, setExternalQueryText] = useState('');
  const [externalSubmitting, setExternalSubmitting] = useState(false);
  const [captureIdea, setCaptureIdea] = useState<DiscoveryIdea | null>(null);
  const [captureType, setCaptureType] = useState<CaptureType>('MARKETPLACE_SCREENSHOT');
  const [captureUrl, setCaptureUrl] = useState('');
  const [captureText, setCaptureText] = useState('');
  const [captureNotes, setCaptureNotes] = useState('');
  const [captureFile, setCaptureFile] = useState<File | null>(null);
  const [captureSubmitting, setCaptureSubmitting] = useState(false);
  const [candidateTaskLinks, setCandidateTaskLinks] = useState<Record<string, string>>({});
  const [scoutingIdeaId, setScoutingIdeaId] = useState<string | null>(null);

  async function loadIdeas() {
    setLoading(true);
    setError(null);
    try {
      const [ideaList, boardRows, jobs, candidates] = await Promise.all([
        listDiscoveryIdeas(),
        getOpportunityBoard(),
        listExternalResearchJobs(),
        listEvidenceCandidates(),
      ]);
      setIdeas(ideaList);
      setBoard(boardRows);
      setExternalJobs(jobs);
      setEvidenceCandidates(candidates);
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

  async function handleOpportunityScout(ideaId: string) {
    setScoutingIdeaId(ideaId);
    setError(null);
    try {
      await runOpportunityScout(ideaId);
      await loadIdeas();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Opportunity scout failed');
    } finally {
      setScoutingIdeaId(null);
    }
  }

  async function handleRunExternalResearch() {
    if (!externalResearchIdea) return;
    setExternalSubmitting(true);
    setError(null);
    try {
      const queries = externalQueryText
        .split('\n')
        .map((value) => value.trim())
        .filter(Boolean);
      await runExternalResearchGoogleShopping({
        idea_id: externalResearchIdea.id,
        queries,
        max_results: 20,
        queue: 'standard',
      });
      setExternalResearchIdea(null);
      setExternalQueryText('');
      await loadIdeas();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'External research failed');
    } finally {
      setExternalSubmitting(false);
    }
  }

  async function handlePollJob(jobId: string) {
    setError(null);
    try {
      await pollExternalResearchJob(jobId);
      await loadIdeas();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not poll external research job');
    }
  }

  async function handleApproveCandidate(candidateId: string, approveAs: 'MARKETPLACE_EVIDENCE' | 'COMPETITOR_LISTING' | 'SUPPLIER_SOURCE') {
    setError(null);
    try {
      await approveEvidenceCandidate(candidateId, {
        approve_as: approveAs,
        task_id: candidateTaskLinks[candidateId] || undefined,
      });
      await loadIdeas();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not approve candidate');
    }
  }

  async function handleRejectCandidate(candidateId: string) {
    setError(null);
    try {
      await rejectEvidenceCandidate(candidateId, {});
      await loadIdeas();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not reject candidate');
    }
  }

  async function handleCaptureManual() {
    if (!captureIdea) return;
    setCaptureSubmitting(true);
    setError(null);
    try {
      const payload: ManualCaptureInput = {
        idea_id: captureIdea.id,
        product_id: captureIdea.promoted_product_id || undefined,
        capture_type: captureType,
        url: captureUrl || undefined,
        pasted_text: captureText || undefined,
        notes: captureNotes || undefined,
        screenshot: captureFile,
      };
      await captureManualEvidence(payload);
      setCaptureIdea(null);
      setCaptureType('MARKETPLACE_SCREENSHOT');
      setCaptureUrl('');
      setCaptureText('');
      setCaptureNotes('');
      setCaptureFile(null);
      await loadIdeas();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Manual capture failed');
    } finally {
      setCaptureSubmitting(false);
    }
  }

  const readyCount = ideas.filter((idea) => idea.quick_scan_verdict === 'PROMISING_FOR_RESEARCH').length;
  const marketCheckCount = ideas.filter((idea) => idea.quick_scan_verdict === 'NEEDS_MARKET_CHECK').length;
  const supplierCheckCount = ideas.filter((idea) => idea.quick_scan_verdict === 'NEEDS_SUPPLIER_CHECK').length;
  const shortlistCount = ideas.filter((idea) => idea.scout_status === 'SHORTLIST').length;
  const needsSoldProofCount = ideas.filter((idea) => idea.scout_status === 'NEEDS_SOLD_PROOF').length;
  const watchScoutCount = ideas.filter((idea) => idea.scout_status === 'WATCH').length;
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
              <Pill label={`Promising for research: ${readyCount}`} />
              <Pill label={`Need market check: ${marketCheckCount}`} />
              <Pill label={`Need supplier check: ${supplierCheckCount}`} />
              <Pill label={`Scout shortlist: ${shortlistCount}`} />
              <Pill label={`Need sold proof: ${needsSoldProofCount}`} />
              <Pill label={`Scout watch: ${watchScoutCount}`} />
              <Pill label={`Promoted: ${promotedCount}`} />
              <Pill label={`Jobs: ${externalJobs.length}`} />
              <Pill label={`Candidates: ${evidenceCandidates.length}`} />
              <Link href="/discovery/campaigns" className="rounded-full border border-indigo-500/30 bg-indigo-500/10 px-3 py-1 text-indigo-200 hover:bg-indigo-500/20">
                Campaigns
              </Link>
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
                  isScouting={scoutingIdeaId === idea.id}
                  onPromote={() => handlePromoteIdea(idea.id)}
                  onDelete={() => handleDeleteIdea(idea.id)}
                  onGenerateTasks={() => handleGenerateTasks(idea.id)}
                  onArchive={() => handleArchiveIdea(idea.id)}
                  onRunScout={() => handleOpportunityScout(idea.id)}
                  onRunExternalResearch={() => {
                    setExternalResearchIdea(idea);
                    setExternalQueryText(buildExternalResearchQueries(idea).join('\n'));
                  }}
                  onCaptureManual={() => {
                    setCaptureIdea(idea);
                    setCaptureType('MARKETPLACE_SCREENSHOT');
                    setCaptureUrl(idea.source_url || '');
                    setCaptureText('');
                    setCaptureNotes(idea.notes || '');
                    setCaptureFile(null);
                  }}
                  onUpdateTask={async (taskId, status, notes, linkData) => {
                    setError(null);
                    try {
                      await updateDiscoveryTask(taskId, { status, notes, ...linkData });
                      await loadIdeas();
                    } catch (err) {
                      setError(err instanceof Error ? err.message : 'Could not update task');
                    }
                  }}
                />
              ))
            )}
          </div>
        </section>

        <section className="rounded-[24px] border border-zinc-800 bg-zinc-950/80 p-5 shadow-xl shadow-black/10">
          <div className="mb-4 flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-xl border border-zinc-800 bg-zinc-900 text-zinc-300">
              <Search className="h-4 w-4" />
            </div>
            <h2 className="text-sm font-semibold uppercase tracking-[0.18em] text-zinc-200">External Research</h2>
          </div>
          <div className="grid gap-4 xl:grid-cols-2">
            <div className="rounded-2xl border border-zinc-800 bg-zinc-950/60 p-4">
              <div className="flex items-center justify-between gap-4">
                <div>
                  <div className="font-medium text-white">DataForSEO jobs</div>
                  <div className="text-xs text-zinc-500">Google Shopping active listings only. Standard queue. Human review required.</div>
                </div>
                <span className="rounded-full border border-zinc-800 bg-zinc-900 px-2 py-0.5 text-[10px] uppercase tracking-[0.16em] text-zinc-300">
                  {externalJobs.length} jobs
                </span>
              </div>
              <div className="mt-4 space-y-3">
                {externalJobs.length ? (
                  externalJobs.map((job) => (
                    <div key={job.id} className="rounded-xl border border-zinc-800 bg-zinc-950/80 p-3">
                      <div className="flex flex-wrap items-start justify-between gap-3">
                        <div>
                          <div className="text-sm font-medium text-white">{job.query}</div>
                          <div className="text-[11px] uppercase tracking-[0.14em] text-zinc-500">
                            {job.status} · {job.queue} · {job.provider}
                          </div>
                        </div>
                        <div className="text-right text-xs text-zinc-400">
                          <div>{money(job.cost_estimate)}</div>
                          <div>{job.result_count ?? 0} results</div>
                        </div>
                      </div>
                      <div className="mt-3 flex flex-wrap gap-2">
                        <button
                          type="button"
                          onClick={() => handlePollJob(job.id)}
                          className="rounded-lg border border-zinc-700 bg-zinc-900 px-3 py-1.5 text-xs text-zinc-300 hover:border-zinc-600"
                        >
                          Poll
                        </button>
                      </div>
                    </div>
                  ))
                ) : (
                  <EmptyState title="No jobs yet" description="Run external research from an idea card to create DataForSEO jobs." />
                )}
              </div>
            </div>

            <div className="rounded-2xl border border-zinc-800 bg-zinc-950/60 p-4">
              <div className="flex items-center justify-between gap-4">
                <div>
                  <div className="font-medium text-white">Evidence candidates</div>
                  <div className="text-xs text-zinc-500">Review and approve candidate rows before they become evidence.</div>
                </div>
                <span className="rounded-full border border-zinc-800 bg-zinc-900 px-2 py-0.5 text-[10px] uppercase tracking-[0.16em] text-zinc-300">
                  {evidenceCandidates.length} candidates
                </span>
              </div>
              <div className="mt-4 space-y-3">
                {evidenceCandidates.length ? (
                  evidenceCandidates.map((candidate) => (
                    <EvidenceCandidateCard
                      key={candidate.id}
                      candidate={candidate}
                      idea={ideas.find((idea) => idea.id === candidate.idea_id) || null}
                      taskLink={candidateTaskLinks[candidate.id] || ''}
                      onTaskLinkChange={(value) => setCandidateTaskLinks((current) => ({ ...current, [candidate.id]: value }))}
                      onApprove={handleApproveCandidate}
                      onReject={handleRejectCandidate}
                    />
                  ))
                ) : (
                  <EmptyState title="No candidates yet" description="Poll a job or use manual capture to generate review items." />
                )}
              </div>
            </div>
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
                  <th className="px-4 py-3">Progress</th>
                  <th className="px-4 py-3">Evidence</th>
                  <th className="px-4 py-3">Market</th>
                  <th className="px-4 py-3">Best Cost</th>
                  <th className="px-4 py-3">Verdict</th>
                  <th className="px-4 py-3">Scout</th>
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
                    <td className="px-4 py-3 text-zinc-300">
                      <div className="font-medium">
                        {row.entity_type === 'idea'
                          ? `${row.discovery_completeness_score ?? row.research_completeness_score}%`
                          : `${row.research_completeness_score}%`}
                      </div>
                      <div className="text-xs text-zinc-500">
                        {row.entity_type === 'idea' ? 'Discovery completeness' : 'Research completeness'}
                      </div>
                    </td>
                    <td className="px-4 py-3 text-zinc-300">
                      {row.entity_type === 'product' ? (
                        <div>
                          <div>{row.sold_evidence_count_verified ?? row.sold_evidence_count} sold / {row.active_evidence_count_verified ?? row.active_evidence_count} active verified</div>
                          {(row.sold_evidence_count !== row.sold_evidence_count_verified || row.active_evidence_count !== row.active_evidence_count_verified) ? (
                            <div className="text-xs text-zinc-500">{row.sold_evidence_count} sold / {row.active_evidence_count} active total</div>
                          ) : null}
                          {(row.test_data_count ?? 0) > 0 ? (
                            <div className="text-xs text-red-400">{row.test_data_count} test data</div>
                          ) : null}
                        </div>
                      ) : (
                        <div>0 sold / 0 active</div>
                      )}
                    </td>
                    <td className="px-4 py-3 text-zinc-300">
                      {row.median_sold_price != null ? money(row.median_sold_price) : '—'}
                      {(row.median_sold_price_total != null && row.median_sold_price != null && row.median_sold_price_total !== row.median_sold_price) ? (
                        <div className="text-xs text-zinc-500">total: {money(row.median_sold_price_total)}</div>
                      ) : null}
                    </td>
                    <td className="px-4 py-3 text-zinc-300">
                      {money(row.best_landed_cost)}
                    </td>
                    <td className="px-4 py-3 text-zinc-300">{row.research_verdict || row.status || '—'}</td>
                    <td className="px-4 py-3 text-zinc-300">
                      {row.scout_status ? `${scoutLabel(row.scout_status)}${row.scout_score != null ? ` · ${row.scout_score}` : ''}` : '—'}
                    </td>
                    <td className="px-4 py-3 text-zinc-400">{row.next_action || '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        {externalResearchIdea ? (
          <Modal title="Run External Research" onClose={() => setExternalResearchIdea(null)}>
            <div className="space-y-4 text-sm text-zinc-300">
              <div className="rounded-2xl border border-zinc-800 bg-zinc-950/70 p-4">
                <div className="font-medium text-white">{externalResearchIdea.idea_name}</div>
                <div className="mt-1 text-xs text-zinc-500">
                  DataForSEO Merchant / Google Shopping · Standard queue · Active listings only
                </div>
              </div>

              <label className="block space-y-1">
                <div className="text-xs uppercase tracking-[0.16em] text-zinc-500">Queries</div>
                <textarea
                  value={externalQueryText}
                  onChange={(event) => setExternalQueryText(event.target.value)}
                  rows={5}
                  className="w-full rounded-xl border border-zinc-800 bg-zinc-950/80 px-3 py-2 text-sm text-white outline-none transition focus:border-indigo-500/50"
                />
              </label>

              <div className="rounded-2xl border border-zinc-800 bg-zinc-950/70 p-4 text-sm text-zinc-300">
                <div className="flex items-center justify-between gap-4">
                  <span>Estimated cost</span>
                  <span className="text-white">{money((externalQueryText.split('\n').map((value) => value.trim()).filter(Boolean).length || 0) * 20 * 0.001)}</span>
                </div>
                <div className="mt-1 text-xs text-zinc-500">Standard queue only. Manual review required before any candidate becomes evidence.</div>
              </div>

              <div className="flex justify-end gap-3">
                <button
                  type="button"
                  onClick={() => setExternalResearchIdea(null)}
                  className="rounded-lg border border-zinc-700 bg-zinc-900 px-4 py-2 text-sm text-zinc-300 hover:border-zinc-600"
                >
                  Cancel
                </button>
                <button
                  type="button"
                  onClick={handleRunExternalResearch}
                  disabled={
                    externalSubmitting ||
                    externalQueryText
                      .split('\n')
                      .map((value) => value.trim())
                      .filter(Boolean).length === 0
                  }
                  className="rounded-lg border border-cyan-500/20 bg-cyan-500/10 px-4 py-2 text-sm text-cyan-300 hover:bg-cyan-500/20 disabled:opacity-60"
                >
                  {externalSubmitting ? 'Submitting...' : 'Run Research'}
                </button>
              </div>
            </div>
          </Modal>
        ) : null}

        {captureIdea ? (
          <Modal title="Manual Capture" onClose={() => setCaptureIdea(null)}>
            <div className="space-y-4 text-sm text-zinc-300">
              <div className="rounded-2xl border border-zinc-800 bg-zinc-950/70 p-4">
                <div className="font-medium text-white">{captureIdea.idea_name}</div>
                <div className="mt-1 text-xs text-zinc-500">
                  Screenshot or pasted text becomes a review-only candidate. Nothing is saved as evidence until you approve it.
                </div>
              </div>

              <label className="block space-y-1">
                <div className="text-xs uppercase tracking-[0.16em] text-zinc-500">Capture type</div>
                <select
                  value={captureType}
                  onChange={(event) => setCaptureType(event.target.value as CaptureType)}
                  className="w-full rounded-xl border border-zinc-800 bg-zinc-950/80 px-3 py-2 text-sm text-white outline-none transition focus:border-indigo-500/50"
                >
                  <option value="MARKETPLACE_SCREENSHOT">Marketplace screenshot</option>
                  <option value="SUPPLIER_SCREENSHOT">Supplier screenshot</option>
                  <option value="COMPETITOR_SCREENSHOT">Competitor screenshot</option>
                  <option value="VISUAL_RISK">Visual risk</option>
                </select>
              </label>

              <div className="grid gap-3 md:grid-cols-2">
                <Input label="URL" value={captureUrl} onChange={setCaptureUrl} />
                <label className="space-y-1">
                  <div className="text-xs uppercase tracking-[0.16em] text-zinc-500">Screenshot</div>
                  <input
                    type="file"
                    accept="image/*"
                    onChange={(event) => setCaptureFile(event.target.files?.[0] ?? null)}
                    className="w-full rounded-xl border border-zinc-800 bg-zinc-950/80 px-3 py-2 text-sm text-zinc-300 outline-none transition file:mr-3 file:rounded-lg file:border-0 file:bg-zinc-900 file:px-3 file:py-1.5 file:text-xs file:text-zinc-300"
                  />
                </label>
              </div>

              <Textarea label="Pasted text" value={captureText} onChange={setCaptureText} />
              <Textarea label="Notes" value={captureNotes} onChange={setCaptureNotes} />

              <div className="flex justify-end gap-3">
                <button
                  type="button"
                  onClick={() => setCaptureIdea(null)}
                  className="rounded-lg border border-zinc-700 bg-zinc-900 px-4 py-2 text-sm text-zinc-300 hover:border-zinc-600"
                >
                  Cancel
                </button>
                <button
                  type="button"
                  onClick={handleCaptureManual}
                  disabled={captureSubmitting || (!captureFile && !captureText.trim())}
                  className="rounded-lg border border-emerald-500/20 bg-emerald-500/10 px-4 py-2 text-sm text-emerald-300 hover:bg-emerald-500/20 disabled:opacity-60"
                >
                  {captureSubmitting ? 'Saving...' : 'Capture Candidate'}
                </button>
              </div>
            </div>
          </Modal>
        ) : null}
      </div>
    </div>
  );
}

function IdeaCard({
  idea,
  isScouting,
  onPromote,
  onDelete,
  onGenerateTasks,
  onArchive,
  onRunScout,
  onRunExternalResearch,
  onCaptureManual,
  onUpdateTask,
}: {
  idea: DiscoveryIdea;
  isScouting: boolean;
  onPromote: () => void;
  onDelete: () => void;
  onGenerateTasks: () => void;
  onArchive: () => void;
  onRunScout: () => void;
  onRunExternalResearch: () => void;
  onCaptureManual: () => void;
  onUpdateTask: (
    taskId: string,
    status?: string,
    notes?: string,
    linkData?: {
      linked_evidence_id?: string | null;
      linked_source_id?: string | null;
      linked_competitor_id?: string | null;
      linked_product_id?: string | null;
    },
  ) => void;
}) {
  const [draftNotes, setDraftNotes] = useState<Record<string, string>>({});
  const [draftLinks, setDraftLinks] = useState<Record<string, string>>({});
  const [linkedContext, setLinkedContext] = useState<ResearchCockpit | null>(null);
  const [attachTaskId, setAttachTaskId] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    async function loadLinkedContext() {
      if (!idea.promoted_product_id) {
        if (mounted) setLinkedContext(null);
        return;
      }
      try {
        const data = await getProductCockpit(idea.promoted_product_id);
        if (mounted) setLinkedContext(data);
      } catch {
        if (mounted) setLinkedContext(null);
      }
    }
    loadLinkedContext();
    return () => {
      mounted = false;
    };
  }, [idea.promoted_product_id]);

  const linkOptions = buildLinkOptions(linkedContext, idea.promoted_product_id);
  const attachTask = idea.tasks?.find((task) => task.id === attachTaskId) ?? null;
  const attachValue = attachTask ? draftLinks[attachTask.id] ?? taskLinkValue(attachTask) : '';
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
          <button onClick={onRunScout} disabled={isScouting} className="text-xs text-zinc-500 hover:text-emerald-400 disabled:opacity-60">
            {isScouting ? 'Scouting...' : 'Scout'}
          </button>
          <button onClick={onArchive} className="text-xs text-zinc-500 hover:text-yellow-400">
            Archive
          </button>
          <button onClick={onRunExternalResearch} className="text-xs text-zinc-500 hover:text-cyan-400">
            External Research
          </button>
          <button onClick={onCaptureManual} className="inline-flex items-center gap-1 text-xs text-zinc-500 hover:text-green-400">
            <Upload className="h-3 w-3" />
            Capture
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
        <StatRow label="Discovery completeness" value={`${idea.discovery_completeness_score ?? idea.research_completeness_score ?? 0}%`} />
        <StatRow label="Supplier cost" value={money(idea.rough_supplier_cost)} />
        <StatRow label="Landed cost" value={money(idea.estimated_landed_cost)} />
      </div>

      {idea.quick_scan_reason ? (
        <div className="mt-3 rounded-xl border border-zinc-800 bg-zinc-950/70 p-3">
          <div className="text-xs uppercase tracking-[0.16em] text-zinc-500">Quick scan reason</div>
          <div className="mt-1 text-sm text-zinc-200">{idea.quick_scan_reason}</div>
        </div>
      ) : null}

      {idea.scout_status ? (
        <div className="mt-3 rounded-xl border border-zinc-800 bg-zinc-950/70 p-3">
          <div className="text-xs uppercase tracking-[0.16em] text-zinc-500">Scout status</div>
          <div className="mt-2 flex flex-wrap items-center gap-2">
            <span className={`rounded-full border px-2 py-0.5 text-[10px] uppercase tracking-[0.16em] ${scoutBadgeClass(idea.scout_status)}`}>
              {scoutLabel(idea.scout_status)}
            </span>
            <span className="text-xs text-zinc-400">
              Score {idea.scout_score ?? '—'} · {idea.scout_confidence || '—'}
            </span>
          </div>
          <div className="mt-2 text-sm text-zinc-200">{idea.scout_reason || 'No scout reason recorded.'}</div>
          <div className="mt-1 text-xs text-zinc-400">
            {idea.scout_next_step || 'Scout status is an early opportunity signal. It does not mean this product is sample-ready.'}
          </div>
        </div>
      ) : null}

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

      <div className="mt-3 rounded-xl border border-zinc-800 bg-zinc-950/70 p-3">
        <div className="text-xs uppercase tracking-[0.16em] text-zinc-500">Suggested keywords</div>
        <div className="mt-2 space-y-2 text-xs text-zinc-300">
          {renderKeywordGroup('eBay sold', idea.suggested_keywords, 'ebay_sold')}
          {renderKeywordGroup('eBay active', idea.suggested_keywords, 'ebay_active')}
          {renderKeywordGroup('Mercari', idea.suggested_keywords, 'mercari')}
          {renderKeywordGroup('Supplier', idea.suggested_keywords, 'supplier')}
        </div>
      </div>
      <div className="mt-1 text-xs text-zinc-500">
        Risk: {(idea.risk_flags as string[] | undefined)?.join(', ') || 'None'}
      </div>

      <div className="mt-3 rounded-xl border border-zinc-800 bg-zinc-950/70 p-3">
        <div className="text-xs uppercase tracking-[0.16em] text-zinc-500">Research Tasks</div>
        <div className="mt-3 space-y-3">
          {(idea.tasks || []).length ? (
            idea.tasks!.map((task) => (
              <div key={task.id} className="rounded-xl border border-zinc-800 bg-zinc-950/80 p-3">
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div>
                    <div className="text-sm font-medium text-white">{task.title}</div>
                    <div className="text-[11px] uppercase tracking-[0.14em] text-zinc-500">{task.task_type}</div>
                  </div>
                  <span className="rounded-full border border-zinc-800 bg-zinc-900 px-2 py-0.5 text-[10px] uppercase tracking-[0.16em] text-zinc-300">
                    {task.status}
                  </span>
                </div>
                <div className="mt-2 text-xs text-zinc-400">
                  {renderTaskLinkStatus(task) === 'No evidence linked' ? (
                    <span>{renderTaskLinkStatus(task)}</span>
                  ) : (
                    <Link href={taskLinkHref(task, idea.promoted_product_id)} className="text-indigo-300 hover:text-indigo-200">
                      {renderTaskLinkStatus(task)}
                    </Link>
                  )}
                </div>
                {task.status === 'DONE' && !hasTaskLink(task) ? (
                  <div className="mt-1 text-xs text-amber-300">Done by note only — no evidence linked.</div>
                ) : null}
                <textarea
                  value={draftNotes[task.id] ?? task.notes ?? ''}
                  onChange={(event) => setDraftNotes((current) => ({ ...current, [task.id]: event.target.value }))}
                  placeholder="Add a note..."
                  rows={2}
                  className="mt-3 w-full rounded-xl border border-zinc-800 bg-zinc-950/80 px-3 py-2 text-sm text-white outline-none transition focus:border-indigo-500/50"
                />
                <div className="mt-3 rounded-xl border border-zinc-800 bg-zinc-950/80 p-3">
                  <div className="text-[11px] uppercase tracking-[0.14em] text-zinc-500">Proof</div>
                  <div className="mt-2 text-sm text-zinc-300">{renderTaskLinkStatus(task)}</div>
                  <div className="mt-1 text-[11px] text-zinc-500">
                    {hasTaskLink(task) ? 'Strong proof attached.' : 'Proof is optional, but linking real evidence makes the task auditable.'}
                  </div>
                </div>
                <div className="mt-3 flex flex-wrap gap-2">
                  <button
                    type="button"
                    onClick={() => onUpdateTask(task.id, task.status, draftNotes[task.id] ?? task.notes ?? '')}
                    className="rounded-lg border border-zinc-700 bg-zinc-900 px-3 py-1.5 text-xs text-zinc-300 hover:border-zinc-600"
                  >
                    Save note
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setAttachTaskId(task.id);
                      if (!draftLinks[task.id] && task.status !== 'TODO') {
                        setDraftLinks((current) => ({ ...current, [task.id]: taskLinkValue(task) }));
                      }
                    }}
                    className="rounded-lg border border-indigo-500/20 bg-indigo-500/10 px-3 py-1.5 text-xs text-indigo-300 hover:bg-indigo-500/20"
                  >
                    Attach proof
                  </button>
                  <button
                    type="button"
                    onClick={() =>
                      onUpdateTask(
                        task.id,
                          'DONE',
                          draftNotes[task.id] ?? task.notes ?? '',
                          taskLinkPayload(draftLinks[task.id] ?? taskLinkValue(task)),
                        )
                      }
                      className="rounded-lg border border-emerald-500/20 bg-emerald-500/10 px-3 py-1.5 text-xs text-emerald-300 hover:bg-emerald-500/20"
                    >
                      Mark done
                    </button>
                    <button
                      type="button"
                      onClick={() =>
                        onUpdateTask(
                          task.id,
                          'SKIPPED',
                          draftNotes[task.id] ?? task.notes ?? '',
                          taskLinkPayload(draftLinks[task.id] ?? taskLinkValue(task)),
                        )
                      }
                      className="rounded-lg border border-zinc-700 bg-zinc-900 px-3 py-1.5 text-xs text-zinc-300 hover:border-zinc-600"
                    >
                      Skip
                    </button>
                    <button
                      type="button"
                      onClick={() =>
                        onUpdateTask(
                          task.id,
                          'BLOCKED',
                          draftNotes[task.id] ?? task.notes ?? '',
                          taskLinkPayload(draftLinks[task.id] ?? taskLinkValue(task)),
                      )
                    }
                    className="rounded-lg border border-red-500/20 bg-red-500/10 px-3 py-1.5 text-xs text-red-300 hover:bg-red-500/20"
                  >
                    Block
                  </button>
                </div>
              </div>
            ))
          ) : (
            <div className="text-sm text-zinc-500">No tasks yet. Generate tasks to start collecting evidence.</div>
          )}
        </div>
      </div>

      {attachTask ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 px-4 py-8">
          <div className="max-h-[88vh] w-full max-w-2xl overflow-auto rounded-[24px] border border-zinc-800 bg-zinc-950 p-5 shadow-2xl shadow-black/40">
            <div className="flex items-start justify-between gap-4">
              <div>
                <div className="text-xs uppercase tracking-[0.16em] text-zinc-500">Attach proof</div>
                <h3 className="mt-1 text-xl font-semibold text-white">{attachTask.title}</h3>
              </div>
              <button
                type="button"
                onClick={() => setAttachTaskId(null)}
                className="rounded-lg border border-zinc-700 bg-zinc-900 px-3 py-1.5 text-xs text-zinc-300 hover:border-zinc-600"
              >
                Close
              </button>
            </div>

            <div className="mt-4 rounded-2xl border border-zinc-800 bg-zinc-950/70 p-4 text-sm text-zinc-300">
              {idea.promoted_product_id ? (
                <>
                  <div className="font-medium text-white">Choose one proof target</div>
                  <div className="mt-1 text-xs text-zinc-500">
                    Pick one marketplace evidence row, supplier source, competitor listing, or the promoted product itself.
                  </div>
                  <div className="mt-4 space-y-4">
                    <label className="block space-y-1">
                      <div className="text-xs uppercase tracking-[0.16em] text-zinc-500">Proof target</div>
                      <select
                        value={attachValue}
                        onChange={(event) => setDraftLinks((current) => ({ ...current, [attachTask.id]: event.target.value }))}
                        className="w-full rounded-xl border border-zinc-800 bg-zinc-950 px-3 py-2 text-sm text-white outline-none transition focus:border-indigo-500/50"
                      >
                        <option value="">No link selected</option>
                        {linkOptions.marketplaceEvidence.length ? (
                          <optgroup label="Marketplace evidence">
                            {linkOptions.marketplaceEvidence.map((option) => (
                              <option key={option.value} value={option.value}>
                                {option.label}
                              </option>
                            ))}
                          </optgroup>
                        ) : null}
                        {linkOptions.sources.length ? (
                          <optgroup label="Supplier sources">
                            {linkOptions.sources.map((option) => (
                              <option key={option.value} value={option.value}>
                                {option.label}
                              </option>
                            ))}
                          </optgroup>
                        ) : null}
                        {linkOptions.competitors.length ? (
                          <optgroup label="Competitor listings">
                            {linkOptions.competitors.map((option) => (
                              <option key={option.value} value={option.value}>
                                {option.label}
                              </option>
                            ))}
                          </optgroup>
                        ) : null}
                        <optgroup label="Product">
                          <option value={linkOptions.product.value}>{linkOptions.product.label}</option>
                        </optgroup>
                      </select>
                    </label>

                    <div className="rounded-2xl border border-zinc-800 bg-zinc-950/80 p-4">
                      <div className="text-xs uppercase tracking-[0.16em] text-zinc-500">Linked summary</div>
                      <div className="mt-2 text-sm text-zinc-200">{renderTaskLinkStatus(attachTask)}</div>
                    </div>
                  </div>
                </>
              ) : (
                <div className="space-y-3">
                  <div className="font-medium text-white">
                    Promote this idea to a product before linking marketplace evidence, suppliers, or competitors.
                  </div>
                  <div className="text-zinc-400">
                    You can still save notes and status on the task card for now. Evidence linking becomes available after promotion.
                  </div>
                </div>
              )}
            </div>

            <div className="mt-4 flex flex-wrap justify-end gap-3">
              <button
                type="button"
                onClick={() => setAttachTaskId(null)}
                className="rounded-lg border border-zinc-700 bg-zinc-900 px-4 py-2 text-sm text-zinc-300 hover:border-zinc-600"
              >
                Cancel
              </button>
              {idea.promoted_product_id ? (
                <button
                  type="button"
                  onClick={() => {
                    onUpdateTask(
                      attachTask.id,
                      attachTask.status,
                      draftNotes[attachTask.id] ?? attachTask.notes ?? '',
                      taskLinkPayload(attachValue),
                    );
                    setAttachTaskId(null);
                  }}
                  className="rounded-lg border border-indigo-500/20 bg-indigo-500/10 px-4 py-2 text-sm text-indigo-300 hover:bg-indigo-500/20"
                >
                  Attach
                </button>
              ) : null}
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}

function EvidenceCandidateCard({
  candidate,
  idea,
  taskLink,
  onTaskLinkChange,
  onApprove,
  onReject,
}: {
  candidate: EvidenceCandidate;
  idea: DiscoveryIdea | null;
  taskLink: string;
  onTaskLinkChange: (value: string) => void;
  onApprove: (candidateId: string, approveAs: 'MARKETPLACE_EVIDENCE' | 'COMPETITOR_LISTING' | 'SUPPLIER_SOURCE') => void;
  onReject: (candidateId: string) => void;
}) {
  const canApprove = Boolean(idea?.promoted_product_id || candidate.product_id);
  const canReview = candidate.review_status === 'PENDING';
  const tasks = idea?.tasks || [];
  const reviewTypeLabel =
    candidate.candidate_type === 'SUPPLIER_SOURCE'
      ? 'Supplier source'
      : candidate.candidate_type === 'COMPETITOR_LISTING'
        ? 'Competitor listing'
        : candidate.candidate_type === 'RISK_FLAG'
          ? 'Risk flag'
          : 'Marketplace evidence';

  return (
    <div className="rounded-xl border border-zinc-800 bg-zinc-950/80 p-3">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <div className="text-sm font-medium text-white">{candidate.title || candidate.marketplace || 'Untitled candidate'}</div>
          <div className="text-[11px] uppercase tracking-[0.14em] text-zinc-500">
            {candidate.source} · {reviewTypeLabel} · {candidate.review_status}
          </div>
        </div>
        <div className="text-right text-xs text-zinc-400">
          <div>{money(candidate.price)}</div>
          <div>{candidate.seller || candidate.marketplace || 'Unknown seller'}</div>
        </div>
      </div>

      <div className="mt-2 text-xs text-zinc-500">
        {candidate.evidence_type ? `${candidate.evidence_type} · ` : ''}
        {candidate.rating != null ? `${candidate.rating}★` : 'No rating'}
        {candidate.review_count != null ? ` · ${candidate.review_count} reviews` : ''}
      </div>

      <div className="mt-3 rounded-xl border border-zinc-800 bg-zinc-950/80 p-3 text-xs text-zinc-300">
        <div className="text-[11px] uppercase tracking-[0.14em] text-zinc-500">Proof state</div>
        <div className="mt-1 text-sm text-white">
          {candidate.review_status === 'APPROVED' ? 'Approved candidate' : 'Pending review'}
        </div>
        <div className="mt-1 text-zinc-500">
          {canApprove ? 'Linked to a promoted product' : 'Promote the idea first before approving proof into product records.'}
        </div>
      </div>

      {tasks.length ? (
        <label className="mt-3 block space-y-1">
          <div className="text-xs uppercase tracking-[0.16em] text-zinc-500">Optional task link</div>
          <select
            value={taskLink}
            onChange={(event) => onTaskLinkChange(event.target.value)}
            className="w-full rounded-xl border border-zinc-800 bg-zinc-950 px-3 py-2 text-sm text-white outline-none transition focus:border-indigo-500/50"
          >
            <option value="">No task link</option>
            {tasks.map((task) => (
              <option key={task.id} value={task.id}>
                {task.title}
              </option>
            ))}
          </select>
        </label>
      ) : null}

      <div className="mt-3 flex flex-wrap gap-2">
        {candidate.candidate_type === 'RISK_FLAG' ? (
          <div className="text-xs text-zinc-500">Risk candidates stay review-only for now.</div>
        ) : candidate.candidate_type === 'SUPPLIER_SOURCE' ? (
          <button
            type="button"
            onClick={() => onApprove(candidate.id, 'SUPPLIER_SOURCE')}
            disabled={!canApprove || !canReview}
            className="rounded-lg border border-cyan-500/20 bg-cyan-500/10 px-3 py-1.5 text-xs text-cyan-300 hover:bg-cyan-500/20 disabled:opacity-60"
          >
            Approve as supplier
          </button>
        ) : (
          <>
            <button
              type="button"
              onClick={() => onApprove(candidate.id, 'MARKETPLACE_EVIDENCE')}
              disabled={!canApprove || !canReview}
              className="rounded-lg border border-emerald-500/20 bg-emerald-500/10 px-3 py-1.5 text-xs text-emerald-300 hover:bg-emerald-500/20 disabled:opacity-60"
            >
              Approve as evidence
            </button>
            <button
              type="button"
              onClick={() => onApprove(candidate.id, 'COMPETITOR_LISTING')}
              disabled={!canApprove || !canReview}
              className="rounded-lg border border-violet-500/20 bg-violet-500/10 px-3 py-1.5 text-xs text-violet-300 hover:bg-violet-500/20 disabled:opacity-60"
            >
              Approve as competitor
            </button>
          </>
        )}
        <button
          type="button"
          onClick={() => onReject(candidate.id)}
          className="rounded-lg border border-zinc-700 bg-zinc-900 px-3 py-1.5 text-xs text-zinc-300 hover:border-zinc-600"
        >
          Reject
        </button>
      </div>
    </div>
  );
}

function Modal({
  title,
  onClose,
  children,
}: {
  title: string;
  onClose: () => void;
  children: ReactNode;
}) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 px-4 py-8">
      <div className="max-h-[88vh] w-full max-w-2xl overflow-auto rounded-[24px] border border-zinc-800 bg-zinc-950 p-5 shadow-2xl shadow-black/40">
        <div className="flex items-start justify-between gap-4">
          <div>
            <div className="text-xs uppercase tracking-[0.16em] text-zinc-500">Workflow</div>
            <h3 className="mt-1 text-xl font-semibold text-white">{title}</h3>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="rounded-lg border border-zinc-700 bg-zinc-900 px-3 py-1.5 text-xs text-zinc-300 hover:border-zinc-600"
          >
            Close
          </button>
        </div>
        <div className="mt-4">{children}</div>
      </div>
    </div>
  );
}

function buildLinkOptions(
  cockpit: ResearchCockpit | null,
  promotedProductId?: string | null,
) {
  return {
    marketplaceEvidence:
      cockpit?.marketplace_evidence?.map((row) => ({
        value: `evidence:${row.id}`,
        label: `${row.evidence_type === 'SOLD_LISTING' ? 'Sold evidence' : 'Marketplace evidence'}: ${row.title || row.marketplace}`,
      })) ?? [],
    sources:
      cockpit?.sources?.map((source) => ({
        value: `source:${source.id}`,
        label: `Supplier source: ${source.supplier_name || source.supplier_platform || source.id}`,
      })) ?? [],
    competitors:
      cockpit?.competitor_listings?.map((listing) => ({
        value: `competitor:${listing.id}`,
        label: `Competitor listing: ${listing.title || listing.marketplace || listing.id}`,
      })) ?? [],
    product: {
      value: promotedProductId ? `product:${promotedProductId}` : '',
      label: 'Promoted product',
    },
  };
}

function taskLinkHref(
  task: {
    linked_evidence_id?: string | null;
    linked_source_id?: string | null;
    linked_competitor_id?: string | null;
    linked_product_id?: string | null;
  },
  promotedProductId?: string | null,
) {
  const productId = task.linked_product_id || promotedProductId;
  if (!productId) return '#';
  if (task.linked_evidence_id) return `/products/${productId}#evidence-${task.linked_evidence_id}`;
  if (task.linked_source_id) return `/products/${productId}#source-${task.linked_source_id}`;
  if (task.linked_competitor_id) return `/products/${productId}#competitor-${task.linked_competitor_id}`;
  return `/products/${productId}`;
}

function taskLinkValue(task: {
  linked_evidence_id?: string | null;
  linked_source_id?: string | null;
  linked_competitor_id?: string | null;
  linked_product_id?: string | null;
}) {
  if (task.linked_evidence_id) return `evidence:${task.linked_evidence_id}`;
  if (task.linked_source_id) return `source:${task.linked_source_id}`;
  if (task.linked_competitor_id) return `competitor:${task.linked_competitor_id}`;
  if (task.linked_product_id) return `product:${task.linked_product_id}`;
  return '';
}

function taskLinkPayload(value: string) {
  if (!value) {
    return {
      linked_evidence_id: null,
      linked_source_id: null,
      linked_competitor_id: null,
      linked_product_id: null,
    };
  }
  const [kind, id] = value.split(':', 2);
  return {
    linked_evidence_id: kind === 'evidence' ? id : null,
    linked_source_id: kind === 'source' ? id : null,
    linked_competitor_id: kind === 'competitor' ? id : null,
    linked_product_id: kind === 'product' ? id : null,
  };
}

function hasTaskLink(task: {
  linked_evidence_id?: string | null;
  linked_source_id?: string | null;
  linked_competitor_id?: string | null;
  linked_product_id?: string | null;
}) {
  return Boolean(task.linked_evidence_id || task.linked_source_id || task.linked_competitor_id || task.linked_product_id);
}

function renderTaskLinkStatus(task: {
  linked_evidence_id?: string | null;
  linked_source_id?: string | null;
  linked_competitor_id?: string | null;
  linked_product_id?: string | null;
}) {
  if (task.linked_evidence_id) return 'Linked to sold evidence';
  if (task.linked_source_id) return 'Linked to supplier source';
  if (task.linked_competitor_id) return 'Linked to competitor listing';
  if (task.linked_product_id) return 'Linked to product';
  return 'No evidence linked';
}

function renderKeywordGroup(
  label: string,
  keywords: DiscoveryIdea['suggested_keywords'],
  group: string,
) {
  const keywordMap = isKeywordGroupMap(keywords) ? keywords : null;
  const flatList = Array.isArray(keywords) ? keywords : [];
  const values = keywordMap?.[group] ?? (group === 'ebay_sold' ? flatList : []);
  if (!values.length && !keywordMap) {
    return <div key={label}><span className="text-zinc-500">{label}: —</span></div>;
  }
  if (!values.length) {
    return <div key={label}><span className="text-zinc-500">{label}: —</span></div>;
  }
  return (
    <div key={label}>
      <div className="text-zinc-500">{label}:</div>
      <div className="mt-1 flex flex-wrap gap-2">
        {values.map((keyword) => (
          <span key={keyword} className="rounded-full border border-zinc-700 bg-zinc-900 px-2 py-0.5 text-[11px] text-zinc-200">
            {keyword}
          </span>
        ))}
      </div>
    </div>
  );
}

function scoutLabel(status?: string | null) {
  if (!status) return '—';
  return SCOUT_STATUS_LABELS[status as keyof typeof SCOUT_STATUS_LABELS] || status;
}

function scoutBadgeClass(status?: string | null) {
  if (!status) {
    return 'bg-zinc-500/20 text-zinc-300 border-zinc-500/30';
  }
  return SCOUT_STATUS_COLORS[status as keyof typeof SCOUT_STATUS_COLORS] || 'bg-zinc-500/20 text-zinc-300 border-zinc-500/30';
}

function isKeywordGroupMap(
  value: DiscoveryIdea['suggested_keywords'],
): value is Record<string, string[]> {
  return !!value && !Array.isArray(value) && typeof value === 'object';
}

function buildExternalResearchQueries(idea: DiscoveryIdea) {
  const keywords = isKeywordGroupMap(idea.suggested_keywords) ? idea.suggested_keywords : null;
  const flatKeywords = Array.isArray(idea.suggested_keywords) ? idea.suggested_keywords : [];
  const queries: string[] = [];
  const preferredGroups = ['ebay_active', 'ebay_sold', 'supplier', 'mercari'];
  for (const group of preferredGroups) {
    const values = keywords?.[group] ?? (group === 'ebay_sold' ? flatKeywords : []);
    for (const value of values || []) {
      const normalized = String(value).trim();
      if (normalized && !queries.includes(normalized)) {
        queries.push(normalized);
      }
      if (queries.length >= 3) return queries;
    }
  }
  if (queries.length < 3 && idea.idea_name && !queries.includes(idea.idea_name)) {
    queries.unshift(idea.idea_name);
  }
  return queries.slice(0, 3);
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
