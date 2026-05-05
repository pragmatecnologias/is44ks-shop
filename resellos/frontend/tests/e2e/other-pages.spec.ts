import { test, expect } from '@playwright/test';

test.describe('Inventory Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/inventory');
    await page.waitForTimeout(2000);
  });

  test('loads inventory page with heading', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Inventory', exact: true })).toBeVisible();
  });

  test('shows add inventory button', async ({ page }) => {
    await expect(page.getByRole('button', { name: /add inventory/i })).toBeVisible();
  });

  test('shows empty state when no inventory', async ({ page }) => {
    await expect(page.getByText('No inventory yet')).toBeVisible({ timeout: 5000 });
  });
});

test.describe('Sales Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/sales');
    await page.waitForTimeout(2000);
  });

  test('loads sales page with heading', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Sales', exact: true })).toBeVisible();
  });

  test('shows record sale button', async ({ page }) => {
    await expect(page.getByRole('button', { name: /record sale/i })).toBeVisible();
  });

  test('shows empty state when no sales', async ({ page }) => {
    await expect(page.getByText('No sales yet')).toBeVisible({ timeout: 5000 });
  });
});

test.describe('Settings Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/settings');
    await page.waitForTimeout(2000);
  });

  test('loads settings page', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Settings', exact: true })).toBeVisible();
  });
});

test.describe('Ideas Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/ideas');
    await page.waitForTimeout(2000);
  });

  test('loads ideas page', async ({ page }) => {
    await expect(page.getByText('Ideas').first()).toBeVisible({ timeout: 5000 });
  });
});

test.describe('Opportunities Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/opportunities');
    await page.waitForTimeout(2000);
  });

  test('loads opportunities page', async ({ page }) => {
    await expect(page.getByText('Opportunities').first()).toBeVisible({ timeout: 5000 });
  });
});

test.describe('Listings Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/listings');
    await page.waitForTimeout(2000);
  });

  test('loads listings page', async ({ page }) => {
    await expect(page.getByText('Listings').first()).toBeVisible({ timeout: 5000 });
  });
});