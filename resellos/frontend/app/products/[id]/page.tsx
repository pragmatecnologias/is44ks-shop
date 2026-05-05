'use client';

import { useEffect, useMemo, useState } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import {
  ArrowLeft,
  BadgeAlert,
  CheckCircle2,
  Clock3,
  ExternalLink,
  FileText,
  Package,
  Sparkles,
  ShieldAlert,
  TrendingUp,
  Truck,
  Users,
  Wallet,
  XCircle,
  RefreshCw,
} from 'lucide-react';
import { StatusBadge } from '@/components/shared/StatusBadge';
import { RiskBadge } from '@/components/shared/RiskBadge';
import { getProduct } from '@/lib/api';
import type {
  AgentReport,
  MarketplaceEvidence,
  ProfitAnalysis,
  Product,
} from '@/lib/types';

const DEFAULT_MISSING_EVIDENCE = [
  'Sold listings missing',
  'Shipping weight missing',
  'Competitor photo review missing',
  'Supplier comparison missing',
];

const MOCK_EVIDENCE: MarketplaceEvidence[] = [
  {
    id: 'e1',
    product_id: '1',
    marketplace: 'eBay',
    evidence_type: 'SOLD_LISTING',
    title: '2-Pack Car Seat Gap Organizer',
    price: 18.99,
    shipping_price: 0,
    condition: 'New',
    seller_name: 'AutoGearSupply',
    source_method: 'MANUAL',
    confidence: 'HIGH',
    notes: '12 sold examples seen across sold listings.',
  },
  {
    id: 'e2',
    product_id: '1',
    marketplace: 'eBay',
    evidence_type: 'ACTIVE_LISTING',
    title: 'Car Seat Gap Filler Organizer - Black',
    price: 21.99,
    shipping_price: 0,
    condition: 'New',
    seller_name: 'FastParts',
    source_method: 'SCREENSHOT',
    confidence: 'MEDIUM',
    notes: 'Active competition appears crowded but not saturated.',
  },
  {
    id: 'e3',
    product_id: '1',
    marketplace: 'Mercari',
    evidence_type: 'MANUAL_NOTE',
    title: 'Bundle option',
    raw_text: 'Bundle of 2 units seems to land above the break-even line.',
    source_method: 'MANUAL',
    confidence: 'LOW',
    notes: 'Manual note from research session.',
  },
];

const MOCK_SUPPLIERS = [
  {
    id: 's1',
    name: 'Shenzhen Auto Parts',
    platform: 'Alibaba',
    unitCost: 4.15,
    domesticShipping: 0.35,
    internationalShipping: 1.20,
    moq: 50,
    landedCost: 5.7,
    sample: 'Recommended',
  },
  {
    id: 's2',
    name: 'Yiwu Gear House',
    platform: '1688',
    unitCost: 3.95,
    domesticShipping: 0.40,
    internationalShipping: 1.65,
    moq: 100,
    landedCost: 6.0,
    sample: 'Good backup',
  },
];

const MOCK_PROFIT_SCENARIOS: ProfitAnalysis[] = [
  {
    id: 'p1',
    product_id: '1',
    scenario_name: 'eBay buyer-paid shipping',
    expected_sale_price: 18.99,
    landed_cost: 5.7,
    selling_cost: 5.87,
    marketplace_fee: 2.47,
    estimated_net_profit: 7.42,
    margin_percent: 39.1,
    roi_percent: 0,
    verdict: 'GOOD',
  },
  {
    id: 'p2',
    product_id: '1',
    scenario_name: 'eBay free shipping',
    expected_sale_price: 18.99,
    landed_cost: 5.7,
    selling_cost: 9.89,
    marketplace_fee: 2.47,
    estimated_net_profit: 3.10,
    margin_percent: 16.3,
    roi_percent: 0,
    verdict: 'WEAK',
  },
  {
    id: 'p3',
    product_id: '1',
    scenario_name: '2-pack bundle',
    expected_sale_price: 36.99,
    landed_cost: 11.4,
    selling_cost: 13.79,
    marketplace_fee: 4.81,
    estimated_net_profit: 11.8,
    margin_percent: 35.7,
    roi_percent: 0,
    verdict: 'GOOD',
  },
];

