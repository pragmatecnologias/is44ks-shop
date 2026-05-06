'use client';

import { useEffect, useState } from 'react';
import { RefreshCw, Sparkles } from 'lucide-react';
import { getOpportunityBoard } from '@/lib/api';
import type { OpportunityBoardRow } from '@/lib/types';

export default function OpportunitiesPage() {
  const [rows, setRows] = useState<OpportunityBoardRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    async function load() {
      setLoading(true);
      setError(null);
      try {
        const data = await getOpportunityBoard();
        if (mounted) setRows(data);
      } catch (err) {
        if (mounted) setError(err instanceof Error ? err.message : 'Failed to load opportunity board');
      } finally {
        if (mounted) setLoading(false);
      }
    }
    load();
    return () => {
      mounted = false;
    };
  }, []);

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
          <div className="flex items-center justify-between gap-4">
            <div>
              <div className="flex items-center gap-2">
                <Sparkles className="h-5 w-5 text-indigo-400" />
                <h1 className="text-3xl font-semibold tracking-tight text-white">Opportunity Board</h1>
              </div>
              <p className="mt-2 text-sm text-zinc-400">
                Compare rough ideas and full products by research completeness, evidence, risk, and next action.
              </p>
            </div>
            <div className="rounded-2xl border border-zinc-800 bg-zinc-950/60 px-4 py-3 text-sm text-zinc-300">
              {rows.length} rows
            </div>
          </div>
        </header>

        {error ? (
          <div className="rounded-2xl border border-red-500/20 bg-red-500/10 p-4 text-sm text-red-100">
            {error}
          </div>
        ) : null}

        <section className="rounded-[24px] border border-zinc-800 bg-zinc-950/80 p-5 shadow-xl shadow-black/10">
          <div className="overflow-hidden rounded-2xl border border-zinc-800">
            <table className="w-full text-left text-sm">
              <thead className="bg-zinc-950/90 text-xs uppercase tracking-[0.14em] text-zinc-500">
                <tr>
                  <th className="px-4 py-3">Title</th>
                  <th className="px-4 py-3">Type</th>
                  <th className="px-4 py-3">Progress</th>
                  <th className="px-4 py-3">Verdict</th>
                  <th className="px-4 py-3">Evidence</th>
                  <th className="px-4 py-3">Market</th>
                  <th className="px-4 py-3">Competition</th>
                  <th className="px-4 py-3">Cost</th>
                  <th className="px-4 py-3">Next Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-800">
                {rows.map((row) => (
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
                    <td className="px-4 py-3 text-zinc-300">{row.research_verdict || row.status || '—'}</td>
                    <td className="px-4 py-3 text-zinc-300">
                      {row.entity_type === 'product' ? (
                        <div>
                          <div>{row.sold_evidence_count_verified ?? row.sold_evidence_count} sold / {row.active_evidence_count_verified ?? row.active_evidence_count} active verified</div>
                          {(row.sold_evidence_count !== row.sold_evidence_count_verified || row.active_evidence_count !== row.active_evidence_count_verified) ? (
                            <div className="text-xs text-zinc-500">{row.sold_evidence_count} sold / {row.active_evidence_count} active total</div>
                          ) : null}
                          {(row.test_data_count ?? 0) > 0 ? (
                            <div className="text-xs text-red-400">{row.test_data_count} test data item{((row.test_data_count ?? 0) > 1) ? 's' : ''}</div>
                          ) : null}
                          {(row.unverified_evidence_count ?? 0) > 0 && (row.test_data_count ?? 0) === 0 ? (
                            <div className="text-xs text-yellow-400">{row.unverified_evidence_count} unverified — does not count toward readiness</div>
                          ) : null}
                        </div>
                      ) : (
                        <div>0 sold / 0 active</div>
                      )}
                    </td>
                    <td className="px-4 py-3 text-zinc-300">
                      {row.entity_type === 'product' ? (
                        <div>
                          <div>{row.median_sold_price != null ? `Sold ${money(row.median_sold_price)}` : 'Sold —'}</div>
                          <div className="text-xs text-zinc-500">
                            {row.median_active_price != null ? `Active ${money(row.median_active_price)}` : 'Active —'}
                          </div>
                          {(row.median_sold_price_total != null && row.median_sold_price != null && row.median_sold_price_total !== row.median_sold_price) ? (
                            <div className="text-xs text-zinc-500">Sold total: {money(row.median_sold_price_total)}</div>
                          ) : null}
                          {(row.median_active_price_total != null && row.median_active_price != null && row.median_active_price_total !== row.median_active_price) ? (
                            <div className="text-xs text-zinc-500">Active total: {money(row.median_active_price_total)}</div>
                          ) : null}
                          <div className="text-xs text-zinc-500">
                            {row.median_shipping != null
                              ? `Ship ${money(row.median_shipping)}`
                              : row.median_sold_shipping != null
                                ? `Ship ${money(row.median_sold_shipping)}`
                                : row.median_active_shipping != null
                                  ? `Ship ${money(row.median_active_shipping)}`
                                  : 'Ship —'}
                          </div>
                        </div>
                      ) : (
                        <div>
                          <div>Sold —</div>
                          <div className="text-xs text-zinc-500">Active —</div>
                        </div>
                      )}
                    </td>
                    <td className="px-4 py-3 text-zinc-300">
                      {row.competition_gap_score != null ? `${row.competition_gap_score}/100` : '—'}
                    </td>
                    <td className="px-4 py-3 text-zinc-300">{money(row.best_landed_cost)}</td>
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

function money(value?: number | null) {
  if (value == null) return '—';
  return `$${Number(value).toFixed(2)}`;
}
