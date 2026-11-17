import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 390, "height": 844})
        await page.goto("http://localhost:8000/", wait_until="networkidle")
        await page.wait_for_timeout(2000)
        
        # Switch to planner view
        await page.click("#mode-btn-planner")
        await page.wait_for_timeout(1000)
        
        # Click budget / simulator
        await page.evaluate("toggleBottomDrawer(true)")
        await page.wait_for_timeout(1000)
        
        await page.screenshot(path="screenshot_pareto_mobile_planner.png")
        
        drawer = page.locator("#bottom-drawer")
        box = await drawer.bounding_box()
        print(f"Mobile planner drawer bounding box: {box}")
        
        style = await drawer.evaluate("""el => {
            const cs = window.getComputedStyle(el);
            return {
                transform: cs.transform,
                zIndex: cs.zIndex,
                display: cs.display,
                position: cs.position,
                bottom: cs.bottom,
                left: cs.left,
                right: cs.right,
                top: cs.top,
                height: cs.height,
                maxHeight: cs.maxHeight,
                overflowY: cs.overflowY
            };
        }""")
        print(f"Computed style: {style}")

        await browser.close()

asyncio.run(run())
