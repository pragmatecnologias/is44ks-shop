'use client';

import { useEffect, useMemo, useState } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { Loader2, Plus, RefreshCw, Sparkles } from 'lucide-react';
import {
  addPortfolioItem,
  createProductCollection,
  getShopConcept,
  getShopPortfolioReport,
  updatePortfolioItem,
  updateShopConcept,
} from '@/lib/api';
import type {
  PortfolioItem,
  PortfolioItemStatus,
  PortfolioRole,
  ShopConceptDetail,
  ShopPortfolioReport,
} from '@/lib/types';

type CollectionForm = {
  name: string;
  theme: string;
  target_problem: string;
  description: string;
  status: string;
};

type ItemForm = {
  collection_id: string;
  idea_id: string;
  product_id: string;
  role: PortfolioRole;
  status: PortfolioItemStatus;
  assortment_fit_score: string;
  bundle_potential_score: string;
  notes: string;
};

const DEFAULT_COLLECTION_FORM: CollectionForm = {
  name: '',
  theme: '',
  target_problem: '',
  description: '',
  status: 'DRAFT',
};

const DEFAULT_ITEM_FORM: ItemForm = {
  collection_id: '',
  idea_id: '',
  product_id: '',
  role: 'HERO',
  status: 'CONSIDERING',
  assortment_fit_score: '0',
  bundle_potential_score: '0',
  notes: '',
};

