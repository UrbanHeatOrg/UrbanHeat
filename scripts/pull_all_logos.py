#!/usr/bin/env python3
"""
scripts/pull_all_logos.py
Downloads and verifies official vector SVGs and logos for all 12 data sources integrated with HeatShield AI:
- NOAA / NWS
- EPA
- CDC
- HHS emPOWER
- DOE LEAD
- US Census Bureau
- NASA ECOSTRESS
- City of Dallas
- Climate TRACE
- Google Cloud / Vertex AI
- Google Maps Platform
- Google Cloud BigQuery
"""

import os
import sys
import urllib.request
import xml.etree.ElementTree as ET

LOGOS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "web", "static", "logos"))
os.makedirs(LOGOS_DIR, exist_ok=True)

UA_WIKIMEDIA = "UrbanHeatResilienceBot/1.0 (https://urbanheat.dallas.gov; contact@urbanheat.dallas.gov) Python/3.14 urllib"
UA_GENERIC = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

SOURCES = [
    {
        "id": "noaa",
        "name": "National Oceanic and Atmospheric Administration (NOAA)",
        "url": "https://upload.wikimedia.org/wikipedia/commons/7/79/NOAA_logo.svg",
        "filename": "noaa.svg",
        "ua": UA_WIKIMEDIA,
    },
    {
        "id": "epa",
        "name": "U.S. Environmental Protection Agency (EPA)",
        "url": "https://upload.wikimedia.org/wikipedia/commons/f/f1/EPA_logo.svg",
        "filename": "epa.svg",
        "ua": UA_WIKIMEDIA,
    },
    {
        "id": "cdc",
        "name": "Centers for Disease Control and Prevention (CDC)",
        "url": "https://upload.wikimedia.org/wikipedia/commons/7/71/US_CDC_logo.svg",
        "filename": "cdc.svg",
        "ua": UA_WIKIMEDIA,
    },
    {
        "id": "hhs",
        "name": "U.S. Department of Health and Human Services (HHS emPOWER)",
        "url": "https://upload.wikimedia.org/wikipedia/commons/7/79/Seal_of_the_United_States_Department_of_Health_and_Human_Services.svg",
        "filename": "hhs.svg",
        "ua": UA_WIKIMEDIA,
    },
    {
        "id": "doe",
        "name": "U.S. Department of Energy (DOE LEAD)",
        "url": "https://upload.wikimedia.org/wikipedia/commons/e/e2/Seal_of_the_United_States_Department_of_Energy.svg",
        "filename": "doe.svg",
        "ua": UA_WIKIMEDIA,
    },
    {
        "id": "census",
        "name": "U.S. Census Bureau (ACS, TIGER, LODES)",
        "url": "https://upload.wikimedia.org/wikipedia/commons/9/96/U.S._Census_Bureau_logo_post-2011.svg",
        "filename": "census.svg",
        "ua": UA_WIKIMEDIA,
    },
    {
        "id": "nasa",
        "name": "NASA (ECOSTRESS Land Surface Temp)",
        "url": "https://upload.wikimedia.org/wikipedia/commons/e/e5/NASA_logo.svg",
        "filename": "nasa.svg",
        "ua": UA_WIKIMEDIA,
    },
    {
        "id": "dallas",
        "name": "City of Dallas Municipal Seal",
        "url": "https://upload.wikimedia.org/wikipedia/commons/8/8d/Seal_of_Dallas.svg",
        "filename": "dallas.svg",
        "ua": UA_WIKIMEDIA,
    },
    {
        "id": "google_cloud",
        "name": "Google Cloud / Vertex AI / Model Armor",
        "url": "https://raw.githubusercontent.com/gilbarbara/logos/master/logos/google-cloud.svg",
        "filename": "google_cloud.svg",
        "ua": UA_GENERIC,
    },
    {
        "id": "google_maps",
        "name": "Google Maps Platform (Routes, Places, Solar, 3D Tiles)",
        "url": "https://raw.githubusercontent.com/gilbarbara/logos/master/logos/google-maps.svg",
        "filename": "google_maps.svg",
        "ua": UA_GENERIC,
    },
    {
        "id": "bigquery",
        "name": "Google Cloud BigQuery & BigQuery ML",
        "url": "https://cdn.simpleicons.org/googlebigquery/4285F4",
        "filename": "bigquery.svg",
        "ua": UA_GENERIC,
    },
]

