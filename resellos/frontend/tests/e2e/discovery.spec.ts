import { test, expect } from '@playwright/test';

test.describe('Discovery', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/discovery');
    await page.waitForSelector('text=Product Discovery', { timeout: 10000 });
  });

  test('loads discovery page with heading', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Product Discovery' })).toBeVisible();
  });

  test('shows quick scan form', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Quick Scan', exact: true })).toBeVisible();
  });

  test('shows workflow steps', async ({ page }) => {
    await expect(page.getByText('1. Enter an idea')).toBeVisible();
    await expect(page.getByText('2. Quick scan')).toBeVisible();
    await expect(page.getByText('3. Collect evidence')).toBeVisible();
    await expect(page.getByText('4. Promote')).toBeVisible();
  });

  test('shows idea form fields', async ({ page }) => {
    await expect(page.getByLabel(/idea name/i)).toBeVisible();
    await expect(page.getByLabel(/category/i)).toBeVisible();
    await expect(page.getByLabel(/source platform/i)).toBeVisible();
  });

  test('quick scan button is disabled when idea name is empty', async ({ page }) => {
    const quickScanBtn = page.getByRole('button', { name: /quick scan/i });
    await expect(quickScanBtn).toBeDisabled();
  });

  test('quick scan button is enabled when idea name is filled', async ({ page }) => {
    await page.getByLabel(/idea name/i).fill('Test Product Idea');
    const quickScanBtn = page.getByRole('button', { name: /quick scan/i });
    await expect(quickScanBtn).toBeEnabled();
  });

  test('save idea button is enabled when idea name is filled', async ({ page }) => {
    await page.getByLabel(/idea name/i).fill('Test Idea');
    const saveBtn = page.getByRole('button', { name: /save idea/i });
    await expect(saveBtn).toBeEnabled();
  });

  test('shows discovery queue section', async ({ page }) => {
    await expect(page.getByText('Discovery Queue')).toBeVisible();
  });

  test('shows external research section', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'External Research' })).toBeVisible();
    await expect(page.getByText('DataForSEO jobs').first()).toBeVisible();
    await expect(page.getByText('Evidence candidates').first()).toBeVisible();
  });

  test('shows opportunity board', async ({ page }) => {
    await expect(page.getByText('Opportunity Board')).toBeVisible();
  });
});