#!/usr/bin/env node
/**
 * eBay Sold Proof Screenshot Capture
 * Captures eBay sold/finished listings for toilet tank flush lever products
 * Saves screenshots for manual review
 */

const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const OUT_DIR = path.join(__dirname, 'ebay-sold-proofs');
if (!fs.existsSync(OUT_DIR)) fs.mkdirSync(OUT_DIR, { recursive: true });

const SEARCHES = [
  'toilet+tank+flush+lever+replacement',
  'toilet+tank+handle+replacement',
  'universal+toilet+tank+lever',
  'brass+toilet+tank+lever',
  'Korky+toilet+tank+lever',
  'Fluidmaster+toilet+tank+lever',
  'Danco+toilet+tank+lever',
  'toilet+tank+lever+2+inch',
  'metal+toilet+flush+lever+handle',
];

const BASE_URL = 'https://www.ebay.com/sch/i.html?_nkw=SEARCH&LH_Sold=1&_sop=12';

async function captureSearch(page, searchTerm, index) {
  const url = BASE_URL.replace('SEARCH', searchTerm);
  const filename = `${String(index).padStart(2, '0')}_${searchTerm.replace(/\+/g, '_')}.png`;
  const filepath = path.join(OUT_DIR, filename);

  console.log(`[${index}] Navigating: ${searchTerm}`);
  try {
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 15000 });
    await page.waitForTimeout(2000);

    // Check if we got blocked
    const title = await page.title();
    if (title.includes('Access Denied') || title.includes('403')) {
      console.log(`  BLOCKED: ${title}`);
      return null;
    }

    // Scroll to load content
    await page.evaluate(() => window.scrollTo(0, 400));
    await page.waitForTimeout(1000);

    await page.screenshot({ path: filepath, fullPage: false });
    console.log(`  Saved: ${filename} (${title})`);
    return filepath;
  } catch (e) {
    console.log(`  ERROR: ${e.message}`);
    return null;
  }
}

async function captureItem(page, itemUrl, index) {
  const filename = `${String(index).padStart(3, '0')}_item.png`;
  const filepath = path.join(OUT_DIR, filename);

  console.log(`  Item: ${itemUrl}`);
  try {
    await page.goto(itemUrl, { waitUntil: 'domcontentloaded', timeout: 15000 });
    await page.waitForTimeout(2000);

    const title = await page.title();
    if (title.includes('Access Denied') || title.includes('403')) {
      console.log(`    BLOCKED`);
      return null;
    }

    await page.screenshot({ path: filepath, fullPage: false });
    console.log(`    Saved: ${filename}`);
    return filepath;
  } catch (e) {
    console.log(`    ERROR: ${e.message}`);
    return null;
  }
}

async function main() {
  console.log('Starting eBay sold proof capture...');
  console.log(`Output directory: ${OUT_DIR}\n`);

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1280, height: 900 },
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
  });
  const page = await context.newPage();

  let captured = 0;
  const results = [];

  // Capture each search page
  for (let i = 0; i < SEARCHES.length; i++) {
    const result = await captureSearch(page, SEARCHES[i], i + 1);
    if (result) {
      captured++;
      results.push({ search: SEARCHES[i], file: result });
    }
    await page.waitForTimeout(1500);
  }

  // Now try to extract item links from the first search results and capture items
  console.log('\n--- Re-visiting top results for item captures ---');
  const topSearch = SEARCHES[0];
  const topUrl = BASE_URL.replace('SEARCH', topSearch);
  await page.goto(topUrl, { waitUntil: 'domcontentloaded', timeout: 15000 });
  await page.waitForTimeout(2000);

  // Extract item links from search results
  const itemLinks = await page.$$eval('a[href*="/itm/"]', links =>
    links
      .map(a => a.href)
      .filter(h => h.includes('/itm/') && !h.includes('ebay.com/itm/157261456168')) // dedupe
      .slice(0, 8)
  );

  console.log(`Found ${itemLinks.length} item links from top search`);

  for (let j = 0; j < Math.min(itemLinks.length, 6); j++) {
    const result = await captureItem(page, itemLinks[j], 100 + j);
    if (result) {
      captured++;
      results.push({ item: itemLinks[j], file: result });
    }
    await page.waitForTimeout(1500);
  }

  await browser.close();

  // Write results manifest
  const manifest = {
    captured_at: new Date().toISOString(),
    total_captured: captured,
    results,
    searches_run: SEARCHES.length,
  };

  fs.writeFileSync(path.join(OUT_DIR, 'manifest.json'), JSON.stringify(manifest, null, 2));
  console.log(`\nDone. Captured ${captured} screenshots. Manifest written to ${OUT_DIR}/manifest.json`);
}

main().catch(e => {
  console.error('Fatal:', e);
  process.exit(1);
});