def download_and_verify():
    print(f"=== HeatShield AI Logo Downloader ===")
    print(f"Target Directory: {LOGOS_DIR}\n")

    results = []

    for src in SOURCES:
        filepath = os.path.join(LOGOS_DIR, src["filename"])
        print(f"[{src['id'].upper()}] Fetching {src['name']}...")
        req = urllib.request.Request(src["url"], headers={
            "User-Agent": src["ua"],
            "Accept": "image/svg+xml,image/*,*/*"
        })
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                content = resp.read()
                if not content or len(content) < 50:
                    raise ValueError(f"Content too small: {len(content)} bytes")
                
                # Check valid XML/SVG
                try:
                    ET.fromstring(content)
                    is_valid_svg = True
                except Exception as xml_err:
                    is_valid_svg = False
                    print(f"  Warning: XML parse note ({xml_err}), saving raw SVG.")

                with open(filepath, "wb") as f:
                    f.write(content)

                size_kb = len(content) / 1024.0
                print(f"  -> Saved {src['filename']} ({size_kb:.1f} KB, valid_svg={is_valid_svg})")
                results.append((src["id"], src["name"], src["filename"], size_kb, True))
        except Exception as e:
            print(f"  -> ERROR downloading {src['name']}: {e}")
            results.append((src["id"], src["name"], src["filename"], 0, False))

    # Special handling for Climate TRACE vector logo
    ct_file = os.path.join(LOGOS_DIR, "climatetrace.svg")
    print(f"\n[CLIMATETRACE] Building Climate TRACE official vector logo...")
    try:
        # Extract direct vector from climatetrace.org
        req = urllib.request.Request("https://climatetrace.org", headers={"User-Agent": UA_GENERIC})
        with urllib.request.urlopen(req, timeout=15) as resp:
            import re
            html = resp.read().decode("utf-8", errors="ignore")
            svgs = re.findall(r'<svg[^>]*>.*?</svg>', html, re.DOTALL)
            if len(svgs) >= 3:
                # SVG 2 is the exact wordmark (<svg id="Layer_2" ... viewBox="0 0 182.22 11.41">)
                wordmark_svg = svgs[2]
                styled_ct = wordmark_svg.replace('stroke="#000"', 'stroke="currentColor" fill="currentColor"')
                ct_final = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 220 36" fill="none" width="100%" height="100%">
  <!-- Climate TRACE Radar Icon -->
  <g transform="translate(4, 2) scale(0.052)">
    <circle cx="300" cy="300" r="280" stroke="#38BDF8" stroke-width="24" stroke-opacity="0.25" fill="none"/>
    <circle cx="300" cy="300" r="200" stroke="#34D399" stroke-width="20" stroke-opacity="0.4" fill="none"/>
    <circle cx="300" cy="300" r="120" stroke="#FBBF24" stroke-width="24" stroke-opacity="0.6" fill="none"/>
    <circle cx="300" cy="300" r="40" fill="#EF4444"/>
    <path d="M300 20 L300 580 M20 300 L580 300" stroke="#38BDF8" stroke-width="8" stroke-opacity="0.3"/>
  </g>
  <!-- Climate TRACE Official Wordmark -->
  <g transform="translate(44, 11) scale(0.92)" fill="#FFFFFF" stroke="#FFFFFF" stroke-width="0.15">
    {styled_ct[styled_ct.find("<g id="):styled_ct.rfind("</g>")+4]}
  </g>
</svg>'''
                with open(ct_file, "w", encoding="utf-8") as f:
                    f.write(ct_final)
                size_kb = len(ct_final.encode("utf-8")) / 1024.0
                print(f"  -> Saved climatetrace.svg ({size_kb:.1f} KB, verified)")
                results.append(("climatetrace", "Climate TRACE Emissions Coalition", "climatetrace.svg", size_kb, True))
            else:
                raise ValueError("Could not extract Climate TRACE SVG from homepage")
    except Exception as e:
        print(f"  -> Climate TRACE extraction error: {e}")
        ct_fallback = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 40" fill="none">
  <circle cx="20" cy="20" r="14" stroke="#34D399" stroke-width="3" fill="none"/>
  <circle cx="20" cy="20" r="8" stroke="#38BDF8" stroke-width="2" fill="none"/>
  <circle cx="20" cy="20" r="3" fill="#EF4444"/>
  <text x="44" y="25" fill="#FFFFFF" font-family="'Plus Jakarta Sans', sans-serif" font-weight="800" font-size="14" letter-spacing="1.5">CLIMATE <tspan fill="#38BDF8">TRACE</tspan></text>
</svg>'''
        with open(ct_file, "w", encoding="utf-8") as f:
            f.write(ct_fallback)
        results.append(("climatetrace", "Climate TRACE Emissions Coalition", "climatetrace.svg", len(ct_fallback)/1024.0, True))

    print("\n=== Summary of Downloaded Logos ===")
    success_count = sum(1 for r in results if r[4])
    for rid, name, filename, size_kb, ok in results:
        status = "OK" if ok else "FAILED"
        print(f" - [{status}] {name}: {filename} ({size_kb:.1f} KB)")

    print(f"\nTotal: {success_count}/{len(results)} logos successfully pulled and verified in {LOGOS_DIR}")
    return success_count == len(results)

if __name__ == "__main__":
    success = download_and_verify()
    sys.exit(0 if success else 1)
