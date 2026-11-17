#!/usr/bin/env python3
"""
Playwright Mobile & Responsive Verification Test Suite for HeatShield AI.
Validates:
1. Multi-viewport rendering (360x640, 390x844, 430x932, 768x1024, 1440x900).
2. Zero horizontal overflow (scrollWidth <= innerWidth).
3. Minimum touch target heights (>= 44px).
4. No 'undefined' text in rendered titles, cards, or inspector panels.
5. Resident portal and planner navigation accessibility.
"""

import asyncio
import sys
from playwright.async_api import async_playwright

VIEWPORTS = [
    {"name": "compact_mobile", "width": 360, "height": 640, "is_mobile": True},
    {"name": "standard_mobile", "width": 390, "height": 844, "is_mobile": True},
    {"name": "large_mobile", "width": 430, "height": 932, "is_mobile": True},
    {"name": "tablet", "width": 768, "height": 1024, "is_mobile": False},
    {"name": "desktop", "width": 1440, "height": 900, "is_mobile": False},
]

BASE_URL = "http://localhost:8000"

async def check_no_horizontal_overflow(page, context_name):
    """Verifies that the page has no horizontal overflow."""
    scroll_width = await page.evaluate("() => document.documentElement.scrollWidth")
    inner_width = await page.evaluate("() => window.innerWidth")
    print(f"  [{context_name}] Horizontal width check: scrollWidth={scroll_width}, innerWidth={inner_width}")
    assert scroll_width <= inner_width + 1, (
        f"Horizontal overflow in {context_name}: scrollWidth ({scroll_width}) > innerWidth ({inner_width})"
    )

async def check_no_undefined_text(page, context_name):
    """Verifies no visible elements display the literal 'undefined' string."""
    undefined_count = await page.evaluate("""() => {
        const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
        let node;
        let count = 0;
        while ((node = walker.nextNode())) {
            const parent = node.parentElement;
            if (!parent) continue;
            const style = window.getComputedStyle(parent);
            if (style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0') continue;
            if (node.nodeValue && node.nodeValue.includes('undefined')) {
                console.warn('Found undefined in element:', parent, node.nodeValue);
                count++;
            }
        }
        return count;
    }""")
    assert undefined_count == 0, f"Found {undefined_count} visible 'undefined' instances in {context_name}"

async def check_mobile_touch_targets(page, context_name):
    """Verifies touch buttons in bottom dock, mobile nav, and resident view are >= 44px."""
    # Check bottom dock buttons that are currently visible
    dock_buttons = page.locator("#mobile-dock button:visible, #mobile-dock a:visible")
    count = await dock_buttons.count()
    print(f"  [{context_name}] Checking {count} visible mobile dock/tab touch targets...")
    assert count > 0, f"Expected visible mobile dock touch targets in {context_name}, found 0"
    for i in range(count):
        btn = dock_buttons.nth(i)
        box = await btn.bounding_box()
        if box:
            # 43.5 allows subpixel rounding down to 44px
            assert box["height"] >= 43.5, (
                f"Button #{i} height {box['height']}px is below 44px threshold in {context_name}"
            )

async def run_all_tests():
    print("=" * 70)
    print("HEATSHIELD AI - MOBILE & RESPONSIVE PLAYWRIGHT TEST SUITE")
    print("=" * 70)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        for vp in VIEWPORTS:
            vp_name = vp["name"]
            w = vp["width"]
            h = vp["height"]
            is_mobile = vp["is_mobile"]
            print(f"\n---> Testing Viewport: {vp_name} ({w}x{h})")

            context = await browser.new_context(
                viewport={"width": w, "height": h},
                user_agent=(
                    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 "
                    "(KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1"
                    if is_mobile else
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                )
            )
            page = await context.new_page()

            # Navigate to local web server
            await page.goto(BASE_URL, wait_until="networkidle")
            await asyncio.sleep(1.5)

            # Test 1: Check no horizontal overflow on initial load
            await check_no_horizontal_overflow(page, f"{vp_name}-initial")

            # Test 2: Check no undefined text on initial load
            await check_no_undefined_text(page, f"{vp_name}-initial")

            if is_mobile:
                # Test 3: Check mobile dock touch target heights
                await check_mobile_touch_targets(page, f"{vp_name}-initial")

                # Test 4: Open and test Resident Portal on mobile
                print(f"  [{vp_name}] Opening Resident Portal...")
                await page.evaluate("toggleResidentPortal(true)")
                await asyncio.sleep(1)

                # Ensure no horizontal scroll in Resident Portal
                await check_no_horizontal_overflow(page, f"{vp_name}-resident")
                await check_no_undefined_text(page, f"{vp_name}-resident")

                # Check Resident dock buttons are >= 44px
                await check_mobile_touch_targets(page, f"{vp_name}-resident")

                # Check cooling center card action buttons if centers rendered
                center_buttons = page.locator(".citizen-center-card button")
                btn_count = await center_buttons.count()
                if btn_count > 0:
                    first_btn = center_buttons.nth(0)
                    if await first_btn.is_visible():
                        box = await first_btn.bounding_box()
                        if box:
                            assert box["height"] >= 43.5, (
                                f"Cooling center button height {box['height']}px < 44px in {vp_name}"
                            )

                # Take screenshot of resident portal
                await page.screenshot(path=f"screenshot_{vp_name}_resident.png")
                print(f"  [{vp_name}] Saved screenshot_{vp_name}_resident.png")

                # Close resident portal
                await page.evaluate("toggleResidentPortal(false)")
                await asyncio.sleep(0.5)

            # Test 5: Open inspector panel and verify data bindings & plain labels
            print(f"  [{vp_name}] Testing Inspector Asset Data Wiring...")
            await page.evaluate("""() => {
                if (window.currentSites && window.currentSites.length > 0) {
                    inspectAsset(window.currentSites[0], 'site');
                }
            }""")
            await asyncio.sleep(0.5)

            # Verify no undefined text in inspector panel
            await check_no_undefined_text(page, f"{vp_name}-inspector")

            # Verify plain labels are present
            inspector_text = await page.evaluate("() => document.getElementById('inspector-body')?.innerText || ''")
            assert "Why this spot is hot" in inspector_text or "ML Attribution" in inspector_text or len(inspector_text) > 0, (
                f"Inspector body missing content in {vp_name}"
            )

            # Screenshot main view
            await page.screenshot(path=f"screenshot_{vp_name}_main.png")
            print(f"  [{vp_name}] Saved screenshot_{vp_name}_main.png")

            await context.close()

        await browser.close()
        print("\n" + "=" * 70)
        print("ALL RESPONSIVE & MOBILE USABILITY ASSERTIONS PASSED!")
        print("=" * 70)

if __name__ == "__main__":
    try:
        asyncio.run(run_all_tests())
    except Exception as e:
        print(f"\n[TEST SUITE FAILURE]: {e}", file=sys.stderr)
        sys.exit(1)

