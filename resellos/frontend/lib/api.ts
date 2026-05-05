import type { Product, ProductStatus, DashboardStats, CreateProductInput } from './types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// ─── Dashboard ───────────────────────────────────────────────────────────────

export async function getDashboardStats(): Promise<DashboardStats> {
  return {
    total_products: 147,
    blocked_count: 23,
    watchlist_count: 12,
    buy_sample_candidates: 8,
    products_ordered: 34,
    products_listed: 28,
    top_categories: [
      { category: 'Electronics', count: 42 },
      { category: 'Home & Garden', count: 31 },
      { category: 'Toys & Games', count: 28 },
      { category: 'Sports', count: 24 },
      { category: 'Books', count: 22 },
    ],
    recent_products: [
      {
        id: '1',
        sku: 'RS-000001',
        name: 'Portable Bluetooth Speaker',
        category: 'Electronics',
        status: 'BUY_SAMPLE',
        risk_level: 'LOW',
        final_score: 78,
        expected_profit: 24.50,
        created_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
        updated_at: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString(),
      },
      {
        id: '2',
        sku: 'RS-000002',
        name: 'Ceramic Plant Pot Set',
        category: 'Home & Garden',
        status: 'RESEARCHING',
        risk_level: 'MEDIUM',
        final_score: 65,
        expected_profit: 18.00,
        created_at: new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString(),
        updated_at: new Date(Date.now() - 3 * 60 * 60 * 1000).toISOString(),
      },
      {
        id: '3',
        sku: 'RS-000003',
        name: 'Mechanical Keyboard',
        category: 'Electronics',
        status: 'WATCHLIST',
        risk_level: 'LOW',
        final_score: 82,
        expected_profit: 45.00,
        created_at: new Date(Date.now() - 8 * 60 * 60 * 1000).toISOString(),
        updated_at: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(),
      },
      {
        id: '4',
        sku: 'RS-000004',
        name: 'Board Game Collection',
        category: 'Toys & Games',
        status: 'BLOCKED',
        risk_level: 'HIGH',
        final_score: 15,
        expected_profit: 5.00,
        created_at: new Date(Date.now() - 12 * 60 * 60 * 1000).toISOString(),
        updated_at: new Date(Date.now() - 10 * 60 * 60 * 1000).toISOString(),
      },
      {
        id: '5',
        sku: 'RS-000005',
        name: 'Fitness Resistance Band Set',
        category: 'Sports',
        status: 'APPROVED_TO_LIST',
        risk_level: 'LOW',
        final_score: 88,
        expected_profit: 15.75,
        created_at: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
        updated_at: new Date(Date.now() - 20 * 60 * 60 * 1000).toISOString(),
      },
    ],
    reorder_recommendations: [
      {
        id: '10',
        sku: 'RS-000010',
        name: 'LED Desk Lamp',
        category: 'Electronics',
        status: 'REORDER_CANDIDATE',
        risk_level: 'LOW',
        final_score: 75,
        expected_profit: 22.00,
        created_at: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
        updated_at: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
      },
      {
        id: '11',
        sku: 'RS-000011',
        name: 'Stainless Steel Water Bottle',
        category: 'Sports',
        status: 'REORDER_CANDIDATE',
        risk_level: 'LOW',
        final_score: 79,
        expected_profit: 12.50,
        created_at: new Date(Date.now() - 25 * 24 * 60 * 60 * 1000).toISOString(),
        updated_at: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
      },
      {
        id: '12',
        sku: 'RS-000012',
        name: 'Cotton Throw Blanket',
        category: 'Home & Garden',
        status: 'REORDER_CANDIDATE',
        risk_level: 'LOW',
        final_score: 71,
        expected_profit: 19.00,
        created_at: new Date(Date.now() - 20 * 24 * 60 * 60 * 1000).toISOString(),
        updated_at: new Date(Date.now() - 4 * 24 * 60 * 60 * 1000).toISOString(),
      },
    ],
    agent_activity: [
      {
        agent_type: 'market',
        status: 'completed',
        summary: 'Market analysis completed for 3 products',
        confidence: 'HIGH',
        started_at: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
        completed_at: new Date(Date.now() - 25 * 60 * 1000).toISOString(),
        duration_seconds: 300,
      },
      {
        agent_type: 'profit',
        status: 'completed',
        summary: 'Profit analysis completed for 5 products',
        confidence: 'HIGH',
        started_at: new Date(Date.now() - 40 * 60 * 1000).toISOString(),
        completed_at: new Date(Date.now() - 35 * 60 * 1000).toISOString(),
        duration_seconds: 180,
      },
      {
        agent_type: 'decision',
        status: 'running',
        summary: 'Decision agent is waiting on more evidence.',
        started_at: new Date(Date.now() - 5 * 60 * 1000).toISOString(),
      },
    ],
  };
}

// ─── Products ────────────────────────────────────────────────────────────────

