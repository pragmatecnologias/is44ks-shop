import { test, expect } from '@playwright/test';

test.describe('Products Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/products');
    await page.waitForTimeout(2000); // Allow API to load
  });

  test('loads products page with heading', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Products' })).toBeVisible();
  });

  test('shows products count', async ({ page }) => {
    await expect(page.getByText(/\d+ product/)).toBeVisible({ timeout: 5000 });
  });

  test('shows new product button', async ({ page }) => {
    await expect(page.getByRole('link', { name: /new product/i })).toBeVisible();
  });

  test('shows search input', async ({ page }) => {
    await expect(page.getByPlaceholder(/search by name/i)).toBeVisible();
  });

  test('shows status filter dropdown', async ({ page }) => {
    const select = page.locator('select').first();
    await expect(select).toBeVisible();
  });

  test('shows action buttons', async ({ page }) => {
    await expect(page.getByText('Create')).toBeVisible();
    await expect(page.getByText('Import')).toBeVisible();
    await expect(page.getByText('Run Research')).toBeVisible();
  });

  test('search input accepts text', async ({ page }) => {
    const searchInput = page.getByPlaceholder(/search by name/i);
    await searchInput.fill('test search');
    await expect(searchInput).toHaveValue('test search');
  });
});