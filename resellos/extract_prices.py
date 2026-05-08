#!/usr/bin/env python3
"""Extract active and competitor prices from eBay and supplier pages"""

from playwright.sync_api import sync_playwright
import subprocess, json, re, base64
from pathlib import Path

OUT_DIR = Path("/Users/admin/CascadeProjects/is44ks-shop/resellos/ebay-sold-proofs/evidence_capture")

# Reusable price extraction function
def extract_prices(page):
    data = page.evaluate("""() => {
        const text = document.body.innerText;
        // Find price patterns
        const priceRegex = /\\$[\\d,]+\\.\\d{2}/g;
        const prices = text.match(priceRegex) || [];
        const uniquePrices = [...new Set(prices)].slice(0, 10);

        // Look for structured price elements
        const priceEls = Array.from(document.querySelectorAll('[data-automation*="price"], .price, .product-price, #priceblock_ourprice, #priceblock_dealprice, .a-price .a-offscreen, .price-current'));
        const structuredPrices = priceEls.map(el => (el.innerText || el.textContent || '').trim()).filter(t => t.includes('$')).slice(0, 5);

        // Get title
        const title = document.title || '';

        return {
            title,
            prices: uniquePrices.length ? uniquePrices : structuredPrices,
            url: window.location.href,
        };
    }""")
    return data

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        viewport={"width": 1280, "height": 900},
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    )
    page = context.new_page()

    results = []

    # === eBay ACTIVE LISTINGS - specific product pages ===
    active_urls = [
        ("https://www.ebay.com/itm/374726059776", "Korky 4002BP Toilet Tank Lever"),
        ("https://www.ebay.com/itm/266892301404", "Universal Toilet Tank Flush Handle"),
        ("https://www.ebay.com/itm/384320427729", "Brass Toilet Tank Flush Handle"),
        ("https://www.ebay.com/itm/325693924660", "Danco Toilet Tank Lever"),
        ("https://www.ebay.com/itm/166974421740", "Fluidmaster Toilet Tank Lever"),
    ]

    print("=== CAPTURING eBay ACTIVE LISTINGS ===")
    for i, (url, name) in enumerate(active_urls):
        print(f"[{i+1}] {name}: {url[:70]}")
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=15000)
            page.wait_for_timeout(2000)

            title = page.title()
            if "Access Denied" in title or "403" in title or "Error" in title:
                print(f"  BLOCKED: {title}")
                continue

            screenshot = OUT_DIR / f"active_ebay_{i+1:02d}.png"
            page.screenshot(path=str(screenshot))

            data = extract_prices(page)
            print(f"  Title: {data['title'][:60]}")
            print(f"  Prices: {data['prices'][:4]}")

            results.append({
                "type": "active",
                "url": data['url'],
                "name": name,
                "title": data['title'],
                "prices": data['prices'],
                "screenshot": str(screenshot),
                "status": "captured"
            })
        except Exception as e:
            print(f"  ERROR: {e}")
        page.wait_for_timeout(1000)

    # === COMPETITOR pages ===
    competitor_urls = [
        ("https://www.ebay.com/itm/374726059776", "Korky 4002BP competitor"),
        ("https://www.ebay.com/itm/325693924660", "Danco competitor"),
    ]

    print("\n=== CAPTURING COMPETITORS ===")
    for i, (url, name) in enumerate(competitor_urls):
        print(f"[{i+1}] {name}: {url[:70]}")
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=15000)
            page.wait_for_timeout(2000)
            data = extract_prices(page)
            print(f"  Prices: {data['prices'][:4]}")
            results.append({
                "type": "competitor",
                "url": data['url'],
                "name": name,
                "title": data['title'],
                "prices": data['prices'],
                "status": "captured"
            })
        except Exception as e:
            print(f"  ERROR: {e}")
        page.wait_for_timeout(1000)

    browser.close()

# Write captured data
with open(OUT_DIR / "price_extraction.json", "w") as f:
    json.dump(results, f, indent=2)

print(f"\nDone. Captured {len(results)} results.")
for r in results:
    print(f"  {r['type']} - {r.get('prices', [])[:3]}")