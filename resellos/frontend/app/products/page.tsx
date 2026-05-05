'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import {
  Plus,
  Search,
  RefreshCw,
  FileUp,
  Brain,
  Eye,
  Archive,
  Copy,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';
import { StatusBadge } from '@/components/shared/StatusBadge';
import { RiskBadge } from '@/components/shared/RiskBadge';
import { getProducts } from '@/lib/api';
import type { Product, ProductStatus } from '@/lib/types';

const ITEMS_PER_PAGE = 10;

const ACTION_BUTTONS = [
  { label: 'Create', icon: Plus, color: 'text-indigo-400' },
  { label: 'Import', icon: FileUp, color: 'text-slate-400' },
  { label: 'Run Research', icon: Brain, color: 'text-purple-400' },
  { label: 'View Report', icon: Eye, color: 'text-blue-400' },
  { label: 'Archive', icon: Archive, color: 'text-slate-400' },
  { label: 'Duplicate', icon: Copy, color: 'text-slate-400' },
];

const STATUS_OPTIONS: Array<{ value: string; label: string }> = [
  { value: '', label: 'All Statuses' },
  { value: 'NEW', label: 'New' },
  { value: 'NEEDS_RESEARCH', label: 'Needs Research' },
  { value: 'RESEARCHING', label: 'Researching' },
  { value: 'BLOCKED', label: 'Blocked' },
  { value: 'WATCHLIST', label: 'Watchlist' },
  { value: 'BUY_SAMPLE', label: 'Buy Sample' },
  { value: 'APPROVED_TO_LIST', label: 'Approved to List' },
  { value: 'LISTED', label: 'Listed' },
  { value: 'SELLING', label: 'Selling' },
  { value: 'SLOW_MOVING', label: 'Slow Moving' },
  { value: 'REORDER_CANDIDATE', label: 'Reorder Candidate' },
  { value: 'ARCHIVED', label: 'Archived' },
];