const MOCK_REPORTS: AgentReport[] = [
  {
    id: 'r1',
    product_id: '1',
    agent_name: 'risk_agent',
    report_type: 'risk_agent',
    summary: 'No counterfeit brand terms found. Pet accessory terms allowed.',
    confidence: 'HIGH',
    evidence_refs: ['rule:pet_accessory'],
    created_at: new Date().toISOString(),
  },
  {
    id: 'r2',
    product_id: '1',
    agent_name: 'market_agent',
    report_type: 'market_agent',
    summary: 'Marketplace evidence is medium quality and enough for a cautious sample decision.',
    confidence: 'MEDIUM',
    evidence_refs: ['e1', 'e2'],
    created_at: new Date().toISOString(),
  },
  {
    id: 'r3',
    product_id: '1',
    agent_name: 'profit_agent',
    report_type: 'profit_agent',
    summary: 'The 2-pack bundle is the strongest scenario.',
    confidence: 'MEDIUM',
    evidence_refs: ['p3'],
    created_at: new Date().toISOString(),
  },
  {
    id: 'r4',
    product_id: '1',
    agent_name: 'decision_agent',
    report_type: 'decision_agent',
    summary: 'BUY_SAMPLE with medium confidence. Add sold listings and supplier comparison before ordering.',
    confidence: 'MEDIUM',
    evidence_refs: ['e1', 'p1'],
    created_at: new Date().toISOString(),
  },
];

const TIMELINE = [
  { label: 'Product created', detail: 'Added to research queue', time: '09:20' },
  { label: 'Risk check', detail: 'Pet accessory allowed, no brand issues', time: '09:31' },
  { label: 'Marketplace evidence', detail: '2 sold listings and 1 active listing captured', time: '09:44' },
  { label: 'Profit scenarios', detail: '2-pack bundle returned the best margin', time: '09:52' },
  { label: 'Decision', detail: 'BUY_SAMPLE with missing evidence noted', time: '09:58' },
];

