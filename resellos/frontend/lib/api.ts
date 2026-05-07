import type {
  AgentResult,
  CreateProductInput,
  DashboardStats,
  DiscoveryCampaign,
  DiscoveryCampaignDetail,
  DiscoveryCampaignInput,
  DiscoveryCampaignReport,
  DiscoveryCampaignTask,
  DiscoveryCampaignTaskInput,
  DiscoveryCampaignTaskUpdateInput,
  DiscoveryCampaignUpdateInput,
  DiscoveryIdea,
  DiscoveryQuickScanInput,
  DiscoveryQuickScanResponse,
  DiscoveryTaskUpdate,
  ExternalResearchJob,
  ExternalResearchJobDetailResponse,
  ExternalResearchRunInput,
  EvidenceCandidate,
  EvidenceCandidateReviewInput,
  EvidenceCandidateReviewResponse,
  ManualCaptureInput,
  ManualCaptureResponse,
  OpportunityBoardRow,
  MarketplaceEvidenceInput,
  Product,
  ProductIdea,
  DiscoveryTask,
  ProductIdeaQuickScanInput,
  ProductIdeaQuickScanResponse,
  ProductSource,
  ProductStatus,
  ResearchCockpit,
  ResearchRunResponse,
  SupplierInput,
  ProductDemandResearch,
  ProductDemandResearchInput,
  ProductDemandResearchVerifyInput,
  ProductTrendResearch,
  ProductTrendResearchInput,
  ProductTrendResearchVerifyInput,
  PortfolioItem,
  PortfolioItemStatus,
  PortfolioRole,
  ProductCollection,
  ShopConcept,
  ShopConceptDetail,
  ShopPortfolioReport,
  PortfolioContext,
  ValidationChecklistResponse,
} from './types';

export const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

async function requestJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers || {}),
    },
    cache: 'no-store',
  });

  if (!response.ok) {
    const text = await response.text().catch(() => '');
    throw new Error(`API ${response.status}: ${text || response.statusText}`);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

async function requestFormData<T>(path: string, formData: FormData): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    body: formData,
    cache: 'no-store',
  });

  if (!response.ok) {
    const text = await response.text().catch(() => '');
    throw new Error(`API ${response.status}: ${text || response.statusText}`);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

// Module-level flag to track if API fallback to demo data occurred
let _isOffline = false;

export function isOfflineMode(): boolean {
  return _isOffline;
}

export function setOfflineMode(value: boolean): void {
  _isOffline = value;
}

function asQuery(params: Record<string, string | undefined>) {
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value) search.set(key, value);
  }
  return search.toString();
}

const DEMO_PRODUCTS: Product[] = [
  {
    id: 'demo-1',
    sku: 'RS-DEMO-001',
    name: '2-Pack Car Seat Gap Organizer',
    category: 'Automotive',
    subcategory: 'Accessories',
    description: 'A simple high-intent car accessory for testing the end-to-end research flow.',
    status: 'WATCHLIST',
    risk_level: 'LOW',
    final_score: 78,
    final_decision: 'WATCHLIST',
    target_sale_price: 18.99,
    expected_profit: 7.42,
    confidence: 'MEDIUM',
    next_action: 'Backend offline — demo data shown.',
    missing_evidence: ['Demo data — real evidence not available'],
    created_at: '2026-05-01T10:00:00Z',
    updated_at: '2026-05-04T14:30:00Z',
    sources: [],
    marketplace_research: [],
    marketplace_evidence: [],
    competitor_listings: [],
    profit_analyses: [],
    agent_reports: [],
    inventory: [],
    sales: [],
    files: [],
  },
];

