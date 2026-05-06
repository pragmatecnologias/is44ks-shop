import type { AppConfig, ToolResult } from '../types.js';
import { buildAudit } from '../utils/audit.js';
import { ensureDefined } from '../utils/validation.js';
import { guardWriteEnabled } from '../guards/approvalGuards.js';
import type { ResellOSClient } from '../resellosClient.js';

function wrap(
  tool: string,
  config: AppConfig,
  input: Record<string, unknown>,
  data: unknown,
  summary: string,
  nextRecommendedTool: string | null,
): ToolResult {
  return {
    ok: true,
    data,
    summary,
    warnings: [],
    next_recommended_tool: nextRecommendedTool,
    audit: buildAudit(tool, config.actor, input),
  };
}

export async function createShopConcept(
  client: ResellOSClient,
  input: {
    name: string;
    description?: string;
    target_customer?: string;
    category?: string;
    price_min?: number | null;
    price_max?: number | null;
    avoid_list_json?: Record<string, unknown>;
    preferred_attributes_json?: Record<string, unknown>;
    brand_angle?: string;
    status?: string;
  },
  config: AppConfig,
): Promise<ToolResult> {
  guardWriteEnabled(config);
  const payload = {
    name: ensureDefined(input.name, 'name'),
    description: input.description ?? undefined,
    target_customer: input.target_customer ?? undefined,
    category: input.category ?? undefined,
    price_min: input.price_min ?? undefined,
    price_max: input.price_max ?? undefined,
    avoid_list_json: input.avoid_list_json ?? {},
    preferred_attributes_json: input.preferred_attributes_json ?? {},
    brand_angle: input.brand_angle ?? undefined,
    status: input.status ?? 'DRAFT',
  };
  const shop = await client.post<any>('/api/portfolio/shops', payload);
  return wrap('resellos_create_shop_concept', config, payload, shop, `Created shop concept "${shop.name ?? payload.name}".`, 'resellos_list_shop_concepts');
}

export async function listShopConcepts(client: ResellOSClient, config: AppConfig): Promise<ToolResult> {
  const shops = await client.get<any[]>('/api/portfolio/shops');
  return {
    ok: true,
    data: { shops },
    summary: `Loaded ${shops.length} shop concept(s).`,
    warnings: [],
    next_recommended_tool: shops.length ? 'resellos_get_shop_concept' : 'resellos_create_shop_concept',
    audit: buildAudit('resellos_list_shop_concepts', config.actor, {}),
  };
}

export async function getShopConcept(client: ResellOSClient, shopId: string, config: AppConfig): Promise<ToolResult> {
  const detail = await client.get<any>(`/api/portfolio/shops/${shopId}`);
  return {
    ok: true,
    data: detail,
    summary: `Loaded shop concept "${detail?.shop_concept?.name ?? shopId}".`,
    warnings: [],
    next_recommended_tool: 'resellos_get_shop_portfolio_report',
    audit: buildAudit('resellos_get_shop_concept', config.actor, { shop_id: shopId }),
  };
}

export async function updateShopConcept(
  client: ResellOSClient,
  input: {
    shop_id: string;
    name?: string;
    description?: string;
    target_customer?: string;
    category?: string;
    price_min?: number | null;
    price_max?: number | null;
    avoid_list_json?: Record<string, unknown>;
    preferred_attributes_json?: Record<string, unknown>;
    brand_angle?: string;
    status?: string;
  },
  config: AppConfig,
): Promise<ToolResult> {
  guardWriteEnabled(config);
  const payload = {
    name: input.name ?? undefined,
    description: input.description ?? undefined,
    target_customer: input.target_customer ?? undefined,
    category: input.category ?? undefined,
    price_min: input.price_min ?? undefined,
    price_max: input.price_max ?? undefined,
    avoid_list_json: input.avoid_list_json ?? undefined,
    preferred_attributes_json: input.preferred_attributes_json ?? undefined,
    brand_angle: input.brand_angle ?? undefined,
    status: input.status ?? undefined,
  };
  const shop = await client.patch<any>(`/api/portfolio/shops/${input.shop_id}`, payload);
  return wrap('resellos_update_shop_concept', config, { ...payload, shop_id: input.shop_id }, shop, `Updated shop concept "${shop.name ?? input.shop_id}".`, 'resellos_get_shop_concept');
}

