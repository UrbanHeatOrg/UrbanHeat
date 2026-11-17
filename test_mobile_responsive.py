import asyncio
from playwright.async_api import async_playwright

async def run_tests():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        # 1. Mobile Test (390 x 844) - iPhone 14
        print("--- Testing Mobile Viewport (390x844) ---")
        context_mobile = await browser.new_context(
            viewport={"width": 390, "height": 844},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1"
        )
        page_mobile = await context_mobile.new_page()
        await page_mobile.goto("http://localhost:8000", wait_until="networkidle")
        await asyncio.sleep(2)
        
        # Explicitly ensure mobile starts on clean map view
        await page_mobile.click("#dock-btn-map")
        await asyncio.sleep(1)
        await page_mobile.screenshot(path="screenshot_mobile_map.png")
        print("Captured screenshot_mobile_map.png")
        
        # Click "Layers" in mobile dock
        await page_mobile.click("#dock-btn-layers")
        await asyncio.sleep(1)
        await page_mobile.screenshot(path="screenshot_mobile_layers.png")
        print("Captured screenshot_mobile_layers.png")
        
        # Click "Intel" in mobile dock
        await page_mobile.click("#dock-btn-intel")
        await asyncio.sleep(1)
        await page_mobile.screenshot(path="screenshot_mobile_intel.png")
        print("Captured screenshot_mobile_intel.png")
        
        # Click "Solar" in mobile dock
        await page_mobile.click("#dock-btn-solar")
        await asyncio.sleep(1)
        await page_mobile.screenshot(path="screenshot_mobile_solar.png")
        print("Captured screenshot_mobile_solar.png")

        # Test Mobile Track Bar: Click "Track 1: Dispatch"
        await page_mobile.click("#nav-mobile-track1")
        await asyncio.sleep(1)
        await page_mobile.screenshot(path="screenshot_mobile_track1.png")
        print("Captured screenshot_mobile_track1.png")

        # Click Copilot button
        await page_mobile.click("#btn-open-copilot")
        await asyncio.sleep(1)
        await page_mobile.screenshot(path="screenshot_mobile_copilot_drawer.png")
        print("Captured screenshot_mobile_copilot_drawer.png")

        # Close Copilot
        await page_mobile.click("#copilot-drawer button:has(.fa-xmark)")
        await asyncio.sleep(0.5)

        # Test Find Cool Now Resident Portal on mobile
        await page_mobile.click("#nav-mobile-resident")
        await asyncio.sleep(1)
        await page_mobile.screenshot(path="screenshot_mobile_resident_portal.png")
        print("Captured screenshot_mobile_resident_portal.png")

        # Close Resident Portal
        await page_mobile.evaluate("toggleResidentPortal(false)")
        await asyncio.sleep(0.5)

        # 2. Tablet Test (768 x 1024) - iPad
        print("\n--- Testing Tablet Viewport (768x1024) ---")
        context_tablet = await browser.new_context(
            viewport={"width": 768, "height": 1024},
            user_agent="Mozilla/5.0 (iPad; CPU OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1"
        )
        page_tablet = await context_tablet.new_page()
        await page_tablet.goto("http://localhost:8000", wait_until="networkidle")
        await asyncio.sleep(2)
        await page_tablet.screenshot(path="screenshot_tablet_responsive.png")
        print("Captured screenshot_tablet_responsive.png")

        # 3. Desktop Test (1440 x 900)
        print("\n--- Testing Desktop Viewport (1440x900) ---")
        context_desktop = await browser.new_context(viewport={"width": 1440, "height": 900})
        page_desktop = await context_desktop.new_page()
        await page_desktop.goto("http://localhost:8000", wait_until="networkidle")
        await asyncio.sleep(2)
        await page_desktop.screenshot(path="screenshot_desktop_verified.png")
        print("Captured screenshot_desktop_verified.png")

        await browser.close()
        print("\nAll responsive screenshots captured successfully!")

if __name__ == "__main__":
    asyncio.run(run_tests())
