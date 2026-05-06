export function ensureDefined(value: string | undefined | null, fieldName: string): string {
  if (!value) {
    throw new Error(`${fieldName} is required.`);
  }
  return value;
}

export function ensureWithin(value: number, max: number, fieldName: string): number {
  if (!Number.isFinite(value) || value <= 0) {
    throw new Error(`${fieldName} must be a positive number.`);
  }
  if (value > max) {
    throw new Error(`${fieldName} must be <= ${max}.`);
  }
  return value;
}

export function ensureOneQuery(queries: string[]): string {
  if (queries.length !== 1) {
    throw new Error('Exactly one query is allowed.');
  }
  const query = queries[0]?.trim();
  if (!query) {
    throw new Error('Query cannot be empty.');
  }
  return query;
}
