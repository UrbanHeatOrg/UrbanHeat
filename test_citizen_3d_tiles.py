import asyncio
from playwright.async_api import async_playwright

async def run_citizen_3d_test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await context.new_page()
        page.on("console", lambda msg: print(f"[BROWSER CONSOLE {msg.type}]: {msg.text}"))
        page.on("pageerror", lambda err: print(f"[BROWSER ERROR]: {err}"))

        print("[1/6] Loading HeatShield AI at http://localhost:8000...")
        await page.goto("http://localhost:8000", wait_until="domcontentloaded")
        await asyncio.sleep(3)

        print("[2/6] Opening Citizen Heat Relief Portal...")
        await page.evaluate("switchAppMode('citizen')")
        await asyncio.sleep(2)
        await page.screenshot(path="screenshot_citizen_2d.png")
        print(" -> Captured screenshot_citizen_2d.png (2D Street Leaflet View)")

        print("[3/6] Testing 2D/3D Toggle to 3D Photorealistic Mesh Mode...")
        await page.click("#citizen-btn-3d")
        await asyncio.sleep(3)

        # Verify DOM visibility
        is_3d_visible = await page.evaluate("!document.getElementById('citizen-cesium-container').classList.contains('hidden')")
        is_2d_hidden = await page.evaluate("document.getElementById('citizen-map').classList.contains('hidden')")
        dimension_mode = await page.evaluate("citizenMapDimension")
        print(f" -> 3D Container Visible: {is_3d_visible}, 2D Container Hidden: {is_2d_hidden}, Mode: {dimension_mode}")
        assert is_3d_visible and is_2d_hidden, "Dimension toggle state failed!"

        await page.screenshot(path="screenshot_citizen_3d.png")
        print(" -> Captured screenshot_citizen_3d.png (3D Photorealistic Tiles View)")

        print("[4/6] Selecting cooling center card in 3D Mode...")
        # Click the second cooling center card
        cards = await page.query_selector_all("#resident-centers-list > div")
        if len(cards) > 1:
            await cards[1].click()
            await asyncio.sleep(2)
            await page.screenshot(path="screenshot_citizen_3d_focus.png")
            print(" -> Captured screenshot_citizen_3d_focus.png (Camera Fly-To & Shaded Route)")

        print("[5/6] Testing toggle button back to 2D Street View...")
        await page.click("#citizen-btn-2d")
        await asyncio.sleep(2)
        is_3d_hidden = await page.evaluate("document.getElementById('citizen-cesium-container').classList.contains('hidden')")
        is_2d_visible = await page.evaluate("!document.getElementById('citizen-map').classList.contains('hidden')")
        print(f" -> 3D Container Hidden: {is_3d_hidden}, 2D Container Visible: {is_2d_visible}")
        assert is_3d_hidden and is_2d_visible, "2D restore toggle state failed!"

        print("[6/6] All Citizen 3D Photorealistic Tiles tests passed successfully!")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_citizen_3d_test())
