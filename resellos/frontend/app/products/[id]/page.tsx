'use client';

import { useEffect, useMemo, useState } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import {
  ArrowLeft,
  BadgeAlert,
  CheckCircle2,
  ExternalLink,
  FileText,
  Loader2,
  Package,
  RefreshCw,
  ShieldAlert,
  Sparkles,
  Trash2,
  Truck,
  Users,
  Wallet,
  XCircle,
} from 'lucide-react';
import { StatusBadge } from '@/components/shared/StatusBadge';
import { RiskBadge } from '@/components/shared/RiskBadge';
import {
  createMarketplaceEvidence,
  createProductSource,
  deleteMarketplaceEvidence,
  deleteProductSource,
  getProductCockpit,
  runProductResearch,
} from '@/lib/api';
import type {
  MarketplaceEvidenceInput,
  ProductSource,
  ResearchCockpit,
  SupplierInput,
} from '@/lib/types';

const emptyEvidenceForm: MarketplaceEvidenceInput = {
  marketplace: 'eBay',
  evidence_type: 'SOLD_LISTING',
  confidence: 'MEDIUM',
};

const emptySupplierForm: SupplierInput = {
  supplier_platform: 'Alibaba',
  is_primary: false,
};

export default function ProductDetailPage() {
  const params = useParams();
  const productId = params.id as string;
  const [cockpit, setCockpit] = useState<ResearchCockpit | null>(null);
  const [loading, setLoading] = useState(true);
  const [savingEvidence, setSavingEvidence] = useState(false);
  const [savingSupplier, setSavingSupplier] = useState(false);
  const [runningResearch, setRunningResearch] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [evidenceForm, setEvidenceForm] = useState<MarketplaceEvidenceInput>(emptyEvidenceForm);
  const [supplierForm, setSupplierForm] = useState<SupplierInput>(emptySupplierForm);

  async function loadCockpit() {
    setLoading(true);
    setError(null);
    try {
      const data = await getProductCockpit(productId);
      setCockpit(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load product cockpit');
      setCockpit(null);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadCockpit();
  }, [productId]);

  const product = cockpit?.product ?? null;
  const decision = cockpit?.decision ?? {};
  const finalDecision = (decision?.recommendation as string) || product?.final_decision || 'NEEDS_RESEARCH';
  const confidence = (decision?.confidence as string) || cockpit?.confidence || product?.confidence || 'LOW';
  const score = (decision?.total_score as number) ?? product?.final_score ?? 0;
  const nextAction = (decision?.next_action as string) || cockpit?.next_action || product?.next_action || 'Add evidence and run research.';
  const missingEvidence = cockpit?.missing_evidence?.length ? cockpit.missing_evidence : product?.missing_evidence ?? [];
  const supplierSources = cockpit?.sources ?? [];
  const evidenceRows = cockpit?.marketplace_evidence ?? [];
  const profitRows = cockpit?.profit_analyses ?? [];
  const reports = cockpit?.agent_reports ?? [];

  const decisionAccent =
    finalDecision === 'BLOCKED'
      ? 'text-red-400'
      : finalDecision === 'BUY_SAMPLE' || finalDecision === 'BUY_SMALL_BATCH'
        ? 'text-emerald-400'
        : finalDecision === 'WATCHLIST'
          ? 'text-yellow-400'
          : 'text-zinc-200';

  const highLevelSummary = useMemo(() => {
    if (!product) return [];
    return [
      { label: 'Status', value: cockpit?.current_status || product.status },
      { label: 'Decision', value: finalDecision.replace(/_/g, ' ') },
      { label: 'Score', value: `${score}/100` },
      { label: 'Confidence', value: confidence },
    ];
  }, [product, cockpit?.current_status, finalDecision, score, confidence]);

  async function handleRunResearch() {
    if (!product) return;
    setRunningResearch(true);
    setError(null);
    try {
      await runProductResearch(product.id);
      await loadCockpit();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Research run failed');
    } finally {
      setRunningResearch(false);
    }
  }

  async function handleAddEvidence() {
    if (!product) return;
    setSavingEvidence(true);
    setError(null);
    try {
      await createMarketplaceEvidence(product.id, evidenceForm);
      setEvidenceForm(emptyEvidenceForm);
      await loadCockpit();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not save evidence');
    } finally {
      setSavingEvidence(false);
    }
  }

  async function handleAddSupplier() {
    if (!product) return;
    setSavingSupplier(true);
    setError(null);
    try {
      await createProductSource(product.id, supplierForm);
      setSupplierForm(emptySupplierForm);
      await loadCockpit();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not save supplier');
    } finally {
      setSavingSupplier(false);
    }
  }

  async function handleDeleteEvidence(evidenceId: string) {
    setError(null);
    try {
      await deleteMarketplaceEvidence(evidenceId);
      await loadCockpit();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not delete evidence');
    }
  }

  async function handleDeleteSupplier(sourceId: string) {
    if (!product) return;
    setError(null);
    try {
      await deleteProductSource(product.id, sourceId);
      await loadCockpit();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not delete supplier');
    }
  }

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <RefreshCw className="h-6 w-6 animate-spin text-indigo-400" />
      </div>
    );
  }

  if (error && !product) {
    return (
      <div className="p-6">
        <div className="mx-auto max-w-xl rounded-3xl border border-zinc-800 bg-zinc-950/80 p-10 text-center">
          <XCircle className="mx-auto mb-4 h-12 w-12 text-red-400" />
          <h2 className="text-xl font-semibold text-white">Product not found</h2>
          <p className="mt-2 text-sm text-zinc-400">{error}</p>
          <Link href="/products" className="mt-6 inline-flex text-sm text-indigo-400 hover:text-indigo-300">
            Back to Products
          </Link>
        </div>
      </div>
    );
  }

  if (!product) return null;

  return (
    <div className="p-6">
      <div className="mx-auto max-w-[1440px] space-y-6">
        <header className="rounded-[28px] border border-zinc-800 bg-[radial-gradient(circle_at_top_left,_rgba(79,70,229,0.22),_transparent_28%),linear-gradient(180deg,rgba(9,9,11,0.96),rgba(17,17,17,0.96))] p-6 shadow-2xl shadow-black/20">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div className="flex items-start gap-4">
              <Link href="/products" className="mt-1 rounded-xl border border-zinc-800 bg-zinc-950/60 p-2 text-zinc-400 transition hover:text-white hover:border-zinc-700">
                <ArrowLeft className="h-5 w-5" />
              </Link>
              <div>
                <div className="flex flex-wrap items-center gap-3">
                  <h1 className="text-3xl font-semibold tracking-tight text-white">{product.name}</h1>
                  <StatusBadge status={product.status} />
                  {product.risk_level && <RiskBadge risk={product.risk_level} />}
                </div>
                <p className="mt-2 text-sm text-zinc-400">
                  {product.category ?? 'Uncategorized'} {product.subcategory ? `· ${product.subcategory}` : ''}
                </p>
                <div className="mt-4 flex flex-wrap gap-3 text-xs text-zinc-400">
                  {highLevelSummary.map((item) => (
                    <Pill key={item.label} label={`${item.label}: ${item.value}`} />
                  ))}
                </div>
              </div>
            </div>
            <div className="flex flex-col items-end gap-3">
              <button
                type="button"
                onClick={handleRunResearch}
                disabled={runningResearch}
                className="inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-indigo-500 disabled:cursor-not-allowed disabled:opacity-70"
              >
                {runningResearch ? <Loader2 className="h-4 w-4 animate-spin" /> : <Sparkles className="h-4 w-4" />}
                Run Research
              </button>
              <div className={`text-right text-lg font-semibold ${decisionAccent}`}>{finalDecision.replace(/_/g, ' ')}</div>
              <div className="text-xs text-zinc-400">Next: {nextAction}</div>
            </div>
          </div>

          {error ? (
            <div className="mt-5 rounded-2xl border border-amber-500/20 bg-amber-500/10 p-4 text-sm text-amber-100">
              {error}
            </div>
          ) : null}
        </header>

        <div className="grid gap-6 xl:grid-cols-3">
          <Panel title="Missing Evidence" icon={BadgeAlert}>
            <Checklist items={missingEvidence} />
          </Panel>

          <Panel title="Risk Panel" icon={ShieldAlert}>
            <div className="space-y-3">
              <div className="rounded-2xl border border-zinc-800 bg-zinc-950/60 p-4">
                <p className="text-xs uppercase tracking-[0.18em] text-zinc-500">Risk level</p>
                <div className="mt-2 text-lg font-semibold text-white">{product.risk_level ?? 'MEDIUM'}</div>
              </div>
              <div className="rounded-2xl border border-zinc-800 bg-zinc-950/60 p-4 text-sm text-zinc-300">
                Product decisions are blocked when risk is BLOCKED and downgraded to WATCHLIST when evidence is thin.
              </div>
            </div>
          </Panel>

          <Panel title="Decision Summary" icon={CheckCircle2}>
            <div className="space-y-3">
              <StatRow label="Decision" value={finalDecision.replace(/_/g, ' ')} />
              <StatRow label="Score" value={`${score}/100`} />
              <StatRow label="Confidence" value={confidence} />
            </div>
          </Panel>
        </div>

        <div className="grid gap-6 xl:grid-cols-2">
          <Panel title="Marketplace Evidence" icon={Users}>
            <div className="space-y-4">
              <form
                className="grid gap-3 rounded-2xl border border-zinc-800 bg-zinc-950/60 p-4"
                onSubmit={(e) => {
                  e.preventDefault();
                  handleAddEvidence();
                }}
              >
                <div className="grid gap-3 md:grid-cols-2">
                  <Input label="Marketplace" value={evidenceForm.marketplace || ''} onChange={(value) => setEvidenceForm((s) => ({ ...s, marketplace: value }))} />
                  <Input label="Evidence Type" value={evidenceForm.evidence_type || ''} onChange={(value) => setEvidenceForm((s) => ({ ...s, evidence_type: value }))} />
                  <Input label="Title" value={evidenceForm.title || ''} onChange={(value) => setEvidenceForm((s) => ({ ...s, title: value }))} />
                  <Input label="Price" type="number" step="0.01" value={evidenceForm.price?.toString() ?? ''} onChange={(value) => setEvidenceForm((s) => ({ ...s, price: value ? Number(value) : undefined }))} />
                  <Input label="Shipping" type="number" step="0.01" value={evidenceForm.shipping_price?.toString() ?? ''} onChange={(value) => setEvidenceForm((s) => ({ ...s, shipping_price: value ? Number(value) : undefined }))} />
                  <Input label="URL" value={evidenceForm.url || ''} onChange={(value) => setEvidenceForm((s) => ({ ...s, url: value }))} />
                </div>
                <Textarea label="Notes" value={evidenceForm.notes || ''} onChange={(value) => setEvidenceForm((s) => ({ ...s, notes: value }))} />
                <div className="flex justify-end">
                  <button type="submit" disabled={savingEvidence} className="inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-indigo-500 disabled:opacity-70">
                    {savingEvidence ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
                    Add Evidence
                  </button>
                </div>
              </form>

              <div className="space-y-3">
                {evidenceRows.length === 0 ? (
                  <EmptyState title="No evidence yet" description="Add sold or active listings to unlock better decisions." />
                ) : (
                  evidenceRows.map((row) => (
                    <div key={row.id} className="rounded-2xl border border-zinc-800 bg-zinc-950/60 p-4">
                      <div className="flex items-start justify-between gap-3">
                        <div>
                          <div className="text-sm font-medium text-white">{row.title || row.marketplace}</div>
                          <div className="text-xs text-zinc-500">
                            {row.marketplace} · {row.evidence_type.replace(/_/g, ' ')} · {row.confidence ?? 'LOW'}
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          {row.url ? (
                            <a href={row.url} className="text-xs text-indigo-400 hover:text-indigo-300" target="_blank" rel="noreferrer">
                              <ExternalLink className="h-3.5 w-3.5" />
                            </a>
                          ) : null}
                          <button type="button" onClick={() => handleDeleteEvidence(row.id)} className="text-zinc-500 hover:text-red-400">
                            <Trash2 className="h-4 w-4" />
                          </button>
                        </div>
                      </div>
                      <div className="mt-2 text-sm text-zinc-300">
                        {row.notes || row.raw_text || 'No notes recorded.'}
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </Panel>

          <Panel title="Supplier Comparison" icon={Truck}>
            <div className="space-y-4">
              <form
                className="grid gap-3 rounded-2xl border border-zinc-800 bg-zinc-950/60 p-4"
                onSubmit={(e) => {
                  e.preventDefault();
                  handleAddSupplier();
                }}
              >
                <div className="grid gap-3 md:grid-cols-2">
                  <Input label="Supplier Name" value={supplierForm.supplier_name || ''} onChange={(value) => setSupplierForm((s) => ({ ...s, supplier_name: value }))} />
                  <Input label="Platform" value={supplierForm.supplier_platform || ''} onChange={(value) => setSupplierForm((s) => ({ ...s, supplier_platform: value }))} />
                  <Input label="Unit Cost" type="number" step="0.01" value={supplierForm.unit_cost?.toString() ?? ''} onChange={(value) => setSupplierForm((s) => ({ ...s, unit_cost: value ? Number(value) : undefined }))} />
                  <Input label="Domestic Shipping" type="number" step="0.01" value={supplierForm.domestic_shipping?.toString() ?? ''} onChange={(value) => setSupplierForm((s) => ({ ...s, domestic_shipping: value ? Number(value) : undefined }))} />
                  <Input label="International Shipping" type="number" step="0.01" value={supplierForm.international_shipping_estimate?.toString() ?? ''} onChange={(value) => setSupplierForm((s) => ({ ...s, international_shipping_estimate: value ? Number(value) : undefined }))} />
                  <Input label="MOQ" type="number" value={supplierForm.moq?.toString() ?? ''} onChange={(value) => setSupplierForm((s) => ({ ...s, moq: value ? Number(value) : undefined }))} />
                </div>
                <Textarea label="Notes" value={supplierForm.notes || ''} onChange={(value) => setSupplierForm((s) => ({ ...s, notes: value }))} />
                <label className="flex items-center gap-2 text-sm text-zinc-300">
                  <input type="checkbox" checked={Boolean(supplierForm.is_primary)} onChange={(e) => setSupplierForm((s) => ({ ...s, is_primary: e.target.checked }))} />
                  Primary supplier
                </label>
                <div className="flex justify-end">
                  <button type="submit" disabled={savingSupplier} className="inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-indigo-500 disabled:opacity-70">
                    {savingSupplier ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
                    Add Supplier
                  </button>
                </div>
              </form>

              <div className="space-y-3">
                {supplierSources.length === 0 ? (
                  <EmptyState title="No supplier comparison yet" description="Add 2-3 suppliers so landed cost can be compared." />
                ) : (
                  supplierSources.map((source) => (
                    <div key={source.id} className="rounded-2xl border border-zinc-800 bg-zinc-950/60 p-4">
                      <div className="flex items-start justify-between gap-3">
                        <div>
                          <div className="text-sm font-medium text-white">{source.supplier_name || 'Unnamed supplier'}</div>
                          <div className="text-xs text-zinc-500">
                            {source.supplier_platform || 'Platform unknown'} · MOQ {source.moq ?? '—'}
                          </div>
                        </div>
                        <button type="button" onClick={() => handleDeleteSupplier(source.id)} className="text-zinc-500 hover:text-red-400">
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                      <div className="mt-3 grid gap-2 text-sm text-zinc-300 md:grid-cols-2">
                        <StatRow label="Unit cost" value={money(source.unit_cost)} />
                        <StatRow label="Domestic" value={money(source.domestic_shipping)} />
                        <StatRow label="International" value={money(source.international_shipping_estimate)} />
                        <StatRow label="Estimated landed" value={money(source.estimated_landed_cost)} />
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </Panel>
        </div>

        <div className="grid gap-6 xl:grid-cols-3">
          <Panel title="Profit Scenarios" icon={Wallet}>
            <div className="space-y-3">
              {profitRows.length === 0 ? (
                <EmptyState title="No profit analysis yet" description="Run research after adding evidence and suppliers." />
              ) : (
                profitRows.map((row) => (
                  <div key={row.id} className="rounded-2xl border border-zinc-800 bg-zinc-950/60 p-4">
                    <div className="flex items-center justify-between gap-3">
                      <div>
                        <div className="text-sm font-medium text-white">{row.scenario_name || 'Scenario'}</div>
                        <div className="text-xs text-zinc-500">Break-even {money(row.break_even_price)}</div>
                      </div>
                      <div className="text-right">
                        <div className="font-mono text-emerald-400">{money(row.estimated_net_profit)}</div>
                        <div className="text-xs text-zinc-500">{row.verdict}</div>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </Panel>

          <Panel title="Agent Reports" icon={FileText}>
            <div className="space-y-3">
              {reports.length === 0 ? (
                <EmptyState title="No agent reports yet" description="Run research to generate risk, market, profit, and decision reports." />
              ) : (
                reports.map((report) => (
                  <div key={report.id} className="rounded-2xl border border-zinc-800 bg-zinc-950/60 p-4">
                    <div className="text-sm font-medium text-white">{report.agent_name.replace(/_/g, ' ')}</div>
                    <div className="mt-2 text-sm text-zinc-300">{report.summary || 'No summary.'}</div>
                    {report.evidence_refs?.length ? <div className="mt-2 text-xs text-zinc-500">{report.evidence_refs.join(', ')}</div> : null}
                  </div>
                ))
              )}
            </div>
          </Panel>

          <Panel title="Timeline" icon={RefreshCw}>
            <div className="space-y-3 text-sm text-zinc-300">
              <TimelineStep title="Create product" detail="Start with a product idea." />
              <TimelineStep title="Add evidence" detail="Capture sold and active listings." />
              <TimelineStep title="Add suppliers" detail="Compare landed cost and MOQ." />
              <TimelineStep title="Run research" detail="Generate decision and next action." />
              <TimelineStep title="Buy sample or watchlist" detail="Only order when evidence is strong enough." />
            </div>
          </Panel>
        </div>
      </div>
    </div>
  );
}

function Panel({
  title,
  icon: Icon,
  children,
}: {
  title: string;
  icon: React.ElementType;
  children: React.ReactNode;
}) {
  return (
    <section className="rounded-[24px] border border-zinc-800 bg-zinc-950/80 p-5 shadow-xl shadow-black/10">
      <div className="mb-4 flex items-center gap-2">
        <div className="flex h-8 w-8 items-center justify-center rounded-xl border border-zinc-800 bg-zinc-900 text-zinc-300">
          <Icon className="h-4 w-4" />
        </div>
        <h2 className="text-sm font-semibold uppercase tracking-[0.18em] text-zinc-200">{title}</h2>
      </div>
      {children}
    </section>
  );
}

function Checklist({ items }: { items: string[] }) {
  if (items.length === 0) {
    return <EmptyState title="No missing evidence" description="This product has the essentials filled in." />;
  }

  return (
    <div className="space-y-3">
      {items.map((item) => (
        <div key={item} className="flex items-start gap-3 rounded-2xl border border-zinc-800 bg-zinc-950/60 p-4">
          <XCircle className="mt-0.5 h-4 w-4 shrink-0 text-zinc-500" />
          <p className="text-sm text-zinc-300">{item}</p>
        </div>
      ))}
    </div>
  );
}

function TimelineStep({ title, detail }: { title: string; detail: string }) {
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
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  type?: string;
  step?: string;
}) {
  return (
    <label className="space-y-1">
      <div className="text-xs uppercase tracking-[0.16em] text-zinc-500">{label}</div>
      <input
        type={type}
        step={step}
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
    <label className="space-y-1">
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

function StatRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between gap-3 rounded-xl border border-zinc-800 bg-zinc-950/60 px-3 py-2">
      <div className="text-xs uppercase tracking-[0.14em] text-zinc-500">{label}</div>
      <div className="text-sm text-white">{value}</div>
    </div>
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

function Pill({ label }: { label: string }) {
  return <span className="inline-flex items-center rounded-full border border-zinc-800 bg-zinc-950/60 px-3 py-1.5 text-xs text-zinc-300">{label}</span>;
}

function money(value?: number | null) {
  if (value == null) return '—';
  return `$${Number(value).toFixed(2)}`;
}

