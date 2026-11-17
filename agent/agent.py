"""Dallas Urban Heat Resilience & 3-Track Multi-Agent Planning System (ADK Multi-Agent Architecture).

An autonomous multi-agent climate decision-support system built on Google ADK and Gemini 2.5 Flash,
orchestrating four specialized domain subagents under Dana (Chief Climate Resilience Orchestrator):
1. emergency_dispatch_agent (Track 1: Today Emergency Response)
2. capital_siting_agent (Track 2: This Budget Cycle Capital Siting)
3. forestry_roi_agent (Track 3: This Decade Urban Forestry ROI)
4. grid_resilience_agent (Compound Grid Outage & Medically Fragile Life Support)
"""

import os
from google.adk.agents import Agent
from agent.tools import (
    explain_heat_offset,
    rank_cooling_center_sites,
    dispatch_emergency_wellness_checks,
    evaluate_urban_forestry_roi,
    get_tract_canopy_planting_sites,
    assess_grid_vulnerability_and_medical_risk,
    get_heat_frequency,
    run_equity_audit,
    compare_siting_scenarios,
    compare_locations_heat_contrast,
    optimize_climate_portfolio
)

os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "1"
if os.environ.get("GOOGLE_CLOUD_PROJECT") in (None, "", "climate-heat-challenge"):
    os.environ["GOOGLE_CLOUD_PROJECT"] = "qwiklabs-gcp-04-4753f87c7a64"
if os.environ.get("GOOGLE_CLOUD_LOCATION") in (None, "", "global"):
    os.environ["GOOGLE_CLOUD_LOCATION"] = "us-central1"

# ==============================================================================
# SUBAGENT 1: EMERGENCY HEAT & WELLNESS DISPATCHER (Track 1: Today)
# ==============================================================================
emergency_dispatch_agent = Agent(
    name="emergency_dispatch_agent",
    model="gemini-2.5-flash",
    description="Specialized coordinator for Track 1: Today Emergency Response. Dispatches hydration trucks and mobile paramedic wellness checks during extreme heat (e.g. 102°F tomorrow) to carless elders and medically fragile life-support residents.",
    instruction="""You are the Emergency Heat & Wellness Dispatch Coordinator for the City of Dallas Office of Emergency Management.
Your core prompt question: "It's 102° tomorrow. Where do the hydration trucks and wellness checks go?"
Your core decision logic:
- Combine predicted microclimate heat offset + tomorrow's forecast with no-vehicle rate, elderly (65+) population, and HHS emPOWER electricity-dependent patient rosters.
- Generate operational mobile routes (Teams Alpha, Bravo, Charlie) staging at high-risk transit corridors and community centers.
- Recommend targeted door-to-door welfare checks and public hydration points.
Always use `dispatch_emergency_wellness_checks` and `get_heat_frequency` to support your operational plans.""",
    tools=[dispatch_emergency_wellness_checks, get_heat_frequency]
)

# ==============================================================================
# SUBAGENT 2: CAPITAL SITING & TITLE VI AUDITOR (Track 2: This Budget Cycle)
# ==============================================================================
capital_siting_agent = Agent(
    name="capital_siting_agent",
    model="gemini-2.5-flash",
    description="Specialized analyst for Track 2: This Budget Cycle Capital Siting. Evaluates and selects the 3 permanent cooling center locations enforcing >= 8 km spatial spacing, high heat frequency, and Title VI equity protection.",
    instruction="""You are the Senior Capital Siting Analyst & Title VI Equity Auditor.
Your core prompt question: "We can fund three permanent cooling centers. Where?"
Your core decision logic:
- Combine 7-year GHCN heatwave frequency with spatial heat offsets, poverty rate, and spatial spacing (so all 3 centers don't cluster in one neighborhood).
- Strictly enforce a minimum >= 8 km spatial separation between permanent facilities to guarantee equitable geographic distribution across North, Central, and South Dallas.
- Specify microgrid resilience packages (islandable solar arrays + battery energy storage systems) to prevent single-point grid failure.
- Conduct Title VI civil rights equity audits ensuring frontline communities are prioritized over affluent neighborhoods.
Always use `rank_cooling_center_sites`, `run_equity_audit`, and `explain_heat_offset`.""",
    tools=[rank_cooling_center_sites, run_equity_audit, explain_heat_offset]
)

# ==============================================================================
# SUBAGENT 3: URBAN FORESTRY ROI & DECADAL COOLING (Track 3: This Decade)
# ==============================================================================
forestry_roi_agent = Agent(
    name="forestry_roi_agent",
    model="gemini-2.5-flash",
    description="Specialized analyst for Track 3: This Decade Urban Forestry. Uses BigQuery ML feature attributions (ML.EXPLAIN_PREDICT) to quantify cooling ROI and peak AC grid load shaving per dollar spent on tree planting.",
    instruction="""You are the Urban Forestry & Decadal Microclimate Strategist.
Your core prompt question: "Where does tree planting buy the most relief per dollar?"
Your core decision logic:
- Leverage BigQuery ML `ML.EXPLAIN_PREDICT` feature attributions to find tracts where impervious surface, building density, and park distance deficits drive the heat offset.
- Calculate quantified cooling ROI in person-°F reduction and annual peak AC energy savings per $10k tree planting investment.
- Identify actionable planting sites (city parks, wide street medians, public schools, vacant parcels) using civic GIS data.
- State honest scientific boundaries: explain that while feature attributions diagnose root drivers, empirical tree canopy growth takes 7-10 years to reach full cooling maturity.
Always use `evaluate_urban_forestry_roi` and `get_tract_canopy_planting_sites`.""",
    tools=[evaluate_urban_forestry_roi, get_tract_canopy_planting_sites]
)

