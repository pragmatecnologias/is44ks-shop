import type {
  AgentResult,
  CreateProductInput,
  DashboardStats,
  DiscoveryIdea,
  DiscoveryQuickScanInput,
  DiscoveryQuickScanResponse,
  DiscoveryTaskUpdate,
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
} from './types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

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
    status: 'BUY_SAMPLE',
    risk_level: 'LOW',
    final_score: 78,
    final_decision: 'BUY_SAMPLE',
    target_sale_price: 18.99,
    expected_profit: 7.42,
    confidence: 'MEDIUM',
    next_action: 'Add 10 sold examples before ordering.',
    missing_evidence: ['Sold listings missing', 'Supplier comparison missing'],
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
        summary: 'BUY_SAMPLE with medium confidence.',
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
      recommendation: 'BUY_SAMPLE',
      total_score: 78,
      research_verdict: 'READY_FOR_SAMPLE',
      buy_readiness_status: 'READY',
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
    missing_evidence: ['Sold listings missing', 'Supplier comparison missing'],
    next_action: 'Add 10 sold examples before ordering.',
    confidence: 'MEDIUM',
    current_status: 'BUY_SAMPLE',
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
    return await requestJson<T>(path);
  } catch {
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
