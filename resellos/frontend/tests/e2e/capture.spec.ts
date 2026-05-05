import { test, expect } from '@playwright/test';

test.describe('Capture', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/capture');
    await page.waitForSelector('text=Capture Evidence', { timeout: 10000 });
  });

  test('loads capture page with heading', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Capture Evidence' })).toBeVisible();
    await expect(page.getByText('Manually capture marketplace data')).toBeVisible();
  });

  test('shows all capture type options', async ({ page }) => {
    const select = page.locator('select').first();
    await expect(select).toBeVisible();
    const options = await select.locator('option').allTextContents();
    expect(options).toContain('Marketplace screenshot');
    expect(options).toContain('Supplier screenshot');
    expect(options).toContain('Competitor screenshot');
    expect(options).toContain('Visual risk');
  });

  test('shows capture type dropdown with default selection', async ({ page }) => {
    const select = page.locator('select').first();
    await expect(select).toBeVisible();
    await expect(select).toHaveValue('MARKETPLACE_SCREENSHOT');
  });

  test('capture button is disabled when no data provided', async ({ page }) => {
    const captureBtn = page.getByRole('button', { name: /capture evidence/i });
    await expect(captureBtn).toBeDisabled();
  });

  test('capture button is enabled when pasted text is provided', async ({ page }) => {
    await page.getByPlaceholder('Paste listing text, competitor data, or any raw evidence here...').fill('Test listing data from eBay');
    const captureBtn = page.getByRole('button', { name: /capture evidence/i });
    await expect(captureBtn).toBeEnabled();
  });

  test('capture button is enabled when URL is provided', async ({ page }) => {
    await page.getByPlaceholder('https://www.ebay.com/itm/...').fill('https://www.ebay.com/itm/123456');
    const captureBtn = page.getByRole('button', { name: /capture evidence/i });
    await expect(captureBtn).toBeEnabled();
  });

  test('shows idea ID field', async ({ page }) => {
    await expect(page.getByPlaceholder('Paste a discovery idea ID to link this capture...')).toBeVisible();
  });

  test('shows pasted text textarea', async ({ page }) => {
    await expect(page.getByPlaceholder('Paste listing text, competitor data, or any raw evidence here...')).toBeVisible();
  });

  test('shows notes field', async ({ page }) => {
    await expect(page.getByPlaceholder('Any observations, context, or risk flags...')).toBeVisible();
  });

  test('shows source URL field', async ({ page }) => {
    await expect(page.getByPlaceholder('https://www.ebay.com/itm/...')).toBeVisible();
  });

  test('shows screenshot upload field', async ({ page }) => {
    await expect(page.getByText('Screenshot (optional)')).toBeVisible();
  });

  test('navigates back to discovery via arrow button', async ({ page }) => {
    await page.locator('a[href="/discovery"].p-2').click();
    await expect(page).toHaveURL(/\/discovery/);
  });
});