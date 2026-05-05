'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import * as Tabs from '@radix-ui/react-tabs';
import {
  ArrowLeft,
  RefreshCw,
  Package,
  Building2,
  BarChart3,
  DollarSign,
  Users,
  Brain,
  Tag,
  Warehouse,
  TrendingUp,
  ExternalLink,
  Star,
  AlertTriangle,
  CheckCircle2,
  XCircle,
} from 'lucide-react';
import { StatusBadge } from '@/components/shared/status-badge';
import { RiskBadge } from '@/components/shared/risk-badge';
import { getProduct } from '@/lib/api';
import type { Product, AgentReport, ProfitAnalysis, CompetitorListing, MarketplaceResearch, InventoryItem, Sale, Listing } from '@/lib/types';

const MOCK_REPORTS: AgentReport[] = [
  {
    id: 'r1',
    product_id: '1',
    agent_name: 'Risk Agent',
    report_type: 'risk',
    summary: 'Low risk product. Supplier has positive ratings and stable pricing history.',
    confidence: '0.85',
    created_at: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
  },
  {
    id: 'r2',
    product_id: '1',
    agent_name: 'Market Agent',
    report_type: 'market',
    summary: 'Strong demand signal on eBay with 200+ monthly sales in category. Moderate competition.',
    confidence: '0.88',
    created_at: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
  },
  {
    id: 'r3',
    product_id: '1',
    agent_name: 'Profit Agent',
    report_type: 'profit',
    summary: 'Expected ROI of 96% at target sale price of $49.99. Break-even at $30.00.',
    confidence: '0.82',
    created_at: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
  },
  {
    id: 'r4',
    product_id: '1',
    agent_name: 'Decision Agent',
    report_type: 'decision',
    summary: 'Recommendation: BUY_SAMPLE. All factors indicate this is a viable product with good margins.',
    confidence: '0.90',
    created_at: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
  },
];

const MOCK_SUPPLIERS = [
  { id: 's1', name: 'Shenzhen Electronics Co.', cost: 18.50, moq: 10, landed_cost: 22.00, preferred: true },
  { id: 's2', name: 'Guangzhou Trading Ltd.', cost: 16.00, moq: 50, landed_cost: 21.50, preferred: false },
  { id: 's3', name: 'Ningbo Goods Export', cost: 20.00, moq: 5, landed_cost: 23.00, preferred: false },
];

const MOCK_MARKET_RESEARCH: MarketplaceResearch[] = [
  {
    id: 'mr1',
    product_id: '1',
    marketplace: 'eBay',
    active_listing_count: 145,
    sold_listing_count: 892,
    median_active_price: 42.50,
    median_sold_price: 38.99,
    competition_level: 'Moderate',
    demand_signal: 'High',
  },
  {
    id: 'mr2',
    product_id: '1',
    marketplace: 'Mercari',
    active_listing_count: 67,
    sold_listing_count: 423,
    median_active_price: 38.00,
    median_sold_price: 35.50,
    competition_level: 'Low',
    demand_signal: 'Medium',
  },
];

const MOCK_COMPETITORS: CompetitorListing[] = [
  { id: 'c1', product_id: '1', marketplace: 'eBay', title: 'Portable Bluetooth Speaker Waterproof', price: 39.99, sold: true, photo_score: 7, seller_name: 'AudioDeals123' },
  { id: 'c2', product_id: '1', marketplace: 'eBay', title: 'BT Speaker 360 Sound | Black', price: 44.99, sold: false, photo_score: 8, seller_name: 'TechWorld' },
  { id: 'c3', product_id: '1', marketplace: 'Mercari', title: 'Bluetooth Speaker - Like New', price: 32.00, sold: true, photo_score: 9, seller_name: 'User_Seller' },
];

