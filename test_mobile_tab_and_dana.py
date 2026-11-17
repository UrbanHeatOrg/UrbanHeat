#!/usr/bin/env python3
"""
Playwright test to verify:
1. Map is the default tab and first tab in mobile citizen view.
2. Top segmented switcher order: Map first (active), List second.
3. Bottom dock order: Map first (active), List second.
4. Mobile dock button says "Ask CoolAid" (not "Ask Dana").
5. Toggling between tabs functions properly.
"""

import asyncio
import sys
from playwright.async_api import async_playwright

BASE_URL = "http://localhost:8000"

async def test_mobile_citizen_map_default():
    print("=" * 70)
    print("VERIFYING MOBILE CITIZEN MAP DEFAULT & DOCK LABELS")
    print("=" * 70)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Mobile iPhone 14 viewport
        context = await browser.new_context(
            viewport={"width": 390, "height": 844},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1"
        )
        page = await context.new_page()

        print(f"Navigating to {BASE_URL} on mobile viewport (390x844)...")
        await page.goto(BASE_URL, wait_until="networkidle", timeout=15000)
        await asyncio.sleep(2)

        # 1. Verify citizen mode is active on mobile
        app_mode = await page.evaluate("() => currentAppMode")
        print(f"Current app mode on mobile: '{app_mode}'")
        assert app_mode == "citizen", f"Expected 'citizen' mode on mobile, got '{app_mode}'"

        # 2. Verify currentCitizenMobileTab is 'map'
        active_tab = await page.evaluate("() => currentCitizenMobileTab")
        print(f"Current citizen mobile tab: '{active_tab}'")
        assert active_tab == "map", f"Expected default tab to be 'map', got '{active_tab}'"

        # 3. Verify visibility of map container and sidebar
        map_visible = await page.evaluate("""() => {
            const el = document.getElementById('citizen-map-container');
            if (!el) return false;
            const style = window.getComputedStyle(el);
            return style.display !== 'none' && !el.classList.contains('hidden');
        }""")
        sidebar_hidden = await page.evaluate("""() => {
            const el = document.getElementById('citizen-sidebar');
            if (!el) return true;
            return el.classList.contains('hidden');
        }""")
        print(f"Map container visible: {map_visible}, Sidebar hidden: {sidebar_hidden}")
        assert map_visible, "citizen-map-container should be visible by default on mobile!"
        assert sidebar_hidden, "citizen-sidebar should be hidden by default on mobile!"

        # 4. Verify top segmented switcher button order and classes
        top_switcher_info = await page.evaluate("""() => {
            const container = document.querySelector('#citizen-sidebar .md\\\\:hidden.px-3');
            if (!container) return null;
            const buttons = Array.from(container.querySelectorAll('button'));
            return buttons.map(b => ({
                id: b.id,
                text: b.innerText.trim(),
                hasActiveBg: b.classList.contains('bg-cyan-500'),
                classList: Array.from(b.classList)
            }));
        }""")
        print(f"Top switcher buttons: {top_switcher_info}")
        assert top_switcher_info is not None, "Top segmented switcher not found in #citizen-sidebar!"
        assert len(top_switcher_info) == 2, f"Expected 2 buttons in top switcher, got {len(top_switcher_info)}"
        assert top_switcher_info[0]["id"] == "mob-tab-btn-map", f"Expected Map to be first tab in top switcher, got {top_switcher_info[0]['id']}"
        assert top_switcher_info[1]["id"] == "mob-tab-btn-list", f"Expected List to be second tab in top switcher, got {top_switcher_info[1]['id']}"
        assert top_switcher_info[0]["hasActiveBg"], "First tab (Map) in top switcher should have active bg-cyan-500!"

        # 5. Verify bottom dock buttons order and labels
        dock_info = await page.evaluate("""() => {
            const container = document.getElementById('dock-citizen-items');
            if (!container) return null;
            const items = Array.from(container.children);
            return items.map(el => ({
                tag: el.tagName,
                id: el.id,
                text: el.innerText.trim(),
                isCyanText: el.classList.contains('text-cyan-400')
            }));
        }""")
        print(f"Citizen dock items: {dock_info}")
        assert dock_info is not None, "#dock-citizen-items not found!"
        assert len(dock_info) >= 4, f"Expected at least 4 dock items, got {len(dock_info)}"
        assert dock_info[0]["id"] == "dock-btn-res-map", f"Expected dock button 1 to be dock-btn-res-map, got {dock_info[0]['id']}"
        assert dock_info[1]["id"] == "dock-btn-res-list", f"Expected dock button 2 to be dock-btn-res-list, got {dock_info[1]['id']}"
        assert dock_info[0]["isCyanText"], "Map dock button should be active (text-cyan-400) by default!"

        # 6. Verify "Ask CoolAid" label (and NO "Ask Dana")
        dana_count = await page.evaluate("""() => {
            const bodyText = document.body.innerText;
            const matches = bodyText.match(/Ask Dana/gi);
            return matches ? matches.length : 0;
        }""")
        print(f"Occurrences of 'Ask Dana' in page text: {dana_count}")
        assert dana_count == 0, f"Found {dana_count} instances of 'Ask Dana' in page text!"

        coolaid_dock_text = dock_info[3]["text"]
        print(f"Dock button 4 text: '{coolaid_dock_text}'")
        assert "Ask CoolAid" in coolaid_dock_text, f"Expected 'Ask CoolAid' in dock button 4, got '{coolaid_dock_text}'"

        # Capture screenshot of default map view on mobile
        screenshot_map_path = "screenshot_mobile_default_map.png"
        await page.screenshot(path=screenshot_map_path)
        print(f"Saved default map screenshot to {screenshot_map_path}")

        # 7. Test switching to List tab
        print("\nSwitching to 'list' tab via setCitizenMobileTab('list')...")
        await page.evaluate("setCitizenMobileTab('list')")
        await asyncio.sleep(0.5)

        tab_after_list = await page.evaluate("() => currentCitizenMobileTab")
        assert tab_after_list == "list", f"Expected 'list' tab, got '{tab_after_list}'"

        sidebar_visible = await page.evaluate("""() => {
            const el = document.getElementById('citizen-sidebar');
            return el && !el.classList.contains('hidden');
        }""")
        map_hidden = await page.evaluate("""() => {
            const el = document.getElementById('citizen-map-container');
            return el && el.classList.contains('hidden');
        }""")
        print(f"Sidebar visible: {sidebar_visible}, Map hidden: {map_hidden}")
        assert sidebar_visible, "citizen-sidebar should be visible when tab is 'list'!"
        assert map_hidden, "citizen-map-container should be hidden when tab is 'list'!"

        screenshot_list_path = "screenshot_mobile_list_tab.png"
        await page.screenshot(path=screenshot_list_path)
        print(f"Saved list tab screenshot to {screenshot_list_path}")

        # 8. Test switching back to Map tab via dock button click
        print("\nSwitching back to 'map' tab via clicking dock-btn-res-map...")
        await page.click("#dock-btn-res-map")
        await asyncio.sleep(0.5)

        tab_back_map = await page.evaluate("() => currentCitizenMobileTab")
        assert tab_back_map == "map", f"Expected 'map' tab, got '{tab_back_map}'"

        map_visible_again = await page.evaluate("""() => {
            const el = document.getElementById('citizen-map-container');
            return el && !el.classList.contains('hidden');
        }""")
        assert map_visible_again, "citizen-map-container should be visible again after clicking Map tab!"

        await context.close()
        await browser.close()

    print("\n" + "=" * 70)
    print("ALL MOBILE CITIZEN TAB & DOCK ASSERTIONS PASSED PERFECTLY!")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(test_mobile_citizen_map_default())