export default function ShopConceptDetailPage() {
  const params = useParams<{ id: string }>();
  const shopId = params.id;
  const [detail, setDetail] = useState<ShopConceptDetail | null>(null);
  const [report, setReport] = useState<ShopPortfolioReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [collectionForm, setCollectionForm] = useState<CollectionForm>(DEFAULT_COLLECTION_FORM);
  const [itemForm, setItemForm] = useState<ItemForm>(DEFAULT_ITEM_FORM);

  async function loadDetail() {
    if (!shopId) return;
    setLoading(true);
    setError(null);
    try {
      const data = await getShopConcept(shopId);
      setDetail(data);
      setReport(data.report);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load shop concept');
      setDetail(null);
      setReport(null);
    } finally {
      setLoading(false);
    }
  }

  async function refreshReport() {
    if (!shopId) return;
    setSaving(true);
    setError(null);
    try {
      setReport(await getShopPortfolioReport(shopId));
      await loadDetail();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to refresh portfolio report');
    } finally {
      setSaving(false);
    }
  }

  useEffect(() => {
    loadDetail();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [shopId]);

  async function handleAddCollection() {
    if (!shopId || !collectionForm.name.trim()) return;
    setSaving(true);
    setError(null);
    try {
      await createProductCollection(shopId, {
        name: collectionForm.name,
        theme: collectionForm.theme || undefined,
        target_problem: collectionForm.target_problem || undefined,
        description: collectionForm.description || undefined,
        status: collectionForm.status || 'DRAFT',
      });
      setCollectionForm(DEFAULT_COLLECTION_FORM);
      await loadDetail();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create collection');
    } finally {
      setSaving(false);
    }
  }

  async function handleAddItem() {
    if (!shopId || (!itemForm.idea_id.trim() && !itemForm.product_id.trim())) return;
    setSaving(true);
    setError(null);
    try {
      await addPortfolioItem(shopId, {
        collection_id: itemForm.collection_id || undefined,
        idea_id: itemForm.idea_id || undefined,
        product_id: itemForm.product_id || undefined,
        role: itemForm.role,
        status: itemForm.status,
        assortment_fit_score: Number(itemForm.assortment_fit_score || 0),
        bundle_potential_score: Number(itemForm.bundle_potential_score || 0),
        notes: itemForm.notes || undefined,
      });
      setItemForm(DEFAULT_ITEM_FORM);
      await loadDetail();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create portfolio item');
    } finally {
      setSaving(false);
    }
  }

  async function handleSaveShopStatus(nextStatus: string) {
    if (!shopId || !detail) return;
    setSaving(true);
    setError(null);
    try {
      await updateShopConcept(shopId, { status: nextStatus });
      await loadDetail();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update shop concept');
    } finally {
      setSaving(false);
    }
  }

  async function handlePromoteItem(item: PortfolioItem) {
    if (!item.product_id && !item.idea_id) return;
    setSaving(true);
    setError(null);
    try {
      await updatePortfolioItem(item.id, {
        status: 'RESEARCHING',
        notes: item.notes ?? undefined,
      });
      await loadDetail();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update portfolio item');
    } finally {
      setSaving(false);
    }
  }

  const portfolioItems = detail?.portfolio_items ?? [];
  const collections = detail?.collections ?? [];
  const byRole = useMemo(() => report?.items_by_role ?? {}, [report?.items_by_role]);
  const byStatus = useMemo(() => report?.items_by_status ?? {}, [report?.items_by_status]);

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
        <div className="rounded-2xl border border-red-500/20 bg-red-500/10 p-4">Shop concept not found.</div>
      </div>
    );
  }

  const { shop_concept } = detail;

  return (
    <div className="p-6">
      <div className="mx-auto max-w-[1440px] space-y-6">
        <header className="rounded-[28px] border border-zinc-800 bg-zinc-950/80 p-6 shadow-2xl shadow-black/20">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div>
              <div className="flex items-center gap-2">
                <Sparkles className="h-5 w-5 text-indigo-400" />
                <h1 className="text-3xl font-semibold tracking-tight text-white">{shop_concept.name}</h1>
              </div>
              <p className="mt-2 text-sm text-zinc-400">
                {shop_concept.category || 'Uncategorized'} · {shop_concept.status}
              </p>
              <p className="mt-2 max-w-4xl text-sm text-zinc-300">{shop_concept.brand_angle || shop_concept.description || 'No shop summary recorded.'}</p>
            </div>
            <div className="flex flex-wrap gap-3 text-xs text-zinc-300">
              <Pill label={`Collections ${shop_concept.collection_count ?? collections.length}`} />
              <Pill label={`Items ${shop_concept.portfolio_item_count ?? portfolioItems.length}`} />
              <Pill label={`Campaigns ${shop_concept.campaign_count ?? 0}`} />
            </div>
          </div>
          <div className="mt-4 flex flex-wrap gap-3">
            <Link href="/portfolio" className="rounded-xl border border-zinc-700 bg-zinc-900 px-4 py-2 text-sm text-zinc-200 hover:border-zinc-600">
              Back to portfolio
            </Link>
            <button
              type="button"
              onClick={refreshReport}
              className="rounded-xl border border-indigo-500/30 bg-indigo-500/10 px-4 py-2 text-sm text-indigo-200 hover:bg-indigo-500/20"
            >
              Refresh report
            </button>
            <button
              type="button"
              onClick={() => handleSaveShopStatus(shop_concept.status === 'ACTIVE' ? 'PAUSED' : 'ACTIVE')}
              className="rounded-xl border border-zinc-700 bg-zinc-900 px-4 py-2 text-sm text-zinc-200 hover:border-zinc-600"
            >
              {shop_concept.status === 'ACTIVE' ? 'Pause shop' : 'Activate shop'}
            </button>
          </div>
        </header>

        {error ? <div className="rounded-2xl border border-red-500/20 bg-red-500/10 p-4 text-sm text-red-100">{error}</div> : null}

        <section className="grid gap-3 md:grid-cols-4">
          <Metric label="Total items" value={String(report?.total_items ?? portfolioItems.length)} />
          <Metric label="Hero items" value={String(byRole.HERO ?? 0)} />
          <Metric label="Add-ons" value={String((byRole.ADD_ON ?? 0) + (byRole.BUNDLE_SUPPORT ?? 0))} />
          <Metric label="Ready for sample" value={String((report?.ready_for_sample_products ?? []).length)} />
        </section>

        <section className="rounded-[24px] border border-zinc-800 bg-zinc-950/80 p-5 shadow-xl shadow-black/10">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <div className="text-xs uppercase tracking-[0.16em] text-zinc-500">Shop readiness</div>
              <div className="mt-1 text-lg font-semibold text-white">{report?.shop_readiness_status ?? 'UNKNOWN'}</div>
            </div>
            <div className="text-right text-sm text-zinc-300">
              <div>Score {report?.shop_readiness_score ?? 0}/100</div>
              <div>{report?.next_recommended_campaign || 'No recommended campaign yet'}</div>
            </div>
          </div>
          <div className="mt-4 grid gap-3 md:grid-cols-2">
            <div className="rounded-2xl border border-zinc-800 bg-zinc-950/60 p-4">
              <div className="text-xs uppercase tracking-[0.16em] text-zinc-500">Blockers</div>
              <div className="mt-2 space-y-2 text-sm text-zinc-300">
                {(report?.shop_readiness_blockers?.length ? report.shop_readiness_blockers : ['No shop readiness blockers recorded.']).map((blocker) => (
                  <div key={blocker} className="rounded-xl border border-zinc-800 bg-zinc-950/80 px-3 py-2">
                    {blocker}
                  </div>
                ))}
              </div>
            </div>
            <div className="rounded-2xl border border-zinc-800 bg-zinc-950/60 p-4">
              <div className="text-xs uppercase tracking-[0.16em] text-zinc-500">Portfolio context</div>
              <div className="mt-2 space-y-2 text-sm text-zinc-300">
                <div>Collections: {collections.length}</div>
                <div>Portfolio items: {portfolioItems.length}</div>
                <div>Sample-ready products: {(report?.ready_for_sample_products ?? []).length}</div>
                <div>{report?.next_action || 'No next action recorded.'}</div>
              </div>
            </div>
          </div>
        </section>

        <section className="rounded-[24px] border border-zinc-800 bg-zinc-950/80 p-5 shadow-xl shadow-black/10">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <div className="text-xs uppercase tracking-[0.16em] text-zinc-500">Portfolio gaps</div>
              <div className="mt-1 text-lg font-semibold text-white">
                {(report?.collection_gaps?.length ?? 0) > 0 ? `${report?.collection_gaps?.length} gaps` : 'No major gaps flagged'}
              </div>
            </div>
            <div className="text-right text-sm text-zinc-300">
              <div>Items by status: {formatCounts(byStatus)}</div>
              <div>Products by decision: {formatCounts(report?.products_by_decision ?? {})}</div>
            </div>
          </div>
          <div className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
            {(report?.collection_gaps?.length ? report.collection_gaps : ['No portfolio gaps recorded.']).map((gap) => (
              <div key={gap} className="rounded-2xl border border-zinc-800 bg-zinc-950/60 p-4 text-sm text-zinc-300">
                {gap}
              </div>
            ))}
          </div>
          <div className="mt-4 rounded-2xl border border-zinc-800 bg-zinc-950/60 p-4">
            <div className="text-xs uppercase tracking-[0.16em] text-zinc-500">Next action</div>
            <div className="mt-2 text-sm text-zinc-200">{report?.next_action || 'Review the shop portfolio.'}</div>
            <div className="mt-2 text-xs text-zinc-500">{report?.next_recommended_campaign || 'No recommended campaign yet.'}</div>
          </div>
        </section>

        <div className="grid gap-6 xl:grid-cols-2">
          <section className="rounded-[24px] border border-zinc-800 bg-zinc-950/80 p-5 shadow-xl shadow-black/10">
            <div className="mb-4 flex items-center gap-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-xl border border-zinc-800 bg-zinc-900 text-zinc-300">
                <Plus className="h-4 w-4" />
              </div>
              <h2 className="text-sm font-semibold uppercase tracking-[0.18em] text-zinc-200">Create Collection</h2>
            </div>
            <div className="space-y-3">
              <Field label="Name" value={collectionForm.name} onChange={(value) => setCollectionForm((current) => ({ ...current, name: value }))} />
              <Field label="Theme" value={collectionForm.theme} onChange={(value) => setCollectionForm((current) => ({ ...current, theme: value }))} />
              <Field label="Target problem" value={collectionForm.target_problem} onChange={(value) => setCollectionForm((current) => ({ ...current, target_problem: value }))} />
              <Field label="Status" value={collectionForm.status} onChange={(value) => setCollectionForm((current) => ({ ...current, status: value }))} />
              <Textarea label="Description" value={collectionForm.description} onChange={(value) => setCollectionForm((current) => ({ ...current, description: value }))} />
            </div>
            <div className="mt-4 flex justify-end">
              <button
                type="button"
                onClick={handleAddCollection}
                disabled={saving || !collectionForm.name.trim()}
                className="inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-indigo-500 disabled:opacity-60"
              >
                {saving ? <Loader2 className="h-4 w-4 animate-spin" /> : <Plus className="h-4 w-4" />}
                Add Collection
              </button>
            </div>
          </section>

          <section className="rounded-[24px] border border-zinc-800 bg-zinc-950/80 p-5 shadow-xl shadow-black/10">
            <div className="mb-4 flex items-center gap-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-xl border border-zinc-800 bg-zinc-900 text-zinc-300">
                <Plus className="h-4 w-4" />
              </div>
              <h2 className="text-sm font-semibold uppercase tracking-[0.18em] text-zinc-200">Add Portfolio Item</h2>
            </div>
            <div className="space-y-3">
              <Field label="Collection ID" value={itemForm.collection_id} onChange={(value) => setItemForm((current) => ({ ...current, collection_id: value }))} />
              <Field label="Idea ID" value={itemForm.idea_id} onChange={(value) => setItemForm((current) => ({ ...current, idea_id: value }))} />
              <Field label="Product ID" value={itemForm.product_id} onChange={(value) => setItemForm((current) => ({ ...current, product_id: value }))} />
              <Field label="Role" value={itemForm.role} onChange={(value) => setItemForm((current) => ({ ...current, role: value as PortfolioRole }))} />
              <Field label="Status" value={itemForm.status} onChange={(value) => setItemForm((current) => ({ ...current, status: value as PortfolioItemStatus }))} />
              <Field label="Assortment fit score" type="number" value={itemForm.assortment_fit_score} onChange={(value) => setItemForm((current) => ({ ...current, assortment_fit_score: value }))} />
              <Field label="Bundle potential score" type="number" value={itemForm.bundle_potential_score} onChange={(value) => setItemForm((current) => ({ ...current, bundle_potential_score: value }))} />
              <Textarea label="Notes" value={itemForm.notes} onChange={(value) => setItemForm((current) => ({ ...current, notes: value }))} />
            </div>
            <div className="mt-4 flex justify-end">
              <button
                type="button"
                onClick={handleAddItem}
                disabled={saving || (!itemForm.idea_id.trim() && !itemForm.product_id.trim())}
                className="inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-indigo-500 disabled:opacity-60"
              >
                {saving ? <Loader2 className="h-4 w-4 animate-spin" /> : <Plus className="h-4 w-4" />}
                Add Item
              </button>
            </div>
          </section>
        </div>

        <div className="grid gap-6 xl:grid-cols-2">
          <section className="rounded-[24px] border border-zinc-800 bg-zinc-950/80 p-5 shadow-xl shadow-black/10">
            <div className="mb-4 flex items-center justify-between gap-3">
              <h2 className="text-sm font-semibold uppercase tracking-[0.18em] text-zinc-200">Collections</h2>
              <div className="text-xs text-zinc-500">{collections.length} collections</div>
            </div>
            <div className="space-y-3">
              {collections.length ? (
                collections.map((collection) => (
                  <div key={collection.id} className="rounded-2xl border border-zinc-800 bg-zinc-950/60 p-4">
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <div className="text-sm font-medium text-white">{collection.name}</div>
                        <div className="text-xs text-zinc-500">{collection.theme || 'No theme'} · {collection.status}</div>
                        <div className="mt-2 text-sm text-zinc-300">{collection.target_problem || collection.description || 'No target problem recorded.'}</div>
                      </div>
                      <div className="text-right text-xs text-zinc-400">
                        <div>Items {collection.portfolio_item_count ?? 0}</div>
                        <div>Products {collection.product_count ?? 0}</div>
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <EmptyState title="No collections yet" description="Add a collection to group related products and ideas." />
              )}
            </div>
          </section>

          <section className="rounded-[24px] border border-zinc-800 bg-zinc-950/80 p-5 shadow-xl shadow-black/10">
            <div className="mb-4 flex items-center justify-between gap-3">
              <h2 className="text-sm font-semibold uppercase tracking-[0.18em] text-zinc-200">Portfolio Items</h2>
              <div className="text-xs text-zinc-500">{portfolioItems.length} items</div>
            </div>
            <div className="space-y-3">
              {portfolioItems.length ? (
                portfolioItems.map((item) => (
                  <div key={item.id} className="rounded-2xl border border-zinc-800 bg-zinc-950/60 p-4">
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <div className="text-sm font-medium text-white">
                          {item.product_name || item.idea_name || 'Untitled portfolio item'}
                        </div>
                        <div className="text-xs text-zinc-500">
                          {item.role} · {item.status}
                          {item.collection_name ? ` · ${item.collection_name}` : ''}
                        </div>
                      </div>
                      <div className="text-right text-xs text-zinc-400">
                        <div>Fit {item.assortment_fit_score}</div>
                        <div>Bundle {item.bundle_potential_score}</div>
                      </div>
                    </div>
                    <div className="mt-2 text-sm text-zinc-300">
                      {item.notes || 'No notes recorded.'}
                    </div>
                    <div className="mt-3 flex justify-end">
                      <button
                        type="button"
                        onClick={() => handlePromoteItem(item)}
                        className="rounded-lg border border-zinc-700 bg-zinc-900 px-3 py-1.5 text-xs text-zinc-200 hover:border-zinc-600"
                      >
                        Mark research progress
                      </button>
                    </div>
                  </div>
                ))
              ) : (
                <EmptyState title="No portfolio items yet" description="Add existing ideas or products to the shop portfolio." />
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

function Textarea(props: { label: string; value: string; onChange: (value: string) => void }) {
  return (
    <label className="block">
      <div className="mb-1 text-xs uppercase tracking-[0.16em] text-zinc-500">{props.label}</div>
      <textarea
        value={props.value}
        onChange={(event) => props.onChange(event.target.value)}
        rows={4}
        className="w-full rounded-xl border border-zinc-800 bg-zinc-950/80 px-3 py-2 text-sm text-white outline-none transition focus:border-indigo-500/50"
      />
    </label>
  );
}

function Pill({ label }: { label: string }) {
  return <span className="rounded-full border border-zinc-800 bg-zinc-900 px-3 py-1">{label}</span>;
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-zinc-800 bg-zinc-950/80 p-4">
      <div className="text-[10px] uppercase tracking-[0.16em] text-zinc-500">{label}</div>
      <div className="mt-2 text-2xl font-semibold text-white">{value}</div>
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

function formatCounts(counts: Record<string, number> | undefined) {
  if (!counts || !Object.keys(counts).length) return 'None';
  return Object.entries(counts)
    .map(([key, value]) => `${key}: ${value}`)
    .join(' · ');
}
