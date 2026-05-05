export type ProductStatus =
  | 'NEW'
  | 'NEEDS_RESEARCH'
  | 'RESEARCHING'
  | 'BLOCKED'
  | 'WATCHLIST'
  | 'BUY_SAMPLE'
  | 'SAMPLE_ORDERED'
  | 'SAMPLE_RECEIVED'
  | 'APPROVED_TO_LIST'
  | 'LISTED'
  | 'SELLING'
  | 'SLOW_MOVING'
  | 'REORDER_CANDIDATE'
  | 'REORDERED'
  | 'KILL_PRODUCT'
  | 'ARCHIVED';

export const STATUS_LABELS: Record<ProductStatus, string> = {
  NEW: 'New',
  NEEDS_RESEARCH: 'Needs Research',
  RESEARCHING: 'Researching',
  BLOCKED: 'Blocked',
  WATCHLIST: 'Watchlist',
  BUY_SAMPLE: 'Buy Sample',
  SAMPLE_ORDERED: 'Sample Ordered',
  SAMPLE_RECEIVED: 'Sample Received',
  APPROVED_TO_LIST: 'Approved to List',
  LISTED: 'Listed',
  SELLING: 'Selling',
  SLOW_MOVING: 'Slow Moving',
  REORDER_CANDIDATE: 'Reorder Candidate',
  REORDERED: 'Reordered',
  KILL_PRODUCT: 'Kill Product',
  ARCHIVED: 'Archived',
};

export const STATUS_COLORS: Record<ProductStatus, string> = {
  NEW: 'bg-slate-500/20 text-slate-400 border-slate-500/30',
  NEEDS_RESEARCH: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
  RESEARCHING: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
  BLOCKED: 'bg-red-500/20 text-red-400 border-red-500/30',
  WATCHLIST: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
  BUY_SAMPLE: 'bg-purple-500/20 text-purple-400 border-purple-500/30',
  SAMPLE_ORDERED: 'bg-purple-500/20 text-purple-400 border-purple-500/30',
  SAMPLE_RECEIVED: 'bg-purple-500/20 text-purple-400 border-purple-500/30',
  APPROVED_TO_LIST: 'bg-green-500/20 text-green-400 border-green-500/30',
  LISTED: 'bg-green-500/20 text-green-400 border-green-500/30',
  SELLING: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
  SLOW_MOVING: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
  REORDER_CANDIDATE: 'bg-cyan-500/20 text-cyan-400 border-cyan-500/30',
  REORDERED: 'bg-cyan-500/20 text-cyan-400 border-cyan-500/30',
  KILL_PRODUCT: 'bg-red-500/20 text-red-400 border-red-500/30',
  ARCHIVED: 'bg-slate-500/20 text-slate-400 border-slate-500/30',
};

export type RiskLevel = 'LOW' | 'MEDIUM' | 'HIGH' | 'BLOCKED';

export const RISK_COLORS: Record<RiskLevel, string> = {
  LOW: 'bg-green-500/20 text-green-400 border-green-500/30',
  MEDIUM: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
  HIGH: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
  BLOCKED: 'bg-red-500/20 text-red-400 border-red-500/30',
};

export type FinalDecision =
  | 'BLOCKED'
  | 'SKIP'
  | 'WATCHLIST'
  | 'BUY_SAMPLE'
  | 'BUY_SMALL_BATCH'
  | 'REORDER'
  | 'SCALE';

export interface Product {
  id: string;
  sku: string;
  name: string;
  category?: string;
  subcategory?: string;
  description?: string;
  status: ProductStatus;
  risk_level?: RiskLevel;
  final_score?: number;
  final_decision?: FinalDecision;
  target_sale_price?: number;
  expected_profit?: number;
  target_cost?: number;
  created_at: string;
  updated_at: string;
  sources?: ProductSource[];
  marketplace_research?: MarketplaceResearch[];
  competitor_listings?: CompetitorListing[];
  profit_analyses?: ProfitAnalysis[];
  agent_reports?: AgentReport[];
  inventory?: InventoryItem[];
  sales?: Sale[];
  files?: ProductFile[];
}

export interface ProductSource {
  id: string;
  product_id: string;
  supplier_name?: string;
  supplier_platform?: string;
  supplier_url?: string;
  unit_cost?: number;
  domestic_shipping?: number;
  international_shipping_estimate?: number;
  estimated_landed_cost?: number;
  moq?: number;
  supplier_rating?: string;
  is_primary?: boolean;
}

export interface MarketplaceResearch {
  id: string;
  product_id: string;
  marketplace: string;
  keyword?: string;
  active_listing_count?: number;
  sold_listing_count?: number;
  median_active_price?: number;
  median_sold_price?: number;
  competition_level?: string;
  demand_signal?: string;
}

export interface CompetitorListing {
  id: string;
  product_id: string;
  marketplace?: string;
  title?: string;
  url?: string;
  price?: number;
  shipping_price?: number;
  condition?: string;
  seller_name?: string;
  sold?: boolean;
  photo_score?: number;
  title_patterns?: string[];
  weaknesses?: string[];
  differentiation_ideas?: string[];
}

export interface ProfitAnalysis {
  id: string;
  product_id: string;
  scenario_name?: string;
  expected_sale_price?: number;
  landed_cost?: number;
  marketplace_fee?: number;
  estimated_net_profit?: number;
  margin_percent?: number;
  roi_percent?: number;
  verdict?: string;
}

export interface AgentReport {
  id: string;
  product_id: string;
  agent_name: string;
  report_type: string;
  input_json?: string;
  output_json?: string;
  summary?: string;
  confidence?: string;
  created_at: string;
}

export interface AgentResult {
  agent_type: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  output?: string;
  confidence?: number;
  warnings?: string[];
  errors?: string[];
  started_at?: string;
  completed_at?: string;
  duration_seconds?: number;
}

export interface InventoryItem {
  id: string;
  product_id: string;
  quantity_on_hand: number;
  quantity_ordered: number;
  quantity_sold: number;
  quantity_returned: number;
  average_landed_cost?: number;
  location_code?: string;
  reorder_point?: number;
}

export interface Sale {
  id: string;
  product_id: string;
  marketplace?: string;
  sale_date?: string;
  quantity: number;
  sale_price?: number;
  marketplace_fee?: number;
  net_profit?: number;
  returned?: boolean;
}

export interface ProductFile {
  id: string;
  product_id: string;
  file_type?: string;
  file_url?: string;
  original_filename?: string;
  notes?: string;
}

export interface Listing {
  id: string;
  product_id: string;
  marketplace: 'ebay' | 'mercari' | 'facebook' | 'other';
  title?: string;
  description?: string;
  price?: number;
  quantity?: number;
  status: 'draft' | 'published' | 'sold' | 'ended';
  url?: string;
}

export interface DashboardStats {
  total_products: number;
  blocked_count: number;
  watchlist_count: number;
  buy_sample_candidates: number;
  products_ordered: number;
  products_listed: number;
  top_categories: Array<{ category: string; count: number }>;
  recent_products: Product[];
  reorder_recommendations: Product[];
  agent_activity: AgentResult[];
}

export interface CreateProductInput {
  name: string;
  category: string;
  subcategory?: string;
  description?: string;
  supplier_url?: string;
}