export async function createProductCollection(
  client: ResellOSClient,
  input: {
    shop_concept_id?: string;
    name: string;
    theme?: string;
    target_problem?: string;
    description?: string;
    status?: string;
  },
  config: AppConfig,
): Promise<ToolResult> {
  guardWriteEnabled(config);
  const shopId = ensureDefined(input.shop_concept_id, 'shop_concept_id');
  const payload = {
    shop_concept_id: shopId,
    name: ensureDefined(input.name, 'name'),
    theme: input.theme ?? undefined,
    target_problem: input.target_problem ?? undefined,
    description: input.description ?? undefined,
    status: input.status ?? 'DRAFT',
  };
  const collection = await client.post<any>(`/api/portfolio/shops/${shopId}/collections`, payload);
  return wrap('resellos_create_product_collection', config, payload, collection, `Created collection "${collection.name ?? payload.name}".`, 'resellos_get_shop_concept');
}

export async function updateProductCollection(
  client: ResellOSClient,
  input: {
    collection_id: string;
    shop_concept_id?: string;
    name?: string;
    theme?: string;
    target_problem?: string;
    description?: string;
    status?: string;
  },
  config: AppConfig,
): Promise<ToolResult> {
  guardWriteEnabled(config);
  const payload = {
    shop_concept_id: input.shop_concept_id ?? undefined,
    name: input.name ?? undefined,
    theme: input.theme ?? undefined,
    target_problem: input.target_problem ?? undefined,
    description: input.description ?? undefined,
    status: input.status ?? undefined,
  };
  const collection = await client.patch<any>(`/api/portfolio/collections/${input.collection_id}`, payload);
  return wrap('resellos_update_product_collection', config, { ...payload, collection_id: input.collection_id }, collection, `Updated collection "${collection.name ?? input.collection_id}".`, 'resellos_get_shop_concept');
}

export async function addPortfolioItem(
  client: ResellOSClient,
  input: {
    shop_concept_id?: string;
    collection_id?: string;
    idea_id?: string;
    product_id?: string;
    role?: string;
    status?: string;
    assortment_fit_score?: number;
    bundle_potential_score?: number;
    notes?: string;
  },
  config: AppConfig,
): Promise<ToolResult> {
  guardWriteEnabled(config);
  const shopId = ensureDefined(input.shop_concept_id, 'shop_concept_id');
  const payload = {
    shop_concept_id: shopId,
    collection_id: input.collection_id ?? undefined,
    idea_id: input.idea_id ?? undefined,
    product_id: input.product_id ?? undefined,
    role: input.role ?? 'CONSIDERING',
    status: input.status ?? 'CONSIDERING',
    assortment_fit_score: input.assortment_fit_score ?? 0,
    bundle_potential_score: input.bundle_potential_score ?? 0,
    notes: input.notes ?? undefined,
  };
  const item = await client.post<any>(`/api/portfolio/shops/${shopId}/items`, payload);
  return wrap('resellos_add_portfolio_item', config, payload, item, `Added portfolio item "${item.product_name ?? item.idea_name ?? item.id}".`, 'resellos_get_shop_concept');
}

export async function updatePortfolioItem(
  client: ResellOSClient,
  input: {
    item_id: string;
    shop_concept_id?: string;
    collection_id?: string;
    idea_id?: string;
    product_id?: string;
    role?: string;
    status?: string;
    assortment_fit_score?: number;
    bundle_potential_score?: number;
    notes?: string;
  },
  config: AppConfig,
): Promise<ToolResult> {
  guardWriteEnabled(config);
  const payload = {
    shop_concept_id: input.shop_concept_id ?? undefined,
    collection_id: input.collection_id ?? undefined,
    idea_id: input.idea_id ?? undefined,
    product_id: input.product_id ?? undefined,
    role: input.role ?? undefined,
    status: input.status ?? undefined,
    assortment_fit_score: input.assortment_fit_score ?? undefined,
    bundle_potential_score: input.bundle_potential_score ?? undefined,
    notes: input.notes ?? undefined,
  };
  const item = await client.patch<any>(`/api/portfolio/items/${input.item_id}`, payload);
  return wrap('resellos_update_portfolio_item', config, { ...payload, item_id: input.item_id }, item, `Updated portfolio item "${item.product_name ?? item.idea_name ?? input.item_id}".`, 'resellos_get_shop_concept');
}

export async function getShopPortfolioReport(client: ResellOSClient, shopId: string, config: AppConfig): Promise<ToolResult> {
  const report = await client.get<any>(`/api/portfolio/shops/${shopId}/report`);
  return {
    ok: true,
    data: report,
    summary: `Loaded portfolio report for shop ${shopId}.`,
    warnings: [],
    next_recommended_tool: 'resellos_get_shop_concept',
    audit: buildAudit('resellos_get_shop_portfolio_report', config.actor, { shop_id: shopId }),
  };
}
