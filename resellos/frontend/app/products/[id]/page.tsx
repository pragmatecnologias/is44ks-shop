'use client';

import { useEffect, useMemo, useState } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import {
  ArrowLeft,
  BadgeAlert,
  CheckCircle2,
  ClipboardCheck,
  AlertTriangle,
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
  Target,
  XCircle,
} from 'lucide-react';
import { StatusBadge } from '@/components/shared/StatusBadge';
import { RiskBadge } from '@/components/shared/RiskBadge';
import { VerificationBadge } from '@/components/shared/VerificationBadge';
import {
  createMarketplaceEvidence,
  createProductSource,
  deleteMarketplaceEvidence,
  deleteProductSource,
  getProductCockpit,
  runProductResearch,
  verifyEvidenceItem,
  verifyCompetitor,
} from '@/lib/api';
import type {
  MarketplaceEvidenceInput,
  ProductSource,
  ResearchCockpit,
  DecisionSummary,
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
  const decision = (cockpit?.decision ?? {}) as DecisionSummary;
  const finalDecision = decision.recommendation || product?.final_decision || 'NEEDS_RESEARCH';
  const confidence = decision.confidence || cockpit?.confidence || product?.confidence || 'LOW';
  const score = decision.total_score ?? product?.final_score ?? 0;
  const researchCompleteness = decision.research_completeness_score ?? 0;
  const nextAction = decision.next_action || cockpit?.next_action || product?.next_action || 'Add evidence and run research.';
  const missingEvidence = cockpit?.missing_evidence?.length ? cockpit.missing_evidence : product?.missing_evidence ?? [];
  const supplierSources = cockpit?.sources ?? [];
  const evidenceRows = cockpit?.marketplace_evidence ?? [];
  const competitorRows = cockpit?.competitor_listings ?? [];
  const profitRows = cockpit?.profit_analyses ?? [];
  const reports = cockpit?.agent_reports ?? [];
  const discoveryContext = getDiscoveryContext(cockpit?.discovery_context ?? reports.find((report) => report.agent_name === 'discovery_context')?.output_json);
  const competition = cockpit?.competition ?? null;
  const reorder = cockpit?.reorder ?? null;
  const researchVerdict = decision.research_verdict || 'NEEDS_MORE_RESEARCH';
  const buyReadinessStatus = decision.buy_readiness_status || 'NOT_READY';
  const marketReport = reports.find((report) => report.agent_name === 'market_agent');
  const marketData = safeJson(marketReport?.output_json);
  const hardBlockers = cockpit?.hard_blockers?.length ? cockpit.hard_blockers : decision.hard_blockers ?? [];
  const requiredBeforeBuying = decision.required_before_buying ?? [];
  const maxQuantityToBuy = decision.max_quantity_to_buy ?? 0;
  const maxLandedCost = decision.max_landed_cost ?? 0;
  const targetSalePrice = decision.target_sale_price ?? product?.target_sale_price ?? 0;
  const soldEvidenceCount = evidenceRows.filter((row) => row.evidence_type === 'SOLD_LISTING').length;
  const activeEvidenceCount = evidenceRows.filter((row) => row.evidence_type === 'ACTIVE_LISTING').length;
  const VERIFIED_STATUSES = ['USER_VERIFIED', 'API_IMPORTED'];
  const verifiedSoldCount = evidenceRows.filter((row) => row.evidence_type === 'SOLD_LISTING' && row.verification_status && VERIFIED_STATUSES.includes(row.verification_status)).length;
  const verifiedActiveCount = evidenceRows.filter((row) => row.evidence_type === 'ACTIVE_LISTING' && row.verification_status && VERIFIED_STATUSES.includes(row.verification_status)).length;
  const testDataCount = evidenceRows.filter((row) => row.verification_status === 'TEST_DATA').length;
  const totalTestDataCount = [...evidenceRows, ...competitorRows, ...supplierSources].filter((row) => 'verification_status' in row && (row as { verification_status?: string }).verification_status === 'TEST_DATA').length;
  const supplierCostPresent = supplierSources.some((source) => source.unit_cost != null || source.estimated_landed_cost != null);
  const internationalShippingPresent = supplierSources.some((source) => source.international_shipping_estimate != null);
  const profitScenariosPresent = profitRows.length > 0;
  const riskPassed = product?.risk_level !== 'BLOCKED' && decision.blocked !== true;
  const targetPricePresent = Boolean(targetSalePrice && targetSalePrice > 0);
  const canCompete = competition?.can_compete ?? false;
  const competitionLevel = competition?.competition_level ?? 'UNKNOWN';
  const inventoryRows = cockpit?.inventory ?? [];
  const salesRows = cockpit?.sales ?? [];
  const reorderRecommendation = inventoryRows.length > 0 || salesRows.length > 0 ? reorder?.reorder_recommendation ?? 'DO_NOT_REORDER' : null;

  const readinessChecks = [
    { label: 'Sold evidence (verified)', ok: verifiedSoldCount >= 5, detail: `${verifiedSoldCount}/5+ verified sold listings (${soldEvidenceCount} total)` },
    { label: 'Active evidence (verified)', ok: verifiedActiveCount >= 5, detail: `${verifiedActiveCount}/5+ verified active listings (${activeEvidenceCount} total)` },
    { label: 'No test data', ok: testDataCount === 0, detail: testDataCount > 0 ? `${testDataCount} test data items present` : 'All evidence is real' },
    { label: 'Supplier cost', ok: supplierCostPresent, detail: supplierCostPresent ? 'Entered' : 'Missing' },
    { label: 'International shipping', ok: internationalShippingPresent, detail: internationalShippingPresent ? 'Entered' : 'Missing' },
    { label: 'Profit scenarios', ok: profitScenariosPresent, detail: profitScenariosPresent ? `${profitRows.length} generated` : 'Missing' },
    { label: 'Risk review', ok: riskPassed, detail: riskPassed ? 'Passed' : 'Blocked' },
    { label: 'Target price', ok: targetPricePresent, detail: targetPricePresent ? money(targetSalePrice) : 'Missing' },
  ];
  const readinessScore = Math.round((readinessChecks.filter((check) => check.ok).length / readinessChecks.length) * 100);
  const mainBlocker = decision.main_blocker || readinessChecks.find((check) => !check.ok)?.label || 'None';

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
      { label: 'Research', value: researchVerdict.replace(/_/g, ' ') },
      { label: 'Readiness', value: buyReadinessStatus.replace(/_/g, ' ') },
      { label: 'Score', value: `${score}/100` },
      { label: 'Research %', value: `${researchCompleteness}%` },
      { label: 'Checklist', value: `${readinessScore}%` },
      { label: 'Confidence', value: confidence },
      { label: 'Max qty', value: maxQuantityToBuy ? String(maxQuantityToBuy) : '—' },
      { label: 'Max landed', value: maxLandedCost ? money(maxLandedCost) : '—' },
      { label: 'Target price', value: targetPricePresent ? money(targetSalePrice) : '—' },
      { label: 'Can compete', value: canCompete ? 'Yes' : 'No' },
      ...(reorderRecommendation ? [{ label: 'Reorder', value: reorderRecommendation.replace(/_/g, ' ') }] : []),
    ];
  }, [product, cockpit?.current_status, finalDecision, researchVerdict, buyReadinessStatus, score, researchCompleteness, readinessScore, confidence, maxQuantityToBuy, maxLandedCost, targetSalePrice, targetPricePresent, canCompete, reorderRecommendation]);

  const discoveryReason = discoveryContext?.quick_scan_reason || 'The discovery context was not carried over with this product.';
  const discoveryVerdict = discoveryContext?.quick_scan_verdict || 'UNKNOWN';
  const discoveryPriority = discoveryContext?.research_priority || '—';
  const discoveryKeywords = discoveryContext?.suggested_keywords ?? {};
  const discoveryRequired = normalizeStringList(discoveryContext?.required_next_evidence);
  const discoveryRiskFlags = normalizeStringList(discoveryContext?.risk_flags);

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
              <div className="text-right text-xs text-zinc-400">Research: {researchVerdict.replace(/_/g, ' ')} · {buyReadinessStatus.replace(/_/g, ' ')}</div>
              <div className="text-xs text-zinc-400">Next: {nextAction}</div>
            </div>
          </div>

          {error ? (
            <div className="mt-5 rounded-2xl border border-amber-500/20 bg-amber-500/10 p-4 text-sm text-amber-100">
              {error}
            </div>
          ) : null}

          {totalTestDataCount > 0 ? (
            <div className="mt-4 rounded-2xl border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-200">
              <div className="flex items-center gap-2 font-medium text-red-100">
                <ShieldAlert className="h-4 w-4" />
                {totalTestDataCount} test/synthetic data item{totalTestDataCount > 1 ? 's' : ''} detected
              </div>
              <p className="mt-1 text-xs text-red-300">
                This product&apos;s evidence contains test data that was manually enriched for QA purposes. Test data does not count toward research readiness gates. Replace with real verified evidence before making buy decisions.
              </p>
            </div>
          ) : null}
        </header>

        <div className="grid gap-6 xl:grid-cols-4">
          <Panel title="Discovery Context" icon={Sparkles}>
            <div className="space-y-3">
              <div className="rounded-2xl border border-zinc-800 bg-zinc-950/60 p-4">
                <div className="text-xs uppercase tracking-[0.18em] text-zinc-500">Quick scan verdict</div>
                <div className="mt-2 text-lg font-semibold text-white">{discoveryVerdict.replace(/_/g, ' ')}</div>
                <div className="mt-2 text-xs uppercase tracking-[0.16em] text-zinc-500">Priority</div>
                <div className="mt-1 text-sm text-zinc-200">{discoveryPriority}</div>
              </div>
              <div className="rounded-2xl border border-zinc-800 bg-zinc-950/60 p-4">
                <div className="text-xs uppercase tracking-[0.18em] text-zinc-500">Quick scan reason</div>
                <div className="mt-2 text-sm text-zinc-200">{discoveryReason}</div>
              </div>
              <div className="rounded-2xl border border-zinc-800 bg-zinc-950/60 p-4">
                <div className="text-xs uppercase tracking-[0.18em] text-zinc-500">Required before buying</div>
                <Checklist items={discoveryRequired.length ? discoveryRequired : ['No discovery checklist recorded.']} />
              </div>
              <div className="rounded-2xl border border-zinc-800 bg-zinc-950/60 p-4">
                <div className="text-xs uppercase tracking-[0.18em] text-zinc-500">Keyword buckets</div>
                <div className="mt-3 space-y-3 text-sm text-zinc-300">
                  {renderKeywordGroup('eBay sold', discoveryKeywords, 'ebay_sold')}
                  {renderKeywordGroup('eBay active', discoveryKeywords, 'ebay_active')}
                  {renderKeywordGroup('Mercari', discoveryKeywords, 'mercari')}
                  {renderKeywordGroup('Supplier', discoveryKeywords, 'supplier')}
                </div>
              </div>
              <div className="rounded-2xl border border-zinc-800 bg-zinc-950/60 p-4">
                <div className="text-xs uppercase tracking-[0.18em] text-zinc-500">Discovery risk flags</div>
                <Checklist items={discoveryRiskFlags.length ? discoveryRiskFlags : ['No discovery risk flags recorded.']} />
              </div>
            </div>
          </Panel>

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

          <Panel title="Market Signal" icon={Target}>
            <div className="space-y-3">
              <StatRow label="Evidence quality" value={(marketData?.evidence_quality as string) || 'LOW'} />
              <StatRow label="Sell-through" value={(marketData?.sell_through_signal as string) || 'UNKNOWN'} />
              <StatRow label="Sold listings" value={`${verifiedSoldCount} verified / ${soldEvidenceCount} total`} />
              <StatRow label="Active listings" value={`${verifiedActiveCount} verified / ${activeEvidenceCount} total`} />
              <StatRow label="Test data items" value={String(testDataCount)} />
              <StatRow label="Verification coverage" value={marketData?.verification_coverage != null ? `${Math.round(marketData.verification_coverage * 100)}%` : soldEvidenceCount + activeEvidenceCount > 0 ? '0%' : '—'} />
              <StatRow label="Median sold" value={money((marketData?.median_sold_price as number) ?? null)} />
              <StatRow label="Median active" value={money((marketData?.median_active_price as number) ?? null)} />
              <div className="rounded-2xl border border-zinc-800 bg-zinc-950/60 p-4 text-sm text-zinc-300">
                {marketData?.recommended_research_action || 'Add sold and active listings to get a market action.'}
              </div>
            </div>
          </Panel>

          <Panel title="Decision Summary" icon={CheckCircle2}>
            <div className="space-y-3">
              <StatRow label="Decision" value={finalDecision.replace(/_/g, ' ')} />
              <StatRow label="Research verdict" value={researchVerdict.replace(/_/g, ' ')} />
              <StatRow label="Buy readiness" value={buyReadinessStatus.replace(/_/g, ' ')} />
              <StatRow label="Score" value={`${score}/100`} />
              <StatRow label="Research %" value={`${researchCompleteness}%`} />
              <StatRow label="Confidence" value={confidence} />
              <StatRow label="Max quantity" value={maxQuantityToBuy ? String(maxQuantityToBuy) : '—'} />
              <StatRow label="Target price" value={targetPricePresent ? money(targetSalePrice) : '—'} />
            </div>
          </Panel>
        </div>

        <div className="grid gap-6 xl:grid-cols-2">
          <Panel title="Research Readiness" icon={ClipboardCheck}>
            <div className="space-y-3">
              <div className="rounded-2xl border border-zinc-800 bg-zinc-950/60 p-4">
                <div className="flex items-center justify-between gap-3">
                  <div>
                    <div className="text-xs uppercase tracking-[0.18em] text-zinc-500">Readiness score</div>
                    <div className="mt-1 text-2xl font-semibold text-white">{readinessScore}%</div>
                  </div>
                  <div className={`text-xs font-semibold ${buyReadinessStatus === 'READY' ? 'text-emerald-400' : 'text-yellow-400'}`}>{buyReadinessStatus.replace(/_/g, ' ')}</div>
                </div>
                <div className="mt-2 text-xs text-zinc-400">Main blocker: {mainBlocker}</div>
              </div>
              {readinessChecks.map((check) => (
                <div key={check.label} className="rounded-2xl border border-zinc-800 bg-zinc-950/60 p-4">
                  <div className="flex items-center justify-between gap-3">
                    <div className="text-sm font-medium text-white">{check.label}</div>
                    <div className={`text-xs font-semibold ${check.ok ? 'text-emerald-400' : 'text-red-400'}`}>{check.ok ? 'PASS' : 'FAIL'}</div>
                  </div>
                  <div className="mt-2 text-xs text-zinc-400">{check.detail}</div>
                </div>
              ))}
            </div>
          </Panel>

          <Panel title="Why This Decision?" icon={Target}>
            <div className="space-y-3">
              <div className="rounded-2xl border border-zinc-800 bg-zinc-950/60 p-4">
                <div className="text-xs uppercase tracking-[0.18em] text-zinc-500">Reason</div>
                <div className="mt-2 text-sm text-zinc-200">{decision.reason || 'Run research to generate a decision reason.'}</div>
              </div>
              <div className="rounded-2xl border border-zinc-800 bg-zinc-950/60 p-4">
                <div className="text-xs uppercase tracking-[0.18em] text-zinc-500">Next action</div>
                <div className="mt-2 text-sm text-zinc-200">{nextAction}</div>
              </div>
              <div className="rounded-2xl border border-zinc-800 bg-zinc-950/60 p-4">
                <div className="text-xs uppercase tracking-[0.18em] text-zinc-500">Required before buying</div>
                {requiredBeforeBuying.length ? (
                  <Checklist items={requiredBeforeBuying} />
                ) : (
                  <EmptyState title="No extra requirements" description="The latest decision report does not list any additional prerequisites." />
                )}
              </div>
            </div>
          </Panel>
        </div>

        <div className="grid gap-6 xl:grid-cols-2">
          <Panel title="Marketplace Evidence" icon={Users} panelId="marketplace-evidence">
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
                    <div key={row.id} id={`evidence-${row.id}`} className="rounded-2xl border border-zinc-800 bg-zinc-950/60 p-4">
                      <div className="flex items-start justify-between gap-3">
                        <div>
                          <div className="flex items-center gap-2">
                            <span className="text-sm font-medium text-white">{row.title || row.marketplace}</span>
                            <VerificationBadge status={row.verification_status} />
                          </div>
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
                          {row.verification_status && row.verification_status !== 'USER_VERIFIED' && row.verification_status !== 'API_IMPORTED' ? (
                            <button
                              type="button"
                              onClick={async () => { await verifyEvidenceItem(row.id, 'USER_VERIFIED'); await loadCockpit(); }}
                              className="rounded-lg border border-green-500/30 bg-green-500/10 px-2 py-1 text-xs text-green-400 hover:bg-green-500/20"
                            >
                              Verify
                            </button>
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

          <Panel title="Competition Intelligence" icon={Target} panelId="competition-intelligence">
            <div className="space-y-4">
              <div className="grid gap-3 md:grid-cols-2">
                <StatRow label="Competition" value={competitionLevel} />
                <StatRow label="Gap score" value={competition?.listing_gap_score != null ? `${competition.listing_gap_score}/100` : '—'} />
                <StatRow label="Can compete" value={canCompete ? 'Yes' : 'No'} />
                <StatRow label="Competitors" value={competition?.competitor_count != null ? String(competition.competitor_count) : '—'} />
              </div>
              <div className="rounded-2xl border border-zinc-800 bg-zinc-950/60 p-4">
                <div className="text-xs uppercase tracking-[0.18em] text-zinc-500">Recommended angle</div>
                <div className="mt-2 text-sm text-zinc-200">{competition?.recommended_angle || 'Add competitor listings to generate an angle.'}</div>
              </div>
              <div className="rounded-2xl border border-zinc-800 bg-zinc-950/60 p-4">
                <div className="text-xs uppercase tracking-[0.18em] text-zinc-500">Weaknesses</div>
                <Checklist items={competition?.weaknesses?.length ? competition.weaknesses : ['No competition weaknesses captured yet.']} />
              </div>
              <div className="space-y-3">
                {competitorRows.length === 0 ? (
                  <div className="rounded-2xl border border-dashed border-zinc-800 bg-zinc-950/40 p-4 text-sm text-zinc-400">
                    No competitor listings yet.
                  </div>
                ) : (
                  competitorRows.map((row) => (
                    <div key={row.id} id={`competitor-${row.id}`} className="rounded-2xl border border-zinc-800 bg-zinc-950/60 p-4">
                      <div className="flex items-start justify-between gap-3">
                        <div>
                          <div className="flex items-center gap-2">
                            <span className="text-sm font-medium text-white">{row.title || 'Competitor listing'}</span>
                            <VerificationBadge status={row.verification_status} />
                          </div>
                          <div className="text-xs text-zinc-500">
                            {row.marketplace || 'Marketplace unknown'} · {row.sold ? 'Sold' : 'Active'}
                          </div>
                        </div>
                        {row.url ? (
                          <a href={row.url} className="text-xs text-indigo-400 hover:text-indigo-300" target="_blank" rel="noreferrer">
                            <ExternalLink className="h-3.5 w-3.5" />
                          </a>
                        ) : null}
                      </div>
                      <div className="mt-2 grid gap-2 text-sm text-zinc-300 md:grid-cols-2">
                        <StatRow label="Price" value={money(row.price)} />
                        <StatRow label="Shipping" value={money(row.shipping_price)} />
                        <StatRow label="Photo" value={row.photo_score != null ? `${row.photo_score}/100` : '—'} />
                        <StatRow label="Title" value={row.title_patterns?.length ? String(row.title_patterns.length) : '—'} />
                      </div>
                      {row.weaknesses?.length ? (
                        <Checklist items={row.weaknesses} />
                      ) : null}
                    </div>
                  ))
                )}
              </div>
            </div>
          </Panel>

          {inventoryRows.length > 0 || salesRows.length > 0 ? (
            <Panel title="Reorder Intelligence" icon={RefreshCw} panelId="reorder-intelligence">
              <div className="space-y-4">
                <div className="grid gap-3 md:grid-cols-2">
                  <StatRow label="Recommendation" value={(reorderRecommendation ?? 'DO_NOT_REORDER').replace(/_/g, ' ')} />
                  <StatRow label="On hand" value={reorder?.current_inventory != null ? String(reorder.current_inventory) : '—'} />
                  <StatRow label="Sold" value={reorder?.quantity_sold != null ? String(reorder.quantity_sold) : '—'} />
                  <StatRow label="Days cover" value={reorder?.days_of_cover != null ? String(reorder.days_of_cover) : '—'} />
                  <StatRow label="Stockout risk" value={reorder?.stockout_risk ?? '—'} />
                  <StatRow label="Max reorder" value={reorder?.max_reorder_qty != null ? String(reorder.max_reorder_qty) : '—'} />
                </div>
                <div className="rounded-2xl border border-zinc-800 bg-zinc-950/60 p-4">
                  <div className="text-xs uppercase tracking-[0.18em] text-zinc-500">Reason</div>
                  <div className="mt-2 text-sm text-zinc-200">{reorder?.reorder_reason || 'Add inventory and sales history to evaluate reorder risk.'}</div>
                </div>
                <div className="rounded-2xl border border-zinc-800 bg-zinc-950/60 p-4">
                  <div className="text-xs uppercase tracking-[0.18em] text-zinc-500">Inventory / Sales</div>
                  <div className="mt-2 grid gap-2 text-sm text-zinc-300 md:grid-cols-2">
                    <StatRow label="Inventory rows" value={String(inventoryRows.length)} />
                    <StatRow label="Sales rows" value={String(salesRows.length)} />
                  </div>
                </div>
              </div>
            </Panel>
          ) : null}

          <Panel title="Supplier Comparison" icon={Truck} panelId="supplier-comparison">
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
                    <div key={source.id} id={`source-${source.id}`} className="rounded-2xl border border-zinc-800 bg-zinc-950/60 p-4">
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
          <Panel title="Hard Blockers" icon={AlertTriangle}>
            <div className="space-y-3">
              {hardBlockers.length === 0 ? (
                <EmptyState title="No hard blockers" description="The current decision flow does not report any blocking issues." />
              ) : (
                hardBlockers.map((item) => (
                  <div key={item} className="rounded-2xl border border-red-500/20 bg-red-500/10 p-4 text-sm text-red-100">
                    {item}
                  </div>
                ))
              )}
            </div>
          </Panel>

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
  panelId,
  children,
}: {
  title: string;
  icon: React.ElementType;
  panelId?: string;
  children: React.ReactNode;
}) {
  return (
    <section id={panelId} className="rounded-[24px] border border-zinc-800 bg-zinc-950/80 p-5 shadow-xl shadow-black/10">
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

function getDiscoveryContext(value: unknown) {
  if (!value) return null;
  if (typeof value === 'object') return value as Record<string, unknown>;
  if (typeof value === 'string') return safeJson(value);
  return null;
}

function normalizeStringList(value: unknown): string[] {
  if (!value) return [];
  if (Array.isArray(value)) {
    return value.map((item) => String(item)).filter(Boolean);
  }
  if (typeof value === 'string') {
    return value
      .split(',')
      .map((item) => item.trim())
      .filter(Boolean);
  }
  return [];
}

function renderKeywordGroup(
  label: string,
  keywords: unknown,
  group: string,
) {
  const keywordMap = keywords && typeof keywords === 'object' && !Array.isArray(keywords) ? (keywords as Record<string, unknown>) : null;
  const flatList = normalizeStringList(keywords);
  const values = normalizeStringList(keywordMap?.[group] ?? (group === 'ebay_sold' ? flatList : []));
  if (!values.length) {
    return (
      <div>
        <span className="text-zinc-500">{label}: —</span>
      </div>
    );
  }
  return (
    <div>
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

function safeJson(value?: string | null): any {
  if (!value) return {};
  try {
    return JSON.parse(value);
  } catch {
    return {};
  }
}
