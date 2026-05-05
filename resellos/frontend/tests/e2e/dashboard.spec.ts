import { test, expect } from '@playwright/test';

test.describe('Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/dashboard');
    await page.waitForSelector('text=ResellOS Command Center', { timeout: 10000 });
  });

  test('loads and shows stat cards', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'ResellOS Command Center' })).toBeVisible();
    await expect(page.getByText('Total Products')).toBeVisible();
    await expect(page.getByText('Blocked')).toBeVisible();
    await expect(page.getByText('Watchlist')).toBeVisible();
  });

  test('shows recent products section', async ({ page }) => {
    await expect(page.getByText('Recent Products')).toBeVisible();
  });

  test('shows agent activity section', async ({ page }) => {
    await expect(page.getByText('Agent Activity')).toBeVisible();
  });

  test('shows top categories section', async ({ page }) => {
    await expect(page.getByText('Top Categories')).toBeVisible();
  });

  test('new product button navigates to products new page', async ({ page }) => {
    await page.goto('/products/new');
    await expect(page.getByRole('heading', { name: 'New Product' })).toBeVisible({ timeout: 5000 });
  });

  test('stat cards are clickable links', async ({ page }) => {
    const totalProductsCard = page.locator('a[href="/products"]').first();
    await expect(totalProductsCard).toBeVisible();
  });
});