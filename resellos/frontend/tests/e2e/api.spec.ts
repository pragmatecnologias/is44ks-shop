import { test, expect } from '@playwright/test';

test.describe('API Health Checks', () => {
  test('backend API docs accessible', async ({ request }) => {
    const response = await request.get('http://localhost:8000/docs');
    expect(response.status()).toBe(200);
  });

  test('dashboard stats endpoint returns valid JSON', async ({ request }) => {
    const response = await request.get('http://localhost:8000/api/dashboard/stats');
    expect(response.status()).toBe(200);
    const data = await response.json();
    expect(data).toHaveProperty('total_products');
    expect(data).toHaveProperty('blocked_count');
    expect(data).toHaveProperty('watchlist_count');
  });

  test('products API returns empty array initially', async ({ request }) => {
    const response = await request.get('http://localhost:8000/api/products');
    expect(response.status()).toBe(200);
    const data = await response.json();
    expect(Array.isArray(data)).toBe(true);
  });

  test('discovery list endpoint works', async ({ request }) => {
    const response = await request.get('http://localhost:8000/api/discovery');
    expect(response.status()).toBe(200);
    const data = await response.json();
    expect(Array.isArray(data)).toBe(true);
  });

  test('can create a discovery idea via API', async ({ request }) => {
    const response = await request.post('http://localhost:8000/api/discovery', {
      data: {
        idea_name: 'Test Idea from Playwright',
        category: 'Car accessories',
        source_platform: 'Alibaba',
      },
    });
    expect(response.status()).toBe(201);
    const data = await response.json();
    expect(data.idea_name).toBe('Test Idea from Playwright');
  });

  test('quick scan creates idea and returns verdict', async ({ request }) => {
    const response = await request.post('http://localhost:8000/api/discovery/quick-scan', {
      data: {
        idea_name: 'Quick Scan Test Product',
        category: 'Desk accessories',
        source_platform: 'Alibaba',
      },
    });
    expect(response.status()).toBe(200);
    const data = await response.json();
    expect(data).toHaveProperty('quick_scan_verdict');
    expect(data).toHaveProperty('idea');
    expect(data.idea.idea_name).toBe('Quick Scan Test Product');
  });
});
