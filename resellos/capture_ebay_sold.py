#!/usr/bin/env python3
"""
eBay Sold Proof Screenshot Capture
Captures eBay sold/completed listings for toilet tank flush lever products
Saves screenshots for manual review
"""

from playwright.sync_api import sync_playwright
import subprocess, json, os
from pathlib import Path

OUT_DIR = Path("/Users/admin/CascadeProjects/is44ks-shop/resellos/ebay-sold-proofs")
OUT_DIR.mkdir(exist_ok=True)

SEARCHES = [
    ("toilet+tank+flush+lever+replacement", "01_lever"),
    ("toilet+tank+handle+replacement", "02_handle"),
    ("universal+toilet+tank+lever", "03_universal"),
    ("brass+toilet+tank+lever", "04_brass"),
    ("Korky+toilet+tank+lever", "05_korky"),
    ("Fluidmaster+toilet+tank+lever", "06_fluidmaster"),
    ("Danco+toilet+tank+lever", "07_danco"),
    ("toilet+tank+lever+2+inch", "08_2inch"),
    ("metal+toilet+flush+lever+handle", "09_metal"),
]

BASE_URL = "https://www.ebay.com/sch/i.html?_nkw={search}&LH_Sold=1&_sop=12"

results = []

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        viewport={"width": 1280, "height": 900},
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    )
    page = context.new_page()

    for search_term, label in SEARCHES:
        url = BASE_URL.format(search=search_term)
        screenshot_path = OUT_DIR / f"search_{label}.png"
        print(f"[{label}] Navigating: {search_term}")

        try:
            page.goto(url, wait_until="domcontentloaded", timeout=15000)
            page.wait_for_timeout(2000)
            title = page.title()

            if "Access Denied" in title or "403" in title:
                print(f"  BLOCKED: {title}")
            else:
                page.evaluate("window.scrollTo(0, 400)")
                page.wait_for_timeout(1000)
                page.screenshot(path=str(screenshot_path), full_page=False)
                print(f"  Saved: {screenshot_path.name}")

                # Extract item links
                item_links = page.evaluate("""() => {
                    const links = Array.from(document.querySelectorAll('a[href*="/itm/"]'));
                    return links
                        .map(a => a.href)
                        .filter(u => u.match(/\\/itm\\/\\d+/))
                        .filter(u => !u.includes('ebay.com/itm/157261456168'));
                }""")
                print(f"  Found {len(item_links)} item links")
                results.append({
                    "search": search_term,
                    "label": label,
                    "screenshot": str(screenshot_path),
                    "title": title,
                    "item_count": len(item_links),
                    "items": item_links[:6],
                })

        except Exception as e:
            print(f"  ERROR: {e}")

        page.wait_for_timeout(1500)

    # Capture individual item pages
    print("\n--- Capturing individual sold items ---")
    item_id = 1
    seen_urls = set()

    for search_result in results:
        for item_url in search_result.get("items", []):
            if item_url in seen_urls:
                continue
            seen_urls.add(item_url)

            screenshot_path = OUT_DIR / f"item_{item_id:03d}.png"
            print(f"  Item {item_id}: {item_url[:80]}")

            try:
                page.goto(item_url, wait_until="domcontentloaded", timeout=15000)
                page.wait_for_timeout(2000)

                title = page.title()
                if "Access Denied" in title or "403" in title:
                    print(f"    BLOCKED")
                    continue

                page.screenshot(path=str(screenshot_path), full_page=False)
                print(f"    Saved: {screenshot_path.name}")

                # Extract sold info
                sold_info = page.evaluate("""() => {
                    const text = document.body.innerText;
                    const soldMatch = text.match(/(\\d+)\\s*sold/i);
                    const priceMatch = text.match(/\\$[\\d,]+\\.\\d{2}/g);
                    return {
                        soldCount: soldMatch ? soldMatch[1] : null,
                        prices: priceMatch ? priceMatch.slice(0, 5) : [],
                        title: document.title,
                        url: window.location.href,
                    };
                }""")
                print(f"    Sold count: {sold_info['soldCount']}, Prices: {sold_info['prices'][:3]}")
                results.append({
                    "type": "item",
                    "url": item_url,
                    "screenshot": str(screenshot_path),
                    "title": sold_info["title"],
                    "sold_count": sold_info["soldCount"],
                    "prices": sold_info["prices"],
                })

            except Exception as e:
                print(f"    ERROR: {e}")

            item_id += 1
            page.wait_for_timeout(1500)

    browser.close()

manifest = {
    "captured_at": "2026-05-08",
    "total_searches": len(SEARCHES),
    "results": results,
}
manifest_path = OUT_DIR / "manifest.json"
with open(manifest_path, "w") as f:
    json.dump(manifest, f, indent=2)

print(f"\nDone. Manifest: {manifest_path}")
print(f"Screenshots: {len(list(OUT_DIR.glob('*.png')))}")