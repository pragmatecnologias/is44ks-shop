'use client';

import { useEffect, useMemo, useState } from 'react';
import Link from 'next/link';
import { Loader2, Plus, RefreshCw, Sparkles } from 'lucide-react';
import { createShopConcept, listShopConcepts } from '@/lib/api';
import type { ShopConcept } from '@/lib/types';

type FormState = {
  name: string;
  description: string;
  target_customer: string;
  category: string;
  price_min: string;
  price_max: string;
  brand_angle: string;
  status: string;
  avoid_text: string;
  preferred_text: string;
};

const DEFAULT_FORM: FormState = {
  name: 'Practical Pet Home',
  description: 'A coherent small shop for practical pet home products.',
  target_customer: 'Pet owners who want cleaner homes and easier pet care.',
  category: 'Pet accessories',
  price_min: '12',
  price_max: '39',
  brand_angle: 'Cleaner home, happier pet.',
  status: 'DRAFT',
  avoid_text: JSON.stringify(['medicine', 'supplements', 'ingestibles', 'flea/tick', 'electric/shock', 'bulky products'], null, 2),
  preferred_text: JSON.stringify(['small', 'lightweight', 'easy to demonstrate', 'reusable'], null, 2),
};

export default function PortfolioPage() {
  const [shops, setShops] = useState<ShopConcept[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState<FormState>(DEFAULT_FORM);

  async function loadShops() {
    setLoading(true);
    setError(null);
    try {
      setShops(await listShopConcepts());
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load shop concepts');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadShops();
  }, []);

  async function handleCreate() {
    setSaving(true);
    setError(null);
    try {
      await createShopConcept({
        name: form.name,
        description: form.description || undefined,
        target_customer: form.target_customer || undefined,
        category: form.category || undefined,
        price_min: form.price_min ? Number(form.price_min) : undefined,
        price_max: form.price_max ? Number(form.price_max) : undefined,
        avoid_list_json: parseJson(form.avoid_text),
        preferred_attributes_json: parseJson(form.preferred_text),
        brand_angle: form.brand_angle || undefined,
        status: form.status || 'DRAFT',
      });
      setForm(DEFAULT_FORM);
      await loadShops();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create shop concept');
    } finally {
      setSaving(false);
    }
  }

  const activeCount = useMemo(() => shops.filter((shop) => shop.status === 'ACTIVE').length, [shops]);

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
                <h1 className="text-3xl font-semibold tracking-tight text-white">Shop Portfolio</h1>
              </div>
              <p className="mt-2 text-sm text-zinc-400">
                Define shop concepts, then attach campaigns, collections, and portfolio items to build a coherent assortment.
              </p>
            </div>
            <div className="flex flex-wrap gap-3 text-xs text-zinc-300">
              <Pill label={`Shop concepts: ${shops.length}`} />
              <Pill label={`Active: ${activeCount}`} />
            </div>
          </div>
        </header>

        {error ? <div className="rounded-2xl border border-red-500/20 bg-red-500/10 p-4 text-sm text-red-100">{error}</div> : null}

        <div className="grid gap-6 xl:grid-cols-[1fr_1.2fr]">
          <section className="rounded-[24px] border border-zinc-800 bg-zinc-950/80 p-5 shadow-xl shadow-black/10">
            <div className="mb-4 flex items-center gap-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-xl border border-zinc-800 bg-zinc-900 text-zinc-300">
                <Plus className="h-4 w-4" />
              </div>
              <h2 className="text-sm font-semibold uppercase tracking-[0.18em] text-zinc-200">Create Shop Concept</h2>
            </div>
            <div className="space-y-3">
              <Field label="Name" value={form.name} onChange={(value) => setForm((current) => ({ ...current, name: value }))} />
              <Field label="Target customer" value={form.target_customer} onChange={(value) => setForm((current) => ({ ...current, target_customer: value }))} />
              <Field label="Category" value={form.category} onChange={(value) => setForm((current) => ({ ...current, category: value }))} />
              <Field label="Brand angle" value={form.brand_angle} onChange={(value) => setForm((current) => ({ ...current, brand_angle: value }))} />
              <Field label="Price min" type="number" value={form.price_min} onChange={(value) => setForm((current) => ({ ...current, price_min: value }))} />
              <Field label="Price max" type="number" value={form.price_max} onChange={(value) => setForm((current) => ({ ...current, price_max: value }))} />
              <Field label="Status" value={form.status} onChange={(value) => setForm((current) => ({ ...current, status: value }))} />
              <Textarea label="Description" value={form.description} onChange={(value) => setForm((current) => ({ ...current, description: value }))} />
              <Textarea label="Avoid list JSON" value={form.avoid_text} onChange={(value) => setForm((current) => ({ ...current, avoid_text: value }))} />
              <Textarea label="Preferred attributes JSON" value={form.preferred_text} onChange={(value) => setForm((current) => ({ ...current, preferred_text: value }))} />
            </div>
            <div className="mt-4 flex justify-end">
              <button
                type="button"
                onClick={handleCreate}
                disabled={saving || !form.name.trim()}
                className="inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-indigo-500 disabled:opacity-60"
              >
                {saving ? <Loader2 className="h-4 w-4 animate-spin" /> : <Plus className="h-4 w-4" />}
                Create Concept
              </button>
            </div>
          </section>

          <section className="rounded-[24px] border border-zinc-800 bg-zinc-950/80 p-5 shadow-xl shadow-black/10">
            <div className="mb-4 flex items-center justify-between gap-3">
              <div className="flex items-center gap-2">
                <div className="flex h-8 w-8 items-center justify-center rounded-xl border border-zinc-800 bg-zinc-900 text-zinc-300">
                  <Sparkles className="h-4 w-4" />
                </div>
                <h2 className="text-sm font-semibold uppercase tracking-[0.18em] text-zinc-200">Concept Queue</h2>
              </div>
              <button
                type="button"
                onClick={loadShops}
                className="rounded-lg border border-zinc-700 bg-zinc-900 px-3 py-1.5 text-xs text-zinc-300 hover:border-zinc-600"
              >
                Refresh
              </button>
            </div>

            <div className="space-y-3">
              {shops.length ? (
                shops.map((shop) => (
                  <Link
                    key={shop.id}
                    href={`/portfolio/${shop.id}`}
                    className="block rounded-2xl border border-zinc-800 bg-zinc-950/60 p-4 transition hover:border-zinc-700 hover:bg-zinc-900/40"
                  >
                    <div className="flex flex-wrap items-start justify-between gap-3">
                      <div>
                        <div className="text-base font-medium text-white">{shop.name}</div>
                        <div className="text-xs text-zinc-500">
                          {shop.category || 'Uncategorized'} · {shop.status}
                        </div>
                        <div className="mt-2 text-sm text-zinc-300">{shop.brand_angle || shop.description || 'No summary recorded.'}</div>
                      </div>
                      <div className="text-right text-xs text-zinc-400">
                        <div>Collections {shop.collection_count ?? 0}</div>
                        <div>Portfolio items {shop.portfolio_item_count ?? 0}</div>
                      </div>
                    </div>
                    <div className="mt-3 grid grid-cols-4 gap-2 text-xs text-zinc-300">
                      <Stat label="Campaigns" value={String(shop.campaign_count ?? 0)} />
                      <Stat label="Ideas" value={String(shop.idea_count ?? 0)} />
                      <Stat label="Products" value={String(shop.product_count ?? 0)} />
                      <Stat label="Items" value={String(shop.portfolio_item_count ?? 0)} />
                    </div>
                  </Link>
                ))
              ) : (
                <EmptyState title="No shop concepts yet" description="Create the first shop concept to anchor campaigns and collections." />
              )}
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}

function parseJson(value: string): Record<string, unknown> {
  try {
    return value.trim() ? JSON.parse(value) : {};
  } catch {
    return {};
  }
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