const MOCK_PROFIT: ProfitAnalysis[] = [
  { id: 'p1', product_id: '1', scenario_name: 'Buyer Paid Shipping', expected_sale_price: 49.99, landed_cost: 22.00, marketplace_fee: 5.50, estimated_net_profit: 22.49, margin_percent: 45, roi_percent: 102 },
  { id: 'p2', product_id: '1', scenario_name: 'Seller Paid Shipping', expected_sale_price: 49.99, landed_cost: 22.00, marketplace_fee: 5.50, shipping_cost: 5.00, estimated_net_profit: 17.49, margin_percent: 35, roi_percent: 79 },
  { id: 'p3', product_id: '1', scenario_name: 'Bundle Discount', expected_sale_price: 44.99, landed_cost: 22.00, marketplace_fee: 4.95, estimated_net_profit: 18.04, margin_percent: 40, roi_percent: 82 },
];

const MOCK_INVENTORY: InventoryItem[] = [
  { id: 'i1', product_id: '1', quantity_on_hand: 3, quantity_ordered: 10, quantity_sold: 7, quantity_returned: 0, location_code: 'SHELF-A3' },
];

const MOCK_SALES: Sale[] = [
  { id: 'sl1', product_id: '1', marketplace: 'eBay', sale_date: '2026-04-28', quantity: 1, sale_price: 44.99, marketplace_fee: 4.95, net_profit: 18.04 },
  { id: 'sl2', product_id: '1', marketplace: 'eBay', sale_date: '2026-04-20', quantity: 1, sale_price: 47.99, marketplace_fee: 5.28, net_profit: 20.71 },
];

const MOCK_LISTINGS: Listing[] = [
  { id: 'l1', product_id: '1', marketplace: 'ebay', title: 'Portable Bluetooth Speaker - Waterproof 360 Sound', price: 49.99, status: 'draft' },
  { id: 'l2', product_id: '1', marketplace: 'mercari', title: 'Bluetooth Speaker', price: 38.00, status: 'published' },
];

