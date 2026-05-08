#!/usr/bin/env python3
"""Phase 2-4: Capture active, competitor, and supplier evidence via Playwright"""

from playwright.sync_api import sync_playwright
import subprocess, json
from pathlib import Path

OUT_DIR = Path("/Users/admin/CascadeProjects/is44ks-shop/resellos/ebay-sold-proofs/evidence_capture")
OUT_DIR.mkdir(exist_ok=True)

PRODUCT_ID = "3cb810c2-8674-4e1e-9471-9222376b4412"

# === ACTIVE LISTING URLs to capture (specific product pages, not category pages) ===
ACTIVE_URLS = [
    ("https://www.homedepot.com/p/Fluidmaster-Perfect-Fit-Universal-Toilet-Tank-Lever-in-Chrome-641/206943002", "Fluidmaster Perfect Fit Universal Chrome"),
    ("https://www.amazon.com/Qualihome-Universal-Toilet-Handle-Replacement/dp/B07MVPWSGW", "Qualihome Universal Chrome"),
    ("https://www.plumbingsupply.com/case-and-briggs-toilet-tank-levers.html", "PlumbingSupply Tank Levers"),
    ("https://fluidmaster.com/shop/product/premium-lever/", "Fluidmaster Premium Lever"),
    ("https://fluidmaster.com/shop/product/perfect-fit-lever/", "Fluidmaster Perfect Fit Lever"),
    ("https://www.moen.com/bathroom/accessories-hardware/toilet-tank-levers/", "Moen Tank Levers"),
]

# === COMPETITOR URLs ===
COMPETITOR_URLS = [
    ("https://www.homedepot.com/p/Fluidmaster-Perfect-Fit-Universal-Toilet-Tank-Lever-in-Chrome-641/206943002", "Fluidmaster Perfect Fit Universal"),
    ("https://www.amazon.com/Qualihome-Universal-Toilet-Handle-Replacement/dp/B07MVPWSGW", "Qualihome Universal"),
    ("https://www.amazon.com/stores/Qualihome/page/C5A32804-4FE7-4ED4-BA3C-729E23536A1E", "Qualihome Amazon Store"),
]

# === SUPPLIER URLs ===
SUPPLIER_URLS = [
    ("https://www.plumbingsupply.com/case-and-briggs-toilet-tank-levers.html", "PlumbingSupply.com - Tank Levers"),
    ("https://www.signaturehardware.com/toilets-and-bidets/toilet-parts", "Signature Hardware"),
]

