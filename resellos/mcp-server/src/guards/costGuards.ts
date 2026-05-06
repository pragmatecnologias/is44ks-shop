import type { AppConfig } from '../types.js';
import { ensureOneQuery, ensureWithin } from '../utils/validation.js';

export function guardDataForSeoRequest(config: AppConfig, query: string, maxResults: number): { query: string; maxResults: number } {
  const normalizedQuery = query.trim();
  ensureWithin(maxResults, config.maxDataForSeoResults, 'max_results');
  return {
    query: normalizedQuery,
    maxResults,
  };
}

export function guardQueries(config: AppConfig, queries: string[]): string {
  if (queries.length > config.maxDataForSeoQueries) {
    throw new Error(`Only ${config.maxDataForSeoQueries} query(ies) allowed per run.`);
  }
  return ensureOneQuery(queries);
}