export default function ProductDetailPage() {
  const params = useParams();
  const [product, setProduct] = useState<Product | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getProduct(params.id as string).then((p) => {
      setProduct(p);
      setLoading(false);
    });
  }, [params.id]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <RefreshCw className="w-6 h-6 animate-spin text-indigo-400" />
      </div>
    );
  }

  if (!product) {
    return (
      <div className="p-6">
        <div className="text-center py-20">
          <XCircle className="w-12 h-12 text-red-400 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-white mb-2">Product not found</h2>
          <Link href="/products" className="text-indigo-400 hover:text-indigo-300 text-sm">
            Back to Products
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-[1400px]">
      {/* Header */}
      <div className="flex items-start gap-4 mb-6">
        <Link
          href="/products"
          className="mt-1 p-2 rounded-lg text-zinc-400 hover:text-white hover:bg-zinc-800 transition-colors"
        >
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-3 flex-wrap">
            <h1 className="text-2xl font-semibold text-white">{product.name}</h1>
            <StatusBadge status={product.status} />
            {product.risk_level && <RiskBadge risk={product.risk_level} />}
          </div>
          <div className="flex items-center gap-4 mt-1 text-sm text-zinc-500">
            <span>{product.sku}</span>
            {product.category && <span>{product.category}</span>}
            {product.subcategory && <span>· {product.subcategory}</span>}
          </div>
        </div>
        <div className="flex items-center gap-2">
          {product.final_score != null && (
            <div className="text-right mr-4">
              <div className={`text-2xl font-bold ${
                product.final_score >= 70 ? 'text-green-400' : product.final_score >= 50 ? 'text-yellow-400' : 'text-red-400'
              }`}>
                {product.final_score}
              </div>
              <div className="text-xs text-zinc-500">Score</div>
            </div>
          )}
          {product.final_decision && (
            <span className="px-3 py-1.5 text-xs font-medium bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 rounded-lg">
              {product.final_decision.replace(/_/g, ' ')}
            </span>
          )}
        </div>
      </div>

      {/* Tabs */}
      <Tabs.Root defaultValue="overview" className="w-full">
        <Tabs.List className="flex items-center gap-0.5 p-1 bg-zinc-900 rounded-xl border border-zinc-800 mb-6 overflow-x-auto scrollbar-hide">
          {TAB_ITEMS.map((tab) => (
            <Tabs.Trigger
              key={tab.value}
              value={tab.value}
              className="flex items-center gap-1.5 px-3 py-2 text-xs font-medium text-zinc-400 data-[state=active]:text-white data-[state=active]:bg-zinc-800 rounded-lg transition-colors whitespace-nowrap"
            >
              <tab.icon className="w-3.5 h-3.5" />
              {tab.label}
            </Tabs.Trigger>
          ))}
        </Tabs.List>

        <Tabs.Content value="overview" className="outline-none">
          <OverviewTab product={product} />
        </Tabs.Content>

        <Tabs.Content value="suppliers" className="outline-none">
          <SupplierTab />
        </Tabs.Content>

        <Tabs.Content value="marketplace" className="outline-none">
          <MarketplaceTab research={MOCK_MARKET_RESEARCH} competitors={MOCK_COMPETITORS} />
        </Tabs.Content>

        <Tabs.Content value="profit" className="outline-none">
          <ProfitTab analyses={MOCK_PROFIT} />
        </Tabs.Content>

        <Tabs.Content value="competition" className="outline-none">
          <CompetitionTab competitors={MOCK_COMPETITORS} />
        </Tabs.Content>

        <Tabs.Content value="reports" className="outline-none">
          <ReportsTab reports={MOCK_REPORTS} />
        </Tabs.Content>

        <Tabs.Content value="listings" className="outline-none">
          <ListingsTab listings={MOCK_LISTINGS} />
        </Tabs.Content>

        <Tabs.Content value="inventory" className="outline-none">
          <InventoryTab items={MOCK_INVENTORY} />
        </Tabs.Content>

        <Tabs.Content value="sales" className="outline-none">
          <SalesTab sales={MOCK_SALES} />
        </Tabs.Content>

        <Tabs.Content value="reorder" className="outline-none">
          <ReorderTab />
        </Tabs.Content>
      </Tabs.Root>
    </div>
  );
}

const TAB_ITEMS = [
  { value: 'overview', label: 'Overview', icon: Package },
  { value: 'suppliers', label: 'Suppliers', icon: Building2 },
  { value: 'marketplace', label: 'Marketplace', icon: BarChart3 },
  { value: 'profit', label: 'Profit', icon: DollarSign },
  { value: 'competition', label: 'Competition', icon: Users },
  { value: 'reports', label: 'AI Reports', icon: Brain },
  { value: 'listings', label: 'Listings', icon: Tag },
  { value: 'inventory', label: 'Inventory', icon: Warehouse },
  { value: 'sales', label: 'Sales', icon: TrendingUp },
  { value: 'reorder', label: 'Reorder', icon: RefreshCw },
];

// ─── Tab Components ───────────────────────────────────────────────────────────