const MOCK_PRODUCTS: Product[] = [
  {
    id: '1',
    sku: 'RS-000001',
    name: 'Portable Bluetooth Speaker',
    category: 'Electronics',
    subcategory: 'Audio',
    status: 'BUY_SAMPLE',
    risk_level: 'LOW',
    final_score: 78,
    final_decision: 'BUY_SAMPLE',
    expected_profit: 24.50,
    target_sale_price: 49.99,
    target_cost: 25.49,
    created_at: '2026-05-01T10:00:00Z',
    updated_at: '2026-05-04T14:30:00Z',
  },
  {
    id: '2',
    sku: 'RS-000002',
    name: 'Ceramic Plant Pot Set',
    category: 'Home & Garden',
    subcategory: 'Planters',
    status: 'RESEARCHING',
    risk_level: 'MEDIUM',
    final_score: 65,
    expected_profit: 18.00,
    target_sale_price: 39.99,
    created_at: '2026-04-28T09:00:00Z',
    updated_at: '2026-05-03T11:00:00Z',
  },
  {
    id: '3',
    sku: 'RS-000003',
    name: 'Mechanical Keyboard',
    category: 'Electronics',
    subcategory: 'Computer Accessories',
    status: 'WATCHLIST',
    risk_level: 'LOW',
    final_score: 82,
    final_decision: 'WATCHLIST',
    expected_profit: 45.00,
    target_sale_price: 89.99,
    created_at: '2026-04-25T08:00:00Z',
    updated_at: '2026-05-02T16:00:00Z',
  },
  {
    id: '4',
    sku: 'RS-000004',
    name: 'Board Game Collection',
    category: 'Toys & Games',
    status: 'BLOCKED',
    risk_level: 'HIGH',
    final_score: 15,
    final_decision: 'BLOCKED',
    expected_profit: 5.00,
    created_at: '2026-04-20T12:00:00Z',
    updated_at: '2026-05-01T09:00:00Z',
  },
  {
    id: '5',
    sku: 'RS-000005',
    name: 'Fitness Resistance Band Set',
    category: 'Sports',
    subcategory: 'Fitness Equipment',
    status: 'APPROVED_TO_LIST',
    risk_level: 'LOW',
    final_score: 88,
    final_decision: 'BUY_SMALL_BATCH',
    expected_profit: 15.75,
    target_sale_price: 29.99,
    target_cost: 14.24,
    created_at: '2026-04-18T14:00:00Z',
    updated_at: '2026-04-30T10:00:00Z',
  },
  {
    id: '6',
    sku: 'RS-000006',
    name: 'Stainless Steel Water Bottle',
    category: 'Sports',
    subcategory: 'Drinkware',
    status: 'SELLING',
    risk_level: 'LOW',
    final_score: 79,
    final_decision: 'SCALE',
    expected_profit: 12.50,
    target_sale_price: 24.99,
    target_cost: 12.49,
    created_at: '2026-04-10T09:00:00Z',
    updated_at: '2026-04-28T15:00:00Z',
  },
  {
    id: '7',
    sku: 'RS-000007',
    name: 'LED Desk Lamp',
    category: 'Electronics',
    subcategory: 'Lighting',
    status: 'REORDER_CANDIDATE',
    risk_level: 'LOW',
    final_score: 75,
    final_decision: 'REORDER',
    expected_profit: 22.00,
    created_at: '2026-03-15T11:00:00Z',
    updated_at: '2026-04-25T12:00:00Z',
  },
  {
    id: '8',
    sku: 'RS-000008',
    name: 'Cotton Throw Blanket',
    category: 'Home & Garden',
    subcategory: 'Textiles',
    status: 'LISTED',
    risk_level: 'LOW',
    final_score: 71,
    final_decision: 'BUY_SMALL_BATCH',
    expected_profit: 19.00,
    target_sale_price: 34.99,
    target_cost: 15.99,
    created_at: '2026-03-10T08:00:00Z',
    updated_at: '2026-04-20T14:00:00Z',
  },
  {
    id: '9',
    sku: 'RS-000009',
    name: 'Wireless Charging Pad',
    category: 'Electronics',
    subcategory: 'Phone Accessories',
    status: 'SLOW_MOVING',
    risk_level: 'MEDIUM',
    final_score: 52,
    expected_profit: 8.50,
    created_at: '2026-03-05T10:00:00Z',
    updated_at: '2026-04-15T09:00:00Z',
  },
  {
    id: '10',
    sku: 'RS-000010',
    name: 'Yoga Mat Premium',
    category: 'Sports',
    subcategory: 'Fitness Equipment',
    status: 'NEW',
    created_at: '2026-05-04T16:00:00Z',
    updated_at: '2026-05-04T16:00:00Z',
  },
];

export async function getProducts(filters?: {
  status?: ProductStatus;
  search?: string;
  category?: string;
}): Promise<Product[]> {
  let results = [...MOCK_PRODUCTS];

  if (filters?.status) {
    results = results.filter((p) => p.status === filters.status);
  }
  if (filters?.category) {
    results = results.filter((p) => p.category === filters.category);
  }
  if (filters?.search) {
    const q = filters.search.toLowerCase();
    results = results.filter(
      (p) =>
        p.name.toLowerCase().includes(q) ||
        p.sku.toLowerCase().includes(q) ||
        (p.category && p.category.toLowerCase().includes(q))
    );
  }

  return results;
}

export async function getProduct(id: string): Promise<Product | null> {
  return MOCK_PRODUCTS.find((p) => p.id === id) || null;
}

export async function createProduct(data: CreateProductInput): Promise<Product | null> {
  const newProduct: Product = {
    id: String(MOCK_PRODUCTS.length + 1),
    sku: `RS-${String(MOCK_PRODUCTS.length + 1).padStart(6, '0')}`,
    name: data.name,
    category: data.category,
    subcategory: data.subcategory,
    description: data.description,
    status: 'NEW',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  };
  return newProduct;
}

export async function updateProduct(id: string, data: Partial<Product>): Promise<Product | null> {
  const product = MOCK_PRODUCTS.find((p) => p.id === id);
  if (!product) return null;
  return { ...product, ...data, updated_at: new Date().toISOString() };
}

export async function deleteProduct(_id: string): Promise<void> {
  // Mock implementation
}
