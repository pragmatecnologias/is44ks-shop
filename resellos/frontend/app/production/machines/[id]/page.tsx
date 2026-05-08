'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import {
  ArrowLeft, RefreshCw, Plus, Check, X, ExternalLink, ChevronDown, ChevronRight,
  DollarSign, Wrench, AlertTriangle, TrendingUp, Zap, Shield,
} from 'lucide-react';
import {
  getMachineCockpit,
  createMachineEvidence,
  createMachineProductFamily,
  createCostScenario,
  runMachineDecision,
  verifyMachineEvidence,
  promoteMachineProductFamily,
} from '@/lib/api';
import type { MachineCockpit, MachineEvidence, MachineProductFamily, ProductionCostScenario } from '@/lib/types';
import {
  MACHINE_STATUS_COLORS, MACHINE_STATUS_LABELS,
  MACHINE_DECISION_COLORS, MACHINE_DECISION_LABELS,
  VERIFICATION_COLORS, VERIFICATION_LABELS,
} from '@/lib/types';

function money(v?: number | null) {
  if (v == null) return '—';
  return `$${Number(v).toFixed(2)}`;
}

export default function MachineCockpitPage() {
  const params = useParams<{ id: string }>();
  const [cockpit, setCockpit] = useState<MachineCockpit | null>(null);
  const [loading, setLoading] = useState(true);
  const [showAddEvidence, setShowAddEvidence] = useState(false);
  const [showAddFamily, setShowAddFamily] = useState(false);
  const [showAddScenario, setShowAddScenario] = useState(false);

  // Form states
  const [evForm, setEvForm] = useState({ evidence_type: 'NEW_MACHINE_LISTING', title: '', url: '', price: '', source: '', notes: '' });
  const [famForm, setFamForm] = useState({ name: '', material_cost_per_unit: '', estimated_sale_price: '', description: '' });
  const [scenForm, setScenForm] = useState({ scenario_name: '', material_cost: '', labor_cost: '', sale_price: '', units_per_month: '', machine_purchase_price: '' });

  async function loadData() {
    setLoading(true);
    try { setCockpit(await getMachineCockpit(params.id)); } catch { /* */ }
    finally { setLoading(false); }
  }

  useEffect(() => { loadData(); }, [params.id]);

  async function handleAddEvidence(e: React.FormEvent) {
    e.preventDefault();
    await createMachineEvidence(params.id, {
      evidence_type: evForm.evidence_type,
      title: evForm.title || undefined,
      url: evForm.url || undefined,
      price: evForm.price ? parseFloat(evForm.price) : undefined,
      source: evForm.source || undefined,
      notes: evForm.notes || undefined,
    });
    setEvForm({ evidence_type: 'NEW_MACHINE_LISTING', title: '', url: '', price: '', source: '', notes: '' });
    setShowAddEvidence(false);
    loadData();
  }

  async function handleAddFamily(e: React.FormEvent) {
    e.preventDefault();
    await createMachineProductFamily(params.id, {
      name: famForm.name,
      description: famForm.description || undefined,
      material_cost_per_unit: famForm.material_cost_per_unit ? parseFloat(famForm.material_cost_per_unit) : undefined,
      estimated_sale_price: famForm.estimated_sale_price ? parseFloat(famForm.estimated_sale_price) : undefined,
    });
    setFamForm({ name: '', material_cost_per_unit: '', estimated_sale_price: '', description: '' });
    setShowAddFamily(false);
    loadData();
  }

  async function handleAddScenario(familyId: string, e: React.FormEvent) {
    e.preventDefault();
    await createCostScenario(familyId, {
      scenario_name: scenForm.scenario_name,
      material_cost: scenForm.material_cost ? parseFloat(scenForm.material_cost) : undefined,
      labor_cost: scenForm.labor_cost ? parseFloat(scenForm.labor_cost) : undefined,
      sale_price: scenForm.sale_price ? parseFloat(scenForm.sale_price) : undefined,
      units_per_month: scenForm.units_per_month ? parseInt(scenForm.units_per_month) : undefined,
      machine_purchase_price: scenForm.machine_purchase_price ? parseFloat(scenForm.machine_purchase_price) : undefined,
    });
    setScenForm({ scenario_name: '', material_cost: '', labor_cost: '', sale_price: '', units_per_month: '', machine_purchase_price: '' });
    setShowAddScenario(false);
    loadData();
  }

  async function handleDecision() {
    await runMachineDecision(params.id);
    loadData();
  }

  async function handleVerify(evidenceId: string) {
    await verifyMachineEvidence(params.id, evidenceId, 'USER_VERIFIED');
    loadData();
  }

  async function handlePromote(familyId: string) {
    const result = await promoteMachineProductFamily(params.id, familyId);
    alert(`Promoted! Idea: ${result.idea_id}, Product: ${result.product_id || 'N/A'}`);
    loadData();
  }

  if (loading) {
    return <div className="flex items-center justify-center h-64"><RefreshCw className="w-6 h-6 animate-spin text-indigo-400" /></div>;
  }

  if (!cockpit) {
    return <div className="p-6 text-zinc-400">Machine not found</div>;
  }

  const { machine, evidence, product_families, cost_scenarios, decision, next_action, capabilities } = cockpit;

  return (
    <div className="p-6 space-y-6 max-w-[1400px]">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Link href={`/production/campaigns/${machine.campaign_id}`} className="text-zinc-400 hover:text-white"><ArrowLeft className="w-5 h-5" /></Link>
        <div className="flex-1">
          <h1 className="text-2xl font-bold text-white">{machine.name}</h1>
          {machine.brand && <span className="text-zinc-400 text-sm">{machine.brand} {machine.model}</span>}
        </div>
        <span className={`inline-flex items-center px-2.5 py-1 text-xs font-medium border rounded-full ${MACHINE_STATUS_COLORS[machine.status] || ''}`}>
          {MACHINE_STATUS_LABELS[machine.status] || machine.status}
        </span>
      </div>

      {/* Overview stats */}
      <div className="grid gap-3 md:grid-cols-5">
        <StatCard label="New Price" value={money(machine.price_new)} icon={<DollarSign className="w-4 h-4" />} />
        <StatCard label="Evidence" value={String(machine.evidence_count)} icon={<Zap className="w-4 h-4" />} />
        <StatCard label="Product Families" value={String(machine.product_family_count)} icon={<Wrench className="w-4 h-4" />} />
        <StatCard label="Scenarios" value={String(machine.cost_scenario_count)} icon={<TrendingUp className="w-4 h-4" />} />
        <StatCard label="Workspace" value={machine.workspace_needed || 'Unknown'} icon={<Shield className="w-4 h-4" />} />
      </div>

      {/* Capabilities */}
      {capabilities.length > 0 && (
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-4">
          <div className="text-xs uppercase tracking-[0.18em] text-zinc-500 mb-2">Capabilities</div>
          <div className="flex flex-wrap gap-2">
            {capabilities.map((c) => (
              <span key={c.id} className="inline-flex items-center px-3 py-1 text-xs bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 rounded-lg">{c.name}</span>
            ))}
          </div>
        </div>
      )}

      {/* Next Action */}
      {next_action && next_action.action !== 'none' && (
        <div className={`rounded-xl border p-4 ${next_action.priority === 'HIGH' ? 'bg-orange-500/5 border-orange-500/20' : 'bg-blue-500/5 border-blue-500/20'}`}>
          <div className="text-xs uppercase tracking-[0.18em] text-zinc-500 mb-1">Next Action ({next_action.priority})</div>
          <p className="text-white text-sm">{next_action.reason}</p>
        </div>
      )}

      {/* Decision panel */}
      <Panel title="Decision" icon={<AlertTriangle className="w-4 h-4 text-indigo-400" />}>
        {decision ? (
          <div className="space-y-3">
            <div className="flex items-center gap-3">
              <span className={`inline-flex items-center px-3 py-1.5 text-sm font-medium border rounded-full ${MACHINE_DECISION_COLORS[decision.recommendation] || ''}`}>
                {MACHINE_DECISION_LABELS[decision.recommendation] || decision.recommendation}
              </span>
              <span className="text-zinc-400 text-sm">Confidence: {decision.confidence}</span>
            </div>
            {decision.reason && <p className="text-zinc-300 text-sm">{decision.reason}</p>}
            {decision.hard_blockers.length > 0 && (
              <div className="space-y-1">
                <div className="text-xs uppercase tracking-[0.16em] text-red-400">Blockers</div>
                {decision.hard_blockers.map((b, i) => <p key={i} className="text-sm text-red-300">{b}</p>)}
              </div>
            )}
            {decision.warnings.length > 0 && (
              <div className="space-y-1">
                <div className="text-xs uppercase tracking-[0.16em] text-yellow-400">Warnings</div>
                {decision.warnings.map((w, i) => <p key={i} className="text-sm text-yellow-300">{w}</p>)}
              </div>
            )}
            <div className="grid grid-cols-3 gap-3 text-xs text-zinc-400">
              <span>Workspace: {decision.workspace_fit || '—'}</span>
              <span>Safety: {decision.safety_fit || '—'}</span>
              <span>Budget: {decision.budget_fit || '—'}</span>
            </div>
          </div>
        ) : (
          <div className="text-center py-4">
            <p className="text-zinc-500 text-sm mb-3">No decision yet. Add evidence and run the decision engine.</p>
            <button onClick={handleDecision} className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium rounded-lg">
              Run Decision
            </button>
          </div>
        )}
        {decision && (
          <div className="mt-3 pt-3 border-t border-zinc-800">
            <button onClick={handleDecision} className="text-xs text-indigo-400 hover:text-indigo-300">Re-run Decision</button>
          </div>
        )}
      </Panel>

      {/* Evidence */}
      <Panel title="Evidence" icon={<Zap className="w-4 h-4 text-indigo-400" />} action={
        <button onClick={() => setShowAddEvidence(!showAddEvidence)} className="flex items-center gap-1 text-xs text-indigo-400 hover:text-indigo-300">
          <Plus className="w-3 h-3" /> Add
        </button>
      }>
        {showAddEvidence && (
          <form onSubmit={handleAddEvidence} className="mb-4 bg-zinc-950/80 rounded-xl p-4 grid gap-3 md:grid-cols-3">
            <label className="block">
              <div className="mb-1 text-xs uppercase tracking-[0.16em] text-zinc-500">Type</div>
              <select value={evForm.evidence_type} onChange={(e) => setEvForm((s) => ({ ...s, evidence_type: e.target.value }))}
                className="w-full rounded-xl border border-zinc-800 bg-zinc-950/80 px-3 py-2 text-sm text-white">
                {['NEW_MACHINE_LISTING', 'USED_MACHINE_LISTING', 'VENDOR_SPEC', 'REVIEW', 'FORUM_DISCUSSION', 'YOUTUBE_REVIEW', 'SAFETY_REPORT', 'MANUAL'].map((t) => (
                  <option key={t} value={t}>{t.replace(/_/g, ' ')}</option>
                ))}
              </select>
            </label>
            <label className="block"><div className="mb-1 text-xs uppercase tracking-[0.16em] text-zinc-500">Title</div>
              <input value={evForm.title} onChange={(e) => setEvForm((s) => ({ ...s, title: e.target.value }))} className="w-full rounded-xl border border-zinc-800 bg-zinc-950/80 px-3 py-2 text-sm text-white" /></label>
            <label className="block"><div className="mb-1 text-xs uppercase tracking-[0.16em] text-zinc-500">Price ($)</div>
              <input type="number" value={evForm.price} onChange={(e) => setEvForm((s) => ({ ...s, price: e.target.value }))} className="w-full rounded-xl border border-zinc-800 bg-zinc-950/80 px-3 py-2 text-sm text-white" /></label>
            <label className="block"><div className="mb-1 text-xs uppercase tracking-[0.16em] text-zinc-500">URL</div>
              <input value={evForm.url} onChange={(e) => setEvForm((s) => ({ ...s, url: e.target.value }))} className="w-full rounded-xl border border-zinc-800 bg-zinc-950/80 px-3 py-2 text-sm text-white" /></label>
            <label className="block"><div className="mb-1 text-xs uppercase tracking-[0.16em] text-zinc-500">Source</div>
              <input value={evForm.source} onChange={(e) => setEvForm((s) => ({ ...s, source: e.target.value }))} className="w-full rounded-xl border border-zinc-800 bg-zinc-950/80 px-3 py-2 text-sm text-white" placeholder="eBay, Amazon, etc." /></label>
            <label className="block"><div className="mb-1 text-xs uppercase tracking-[0.16em] text-zinc-500">Notes</div>
              <input value={evForm.notes} onChange={(e) => setEvForm((s) => ({ ...s, notes: e.target.value }))} className="w-full rounded-xl border border-zinc-800 bg-zinc-950/80 px-3 py-2 text-sm text-white" /></label>
            <div className="md:col-span-3 flex justify-end"><button type="submit" className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-sm rounded-lg">Add Evidence</button></div>
          </form>
        )}

        {evidence.length === 0 ? (
          <p className="text-zinc-500 text-sm py-4 text-center">No evidence yet</p>
        ) : (
          <div className="space-y-2">
            {evidence.map((ev) => (
              <div key={ev.id} className="flex items-center gap-3 bg-zinc-950/60 rounded-lg p-3">
                <span className="text-xs text-zinc-500 uppercase w-40 shrink-0">{ev.evidence_type.replace(/_/g, ' ')}</span>
                <span className="text-sm text-white flex-1 truncate">{ev.title || ev.source || '—'}</span>
                {ev.price != null && <span className="text-sm text-zinc-300">{money(ev.price)}</span>}
                {ev.url && <a href={ev.url} target="_blank" rel="noopener noreferrer" className="text-indigo-400 hover:text-indigo-300"><ExternalLink className="w-3.5 h-3.5" /></a>}
                <span className={`inline-flex items-center px-2 py-0.5 text-xs border rounded-full ${(VERIFICATION_COLORS as Record<string,string>)[ev.verification_status] || 'bg-zinc-500/20 text-zinc-400 border-zinc-500/30'}`}>
                  {(VERIFICATION_LABELS as Record<string,string>)[ev.verification_status] || ev.verification_status}
                </span>
                {ev.verification_status === 'PENDING' && (
                  <button onClick={() => handleVerify(ev.id)} className="text-xs text-green-400 hover:text-green-300" title="Verify">
                    <Check className="w-3.5 h-3.5" />
                  </button>
                )}
              </div>
            ))}
          </div>
        )}
      </Panel>

      {/* Product Families */}
      <Panel title="Product Families" icon={<Wrench className="w-4 h-4 text-indigo-400" />} action={
        <button onClick={() => setShowAddFamily(!showAddFamily)} className="flex items-center gap-1 text-xs text-indigo-400 hover:text-indigo-300">
          <Plus className="w-3 h-3" /> Add
        </button>
      }>
        {showAddFamily && (
          <form onSubmit={handleAddFamily} className="mb-4 bg-zinc-950/80 rounded-xl p-4 grid gap-3 md:grid-cols-2">
            <label className="block"><div className="mb-1 text-xs uppercase tracking-[0.16em] text-zinc-500">Name *</div>
              <input value={famForm.name} onChange={(e) => setFamForm((s) => ({ ...s, name: e.target.value }))} className="w-full rounded-xl border border-zinc-800 bg-zinc-950/80 px-3 py-2 text-sm text-white" placeholder="e.g. Custom Metal Pet Tags" /></label>
            <label className="block"><div className="mb-1 text-xs uppercase tracking-[0.16em] text-zinc-500">Description</div>
              <input value={famForm.description} onChange={(e) => setFamForm((s) => ({ ...s, description: e.target.value }))} className="w-full rounded-xl border border-zinc-800 bg-zinc-950/80 px-3 py-2 text-sm text-white" /></label>
            <label className="block"><div className="mb-1 text-xs uppercase tracking-[0.16em] text-zinc-500">Material Cost ($)</div>
              <input type="number" value={famForm.material_cost_per_unit} onChange={(e) => setFamForm((s) => ({ ...s, material_cost_per_unit: e.target.value }))} className="w-full rounded-xl border border-zinc-800 bg-zinc-950/80 px-3 py-2 text-sm text-white" /></label>
            <label className="block"><div className="mb-1 text-xs uppercase tracking-[0.16em] text-zinc-500">Est. Sale Price ($)</div>
              <input type="number" value={famForm.estimated_sale_price} onChange={(e) => setFamForm((s) => ({ ...s, estimated_sale_price: e.target.value }))} className="w-full rounded-xl border border-zinc-800 bg-zinc-950/80 px-3 py-2 text-sm text-white" /></label>
            <div className="md:col-span-2 flex justify-end"><button type="submit" className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-sm rounded-lg">Add Family</button></div>
          </form>
        )}

        {product_families.length === 0 ? (
          <p className="text-zinc-500 text-sm py-4 text-center">No product families yet</p>
        ) : (
          <div className="space-y-3">
            {product_families.map((fam) => (
              <div key={fam.id} className="bg-zinc-950/60 rounded-xl p-4">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-medium text-white">{fam.name}</h4>
                  <div className="flex items-center gap-2">
                    <span className={`inline-flex items-center px-2 py-0.5 text-xs font-medium border rounded-full ${MACHINE_STATUS_COLORS[fam.status] || ''}`}>
                      {fam.status}
                    </span>
                    {fam.status !== 'PROMOTED_TO_PRODUCT' && (
                      <button onClick={() => handlePromote(fam.id)} className="text-xs text-indigo-400 hover:text-indigo-300">Promote</button>
                    )}
                  </div>
                </div>
                {fam.description && <p className="text-zinc-400 text-sm mb-2">{fam.description}</p>}
                <div className="flex gap-4 text-xs text-zinc-500">
                  <span>Material: {money(fam.material_cost_per_unit)}</span>
                  <span>Sale: {money(fam.estimated_sale_price)}</span>
                  <span>{fam.market_evidence_count} evidence</span>
                </div>

                {/* Cost scenarios for this family */}
                {cost_scenarios.filter((s) => s.product_family_id === fam.id).length > 0 && (
                  <div className="mt-3 pt-3 border-t border-zinc-800">
                    <div className="text-xs uppercase tracking-[0.16em] text-zinc-500 mb-2">Cost Scenarios</div>
                    {cost_scenarios.filter((s) => s.product_family_id === fam.id).map((sc) => (
                      <div key={sc.id} className="flex items-center gap-4 text-xs text-zinc-400 py-1">
                        <span className="text-white">{sc.scenario_name}</span>
                        <span>Cost: {money(sc.total_cost_per_unit)}</span>
                        <span>Sale: {money(sc.sale_price)}</span>
                        <span>Profit: {money(sc.net_profit_per_unit)}</span>
                        <span>Margin: {sc.margin_percent != null ? `${Number(sc.margin_percent).toFixed(1)}%` : '—'}</span>
                        <span>Payback: {sc.payback_months != null ? `${Number(sc.payback_months).toFixed(0)}mo` : '—'}</span>
                      </div>
                    ))}
                  </div>
                )}

                {/* Add scenario button */}
                {showAddScenario ? (
                  <form onSubmit={(e) => handleAddScenario(fam.id, e)} className="mt-3 pt-3 border-t border-zinc-800 grid gap-2 md:grid-cols-3">
                    <input value={scenForm.scenario_name} onChange={(e) => setScenForm((s) => ({ ...s, scenario_name: e.target.value }))} placeholder="Scenario name" className="rounded-lg border border-zinc-800 bg-zinc-950/80 px-2 py-1.5 text-xs text-white" />
                    <input type="number" value={scenForm.material_cost} onChange={(e) => setScenForm((s) => ({ ...s, material_cost: e.target.value }))} placeholder="Material cost" className="rounded-lg border border-zinc-800 bg-zinc-950/80 px-2 py-1.5 text-xs text-white" />
                    <input type="number" value={scenForm.sale_price} onChange={(e) => setScenForm((s) => ({ ...s, sale_price: e.target.value }))} placeholder="Sale price" className="rounded-lg border border-zinc-800 bg-zinc-950/80 px-2 py-1.5 text-xs text-white" />
                    <input type="number" value={scenForm.labor_cost} onChange={(e) => setScenForm((s) => ({ ...s, labor_cost: e.target.value }))} placeholder="Labor cost" className="rounded-lg border border-zinc-800 bg-zinc-950/80 px-2 py-1.5 text-xs text-white" />
                    <input type="number" value={scenForm.units_per_month} onChange={(e) => setScenForm((s) => ({ ...s, units_per_month: e.target.value }))} placeholder="Units/month" className="rounded-lg border border-zinc-800 bg-zinc-950/80 px-2 py-1.5 text-xs text-white" />
                    <input type="number" value={scenForm.machine_purchase_price} onChange={(e) => setScenForm((s) => ({ ...s, machine_purchase_price: e.target.value }))} placeholder="Machine price" className="rounded-lg border border-zinc-800 bg-zinc-950/80 px-2 py-1.5 text-xs text-white" />
                    <div className="md:col-span-3 flex justify-end gap-2">
                      <button type="button" onClick={() => setShowAddScenario(false)} className="text-xs text-zinc-400">Cancel</button>
                      <button type="submit" className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white text-xs rounded-lg">Save</button>
                    </div>
                  </form>
                ) : (
                  <button onClick={() => setShowAddScenario(true)} className="mt-2 text-xs text-indigo-400 hover:text-indigo-300">+ Add Cost Scenario</button>
                )}
              </div>
            ))}
          </div>
        )}
      </Panel>
    </div>
  );
}

function StatCard({ label, value, icon }: { label: string; value: string; icon?: React.ReactNode }) {
  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-3">
      <div className="flex items-center gap-1.5 text-zinc-500 text-xs mb-1">{icon}{label}</div>
      <div className="text-white font-medium text-sm">{value}</div>
    </div>
  );
}

function Panel({ title, icon, action, children }: { title: string; icon?: React.ReactNode; action?: React.ReactNode; children: React.ReactNode }) {
  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-5">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2 text-xs uppercase tracking-[0.18em] text-zinc-500">
          {icon}{title}
        </div>
        {action}
      </div>
      {children}
    </div>
  );
}
