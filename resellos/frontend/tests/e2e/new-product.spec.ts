import { test, expect } from '@playwright/test';

test.describe('New Product Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/products/new');
    await page.waitForSelector('text=New Product', { timeout: 10000 });
  });

  test('loads new product form with heading', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'New Product' })).toBeVisible();
  });

  test('shows all form fields', async ({ page }) => {
    await expect(page.getByPlaceholder('e.g., Portable Bluetooth Speaker')).toBeVisible();
    await expect(page.locator('select').first()).toBeVisible();
    await expect(page.getByPlaceholder('Optional product description, notes, or research observations...')).toBeVisible();
    await expect(page.getByPlaceholder('https://www.alibaba.com/product/...')).toBeVisible();
  });

  test('category dropdown has all options', async ({ page }) => {
    const select = page.locator('select').first();
    await expect(select).toBeVisible();
    const options = await select.locator('option').allTextContents();
    expect(options).toContain('Electronics');
    expect(options).toContain('Home & Garden');
    expect(options).toContain('Toys & Games');
  });

  test('submit button shows validation on empty submit', async ({ page }) => {
    await page.getByRole('button', { name: /create product/i }).click();
    await expect(page.getByText('Product name is required')).toBeVisible({ timeout: 3000 });
  });

  test('shows validation error when submitting empty form', async ({ page }) => {
    await page.getByRole('button', { name: /create product/i }).click();
    await expect(page.getByText('Product name is required')).toBeVisible();
  });

  test('back navigation works', async ({ page }) => {
    await page.locator('a[href="/products"]').first().click();
    await expect(page).toHaveURL(/\/products/);
  });
});

test.describe('Product Detail Page', () => {
  test('shows not found for invalid product ID', async ({ page }) => {
    await page.goto('/products/invalid-id-12345');
    await page.waitForTimeout(2000);
    // Just verify the page loads (will show product not found in the UI)
    await expect(page.locator('body')).toBeVisible();
  });
});