function OverviewTab({ product }: { product: Product }) {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div className="lg:col-span-2 space-y-6">
        {/* Product Details */}
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-5">
          <h3 className="text-sm font-semibold text-white mb-4">Product Details</h3>
          {product.description ? (
            <p className="text-sm text-zinc-400 leading-relaxed">{product.description}</p>
          ) : (
            <p className="text-sm text-zinc-600 italic">No description provided</p>
          )}
        </div>

        {/* Timeline */}
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-5">
          <h3 className="text-sm font-semibold text-white mb-4">Timeline</h3>
          <div className="space-y-4">
            <TimelineItem label="Created" date={product.created_at} color="blue" />
            <TimelineItem label="Last Updated" date={product.updated_at} color="green" />
          </div>
        </div>
      </div>

      <div className="space-y-6">
        {/* Quick Stats */}
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-5">
          <h3 className="text-sm font-semibold text-white mb-4">Financials</h3>
          <div className="space-y-3">
            <StatRow label="Target Sale Price" value={product.target_sale_price ? `$${product.target_sale_price.toFixed(2)}` : '—'} />
            <StatRow label="Target Cost" value={product.target_cost ? `$${product.target_cost.toFixed(2)}` : '—'} />
            <StatRow label="Est. Profit" value={product.expected_profit ? `$${product.expected_profit.toFixed(2)}` : '—'} highlight />
          </div>
        </div>

        {/* Next Action */}
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-5">
          <h3 className="text-sm font-semibold text-white mb-4">Next Action</h3>
          <div className="p-3 rounded-lg bg-indigo-500/10 border border-indigo-500/20">
            <p className="text-sm text-indigo-400 font-medium">
              {getNextActionText(product.status)}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

function SupplierTab() {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-white">Supplier Options</h3>
        <button className="px-3 py-1.5 text-xs font-medium bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg transition-colors">
          + Add Supplier
        </button>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {MOCK_SUPPLIERS.map((supplier) => (
          <div key={supplier.id} className="bg-zinc-900 border border-zinc-800 rounded-xl p-5">
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center gap-2">
                <Building2 className="w-4 h-4 text-zinc-500" />
                <span className="text-sm font-medium text-white">{supplier.name}</span>
              </div>
              {supplier.preferred && (
                <span className="px-2 py-0.5 text-xs bg-indigo-500/10 text-indigo-400 rounded-full border border-indigo-500/20">
                  Preferred
                </span>
              )}
            </div>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-zinc-500">Unit Cost</span>
                <span className="text-white font-mono">${supplier.cost.toFixed(2)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-zinc-500">MOQ</span>
                <span className="text-white">{supplier.moq} units</span>
              </div>
              <div className="flex justify-between">
                <span className="text-zinc-500">Landed Cost</span>
                <span className="text-green-400 font-mono">${supplier.landed_cost.toFixed(2)}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function MarketplaceTab({ research, competitors }: { research: MarketplaceResearch[]; competitors: CompetitorListing[] }) {
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-sm font-semibold text-white mb-4">Market Research</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {research.map((r) => (
            <div key={r.id} className="bg-zinc-900 border border-zinc-800 rounded-xl p-5">
              <div className="flex items-center gap-2 mb-3">
                <BarChart3 className="w-4 h-4 text-indigo-400" />
                <span className="text-sm font-medium text-white">{r.marketplace}</span>
              </div>
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div>
                  <span className="text-zinc-500 block text-xs">Active Listings</span>
                  <span className="text-white">{r.active_listing_count ?? '—'}</span>
                </div>
                <div>
                  <span className="text-zinc-500 block text-xs">Monthly Sales</span>
                  <span className="text-white">{r.sold_listing_count ?? '—'}</span>
                </div>
                <div>
                  <span className="text-zinc-500 block text-xs">Median Price</span>
                  <span className="text-white">${r.median_active_price?.toFixed(2) ?? '—'}</span>
                </div>
                <div>
                  <span className="text-zinc-500 block text-xs">Median Sold</span>
                  <span className="text-green-400">${r.median_sold_price?.toFixed(2) ?? '—'}</span>
                </div>
                <div>
                  <span className="text-zinc-500 block text-xs">Competition</span>
                  <span className={r.competition_level === 'Low' ? 'text-green-400' : r.competition_level === 'Moderate' ? 'text-yellow-400' : 'text-red-400'}>
                    {r.competition_level ?? '—'}
                  </span>
                </div>
                <div>
                  <span className="text-zinc-500 block text-xs">Demand</span>
                  <span className={r.demand_signal === 'High' ? 'text-green-400' : 'text-yellow-400'}>
                    {r.demand_signal ?? '—'}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function ProfitTab({ analyses }: { analyses: ProfitAnalysis[] }) {
  return (
    <div className="space-y-4">
      <h3 className="text-sm font-semibold text-white">Profit Scenarios</h3>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {analyses.map((a) => (
          <div key={a.id} className="bg-zinc-900 border border-zinc-800 rounded-xl p-5">
            <div className="flex items-center gap-2 mb-3">
              {a.estimated_net_profit && a.estimated_net_profit > 0 ? (
                <CheckCircle2 className="w-4 h-4 text-green-400" />
              ) : (
                <AlertTriangle className="w-4 h-4 text-red-400" />
              )}
              <span className="text-sm font-medium text-white">{a.scenario_name}</span>
            </div>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-zinc-500">Sale Price</span>
                <span className="text-white font-mono">${a.expected_sale_price?.toFixed(2) ?? '—'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-zinc-500">Landed Cost</span>
                <span className="text-white font-mono">${a.landed_cost?.toFixed(2) ?? '—'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-zinc-500">Fees</span>
                <span className="text-red-400 font-mono">-${a.marketplace_fee?.toFixed(2) ?? '—'}</span>
              </div>
              {a.shipping_cost && (
                <div className="flex justify-between">
                  <span className="text-zinc-500">Shipping</span>
                  <span className="text-red-400 font-mono">-${a.shipping_cost.toFixed(2)}</span>
                </div>
              )}
              <div className="border-t border-zinc-800 pt-2 flex justify-between">
                <span className="text-zinc-500">Net Profit</span>
                <span className={`font-mono font-medium ${(a.estimated_net_profit ?? 0) > 0 ? 'text-green-400' : 'text-red-400'}`}>
                  ${a.estimated_net_profit?.toFixed(2) ?? '—'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-zinc-500">Margin</span>
                <span className="text-white">{a.margin_percent ?? '—'}%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-zinc-500">ROI</span>
                <span className="text-indigo-400">{a.roi_percent ?? '—'}%</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function CompetitionTab({ competitors }: { competitors: CompetitorListing[] }) {
  return (
    <div className="space-y-4">
      <h3 className="text-sm font-semibold text-white">Competitor Listings</h3>
      <div className="bg-zinc-900 border border-zinc-800 rounded-xl overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-zinc-800">
              <th className="text-left px-4 py-3 text-zinc-500 font-medium text-xs uppercase">Title</th>
              <th className="text-left px-4 py-3 text-zinc-500 font-medium text-xs uppercase">Marketplace</th>
              <th className="text-right px-4 py-3 text-zinc-500 font-medium text-xs uppercase">Price</th>
              <th className="text-center px-4 py-3 text-zinc-500 font-medium text-xs uppercase">Status</th>
              <th className="text-center px-4 py-3 text-zinc-500 font-medium text-xs uppercase">Photo</th>
              <th className="text-left px-4 py-3 text-zinc-500 font-medium text-xs uppercase">Seller</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-zinc-800">
            {competitors.map((c) => (
              <tr key={c.id} className="hover:bg-zinc-800/30">
                <td className="px-4 py-3">
                  <span className="text-white">{c.title}</span>
                </td>
                <td className="px-4 py-3 text-zinc-400">{c.marketplace}</td>
                <td className="px-4 py-3 text-right text-white font-mono">${c.price?.toFixed(2)}</td>
                <td className="px-4 py-3 text-center">
                  {c.sold ? (
                    <span className="text-xs text-green-400">Sold</span>
                  ) : (
                    <span className="text-xs text-zinc-500">Active</span>
                  )}
                </td>
                <td className="px-4 py-3 text-center">
                  {c.photo_score && (
                    <div className="flex items-center justify-center gap-1">
                      <Star className="w-3 h-3 text-yellow-400 fill-yellow-400" />
                      <span className="text-xs text-white">{c.photo_score}/10</span>
                    </div>
                  )}
                </td>
                <td className="px-4 py-3 text-zinc-500">{c.seller_name}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function ReportsTab({ reports }: { reports: AgentReport[] }) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-white">AI Agent Reports</h3>
        <button className="px-3 py-1.5 text-xs font-medium bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg transition-colors">
          Run All Agents
        </button>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {reports.map((report) => (
          <div key={report.id} className="bg-zinc-900 border border-zinc-800 rounded-xl p-5">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <Brain className="w-4 h-4 text-purple-400" />
                <span className="text-sm font-medium text-white">{report.agent_name}</span>
              </div>
              {report.confidence && (
                <span className="text-xs text-zinc-500">
                  {(parseFloat(report.confidence) * 100).toFixed(0)}% confidence
                </span>
              )}
            </div>
            {report.summary && (
              <p className="text-sm text-zinc-400 leading-relaxed">{report.summary}</p>
            )}
            <div className="mt-3 text-xs text-zinc-600">
              {new Date(report.created_at).toLocaleDateString()}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function ListingsTab({ listings }: { listings: Listing[] }) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-white">Generated Listings</h3>
        <button className="px-3 py-1.5 text-xs font-medium bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg transition-colors">
          Generate New Listing
        </button>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {listings.map((listing) => (
          <div key={listing.id} className="bg-zinc-900 border border-zinc-800 rounded-xl p-5">
            <div className="flex items-center justify-between mb-3">
              <span className="text-sm font-medium text-white capitalize">{listing.marketplace}</span>
              <span className={`px-2 py-0.5 text-xs rounded-full border ${
                listing.status === 'published'
                  ? 'bg-green-500/10 text-green-400 border-green-500/30'
                  : 'bg-zinc-500/10 text-zinc-400 border-zinc-500/30'
              }`}>
                {listing.status}
              </span>
            </div>
            {listing.title && (
              <p className="text-sm text-zinc-400 mb-2 line-clamp-2">{listing.title}</p>
            )}
            <div className="flex items-center justify-between">
              <span className="text-lg font-semibold text-white font-mono">
                ${listing.price?.toFixed(2)}
              </span>
              <div className="flex items-center gap-2">
                <button className="px-2 py-1 text-xs text-indigo-400 hover:bg-indigo-500/10 rounded transition-colors">
                  Edit
                </button>
                {listing.status === 'draft' && (
                  <button className="px-2 py-1 text-xs text-green-400 hover:bg-green-500/10 rounded transition-colors">
                    Publish
                  </button>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function InventoryTab({ items }: { items: InventoryItem[] }) {
  return (
    <div className="space-y-4">
      <h3 className="text-sm font-semibold text-white">Inventory</h3>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {items.map((item) => (
          <div key={item.id} className="bg-zinc-900 border border-zinc-800 rounded-xl p-5">
            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-zinc-500">On Hand</span>
                <span className="text-white font-medium">{item.quantity_on_hand}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-zinc-500">Ordered</span>
                <span className="text-indigo-400">{item.quantity_ordered}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-zinc-500">Sold</span>
                <span className="text-green-400">{item.quantity_sold}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-zinc-500">Returned</span>
                <span className="text-red-400">{item.quantity_returned}</span>
              </div>
              {item.location_code && (
                <div className="flex justify-between">
                  <span className="text-zinc-500">Location</span>
                  <span className="text-white">{item.location_code}</span>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function SalesTab({ sales }: { sales: Sale[] }) {
  return (
    <div className="space-y-4">
      <h3 className="text-sm font-semibold text-white">Sales History</h3>
      <div className="bg-zinc-900 border border-zinc-800 rounded-xl overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-zinc-800">
              <th className="text-left px-4 py-3 text-zinc-500 font-medium text-xs uppercase">Date</th>
              <th className="text-left px-4 py-3 text-zinc-500 font-medium text-xs uppercase">Marketplace</th>
              <th className="text-right px-4 py-3 text-zinc-500 font-medium text-xs uppercase">Sale Price</th>
              <th className="text-right px-4 py-3 text-zinc-500 font-medium text-xs uppercase">Fees</th>
              <th className="text-right px-4 py-3 text-zinc-500 font-medium text-xs uppercase">Net Profit</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-zinc-800">
            {sales.map((s) => (
              <tr key={s.id} className="hover:bg-zinc-800/30">
                <td className="px-4 py-3 text-zinc-400">{s.sale_date}</td>
                <td className="px-4 py-3 text-zinc-400">{s.marketplace}</td>
                <td className="px-4 py-3 text-right text-white font-mono">${s.sale_price?.toFixed(2)}</td>
                <td className="px-4 py-3 text-right text-red-400 font-mono">-${s.marketplace_fee?.toFixed(2)}</td>
                <td className="px-4 py-3 text-right text-green-400 font-mono">
                  ${s.net_profit?.toFixed(2)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function ReorderTab() {
  return (
    <div className="space-y-4">
      <h3 className="text-sm font-semibold text-white">Reorder Recommendations</h3>
      <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-8 text-center">
        <TrendingUp className="w-8 h-8 text-cyan-400 mx-auto mb-3" />
        <p className="text-sm text-zinc-400">
          This product has sold {MOCK_SALES.length} units with positive reviews.
        </p>
        <p className="text-sm text-zinc-500 mt-2">
          Consider reordering when inventory drops below threshold.
        </p>
        <button className="mt-4 px-4 py-2 text-sm font-medium bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg transition-colors">
          Create Reorder
        </button>
      </div>
    </div>
  );
}

// ─── Helpers ─────────────────────────────────────────────────────────────────

function StatRow({ label, value, highlight }: { label: string; value: string; highlight?: boolean }) {
  return (
    <div className="flex justify-between">
      <span className="text-zinc-500">{label}</span>
      <span className={highlight ? 'text-green-400 font-mono font-medium' : 'text-white font-mono'}>
        {value}
      </span>
    </div>
  );
}

function TimelineItem({ label, date, color }: { label: string; date: string; color: string }) {
  const colorMap: Record<string, string> = {
    blue: 'bg-blue-500',
    green: 'bg-green-500',
    yellow: 'bg-yellow-500',
    red: 'bg-red-500',
    purple: 'bg-purple-500',
    gray: 'bg-zinc-500',
  };
  return (
    <div className="flex items-center gap-3">
      <div className={`w-2 h-2 rounded-full ${colorMap[color] || 'bg-zinc-500'}`} />
      <div className="flex-1">
        <span className="text-xs text-zinc-500">{label}</span>
      </div>
      <span className="text-xs text-zinc-400">
        {new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
      </span>
    </div>
  );
}

function getNextActionText(status: string): string {
  const actions: Record<string, string> = {
    NEW: 'Run research pipeline to evaluate this product',
    NEEDS_RESEARCH: 'Initiate marketplace and supplier research',
    RESEARCHING: 'Waiting for agent analysis to complete',
    BLOCKED: 'Review and address blocking issues',
    WATCHLIST: 'Monitor for price changes or new opportunities',
    BUY_SAMPLE: 'Order a sample to evaluate quality',
    SAMPLE_ORDERED: 'Waiting for sample delivery',
    SAMPLE_RECEIVED: 'Inspect sample and finalize decision',
    APPROVED_TO_LIST: 'Create and publish listings',
    LISTED: 'Monitor sales performance',
    SELLING: 'Track inventory and sales velocity',
    SLOW_MOVING: 'Consider price adjustment or promotion',
    REORDER_CANDIDATE: 'Evaluate reorder quantities and timing',
    REORDERED: 'Awaiting new inventory delivery',
    KILL_PRODUCT: 'Archive and discontinue listing',
    ARCHIVED: 'Product is archived',
  };
  return actions[status] || 'No action defined for this status';
}