results = []

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        viewport={"width": 1280, "height": 900},
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    )
    page = context.new_page()

    # === CAPTURE ACTIVE LISTINGS ===
    print("\n=== CAPTURING ACTIVE LISTINGS ===")
    for i, (url, name) in enumerate(ACTIVE_URLS):
        screenshot = OUT_DIR / f"active_{i+1:02d}_{name[:20].replace(' ', '_')}.png"
        print(f"[Active {i+1}] {name}: {url[:70]}")

        try:
            page.goto(url, wait_until="domcontentloaded", timeout=15000)
            page.wait_forTimeout(2500)
            title = page.title()

            if "Access Denied" in title or "403" in title:
                print(f"  BLOCKED")
                results.append({"type": "active", "url": url, "name": name, "status": "blocked"})
                continue

            page.screenshot(path=str(screenshot), fullPage=False)

            # Extract price data
            data = page.evaluate("""() => {
                const text = document.body.innerText;
                const priceMatch = text.match(/\\$[\\d,]+\\.\\d{2}/g);
                const title = document.title;
                // Look for price in structured elements
                const priceEls = Array.from(document.querySelectorAll('[data-automation*="price"], .price, .product-price, #priceblock_ourprice, #priceblock_dealprice, .a-price .a-offscreen'));
                const prices = priceEls.slice(0,3).map(el => el.innerText || el.textContent).filter(t => t.includes('$'));
                return {
                    title,
                    prices: prices.length ? prices : (priceMatch ? priceMatch.slice(0,5) : []),
                    url: window.location.href,
                };
            }""")

            print(f"  Title: {data['title'][:60]}")
            print(f"  Prices: {data['prices'][:3]}")
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
            results.append({"type": "active", "url": url, "name": name, "status": "error", "error": str(e)})

        page.wait_for_timeout(1500)

    # === CAPTURE COMPETITORS ===
    print("\n=== CAPTURING COMPETITORS ===")
    for i, (url, name) in enumerate(COMPETITOR_URLS):
        screenshot = OUT_DIR / f"comp_{i+1:02d}_{name[:20].replace(' ', '_')}.png"
        print(f"[Comp {i+1}] {name}: {url[:70]}")

        try:
            page.goto(url, wait_until="domcontentloaded", timeout=15000)
            page.wait_for_timeout(2500)
            title = page.title()

            if "Access Denied" in title or "403" in title:
                print(f"  BLOCKED")
                results.append({"type": "competitor", "url": url, "name": name, "status": "blocked"})
                continue

            page.screenshot(path=str(screenshot), fullPage=False)

            data = page.evaluate("""() => {
                const text = document.body.innerText;
                const priceMatch = text.match(/\\$[\\d,]+\\.\\d{2}/g);
                const title = document.title;
                return {
                    title,
                    prices: priceMatch ? priceMatch.slice(0,5) : [],
                    url: window.location.href,
                };
            }""")

            print(f"  Title: {data['title'][:60]}")
            print(f"  Prices: {data['prices'][:3]}")
            results.append({
                "type": "competitor",
                "url": data['url'],
                "name": name,
                "title": data['title'],
                "prices": data['prices'],
                "screenshot": str(screenshot),
                "status": "captured"
            })

        except Exception as e:
            print(f"  ERROR: {e}")
            results.append({"type": "competitor", "url": url, "name": name, "status": "error", "error": str(e)})

        page.wait_for_timeout(1500)

    # === CAPTURE SUPPLIERS ===
    print("\n=== CAPTURING SUPPLIERS ===")
    for i, (url, name) in enumerate(SUPPLIER_URLS):
        screenshot = OUT_DIR / f"supplier_{i+1:02d}_{name[:20].replace(' ', '_')}.png"
        print(f"[Supplier {i+1}] {name}: {url[:70]}")

        try:
            page.goto(url, wait_until="domcontentloaded", timeout=15000)
            page.wait_for_timeout(2500)
            title = page.title()

            if "Access Denied" in title or "403" in title:
                print(f"  BLOCKED")
                results.append({"type": "supplier", "url": url, "name": name, "status": "blocked"})
                continue

            page.screenshot(path=str(screenshot), fullPage=False)

            data = page.evaluate("""() => {
                const text = document.body.innerText;
                const priceMatch = text.match(/\\$[\\d,]+\\.\\d{2}/g);
                const title = document.title;
                // Look for supplier pricing
                const bulkMatch = text.match(/(?:wholesale|bulk|moq|per.unit|unit.cost)[^$]*(\\$[\\d,]+\\.\\d{2})/i);
                return {
                    title,
                    prices: priceMatch ? priceMatch.slice(0,8) : [],
                    url: window.location.href,
                    bulk_hint: bulkMatch ? bulkMatch[1] : null,
                };
            }""")

            print(f"  Title: {data['title'][:60]}")
            print(f"  Prices: {data['prices'][:4]}")
            if data.get('bulk_hint'):
                print(f"  Bulk hint: {data['bulk_hint']}")
            results.append({
                "type": "supplier",
                "url": data['url'],
                "name": name,
                "title": data['title'],
                "prices": data['prices'],
                "bulk_hint": data.get('bulk_hint'),
                "screenshot": str(screenshot),
                "status": "captured"
            })

        except Exception as e:
            print(f"  ERROR: {e}")
            results.append({"type": "supplier", "url": url, "name": name, "status": "error", "error": str(e)})

        page.wait_for_timeout(1500)

    browser.close()

# Write results
manifest = {"captured_at": "2026-05-08", "results": results}
with open(OUT_DIR / "evidence_manifest.json", "w") as f:
    json.dump(manifest, f, indent=2)

print(f"\nCaptured {len([r for r in results if r.get('status') == 'captured'])} pages")
print(f"Screenshots: {len(list(OUT_DIR.glob('*.png')))}")