export default function ProductDetailPage() {
  const params = useParams();
  const [product, setProduct] = useState<Product | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getProduct(params.id as string).then((result) => {
      setProduct(result);
      setLoading(false);
    });
  }, [params.id]);

  const cockpit = useMemo(() => {
    if (!product) return null;

    const score = product.final_score ?? (product.final_decision === 'BLOCKED' ? 0 : 78);
    const decision = product.final_decision ?? 'BUY_SAMPLE';
    const confidence = product.confidence ?? 'MEDIUM';
    const nextAction = product.next_action ?? 'Add 10 sold examples and confirm supplier landed cost.';
    const missingEvidence = product.missing_evidence?.length ? product.missing_evidence : DEFAULT_MISSING_EVIDENCE;

    return {
      score,
      decision,
      confidence,
      nextAction,
      missingEvidence,
    };
  }, [product]);

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <RefreshCw className="h-6 w-6 animate-spin text-indigo-400" />
      </div>
    );
  }

  if (!product || !cockpit) {
    return (
      <div className="p-6">
        <div className="mx-auto max-w-xl rounded-3xl border border-zinc-800 bg-zinc-950/80 p-10 text-center">
          <XCircle className="mx-auto mb-4 h-12 w-12 text-red-400" />
          <h2 className="text-xl font-semibold text-white">Product not found</h2>
          <p className="mt-2 text-sm text-zinc-400">The product record could not be loaded.</p>
          <Link href="/products" className="mt-6 inline-flex text-sm text-indigo-400 hover:text-indigo-300">
            Back to Products
          </Link>
        </div>
      </div>
    );
  }

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
                <p className="mt-2 max-w-3xl text-sm text-zinc-400">
                  {product.category ?? 'General'} {product.subcategory ? `· ${product.subcategory}` : ''}
                </p>
                <div className="mt-4 flex flex-wrap gap-3 text-xs text-zinc-400">
                  <Pill icon={Package} label={product.sku} />
                  <Pill icon={ShieldAlert} label={`Decision: ${cockpit.decision.replace(/_/g, ' ')}`} />
                  <Pill icon={Sparkles} label={`Confidence: ${cockpit.confidence}`} />
                  <Pill icon={TrendingUp} label={`Score: ${cockpit.score}/100`} />
                </div>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
              <MetricCard label="Max sample qty" value="5" />
              <MetricCard label="Target sale price" value="$18.99" />
              <MetricCard label="Max landed cost" value="$5.75" />
              <MetricCard label="Next action" value="Evidence first" />
            </div>
          </div>
          <div className="mt-5 rounded-2xl border border-emerald-500/20 bg-emerald-500/10 p-4 text-sm text-emerald-100">
            <div className="flex items-center gap-2 font-medium text-emerald-200">
              <CheckCircle2 className="h-4 w-4" />
              Decision header
            </div>
            <p className="mt-2 text-emerald-50">
              {cockpit.decision.replace(/_/g, ' ')} because the product has enough margin to test, but the app still wants more sold evidence before committing capital.
            </p>
            <p className="mt-2 text-xs text-emerald-100/80">Next action: {cockpit.nextAction}</p>
          </div>
        </header>

        <div className="grid gap-6 xl:grid-cols-3">
          <Panel title="Missing Evidence Checklist" icon={BadgeAlert}>
            <Checklist items={cockpit.missingEvidence} />
          </Panel>

          <Panel title="Risk Panel" icon={ShieldAlert}>
            <div className="space-y-3">
              <div className="flex items-center justify-between rounded-2xl border border-zinc-800 bg-zinc-950/60 p-4">
                <div>
                  <p className="text-xs uppercase tracking-[0.2em] text-zinc-500">Risk level</p>
                  <p className="mt-1 text-lg font-semibold text-white">{product.risk_level ?? 'MEDIUM'}</p>
                </div>
                <RiskBadge risk={product.risk_level ?? 'MEDIUM'} />
              </div>
              <div className="rounded-2xl border border-zinc-800 bg-zinc-950/60 p-4">
                <h3 className="text-sm font-medium text-white">Risk flags</h3>
                <ul className="mt-3 space-y-2 text-sm text-zinc-300">
                  <li>• Generic pet accessory allowed by the rule engine.</li>
                  <li>• No trademark or replica language detected.</li>
                  <li>• Manual review only if compliance-sensitive text appears later.</li>
                </ul>
              </div>
            </div>
          </Panel>

          <Panel title="Marketplace Evidence" icon={Users}>
            <div className="space-y-3">
              {MOCK_EVIDENCE.map((item) => (
                <EvidenceRow key={item.id} item={item} />
              ))}
            </div>
          </Panel>
        </div>

        <div className="grid gap-6 xl:grid-cols-2">
          <Panel title="Profit Scenarios" icon={Wallet}>
            <div className="overflow-hidden rounded-2xl border border-zinc-800">
              <table className="w-full text-sm">
                <thead className="bg-zinc-950/70 text-xs uppercase tracking-[0.18em] text-zinc-500">
                  <tr>
                    <th className="px-4 py-3 text-left">Scenario</th>
                    <th className="px-4 py-3 text-right">Net profit</th>
                    <th className="px-4 py-3 text-right">Margin</th>
                    <th className="px-4 py-3 text-right">Decision</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-zinc-800 bg-zinc-950/40">
                  {MOCK_PROFIT_SCENARIOS.map((scenario) => (
                    <tr key={scenario.id} className="text-zinc-300">
                      <td className="px-4 py-3">
                        <div className="font-medium text-white">{scenario.scenario_name}</div>
                        <div className="text-xs text-zinc-500">
                          landed ${scenario.landed_cost?.toFixed(2)} · selling ${scenario.selling_cost?.toFixed(2)}
                        </div>
                      </td>
                      <td className="px-4 py-3 text-right font-mono text-emerald-400">
                        +${scenario.estimated_net_profit?.toFixed(2)}
                      </td>
                      <td className="px-4 py-3 text-right font-mono text-zinc-100">
                        {scenario.margin_percent?.toFixed(1)}%
                      </td>
                      <td className="px-4 py-3 text-right">
                        <span className="rounded-full border border-emerald-500/20 bg-emerald-500/10 px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.18em] text-emerald-300">
                          {scenario.verdict}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Panel>

          <Panel title="Supplier Comparison" icon={Truck}>
            <div className="space-y-3">
              {MOCK_SUPPLIERS.map((supplier) => (
                <div key={supplier.id} className="rounded-2xl border border-zinc-800 bg-zinc-950/60 p-4">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <h3 className="text-sm font-medium text-white">{supplier.name}</h3>
                      <p className="mt-1 text-xs text-zinc-500">{supplier.platform} · MOQ {supplier.moq}</p>
                    </div>
                    <span className="rounded-full border border-indigo-500/20 bg-indigo-500/10 px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.18em] text-indigo-300">
                      {supplier.sample}
                    </span>
                  </div>
                  <div className="mt-3 grid grid-cols-2 gap-3 text-xs text-zinc-400 sm:grid-cols-4">
                    <Stat label="Unit cost" value={`$${supplier.unitCost.toFixed(2)}`} />
                    <Stat label="Domestic" value={`$${supplier.domesticShipping.toFixed(2)}`} />
                    <Stat label="International" value={`$${supplier.internationalShipping.toFixed(2)}`} />
                    <Stat label="Landed" value={`$${supplier.landedCost.toFixed(2)}`} />
                  </div>
                </div>
              ))}
            </div>
          </Panel>
        </div>

        <div className="grid gap-6 xl:grid-cols-3">
          <Panel title="Agent Reports" icon={FileText}>
            <div className="space-y-3">
              {MOCK_REPORTS.map((report) => (
                <div key={report.id} className="rounded-2xl border border-zinc-800 bg-zinc-950/60 p-4">
                  <div className="flex items-center justify-between gap-3">
                    <div className="text-sm font-medium text-white">{report.agent_name.replace(/_/g, ' ')}</div>
                    <span className="text-[11px] uppercase tracking-[0.18em] text-zinc-500">{report.confidence}</span>
                  </div>
                  <p className="mt-2 text-sm text-zinc-300">{report.summary}</p>
                  {report.evidence_refs?.length ? (
                    <p className="mt-2 text-xs text-zinc-500">Evidence refs: {report.evidence_refs.join(', ')}</p>
                  ) : null}
                </div>
              ))}
            </div>
          </Panel>

          <Panel title="Listing Builder" icon={Sparkles}>
            <div className="space-y-4">
              <div className="rounded-2xl border border-zinc-800 bg-zinc-950/60 p-4">
                <p className="text-xs uppercase tracking-[0.18em] text-zinc-500">Suggested title</p>
                <p className="mt-2 text-sm font-medium text-white">2-Pack Car Seat Gap Organizer - Black, Compact Auto Storage</p>
              </div>
              <div className="rounded-2xl border border-zinc-800 bg-zinc-950/60 p-4">
                <p className="text-xs uppercase tracking-[0.18em] text-zinc-500">Photo checklist</p>
                <ul className="mt-3 space-y-2 text-sm text-zinc-300">
                  <li>• Hero shot on clean background</li>
                  <li>• Installed in car seat gap</li>
                  <li>• Close-up of material and seam</li>
                  <li>• Bundle contents photographed together</li>
                </ul>
              </div>
              <div className="rounded-2xl border border-emerald-500/20 bg-emerald-500/10 p-4 text-sm text-emerald-100">
                Build listing only after the evidence checklist is mostly green.
              </div>
            </div>
          </Panel>

          <Panel title="Sample / Sales / Reorder Timeline" icon={Clock3}>
            <div className="space-y-4">
              {TIMELINE.map((step) => (
                <div key={step.label} className="flex gap-3">
                  <div className="mt-1 h-2.5 w-2.5 rounded-full bg-indigo-400" />
                  <div>
                    <p className="text-sm font-medium text-white">{step.label}</p>
                    <p className="text-xs text-zinc-500">{step.detail}</p>
                    <p className="mt-1 text-[11px] uppercase tracking-[0.18em] text-zinc-600">{step.time}</p>
                  </div>
                </div>
              ))}
              <div className="rounded-2xl border border-zinc-800 bg-zinc-950/60 p-4 text-sm text-zinc-300">
                Reorder candidates only appear after actual sales data confirms demand and profit stability.
              </div>
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
  return (
    <div className="space-y-3">
      {items.map((item) => (
        <div key={item} className="flex items-start gap-3 rounded-2xl border border-zinc-800 bg-zinc-950/60 p-4">
          <XCircle className="mt-0.5 h-4 w-4 shrink-0 text-zinc-500" />
          <p className="text-sm text-zinc-300">{item}</p>
        </div>
      ))}
      <div className="rounded-2xl border border-emerald-500/20 bg-emerald-500/10 p-4 text-sm text-emerald-100">
        Keep missing evidence visible until the product is ready to buy, list, or reorder.
      </div>
    </div>
  );
}

function EvidenceRow({ item }: { item: MarketplaceEvidence }) {
  return (
    <div className="rounded-2xl border border-zinc-800 bg-zinc-950/60 p-4">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-sm font-medium text-white">{item.title ?? item.marketplace}</p>
          <p className="mt-1 text-xs text-zinc-500">
            {item.marketplace} · {item.evidence_type.replace(/_/g, ' ')} · {item.confidence ?? 'LOW'}
          </p>
        </div>
        <div className="text-right">
          {item.price != null ? <p className="text-sm font-mono text-emerald-400">${item.price.toFixed(2)}</p> : null}
          {item.url ? (
            <a href={item.url} className="inline-flex items-center gap-1 text-xs text-indigo-400 hover:text-indigo-300">
              Source <ExternalLink className="h-3 w-3" />
            </a>
          ) : null}
        </div>
      </div>
      {item.notes ? <p className="mt-3 text-sm text-zinc-300">{item.notes}</p> : null}
    </div>
  );
}

function MetricCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-zinc-800 bg-zinc-950/60 p-3">
      <p className="text-[11px] uppercase tracking-[0.18em] text-zinc-500">{label}</p>
      <p className="mt-2 text-sm font-semibold text-white">{value}</p>
    </div>
  );
}

function Pill({ icon: Icon, label }: { icon: React.ElementType; label: string }) {
  return (
    <span className="inline-flex items-center gap-1.5 rounded-full border border-zinc-800 bg-zinc-950/60 px-3 py-1.5 text-xs text-zinc-300">
      <Icon className="h-3.5 w-3.5 text-zinc-500" />
      {label}
    </span>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-zinc-800 bg-zinc-950/60 p-3">
      <div className="text-[11px] uppercase tracking-[0.18em] text-zinc-500">{label}</div>
      <div className="mt-2 text-sm font-semibold text-white">{value}</div>
    </div>
  );
}