export default function ProductsPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [page, setPage] = useState(1);

  useEffect(() => {
    setLoading(true);
    getProducts({
      search: search || undefined,
      status: (statusFilter as ProductStatus) || undefined,
    }).then((data) => {
      setProducts(data);
      setLoading(false);
      setPage(1);
    });
  }, [search, statusFilter]);

  const totalPages = Math.ceil(products.length / ITEMS_PER_PAGE);
  const paginatedProducts = products.slice(
    (page - 1) * ITEMS_PER_PAGE,
    page * ITEMS_PER_PAGE
  );

  return (
    <div className="p-6 space-y-6 max-w-[1400px]">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-white">Products</h1>
          <p className="text-sm text-[#71717a] mt-1">
            {products.length} product{products.length !== 1 ? 's' : ''} found
          </p>
        </div>
        <Link
          href="/products/new"
          className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium rounded-lg transition-colors"
        >
          <Plus className="w-4 h-4" />
          New Product
        </Link>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-3">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#71717a]" />
          <input
            type="text"
            placeholder="Search by name, SKU, or category..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-[#1a1a1a] border border-[#27272a] rounded-lg text-sm text-white placeholder:text-[#71717a] focus:outline-none focus:border-indigo-500/50 focus:ring-1 focus:ring-indigo-500/20"
          />
        </div>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="px-3 py-2 bg-[#1a1a1a] border border-[#27272a] rounded-lg text-sm text-white focus:outline-none focus:border-indigo-500/50"
        >
          {STATUS_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </div>

      {/* Action Bar */}
      <div className="flex items-center gap-4 p-3 bg-[#111111] border border-[#1a1a1a] rounded-xl">
        {ACTION_BUTTONS.map((btn) => (
          <button
            key={btn.label}
            className={`flex items-center gap-1.5 text-xs ${btn.color} hover:bg-[#1a1a1a] px-2 py-1.5 rounded-lg transition-colors`}
          >
            <btn.icon className="w-3.5 h-3.5" />
            {btn.label}
          </button>
        ))}
      </div>

      {/* Table */}
      <div className="bg-[#111111] border border-[#1a1a1a] rounded-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-[#1a1a1a] bg-[#0d0d0d]">
                <th className="text-left px-5 py-3.5 text-[#71717a] font-medium text-xs uppercase tracking-wider">
                  Product
                </th>
                <th className="text-left px-5 py-3.5 text-[#71717a] font-medium text-xs uppercase tracking-wider">
                  Category
                </th>
                <th className="text-left px-5 py-3.5 text-[#71717a] font-medium text-xs uppercase tracking-wider">
                  Status
                </th>
                <th className="text-left px-5 py-3.5 text-[#71717a] font-medium text-xs uppercase tracking-wider">
                  Risk
                </th>
                <th className="text-right px-5 py-3.5 text-[#71717a] font-medium text-xs uppercase tracking-wider">
                  Score
                </th>
                <th className="text-right px-5 py-3.5 text-[#71717a] font-medium text-xs uppercase tracking-wider">
                  Est. Profit
                </th>
                <th className="text-left px-5 py-3.5 text-[#71717a] font-medium text-xs uppercase tracking-wider">
                  Action
                </th>
                <th className="text-right px-5 py-3.5 text-[#71717a] font-medium text-xs uppercase tracking-wider">
                  Updated
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#1a1a1a]">
              {loading ? (
                <tr>
                  <td colSpan={8} className="text-center py-12">
                    <RefreshCw className="w-5 h-5 animate-spin text-[#71717a] mx-auto" />
                  </td>
                </tr>
              ) : paginatedProducts.length === 0 ? (
                <tr>
                  <td colSpan={8} className="text-center py-12 text-[#71717a]">
                    No products found
                  </td>
                </tr>
              ) : (
                paginatedProducts.map((product) => (
                  <tr
                    key={product.id}
                    className="hover:bg-[#1a1a1a]/30 transition-colors"
                  >
                    <td className="px-5 py-3.5">
                      <Link
                        href={`/products/${product.id}`}
                        className="text-white hover:text-indigo-400 font-medium"
                      >
                        {product.name}
                      </Link>
                      <div className="text-xs text-[#71717a]">{product.sku}</div>
                    </td>
                    <td className="px-5 py-3.5 text-[#a1a1aa]">
                      {product.category}
                    </td>
                    <td className="px-5 py-3.5">
                      <StatusBadge status={product.status} />
                    </td>
                    <td className="px-5 py-3.5">
                      {product.risk_level ? (
                        <RiskBadge risk={product.risk_level} />
                      ) : (
                        <span className="text-[#71717a]">—</span>
                      )}
                    </td>
                    <td className="px-5 py-3.5 text-right">
                      {product.final_score != null ? (
                        <span
                          className={`font-mono text-xs ${
                            product.final_score >= 70
                              ? 'text-green-400'
                              : product.final_score >= 50
                              ? 'text-yellow-400'
                              : 'text-red-400'
                          }`}
                        >
                          {product.final_score}
                        </span>
                      ) : (
                        <span className="text-[#71717a]">—</span>
                      )}
                    </td>
                    <td className="px-5 py-3.5 text-right">
                      {product.expected_profit != null ? (
                        <span className="text-green-400 font-mono text-xs">
                          +${product.expected_profit.toFixed(2)}
                        </span>
                      ) : (
                        <span className="text-[#71717a]">—</span>
                      )}
                    </td>
                    <td className="px-5 py-3.5">
                      {product.final_decision && (
                        <span className="inline-block px-2 py-0.5 text-xs bg-indigo-500/10 text-indigo-400 rounded-full border border-indigo-500/20">
                          {product.final_decision.replace(/_/g, ' ')}
                        </span>
                      )}
                    </td>
                    <td className="px-5 py-3.5 text-right text-[#71717a] text-xs">
                      {formatRelativeTime(product.updated_at)}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-between px-5 py-3 border-t border-[#1a1a1a]">
            <span className="text-xs text-[#71717a]">
              Page {page} of {totalPages} · {products.length} products
            </span>
            <div className="flex items-center gap-1">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
                className="p-1.5 rounded-lg text-[#71717a] hover:text-white hover:bg-[#1a1a1a] disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                let pageNum = i + 1;
                if (totalPages > 5) {
                  if (page > 3) pageNum = page - 2 + i;
                  if (page > totalPages - 2) pageNum = totalPages - 4 + i;
                }
                return (
                  <button
                    key={pageNum}
                    onClick={() => setPage(pageNum)}
                    className={`w-8 h-8 rounded-lg text-xs transition-colors ${
                      page === pageNum
                        ? 'bg-indigo-600 text-white'
                        : 'text-[#71717a] hover:text-white hover:bg-[#1a1a1a]'
                    }`}
                  >
                    {pageNum}
                  </button>
                );
              })}
              <button
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
                className="p-1.5 rounded-lg text-[#71717a] hover:text-white hover:bg-[#1a1a1a] disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function formatRelativeTime(dateStr: string): string {
  const date = new Date(dateStr);
  const now = new Date();
  const diff = now.getTime() - date.getTime();
  const hours = Math.floor(diff / (1000 * 60 * 60));
  const days = Math.floor(hours / 24);

  if (days > 0) return `${days}d ago`;
  if (hours > 0) return `${hours}h ago`;
  return 'Just now';
}
