import type {
  AgentResult,
  CreateProductInput,
  DashboardStats,
  MarketplaceEvidenceInput,
  Product,
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
    ],
    decision: {
      recommendation: 'BUY_SAMPLE',
      total_score: 78,
      confidence: 'MEDIUM',
      next_action: 'Add 10 sold examples before ordering.',
    },
    missing_evidence: ['Sold listings missing', 'Supplier comparison missing'],
    next_action: 'Add 10 sold examples before ordering.',
    confidence: 'MEDIUM',
    current_status: 'BUY_SAMPLE',
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
