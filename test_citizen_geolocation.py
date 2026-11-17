import asyncio
from playwright.async_api import async_playwright

async def run_geolocation_tests():
    print("=" * 70)
    print("CITIZEN VIEW AUTOMATIC GEOLOCATION VERIFICATION SUITE")
    print("=" * 70)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        # TEST 1: Direct link ?mode=citizen with Mock Geolocation (Oak Cliff, Dallas)
        print("\n[TEST 1] Direct Citizen Portal Navigation with GPS Enabled...")
        mock_lat = 32.7485
        mock_lon = -96.8150
        context_gps = await browser.new_context(
            permissions=["geolocation"],
            geolocation={"latitude": mock_lat, "longitude": mock_lon},
            viewport={"width": 1440, "height": 900}
        )
        page1 = await context_gps.new_page()

        # Listen for any unexpected alerts
        unexpected_alerts = []
        page1.on("dialog", lambda dialog: unexpected_alerts.append(dialog.message))

        await page1.goto("http://localhost:8000/?mode=citizen", wait_until="load")
        await page1.wait_for_selector(".citizen-center-card", timeout=15000)
        await asyncio.sleep(1)

        # Inspect JS state
        state = await page1.evaluate("""() => {
            const gpsBtn = document.getElementById('res-gps-btn-text');
            const cityBadge = document.getElementById('res-metro-badge');
            const citySelect = document.getElementById('res-city-select');
            const cards = document.querySelectorAll('.citizen-center-card');
            const pulseMarker = document.querySelector('.user-pulse-marker');
            return {
                mode: typeof currentAppMode !== 'undefined' ? currentAppMode : null,
                coords: typeof citizenUserCoords !== 'undefined' ? citizenUserCoords : null,
                dataCount: typeof currentResidentData !== 'undefined' && currentResidentData ? currentResidentData.length : 0,
                gpsBtnText: gpsBtn ? gpsBtn.innerText : null,
                cityBadgeText: cityBadge ? cityBadge.innerText : null,
                citySelectValue: citySelect ? citySelect.value : null,
                citySelectText: citySelect && citySelect.selectedOptions[0] ? citySelect.selectedOptions[0].innerText : null,
                cardsRendered: cards.length,
                hasPulseMarker: !!pulseMarker
            };
        }""")

        print(f"  Mode: {state['mode']}")
        print(f"  Detected Coords: {state['coords']}")
        print(f"  GPS Button Text: '{state['gpsBtnText']}'")
        print(f"  City Badge: '{state['cityBadgeText']}'")
        print(f"  City Dropdown: '{state['citySelectText']}' ({state['citySelectValue']})")
        print(f"  Cooling Centers Loaded: {state['dataCount']} (Rendered Cards: {state['cardsRendered']})")
        print(f"  Leaflet GPS Pulse Marker Active: {state['hasPulseMarker']}")

        assert state['mode'] == 'citizen', f"Expected mode 'citizen', got {state['mode']}"
        assert state['coords'] is not None and len(state['coords']) == 2, "citizenUserCoords not set"
        assert abs(state['coords'][0] - mock_lat) < 0.001, f"Latitude mismatch: {state['coords'][0]} vs {mock_lat}"
        assert abs(state['coords'][1] - mock_lon) < 0.001, f"Longitude mismatch: {state['coords'][1]} vs {mock_lon}"
        assert "GPS Active" in state['gpsBtnText'] or "📍" in state['gpsBtnText'], f"GPS button not active: {state['gpsBtnText']}"
        assert state['cardsRendered'] > 0, "No cooling center cards rendered"
        assert state['hasPulseMarker'], "Leaflet map did not render user pulse marker"
        assert len(unexpected_alerts) == 0, f"Unexpected alert popups: {unexpected_alerts}"

        await page1.screenshot(path="screenshot_citizen_auto_gps.png")
        print("  ✅ TEST 1 PASSED — Screenshot saved to screenshot_citizen_auto_gps.png")
        await context_gps.close()

        # TEST 2: Mode Switch from Planner HUD via Top Bar Button
        print("\n[TEST 2] Switching to Citizen Mode via UI Button (#mode-btn-citizen)...")
        mock_lat_phx = 33.4484
        mock_lon_phx = -112.0740
        context_switch = await browser.new_context(
            permissions=["geolocation"],
            geolocation={"latitude": mock_lat_phx, "longitude": mock_lon_phx},
            viewport={"width": 1440, "height": 900}
        )
        page2 = await context_switch.new_page()
        await page2.goto("http://localhost:8000", wait_until="load")
        await page2.wait_for_selector("#mode-btn-citizen", timeout=15000)
        await asyncio.sleep(1)

        # Confirm starts in planner mode
        mode_initial = await page2.evaluate("() => typeof currentAppMode !== 'undefined' ? currentAppMode : null")
        print(f"  Initial Mode: {mode_initial}")
        assert mode_initial == 'planner'

        # Click citizen mode button and wait for the API response
        async with page2.expect_response(lambda r: "/api/resident/cooling-centers" in r.url and r.status == 200):
            await page2.click("#mode-btn-citizen")
        
        await page2.wait_for_selector(".citizen-center-card", timeout=10000)
        await asyncio.sleep(1)

        state2 = await page2.evaluate("""() => {
            const gpsBtn = document.getElementById('res-gps-btn-text');
            const cityBadge = document.getElementById('res-metro-badge');
            const citySelect = document.getElementById('res-city-select');
            const cards = document.querySelectorAll('.citizen-center-card');
            const pulseMarker = document.querySelector('.user-pulse-marker');
            return {
                mode: currentAppMode,
                coords: citizenUserCoords,
                gpsBtnText: gpsBtn ? gpsBtn.innerText : null,
                cityBadgeText: cityBadge ? cityBadge.innerText : null,
                citySelectText: citySelect && citySelect.selectedOptions[0] ? citySelect.selectedOptions[0].innerText : null,
                dataCount: currentResidentData ? currentResidentData.length : 0,
                cardsRendered: cards.length,
                pulseMarker: !!pulseMarker
            };
        }""")

        print(f"  Switched Mode: {state2['mode']}")
        print(f"  Detected Coords: {state2['coords']}")
        print(f"  GPS Button Text: '{state2['gpsBtnText']}'")
        print(f"  City Badge: '{state2['cityBadgeText']}'")
        print(f"  City Dropdown: '{state2['citySelectText']}'")
        print(f"  Cooling Centers: {state2['dataCount']} (Rendered Cards: {state2['cardsRendered']})")
        print(f"  Pulse Marker: {state2['pulseMarker']}")

        assert state2['mode'] == 'citizen', "Did not switch to citizen mode"
        assert state2['coords'] is not None and abs(state2['coords'][0] - mock_lat_phx) < 0.001, "Coordinates not automatically set"
        assert "GPS Active" in state2['gpsBtnText'] or "📍" in state2['gpsBtnText'], "GPS Button not active"
        assert state2['dataCount'] > 0, "No cooling centers found for detected location"
        assert state2['pulseMarker'], "User pulse marker not on map"

        await page2.screenshot(path="screenshot_citizen_switch_mode.png")
        print("  ✅ TEST 2 PASSED — Screenshot saved to screenshot_citizen_switch_mode.png")
        await context_switch.close()

        # TEST 3: Graceful Fallback when Geolocation is Denied
        print("\n[TEST 3] Geolocation Denied Graceful Fallback...")
        context_denied = await browser.new_context(
            permissions=[],
            viewport={"width": 1440, "height": 900}
        )
        page3 = await context_denied.new_page()

        # Catch any alert popups
        alerts_caught = []
        page3.on("dialog", lambda dialog: (alerts_caught.append(dialog.message), dialog.dismiss()))

        await page3.goto("http://localhost:8000/?mode=citizen", wait_until="load")
        await page3.wait_for_selector(".citizen-center-card", timeout=15000)
        await asyncio.sleep(1)

        state3 = await page3.evaluate("""() => {
            const gpsBtn = document.getElementById('res-gps-btn-text');
            const cityBadge = document.getElementById('res-metro-badge');
            const cards = document.querySelectorAll('.citizen-center-card');
            return {
                mode: currentAppMode,
                dataCount: currentResidentData ? currentResidentData.length : 0,
                cardsRendered: cards.length,
                cityBadgeText: cityBadge ? cityBadge.innerText : null,
                gpsBtnText: gpsBtn ? gpsBtn.innerText : null
            };
        }""")

        print(f"  Mode: {state3['mode']}")
        print(f"  Fallback Centers Loaded: {state3['dataCount']} (Cards: {state3['cardsRendered']})")
        print(f"  City Badge: '{state3['cityBadgeText']}'")
        print(f"  GPS Button Text: '{state3['gpsBtnText']}'")
        print(f"  Alerts Suppressed During Auto-Locate: {len(alerts_caught) == 0}")

        assert state3['mode'] == 'citizen', "Should be in citizen mode"
        assert state3['cardsRendered'] > 0, "Should fall back and render city cooling centers"
        assert len(alerts_caught) == 0, f"Auto-locate should not show modal alerts on denial: {alerts_caught}"

        await page3.screenshot(path="screenshot_citizen_denied_fallback.png")
        print("  ✅ TEST 3 PASSED — Screenshot saved to screenshot_citizen_denied_fallback.png")
        await context_denied.close()

        # TEST 4: Mobile Direct Navigation (Auto-detects Mobile, Defaults to Citizen Relief + GPS)
        print("\n[TEST 4] Mobile Direct Navigation without Query Params (Auto-GPS on Mobile)...")
        mock_mobile_lat = 32.7767
        mock_mobile_lon = -96.7970
        context_mobile = await browser.new_context(
            permissions=["geolocation"],
            geolocation={"latitude": mock_mobile_lat, "longitude": mock_mobile_lon},
            viewport={"width": 390, "height": 844},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1"
        )
        page4 = await context_mobile.new_page()
        # Navigate to root without any ?mode parameter
        await page4.goto("http://localhost:8000/", wait_until="load")
        await page4.wait_for_selector(".citizen-center-card", state="attached", timeout=15000)
        await asyncio.sleep(1)

        state4 = await page4.evaluate("""() => {
            const gpsBtn = document.getElementById('res-gps-btn-text');
            const cityBadge = document.getElementById('res-metro-badge');
            const cards = document.querySelectorAll('.citizen-center-card');
            const pulseMarker = document.querySelector('.user-pulse-marker');
            return {
                mode: typeof currentAppMode !== 'undefined' ? currentAppMode : null,
                coords: typeof citizenUserCoords !== 'undefined' ? citizenUserCoords : null,
                cardsRendered: cards.length,
                cityBadgeText: cityBadge ? cityBadge.innerText : null,
                gpsBtnText: gpsBtn ? gpsBtn.innerText : null,
                hasPulseMarker: !!pulseMarker
            };
        }""")

        print(f"  Mobile Mode: {state4['mode']}")
        print(f"  Detected Mobile Coords: {state4['coords']}")
        print(f"  City Badge: '{state4['cityBadgeText']}'")
        print(f"  GPS Button Text: '{state4['gpsBtnText']}'")
        print(f"  Cards Rendered: {state4['cardsRendered']}")
        print(f"  Pulse Marker Active: {state4['hasPulseMarker']}")

        assert state4['mode'] == 'citizen', f"Expected mode 'citizen' on mobile, got {state4['mode']}"
        assert state4['coords'] is not None and len(state4['coords']) == 2, "Mobile citizenUserCoords not set"
        assert abs(state4['coords'][0] - mock_mobile_lat) < 0.001, f"Latitude mismatch: {state4['coords'][0]} vs {mock_mobile_lat}"
        assert abs(state4['coords'][1] - mock_mobile_lon) < 0.001, f"Longitude mismatch: {state4['coords'][1]} vs {mock_mobile_lon}"
        assert "GPS Active" in state4['gpsBtnText'] or "📍" in state4['gpsBtnText'], f"GPS button not active: {state4['gpsBtnText']}"
        assert state4['cardsRendered'] > 0, "No cooling centers rendered on mobile"
        assert state4['hasPulseMarker'], "Leaflet map did not render user pulse marker on mobile"

        await page4.screenshot(path="screenshot_mobile_auto_gps.png")
        print("  ✅ TEST 4 PASSED — Screenshot saved to screenshot_mobile_auto_gps.png")
        await context_mobile.close()

        await browser.close()

    print("\n" + "=" * 70)
    print("ALL 4 CITIZEN GEOLOCATION AUTOMATION TESTS PASSED (100%)")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(run_geolocation_tests())