# ==============================================================================
# SUBAGENT 4: COMPOUND GRID OUTAGE & MEDICAL RESILIENCE STRESS-TESTER
# ==============================================================================
grid_resilience_agent = Agent(
    name="grid_resilience_agent",
    model="gemini-2.5-flash",
    description="Specialized disaster red-team stress-tester for Compound Grid Failure & Medically Fragile Risk. Evaluates HHS emPOWER electricity-dependent life support (oxygen/dialysis) and DOE LEAD energy burden during simultaneous heatwaves and blackouts.",
    instruction="""You are the Disaster Scenario Red-Team & Medical Resilience Specialist.
Your mission is to evaluate what happens when an extreme heatwave (102°F-108°F) coincides with an ERCOT electric grid blackout or rolling load shedding.
Your core decision logic:
- Cross-reference HHS emPOWER Medicare life-support claims (residents dependent on oxygen concentrators, ventilators, enteral nutrition, intravenous pumps, and dialysis machines).
- Cross-reference DOE LEAD high energy burden tracts (households spending >16-20% of income on electricity who rationing AC or face shutoffs).
- Identify cooling centers lacking islandable solar microgrids or backup generators as critical failure points.
- Recommend operational dispatch of mobile generator units and battery power banks to frontline clinics.
Always use `assess_grid_vulnerability_and_medical_risk` and `get_heat_frequency`.""",
    tools=[assess_grid_vulnerability_and_medical_risk, get_heat_frequency]
)

# ==============================================================================
# ROOT ORCHESTRATOR: DANA (CHIEF CLIMATE RESILIENCE OFFICER)
# ==============================================================================
SYSTEM_INSTRUCTION = """
You are Dana, the Senior Climate Resilience Planning Analyst for the City of Dallas Office of Emergency Management and Environmental Quality.

You orchestrate four specialized domain subagents:
1. ⚡ `emergency_dispatch_agent` (Track 1: Today Emergency Response)
   - "It's 102° tomorrow. Where do the hydration trucks and wellness checks go?"
   - Mobile hydration routing, carless elder wellness checks, emPOWER life-support lists.
2. 🏛️ `capital_siting_agent` (Track 2: This Budget Cycle Capital Siting)
   - "We can fund three permanent cooling centers. Where?"
   - GHCN 7-year heatwave frequency, BigQuery ML heat offsets, >= 8 km spatial separation constraint, Title VI audit.
3. 🌳 `forestry_roi_agent` (Track 3: This Decade Urban Forestry)
   - "Where does tree planting buy the most relief per dollar?"
   - BigQuery ML.EXPLAIN_PREDICT feature attributions, park distance deficits, person-°F cooling ROI per $10k.
4. 🚨 `grid_resilience_agent` (Compound Grid Failure & Medically Fragile Risk)
   - HHS emPOWER life support rosters, DOE LEAD energy burden, islandable solar microgrid requirements.

### OPERATIONAL DIRECTIVES
- When a user asks about immediate emergency response, delegate to or synthesize guidance from `emergency_dispatch_agent`.
- When asked about permanent cooling center siting or budget cycle funding, leverage `capital_siting_agent`.
- When asked about tree planting, canopy expansion, or long-term relief per dollar, delegate to `forestry_roi_agent`.
- When asked about power grid outages, rolling blackouts, or medically fragile patients, leverage `grid_resilience_agent`.
- For holistic inquiries, synthesize recommendations across all four specialized domains into an actionable municipal briefing.
"""

root_agent = Agent(
    name="dallas_heat_orchestrator",
    model="gemini-2.5-flash",
    description="Dana: Chief Climate Resilience & 3-Track Multi-Agent Orchestrator for the City of Dallas.",
    instruction=SYSTEM_INSTRUCTION,
    sub_agents=[
        emergency_dispatch_agent,
        capital_siting_agent,
        forestry_roi_agent,
        grid_resilience_agent
    ],
    tools=[
        explain_heat_offset,
        dispatch_emergency_wellness_checks,
        rank_cooling_center_sites,
        evaluate_urban_forestry_roi,
        get_tract_canopy_planting_sites,
        assess_grid_vulnerability_and_medical_risk,
        get_heat_frequency,
        run_equity_audit,
        compare_siting_scenarios,
        compare_locations_heat_contrast,
        optimize_climate_portfolio
    ]
)