const DEMO_DISCOVERY_IDEAS: DiscoveryIdea[] = [
  {
    id: 'idea-demo-1',
    idea_name: 'Car trash bag holder',
    category: 'Car accessories',
    source_platform: 'Alibaba',
    source_url: 'https://example.com',
    rough_supplier_cost: 1.2,
    estimated_landed_cost: 4.8,
    why_interesting: 'Small, cheap, solves a daily annoyance.',
    risk_flags: [],
    quick_market_signal: 'Need eBay sold check',
    quick_profit_signal: 'Potentially viable',
    research_priority: 'MEDIUM',
    notes: 'Demo discovery idea.',
    status: 'QUICK_SCAN_COMPLETE',
    quick_scan_verdict: 'NEEDS_MARKET_CHECK',
    quick_scan_reason: 'Promising but needs evidence.',
    research_completeness_score: 40,
    opportunity_score: 58,
    buy_readiness_status: 'NOT_READY',
    suggested_keywords: ['car trash bag holder', 'car organizer'],
    required_next_evidence: ['Add 5 sold listings', 'Add 10 active listings'],
    tasks: [
      { id: 'task-demo-1', idea_id: 'idea-demo-1', task_type: 'market_research', title: 'Search eBay sold listings', status: 'TODO', sort_order: 1, created_at: new Date().toISOString() },
    ],
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
];

function demoDashboard(): DashboardStats {
  return {
    total_products: DEMO_PRODUCTS.length,
    blocked_count: 0,
    watchlist_count: 0,
    buy_sample_candidates: 1,
    products_ordered: 0,
    products_listed: 0,
    top_categories: [{ category: 'Automotive', count: 1 }],
    recent_products: DEMO_PRODUCTS,
    reorder_recommendations: [],
    agent_activity: [
      {
        agent_type: 'decision',
        status: 'completed',
        summary: 'Demo decision available while the backend is offline.',
        confidence: 'MEDIUM',
      },
    ] as AgentResult[],
  };
}

function demoDiscovery(): DiscoveryIdea[] {
  return DEMO_DISCOVERY_IDEAS;
}

function demoOpportunityBoard(): OpportunityBoardRow[] {
  const idea = DEMO_DISCOVERY_IDEAS[0];
  const product = DEMO_PRODUCTS[0];
  return [
    {
      id: idea.id,
      entity_type: 'idea',
      title: idea.idea_name,
      category: idea.category,
      research_completeness_score: idea.research_completeness_score ?? 40,
      research_verdict: idea.quick_scan_verdict,
      buy_readiness_status: idea.buy_readiness_status,
      sold_evidence_count: 0,
      active_evidence_count: 0,
      best_landed_cost: idea.estimated_landed_cost ?? null,
      source_platform: idea.source_platform,
      status: idea.status,
    },
    {
      id: product.id,
      entity_type: 'product',
      title: product.name,
      category: product.category,
      research_completeness_score: 78,
      research_verdict: product.final_decision,
      buy_readiness_status: 'READY',
      risk_level: product.risk_level,
      sold_evidence_count: 1,
      active_evidence_count: 0,
      median_sold_price: 18.99,
      best_landed_cost: 5.7,
      best_profit_scenario: 'eBay buyer-paid shipping',
      competition_gap_score: 68,
      supplier_confidence: 'A',
      next_action: product.next_action,
      status: product.status,
    },
  ];
}

function demoCockpit(productId: string): ResearchCockpit {
  const product = DEMO_PRODUCTS[0];
  return {
    product: {
      ...product,
      id: productId,
      sku: productId === product.id ? product.sku : `RS-DEMO-${productId.slice(0, 4).toUpperCase()}`,
    },
    sources: [
      {
        id: 'source-demo-1',
        product_id: productId,
        supplier_name: 'Shenzhen Auto Parts',
        supplier_platform: 'Alibaba',
        unit_cost: 4.15,
        domestic_shipping: 0.35,
        international_shipping_estimate: 1.2,
        estimated_landed_cost: 5.7,
        moq: 50,
        supplier_rating: 'A',
        is_primary: true,
      },
    ],
    marketplace_research: [],
    marketplace_evidence: [
      {
        id: 'evidence-demo-1',
        product_id: productId,
        marketplace: 'eBay',
        evidence_type: 'SOLD_LISTING',
        title: '2-Pack Car Seat Gap Organizer',
        price: 18.99,
        confidence: 'HIGH',
        notes: 'Demo sold listing from the local fallback dataset.',
      },
    ],
    competitor_listings: [],
    profit_analyses: [
      {
        id: 'profit-demo-1',
        product_id: productId,
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
    ],
    competition: {
      competition_level: 'MEDIUM',
      listing_gap_score: 68,
      can_compete: true,
      competitor_count: 8,
      active_competitor_count: 6,
      sold_competitor_count: 2,
      median_competitor_price: 19.99,
      avg_photo_score: 54,
      avg_title_score: 58,
      avg_description_score: 61,
      weaknesses: ['Competitor photos are weak enough to beat with real photos.'],
      recommended_angle: 'Use real photos, dimensions, and fitment clarity.',
      summary: 'Demo competition intelligence available while the backend is offline.',
      confidence: 'MEDIUM',
      warnings: [],
      evidence_refs: [],
    },
    reorder: {
      reorder_recommendation: 'REORDER_SMALL',
      current_inventory: 12,
      quantity_sold: 28,
      quantity_ordered: 40,
      quantity_returned: 1,
      average_daily_sales: 0.9,
      days_of_cover: 13.3,
      reorder_point: 10,
      max_reorder_qty: 20,
      stockout_risk: 'MEDIUM',
      return_rate_percent: 3.57,
      average_landed_cost: 5.7,
      reorder_reason: 'Demo reorder signal based on healthy sell-through.',
      summary: 'Demo reorder intelligence available while the backend is offline.',
      confidence: 'MEDIUM',
      warnings: [],
      evidence_refs: [],
    },
    agent_reports: [
      {
        id: 'report-demo-1',
        product_id: productId,
        agent_name: 'decision_agent',
        report_type: 'decision_agent',
        summary: 'WATCHLIST — demo data, backend offline.',
        confidence: 'MEDIUM',
        evidence_refs: ['evidence-demo-1'],
        created_at: new Date().toISOString(),
      },
      {
        id: 'report-demo-discovery-1',
        product_id: productId,
        agent_name: 'discovery_context',
        report_type: 'discovery_context',
        output_json: JSON.stringify({
          idea_id: 'idea-demo-1',
          idea_name: 'Car trash bag holder',
          category: 'Car accessories',
          quick_scan_verdict: 'PROMISING_FOR_RESEARCH',
          quick_scan_reason: 'Small, low-risk category with no sold evidence yet.',
          research_priority: 'HIGH',
          research_completeness_score: 40,
          opportunity_score: 58,
          required_next_evidence: ['Add 5 sold listings', 'Add 5 active listings', 'Add 2 supplier sources'],
          suggested_keywords: {
            ebay_sold: ['car trash bag holder', 'car organizer'],
            ebay_active: ['car trash bag holder', 'car storage accessory'],
            mercari: ['car organizer', 'car trash bag'],
            supplier: ['car trash bag holder', 'car organizer'],
          },
          risk_flags: [],
        }),
        summary: 'Promoted from discovery.',
        confidence: 'MEDIUM',
        created_at: new Date().toISOString(),
      },
    ],
    decision: {
      recommendation: 'WATCHLIST',
      total_score: 78,
      research_verdict: 'NEEDS_MORE_RESEARCH',
      buy_readiness_status: 'NOT_READY',
      research_completeness_score: 82,
      opportunity_score: 78,
      main_blocker: 'None',
      confidence: 'MEDIUM',
      reason: 'Strong evidence and acceptable profit.',
      next_action: 'Add 10 sold examples before ordering.',
      missing_evidence: ['Sold listings missing', 'Supplier comparison missing'],
      assumptions: ['Demo fallback data'],
      hard_blockers: [],
      max_quantity_to_buy: 5,
      max_landed_cost: 5.75,
      target_sale_price: 18.99,
      required_before_buying: ['Add 10 sold examples before ordering.'],
    },
    buy_readiness: {
      sold_evidence_count: 1,
      active_evidence_count: 0,
      supplier_cost_present: true,
      international_shipping_present: true,
      outbound_shipping_present: true,
      profit_scenarios_present: true,
      risk_passed: true,
      target_price_present: true,
    },
    hard_blockers: [],
    inventory: [
      {
        quantity_on_hand: 12,
        quantity_ordered: 40,
        quantity_sold: 28,
        quantity_returned: 1,
        average_landed_cost: 5.7,
        location_code: 'HOME',
        reorder_point: 10,
      },
    ],
    sales: [
      {
        marketplace: 'eBay',
        sale_date: '2026-05-04T10:00:00Z',
        quantity: 1,
        sale_price: 18.99,
        marketplace_fee: 2.47,
        shipping_cost: 4,
        packaging_cost: 0.4,
        net_profit: 7.42,
        buyer_paid_shipping: true,
        returned: false,
        notes: 'Demo sale',
      },
    ],
    missing_evidence: ['Demo data — backend offline'],
    next_action: 'Connect backend to see real data.',
    confidence: 'MEDIUM',
    current_status: 'WATCHLIST',
    discovery_context: {
      idea_id: 'idea-demo-1',
      idea_name: 'Car trash bag holder',
      category: 'Car accessories',
      quick_scan_verdict: 'PROMISING_FOR_RESEARCH',
      quick_scan_reason: 'Small, low-risk category with no sold evidence yet.',
      research_priority: 'HIGH',
      research_completeness_score: 40,
      opportunity_score: 58,
      required_next_evidence: ['Add 5 sold listings', 'Add 5 active listings', 'Add 2 supplier sources'],
      suggested_keywords: {
        ebay_sold: ['car trash bag holder', 'car organizer'],
        ebay_active: ['car trash bag holder', 'car storage accessory'],
        mercari: ['car organizer', 'car trash bag'],
        supplier: ['car trash bag holder', 'car organizer'],
      },
      risk_flags: [],
    },
  };
}

async function getMaybe<T>(path: string, fallback: T): Promise<T> {
  try {
    const result = await requestJson<T>(path);
    _isOffline = false;
    return result;
  } catch {
    _isOffline = true;
    return fallback;
  }
}

export async function getDashboardStats(): Promise<DashboardStats> {
  return getMaybe('/api/dashboard/stats', demoDashboard());
}

export async function getProducts(filters?: {
  status?: ProductStatus;
  search?: string;
  category?: string;
}): Promise<Product[]> {
  const query = asQuery({
    status: filters?.status,
    search: filters?.search,
    category: filters?.category,
  });
  return getMaybe(`/api/products${query ? `?${query}` : ''}`, DEMO_PRODUCTS);
}

export async function getProduct(id: string): Promise<Product | null> {
  const cockpit = await getProductCockpit(id);
  return cockpit?.product ?? null;
}

export async function getProductCockpit(id: string): Promise<ResearchCockpit | null> {
  return getMaybe(`/api/products/${id}/research/cockpit`, demoCockpit(id));
}

export async function getProductValidationChecklist(productId: string): Promise<ValidationChecklistResponse | null> {
  return getMaybe(`/api/validation/products/${productId}/checklist`, null);
}

export async function runProductValidation(productId: string): Promise<ValidationChecklistResponse> {
  return requestJson<ValidationChecklistResponse>(`/api/validation/products/${productId}/run`, {
    method: 'POST',
  });
}

export async function listKeywordDemand(filters?: {
  product_id?: string;
  idea_id?: string;
  campaign_id?: string;
  verification_status?: string;
}): Promise<ProductDemandResearch[]> {
  const query = asQuery({
    product_id: filters?.product_id,
    idea_id: filters?.idea_id,
    campaign_id: filters?.campaign_id,
    verification_status: filters?.verification_status,
  });
  return getMaybe(`/api/validation/demand${query ? `?${query}` : ''}`, []);
}

export async function createKeywordDemand(payload: ProductDemandResearchInput): Promise<ProductDemandResearch> {
  return requestJson<ProductDemandResearch>('/api/validation/demand', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function verifyKeywordDemand(researchId: string, payload: ProductDemandResearchVerifyInput): Promise<ProductDemandResearch> {
  return requestJson<ProductDemandResearch>(`/api/validation/demand/${researchId}/verify`, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  });
}

export async function listTrendResearch(filters?: {
  product_id?: string;
  idea_id?: string;
  campaign_id?: string;
  verification_status?: string;
}): Promise<ProductTrendResearch[]> {
  const query = asQuery({
    product_id: filters?.product_id,
    idea_id: filters?.idea_id,
    campaign_id: filters?.campaign_id,
    verification_status: filters?.verification_status,
  });
  return getMaybe(`/api/validation/trends${query ? `?${query}` : ''}`, []);
}

export async function createTrendResearch(payload: ProductTrendResearchInput): Promise<ProductTrendResearch> {
  return requestJson<ProductTrendResearch>('/api/validation/trends', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function verifyTrendResearch(researchId: string, payload: ProductTrendResearchVerifyInput): Promise<ProductTrendResearch> {
  return requestJson<ProductTrendResearch>(`/api/validation/trends/${researchId}/verify`, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  });
}

export async function listDiscoveryIdeas(): Promise<DiscoveryIdea[]> {
  return getMaybe('/api/discovery', demoDiscovery());
}

export async function getOpportunityBoard(): Promise<OpportunityBoardRow[]> {
  return getMaybe('/api/discovery/opportunity-board', demoOpportunityBoard());
}

export async function createDiscoveryIdea(data: DiscoveryQuickScanInput): Promise<DiscoveryIdea> {
  return requestJson<DiscoveryIdea>('/api/discovery', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function updateDiscoveryIdea(ideaId: string, data: Partial<DiscoveryQuickScanInput> & Partial<DiscoveryIdea>): Promise<DiscoveryIdea> {
  return requestJson<DiscoveryIdea>(`/api/discovery/${ideaId}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
}

export async function quickScanDiscoveryIdea(data: DiscoveryQuickScanInput): Promise<DiscoveryQuickScanResponse> {
  return requestJson<DiscoveryQuickScanResponse>('/api/discovery/quick-scan', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function generateDiscoveryTasks(ideaId: string): Promise<Array<Record<string, unknown>>> {
  return requestJson<Array<Record<string, unknown>>>(`/api/discovery/${ideaId}/tasks/generate`, {
    method: 'POST',
  });
}

export async function updateDiscoveryTask(
  taskId: string,
  data: DiscoveryTaskUpdate,
): Promise<DiscoveryTask> {
  return requestJson<DiscoveryTask>(`/api/discovery/tasks/${taskId}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
}

export async function archiveDiscoveryIdea(ideaId: string): Promise<DiscoveryIdea> {
  return requestJson<DiscoveryIdea>(`/api/discovery/${ideaId}/archive`, {
    method: 'POST',
  });
}

export async function promoteDiscoveryIdea(ideaId: string): Promise<{ product_id: string }> {
  return requestJson<{ product_id: string }>(`/api/discovery/${ideaId}/promote`, {
    method: 'POST',
  });
}

export async function listDiscoveryCampaigns(): Promise<DiscoveryCampaign[]> {
  return requestJson<DiscoveryCampaign[]>('/api/discovery/campaigns');
}

export async function createDiscoveryCampaign(data: DiscoveryCampaignInput): Promise<DiscoveryCampaign> {
  return requestJson<DiscoveryCampaign>('/api/discovery/campaigns', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function getDiscoveryCampaign(campaignId: string): Promise<DiscoveryCampaignDetail> {
  return requestJson<DiscoveryCampaignDetail>(`/api/discovery/campaigns/${campaignId}`);
}

export async function updateDiscoveryCampaign(campaignId: string, data: DiscoveryCampaignUpdateInput): Promise<DiscoveryCampaign> {
  return requestJson<DiscoveryCampaign>(`/api/discovery/campaigns/${campaignId}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
}

export async function createDiscoveryCampaignTask(
  campaignId: string,
  data: DiscoveryCampaignTaskInput,
): Promise<DiscoveryCampaignTask> {
  return requestJson<DiscoveryCampaignTask>(`/api/discovery/campaigns/${campaignId}/tasks`, {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function updateDiscoveryCampaignTask(
  campaignId: string,
  taskId: string,
  data: DiscoveryCampaignTaskUpdateInput,
): Promise<DiscoveryCampaignTask> {
  return requestJson<DiscoveryCampaignTask>(`/api/discovery/campaigns/${campaignId}/tasks/${taskId}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
}

export async function getDiscoveryCampaignReport(campaignId: string): Promise<DiscoveryCampaignReport> {
  return requestJson<DiscoveryCampaignReport>(`/api/discovery/campaigns/${campaignId}/report`);
}

export async function generateDiscoveryCampaignNextTasks(campaignId: string): Promise<DiscoveryCampaignTask[]> {
  return requestJson<DiscoveryCampaignTask[]>(`/api/discovery/campaigns/${campaignId}/generate-next-tasks`, {
    method: 'POST',
  });
}

export async function addIdeaToCampaign(
  campaignId: string,
  data: DiscoveryQuickScanInput,
): Promise<DiscoveryIdea> {
  return requestJson<DiscoveryIdea>(`/api/discovery/campaigns/${campaignId}/ideas`, {
    method: 'POST',
    body: JSON.stringify({ ...data, campaign_id: campaignId }),
  });
}

export async function listShopConcepts(): Promise<ShopConcept[]> {
  return requestJson<ShopConcept[]>('/api/portfolio/shops');
}

export async function createShopConcept(data: {
  name: string;
  description?: string | null;
  target_customer?: string | null;
  category?: string | null;
  price_min?: number | null;
  price_max?: number | null;
  avoid_list_json?: Record<string, unknown>;
  preferred_attributes_json?: Record<string, unknown>;
  brand_angle?: string | null;
  status?: string;
}): Promise<ShopConcept> {
  return requestJson<ShopConcept>('/api/portfolio/shops', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function getShopConcept(shopId: string): Promise<ShopConceptDetail> {
  return requestJson<ShopConceptDetail>(`/api/portfolio/shops/${shopId}`);
}

export async function updateShopConcept(
  shopId: string,
  data: Partial<{
    name: string;
    description: string | null;
    target_customer: string | null;
    category: string | null;
    price_min: number | null;
    price_max: number | null;
    avoid_list_json: Record<string, unknown>;
    preferred_attributes_json: Record<string, unknown>;
    brand_angle: string | null;
    status: string;
  }>,
): Promise<ShopConcept> {
  return requestJson<ShopConcept>(`/api/portfolio/shops/${shopId}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
}

export async function createProductCollection(
  shopId: string,
  data: {
    shop_concept_id?: string | null;
    name: string;
    theme?: string | null;
    target_problem?: string | null;
    description?: string | null;
    status?: string;
  },
): Promise<ProductCollection> {
  return requestJson<ProductCollection>(`/api/portfolio/shops/${shopId}/collections`, {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function updateProductCollection(
  collectionId: string,
  data: Partial<{
    shop_concept_id: string | null;
    name: string;
    theme: string | null;
    target_problem: string | null;
    description: string | null;
    status: string;
  }>,
): Promise<ProductCollection> {
  return requestJson<ProductCollection>(`/api/portfolio/collections/${collectionId}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
}

export async function addPortfolioItem(
  shopId: string,
  data: {
    shop_concept_id?: string | null;
    collection_id?: string | null;
    idea_id?: string | null;
    product_id?: string | null;
    role?: PortfolioRole;
    status?: PortfolioItemStatus;
    assortment_fit_score?: number;
    bundle_potential_score?: number;
    notes?: string | null;
  },
): Promise<PortfolioItem> {
  return requestJson<PortfolioItem>(`/api/portfolio/shops/${shopId}/items`, {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function updatePortfolioItem(
  itemId: string,
  data: Partial<{
    shop_concept_id: string | null;
    collection_id: string | null;
    idea_id: string | null;
    product_id: string | null;
    role: PortfolioRole;
    status: PortfolioItemStatus;
    assortment_fit_score: number;
    bundle_potential_score: number;
    notes: string | null;
  }>,
): Promise<PortfolioItem> {
  return requestJson<PortfolioItem>(`/api/portfolio/items/${itemId}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
}

export async function getShopPortfolioReport(shopId: string): Promise<ShopPortfolioReport> {
  return requestJson<ShopPortfolioReport>(`/api/portfolio/shops/${shopId}/report`);
}

export async function runExternalResearchGoogleShopping(
  payload: ExternalResearchRunInput,
): Promise<{ jobs: ExternalResearchJob[]; estimated_cost: number; budget_warning?: string | null }> {
  return requestJson<{ jobs: ExternalResearchJob[]; estimated_cost: number; budget_warning?: string | null }>(
    '/api/external-research/google-shopping',
    {
      method: 'POST',
      body: JSON.stringify(payload),
    },
  );
}

export async function listExternalResearchJobs(filters?: {
  idea_id?: string;
  product_id?: string;
  status?: string;
}): Promise<ExternalResearchJob[]> {
  const query = asQuery({
    idea_id: filters?.idea_id,
    product_id: filters?.product_id,
    status: filters?.status,
  });
  return getMaybe(`/api/external-research/jobs${query ? `?${query}` : ''}`, []);
}

export async function getExternalResearchJob(jobId: string): Promise<ExternalResearchJobDetailResponse | null> {
  return getMaybe(`/api/external-research/jobs/${jobId}`, null);
}

export async function pollExternalResearchJob(jobId: string): Promise<ExternalResearchJobDetailResponse> {
  return requestJson<ExternalResearchJobDetailResponse>(`/api/external-research/jobs/${jobId}/poll`, {
    method: 'POST',
  });
}

export async function listEvidenceCandidates(filters?: {
  idea_id?: string;
  product_id?: string;
  job_id?: string;
  review_status?: string;
}): Promise<EvidenceCandidate[]> {
  const query = asQuery({
    idea_id: filters?.idea_id,
    product_id: filters?.product_id,
    job_id: filters?.job_id,
    review_status: filters?.review_status,
  });
  return getMaybe(`/api/evidence-candidates${query ? `?${query}` : ''}`, []);
}

export async function approveEvidenceCandidate(
  candidateId: string,
  payload: EvidenceCandidateReviewInput,
): Promise<EvidenceCandidateReviewResponse> {
  return requestJson<EvidenceCandidateReviewResponse>(`/api/evidence-candidates/${candidateId}/approve`, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function rejectEvidenceCandidate(
  candidateId: string,
  payload: { notes?: string | null } = {},
): Promise<EvidenceCandidate> {
  return requestJson<EvidenceCandidate>(`/api/evidence-candidates/${candidateId}/reject`, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function captureManualEvidence(payload: ManualCaptureInput): Promise<ManualCaptureResponse> {
  const formData = new FormData();
  if (payload.idea_id) formData.append('idea_id', payload.idea_id);
  if (payload.product_id) formData.append('product_id', payload.product_id);
  if (payload.task_id) formData.append('task_id', payload.task_id);
  formData.append('capture_type', payload.capture_type);
  if (payload.url) formData.append('url', payload.url);
  if (payload.pasted_text) formData.append('pasted_text', payload.pasted_text);
  if (payload.notes) formData.append('notes', payload.notes);
  if (payload.screenshot) formData.append('screenshot', payload.screenshot);
  return requestFormData<ManualCaptureResponse>('/api/capture/manual', formData);
}

export async function deleteDiscoveryIdea(ideaId: string): Promise<void> {
  await requestJson<void>(`/api/discovery/${ideaId}`, { method: 'DELETE' });
}

export async function runProductResearch(id: string): Promise<ResearchRunResponse> {
  return requestJson<ResearchRunResponse>(`/api/products/${id}/research/run`, {
    method: 'POST',
  });
}

export async function createProduct(data: CreateProductInput): Promise<Product | null> {
  try {
    return await requestJson<Product>('/api/products', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  } catch {
    const nextId = String(DEMO_PRODUCTS.length + 1);
    const product: Product = {
      id: nextId,
      sku: `RS-DEMO-${nextId.padStart(3, '0')}`,
      name: data.name,
      category: data.category,
      subcategory: data.subcategory,
      description: data.description,
      status: 'NEW',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      sources: [],
      marketplace_research: [],
      marketplace_evidence: [],
      competitor_listings: [],
      profit_analyses: [],
      agent_reports: [],
      inventory: [],
      sales: [],
      files: [],
    };
    return product;
  }
}

export async function updateProduct(id: string, data: Partial<Product>): Promise<Product | null> {
  return requestJson<Product>(`/api/products/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
}

export async function deleteProduct(id: string): Promise<void> {
  await requestJson<void>(`/api/products/${id}`, { method: 'DELETE' });
}

export async function listProductSources(productId: string): Promise<ProductSource[]> {
  return getMaybe(`/api/products/${productId}/sources`, []);
}

export async function createProductSource(productId: string, data: SupplierInput): Promise<ProductSource> {
  return requestJson<ProductSource>(`/api/products/${productId}/sources`, {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function updateProductSource(productId: string, sourceId: string, data: SupplierInput): Promise<ProductSource> {
  return requestJson<ProductSource>(`/api/products/${productId}/sources/${sourceId}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
}

export async function deleteProductSource(productId: string, sourceId: string): Promise<void> {
  await requestJson<void>(`/api/products/${productId}/sources/${sourceId}`, { method: 'DELETE' });
}

export async function listMarketplaceEvidence(productId: string) {
  return getMaybe(`/api/marketplace/evidence/${productId}`, []);
}

export async function createMarketplaceEvidence(productId: string, data: MarketplaceEvidenceInput) {
  return requestJson(`/api/marketplace/evidence/${productId}`, {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function updateMarketplaceEvidence(evidenceId: string, data: Partial<MarketplaceEvidenceInput>) {
  return requestJson(`/api/marketplace/evidence/detail/${evidenceId}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
}

export async function deleteMarketplaceEvidence(evidenceId: string): Promise<void> {
  await requestJson<void>(`/api/marketplace/evidence/detail/${evidenceId}`, { method: 'DELETE' });
}

export async function verifyEvidenceItem(evidenceId: string, status: string) {
  return requestJson(`/api/marketplace/evidence/detail/${evidenceId}/verify`, {
    method: 'PATCH',
    body: JSON.stringify({ verification_status: status }),
  });
}

export async function verifyCompetitor(competitorId: string, status: string) {
  return requestJson(`/api/marketplace/competitors/detail/${competitorId}/verify`, {
    method: 'PATCH',
    body: JSON.stringify({ verification_status: status }),
  });
}

export async function verifySource(sourceId: string, status: string) {
  return requestJson(`/api/marketplace/sources/detail/${sourceId}/verify`, {
    method: 'PATCH',
    body: JSON.stringify({ verification_status: status }),
  });
}

export async function cleanupEvidence(data: {
  product_id?: string;
  verification_status?: string;
  dry_run?: boolean;
}) {
  return requestJson<{
    dry_run: boolean;
    affected_counts: Record<string, number>;
    actions: Array<Record<string, unknown>>;
  }>('/api/marketplace/evidence/cleanup', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

// --- Local Search Broker ---

export type SearchProvider = 'SEARXNG' | 'OPENSERP' | 'PLAYWRIGHT' | 'DATAFORSEO' | 'MANUAL';
export type SearchIntent = 'SOLD_EVIDENCE' | 'ACTIVE_LISTING' | 'SUPPLIER' | 'COMPETITOR' | 'COMPLAINT_RESEARCH' | 'KEYWORD_DEMAND' | 'GENERAL_RESEARCH';
export type ConversionStatus = 'NOT_CONVERTED' | 'CONVERTED_TO_CANDIDATE' | 'REJECTED';
export type ProviderStatusCode = 'OK' | 'ERROR' | 'DISABLED' | 'TIMEOUT';
export type CandidateType = 'SOLD_LISTING' | 'ACTIVE_LISTING' | 'SUPPLIER_SOURCE' | 'COMPETITOR_LISTING' | 'COMPLAINT_NOTE' | 'KEYWORD_DEMAND_NOTE';

export interface ProviderStatus {
  provider: SearchProvider;
  status: ProviderStatusCode;
  message?: string;
  result_count: number;
}

export interface ResearchSearchResult {
  id: string;
  query: string;
  provider: SearchProvider;
  intent: SearchIntent;
  title?: string;
  url: string;
  snippet?: string;
  source_domain?: string;
  rank?: number;
  price_text?: string;
  currency?: string;
  fetched_at?: string;
  product_id?: string;
  idea_id?: string;
  campaign_id?: string;
  conversion_status: ConversionStatus;
  converted_candidate_id?: string;
}

export interface ResearchSearchResponse {
  query: string;
  intent: SearchIntent;
  requested_providers: SearchProvider[];
  provider_statuses: ProviderStatus[];
  result_count: number;
  stored_count: number;
  deduped_count: number;
  results: ResearchSearchResult[];
}

export interface ResearchSearchRequest {
  query: string;
  intent: SearchIntent;
  providers?: SearchProvider[];
  max_results?: number;
  product_id?: string;
  idea_id?: string;
  campaign_id?: string;
  store_results?: boolean;
}

export interface ConvertSearchResultRequest {
  search_result_id: string;
  candidate_type: CandidateType;
  product_id?: string;
  idea_id?: string;
  campaign_id?: string;
  notes?: string;
  price?: number;
  title_override?: string;
}

export interface ConvertSearchResultResponse {
  search_result_id: string;
  candidate_id: string;
  verification_status: string;
  status: string;
}

export async function searchResearch(request: ResearchSearchRequest): Promise<ResearchSearchResponse> {
  return requestJson<ResearchSearchResponse>('/api/research/search', {
    method: 'POST',
    body: JSON.stringify(request),
  });
}

export async function listResearchSearchResults(filters?: {
  product_id?: string;
  idea_id?: string;
  campaign_id?: string;
  intent?: string;
  provider?: string;
  limit?: number;
  offset?: number;
}): Promise<ResearchSearchResult[]> {
  const params: Record<string, string | undefined> = {};
  if (filters?.product_id) params.product_id = filters.product_id;
  if (filters?.idea_id) params.idea_id = filters.idea_id;
  if (filters?.campaign_id) params.campaign_id = filters.campaign_id;
  if (filters?.intent) params.intent = filters.intent;
  if (filters?.provider) params.provider = filters.provider;
  if (filters?.limit !== undefined) params.limit = String(filters.limit);
  if (filters?.offset !== undefined) params.offset = String(filters.offset);
  const query = asQuery(params);
  return getMaybe(`/api/research/search-results${query ? `?${query}` : ''}`, []);
}

export async function convertSearchResultToCandidate(request: ConvertSearchResultRequest): Promise<ConvertSearchResultResponse> {
  return requestJson<ConvertSearchResultResponse>(
    `/api/research/search-results/${request.search_result_id}/candidate`,
    { method: 'POST', body: JSON.stringify(request) },
  );
}

export async function rejectResearchSearchResult(
  searchResultId: string,
  rejectReason: string,
): Promise<{ id: string; conversion_status: 'REJECTED'; reject_reason: string }> {
  return requestJson(`/api/research/search-results/${searchResultId}/reject`, {
    method: 'PATCH',
    body: JSON.stringify({ reject_reason: rejectReason }),
  });
}
