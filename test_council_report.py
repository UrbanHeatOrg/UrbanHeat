"""
Test Suite for City Council Resilience Briefing Packet & Printable Endpoints.
Verifies:
1. Static HTML serving for /council-report, /report, /report/council
2. HTML template structure and 5-page municipal briefing packet integrity
3. Dynamic API endpoint /api/council-report/data for:
   - Dallas, TX (default reference city)
   - Phoenix, AZ (national catalog)
   - Chicago, IL (national catalog)
4. Fiscal allocation calculations, Title VI equity audit metrics, and resolution generation
"""

import sys
from pathlib import Path
from fastapi.testclient import TestClient

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from web.server import app

client = TestClient(app)


def test_html_routes():
    """Verify HTML routes serve the printable report properly."""
    for path in ["/council-report", "/report", "/report/council"]:
        response = client.get(path)
        assert response.status_code == 200, f"Failed route {path}: {response.status_code}"
        assert "text/html" in response.headers.get("content-type", "")
        body = response.text
        # Verify 5 pages are present
        assert "Page 1 of 5 — Executive Action Memo" in body
        assert "Page 2 of 5 — Priority Siting Roster" in body
        assert "Page 3 of 5 — XAI Drivers & Districts" in body
        assert "Page 4 of 5 — Title VI Audit & Fiscal Note" in body
        assert "Page 5 of 5 — Legislative Resolution" in body
        # Verify Print media styles are present
        assert "@media print" in body
        assert "size: letter portrait" in body
    print("✓ HTML routes and 5-page template structure verified successfully.")


def test_api_council_report_dallas():
    """Verify dynamic data hydration endpoint for Dallas, TX."""
    response = client.get("/api/council-report/data?city=Dallas&state=Texas&county=Dallas&budget=10000000")
    assert response.status_code == 200, f"Dallas failed: {response.status_code}"
    data = response.json()
    assert data["status"] == "success"
    assert data["city"] == "Dallas"
    assert data["state"] == "Texas"
    assert data["county"] == "Dallas"

    # Sites
    sites = data["sites"]
    assert len(sites) >= 4, f"Expected at least 4 sites, got {len(sites)}"
    assert sites[0]["rank"] == 1
    assert "Bachman Lake" in sites[0]["facility_name"]

    # Resolution
    res = data["resolution"]
    assert res is not None
    assert "resolution_title" in res or "resolution_id" in res
    assert "Dallas" in res.get("city", "") or "Dallas" in res.get("resolution_title", "")

    # Equity Audit
    equity = data["equity_audit"]
    assert equity is not None
    assert "Passed" in equity.get("audit_status", "") or equity.get("audit_status") == "PASSED"

    # Fiscal Allocation
    fisc = data["fiscal_allocation"]
    assert fisc["total_budget"] == 10000000
    assert fisc["permanent_hubs"]["amount"] == 6800000.0
    assert fisc["mobile_fleet"]["amount"] == 1800000.0
    assert fisc["pedestrian_infrastructure"]["amount"] == 1400000.0

    # Heat Frequency
    hf = data["heat_frequency"]
    assert hf is not None
    assert "historic_extreme_temp_f" in hf or "extreme_max_temperature_f" in hf

    print("✓ Dallas council report API contract and calculations verified.")


def test_api_council_report_national_cities():
    """Verify dynamic data hydration for Phoenix and Chicago."""
    for city, state, county in [
        ("Phoenix", "Arizona", "Maricopa"),
        ("Chicago", "Illinois", "Cook"),
    ]:
        response = client.get(f"/api/council-report/data?city={city}&state={state}&county={county}&budget=15000000")
        assert response.status_code == 200, f"{city} failed: {response.status_code}"
        data = response.json()
        assert data["status"] == "success"
        assert data["city"] == city
        assert len(data["sites"]) >= 3
        assert data["fiscal_allocation"]["total_budget"] == 15000000
        assert data["equity_audit"] is not None
        print(f"✓ {city}, {state} council report contract verified.")


if __name__ == "__main__":
    print("\n--- Running City Council Report Test Suite ---")
    test_html_routes()
    test_api_council_report_dallas()
    test_api_council_report_national_cities()
    print("\n All Council Report Tests PASSED Successfully!\n")
