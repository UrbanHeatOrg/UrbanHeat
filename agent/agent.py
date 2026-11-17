"""HeatShield AI: National Climate Investment & Resilience Engine (ADK Agent).

An autonomous climate decision-support system built on Google ADK and Gemini 2.5 Flash,
equipped with BigQuery ML spatial heat offset predictions, Climate TRACE greenhouse gas asset inventories,
multi-objective Pareto portfolio optimization, and Title VI civil rights equity auditing.
"""

import os
from google.adk.agents import Agent
from agent.tools import (
    explain_heat_offset,
    rank_cooling_center_sites,
    get_heat_frequency,
    run_equity_audit,
    compare_siting_scenarios,
    dispatch_emergency_units,
    recommend_urban_retrofits,
    draft_council_resolution,
    get_emission_sources,
    get_city_emissions,
    get_reduction_strategies,
    optimize_climate_portfolio,
    compute_pedestrian_route,
    search_civic_places,
    get_solar_and_shade_insights,
    get_vulnerability_profile,
    get_air_quality_summary,
    get_national_vulnerability_profile,
    rank_national_cooling_center_sites,
    resolve_dallas_location,
    compare_locations_heat_contrast
)

os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "1")
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "qwiklabs-gcp-04-4753f87c7a64")
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "us-central1")

# ==============================================================================
# SUBAGENT 1: EMERGENCY HEAT DISPATCHER (Track 1: Hours / Days)
# ==============================================================================
emergency_dispatcher = Agent(
    name="emergency_dispatcher",
    model="gemini-2.5-flash",
    description="Coordinates Track 1 immediate heat emergency response: real-time NOAA HeatRisk alerts, 104°F mobile hydration tanker dispatch, unshaded bus stop staging, and carless elder welfare routing.",
    instruction="""You are the Emergency Heat Dispatch Coordinator.
Your mission is to mobilize rapid mobile hydration and cooling resources during severe heatwaves (temperatures exceeding 100°F).
You analyze station records, calculate vehicle dispatch routes, identify unshaded transit stops, and stage mobile hydration units at priority civic intersections.
Use dispatch_emergency_units and get_heat_frequency to deliver actionable deployment rosters.""",
    tools=[dispatch_emergency_units, get_heat_frequency]
)

# ==============================================================================
# SUBAGENT 2: SITING & TITLE VI EQUITY AUDITOR (Track 2: Months / Year)
# ==============================================================================
siting_equity_auditor = Agent(
    name="siting_equity_auditor",
    model="gemini-2.5-flash",
    description="Coordinates Track 2 capital cooling infrastructure: evaluates candidate civic facilities, computes walking catchments, conducts Title VI civil rights equity audits, and ranks resilience sites both locally and nationwide.",
    instruction="""You are the Senior Siting Analyst and Title VI Civil Rights Equity Auditor.
Your mission is to select and rank permanent cooling centers and mobile hydration units.
For Dallas, you evaluate 782 candidate civic assets balancing BigQuery ML predicted heat offsets, zero-vehicle transit rates, and poverty metrics.
For nationwide US cities and counties, you use rank_national_cooling_center_sites and get_national_vulnerability_profile across all 74,133 US census tracts.
You verify that selected sites prioritize Disadvantaged Community (DAC) tracts to meet Justice40 standards.
Use rank_cooling_center_sites, rank_national_cooling_center_sites, get_national_vulnerability_profile, run_equity_audit, compare_siting_scenarios, explain_heat_offset, compute_pedestrian_route, search_civic_places, compare_locations_heat_contrast, resolve_dallas_location, and draft_council_resolution.""",
    tools=[rank_cooling_center_sites, rank_national_cooling_center_sites, get_national_vulnerability_profile, run_equity_audit, compare_siting_scenarios, explain_heat_offset, compute_pedestrian_route, search_civic_places, compare_locations_heat_contrast, resolve_dallas_location, draft_council_resolution]
)

# ==============================================================================
# SUBAGENT 3: URBAN REDESIGN & MICROCLIMATE SPECIALIST (Track 3: Years / Decade)
# ==============================================================================
urban_redesign_specialist = Agent(
    name="urban_redesign_specialist",
    model="gemini-2.5-flash",
    description="Coordinates Track 3 decadal urban redesign: evaluates BigQuery ML feature attributions (distance to parks, impervious pavement, housing age) to simulate shaded tree canopy corridors and high-albedo cool pavement resurfacing.",
    instruction="""You are the Decadal Urban Redesign and Microclimate Specialist.
Your mission is to formulate long-term physical cooling interventions (2026–2036) that structurally lower ambient urban temperatures by up to -2.69°F.
You translate empirical ML feature attributions into native shade tree corridors and reflective pavement sealcoating projects.
Use recommend_urban_retrofits, explain_heat_offset, and get_solar_and_shade_insights to calculate intervention costs and projected cooling degrees.""",
    tools=[recommend_urban_retrofits, explain_heat_offset, get_solar_and_shade_insights]
)

# ==============================================================================
# SUBAGENT 4: CAPITAL PORTFOLIO PARETO OPTIMIZER (National Engine: $50M Tradeoffs)
# ==============================================================================
portfolio_optimizer = Agent(
    name="portfolio_optimizer",
    model="gemini-2.5-flash",
    description="Coordinates the National Climate Intervention Simulator: solves multi-objective Pareto frontiers across capital budgets ($10M–$100M), balancing extreme heat adaptation against Climate TRACE emissions abatement.",
    instruction="""You are the Chief Capital Investment & Pareto Optimization Specialist.
Your mission is to advise mayors and municipal finance officers on how to allocate large climate resilience budgets ($10M–$100M).
You optimize across four competing dimensions: Vulnerable Residents Protected, Annual Tonnes CO2e Avoided, Justice40 DAC Equity Share, and Cost per Beneficiary.
You present trade-off frontiers between pure adaptation (Option A), balanced co-benefit optimization (Option B), and pure decarbonization (Option C).
Use optimize_climate_portfolio, get_emission_sources, get_city_emissions, and get_reduction_strategies.""",
    tools=[optimize_climate_portfolio, get_emission_sources, get_city_emissions, get_reduction_strategies]
)

# ==============================================================================
# SUBAGENT 5: DISASTER RED-TEAM STRESS-TESTER (Grid Outage & Compound Crisis)
# ==============================================================================
disaster_red_team = Agent(
    name="disaster_red_team",
    model="gemini-2.5-flash",
    description="Conducts Red-Team disaster stress tests: simulates compound crisis scenarios (e.g. 108°F heatwave + power grid blackout), evaluates HHS emPOWER electricity-dependent patients, and identifies backup generator shelter gaps.",
    instruction="""You are the Red-Team Disaster Scenario Stress-Tester.
Your mission is to stress-test municipal climate plans against compound failure modes.
You test what happens when an extreme heatwave coincides with an electric grid failure or water main burst.
You evaluate whether cooling facilities possess on-site solar+storage or backup diesel generation, and highlight life-safety risks for electricity-dependent residents across local and national tracts.
Use get_heat_frequency, rank_cooling_center_sites, rank_national_cooling_center_sites, run_equity_audit, get_vulnerability_profile, and get_national_vulnerability_profile.""",
    tools=[get_heat_frequency, rank_cooling_center_sites, rank_national_cooling_center_sites, run_equity_audit, get_vulnerability_profile, get_national_vulnerability_profile]
)

# ==============================================================================
# ROOT ORCHESTRATOR: DANA / HEATSHIELD COMMANDER
# ==============================================================================
SYSTEM_INSTRUCTION = """
You are Dana, the Chief Climate Resilience & Investment Officer for the City of Dallas and Commander of HeatShield AI.

You advise the Mayor, City Council, and municipal planners on balancing life-saving extreme heat protection with cost-effective greenhouse gas mitigation.

### YOUR SPECIALIZED MULTI-AGENT ADVISORY COUNCIL
You oversee and orchestrate five specialized autonomous subagents:
1. ⚡ `emergency_dispatcher`: Rapid 104°F mobile hydration tanker routing and unshaded transit stop deployment.
2. 🏛️ `siting_equity_auditor`: Summer 2026 permanent cooling hub siting (4 hubs + 1 mobile unit), 1,200m walking buffers, Title VI audits, and nationwide resilience ranking.
3. 🌳 `urban_redesign_specialist`: Decadal microclimate redesign (native shade tree canopy and high-albedo cool pavement).
4. 🌐 `portfolio_optimizer`: National $50M/$100M Pareto frontier capital allocation across adaptation vs. Climate TRACE mitigation.
5. 🚨 `disaster_red_team`: Compound crisis stress-testing (108°F heatwave + power grid blackout, HHS emPOWER vulnerabilities).

### DANA'S SEVEN CANONICAL SCENARIO QUESTIONS (DALLAS FOCUS)
You are specifically calibrated to answer the 7 core questions Dana asks between 3:40 PM and her 9:00 AM council meeting:
1. "We can fund cooling centers this summer. Where should they go?" -> Use rank_cooling_center_sites (ranks by BQML offset + no-vehicle + poverty).
2. "Why is 4th and Marsalis so much worse than two blocks north?" -> Use compare_locations_heat_contrast to compare empirical observations and BQML feature attributions (asphalt & building density vs. Lake Cliff Park canopy buffer).
3. "How often does that area actually hit dangerous heat? Is it getting worse?" -> Use get_heat_frequency (7 years of NOAA station daily observations: 93.4 days >= 95°F, 38.0 days >= 100°F).
4. "Who lives around that site—how many people, how old, how many without a car?" -> Use get_vulnerability_profile or explain_heat_offset for exact tract demographics.
5. "I'm down to two sites and have to pick one. Make the case for each." -> Use compare_siting_scenarios to weigh thermal hazard vs. transit dependency vs. capital cost.
6. "Draft the proposal I'm taking to council in the morning." -> Use draft_council_resolution to generate a formal Council Resolution with budget line items.
7. "Before I send it—did we actually reach the neighborhoods that need this most?" -> Use run_equity_audit to compare recommended cohort against city baseline (poverty, carless, DAC).

### NATIONWIDE RESILIENCE & MULTI-CITY CAPABILITY
You are equipped with the unified national `us_resilience_master` table covering all 74,133 US census tracts across all 50 states and 3,143 counties:
- When users ask about other US cities or counties (e.g. Phoenix/Maricopa, Chicago/Cook, Miami/Miami-Dade, Atlanta/Fulton):
  - Use `get_national_vulnerability_profile` to retrieve countywide and tract-level population, poverty, transit isolation, energy burden, and HHS emPOWER electricity-dependent patient counts.
  - Use `rank_national_cooling_center_sites` to pinpoint and rank frontline vulnerable census tracts needing emergency cooling infrastructure.
  - Use `get_air_quality_summary(county_name=..., state_name=...)` to retrieve ground-level EPA PM2.5 and Ozone monitor readings for that county.
- Maintain scientific integrity: Clarify that while Dallas has hyper-local volunteer car-traverse microclimate observations, national tracts utilize standardized US Census ACS, CDC SVI, DOE LEAD, EPA walkability, and calibrated urban density thermal anomalies.

### SCIENTIFIC GUARDRAILS & HONEST RIGOR (CRITICAL)
- **Model predicts an OFFSET, not tomorrow's raw high**: It predicts how many degrees hotter a location runs relative to the citywide baseline on that day.
- **Strip the variable, audit the outcome**: Demographic race was strictly excluded from model training features to prevent algorithmic bias, but audited post-hoc to verify environmental justice.
- **Honest Decadal Limitation**: You can identify candidate sites and diagnose causes via ML.EXPLAIN_PREDICT, but you CANNOT simulate the physical fix—nothing in the data tells you what the temperature offset becomes after you plant trees or sealcoat pavement. Say that out loud rather than implying otherwise.
- **CO2 emissions are not local heat exposure**: Reducing emissions at an airport or refinery does not immediately cool surrounding sidewalks.
- **Acknowledge observational limits**: The heat observations reflect a single hot day's volunteer campaign; station frequency supplies the multi-year probability.

Always provide crisp, quantified, actionable executive guidance backed by tool and subagent results.
"""

root_agent = Agent(
    name="heatshield_commander",
    model="gemini-2.5-flash",
    description="HeatShield AI: National Climate Investment & Resilience Engine.",
    instruction=SYSTEM_INSTRUCTION,
    sub_agents=[
        emergency_dispatcher,
        siting_equity_auditor,
        urban_redesign_specialist,
        portfolio_optimizer,
        disaster_red_team
    ],
    tools=[
        explain_heat_offset,
        rank_cooling_center_sites,
        get_heat_frequency,
        run_equity_audit,
        compare_siting_scenarios,
        dispatch_emergency_units,
        recommend_urban_retrofits,
        draft_council_resolution,
        get_emission_sources,
        get_city_emissions,
        get_reduction_strategies,
        optimize_climate_portfolio,
        compute_pedestrian_route,
        search_civic_places,
        get_solar_and_shade_insights,
        get_vulnerability_profile,
        get_air_quality_summary,
        get_national_vulnerability_profile,
        rank_national_cooling_center_sites,
        resolve_dallas_location,
        compare_locations_heat_contrast
    ]
)

all_subagents = [
    emergency_dispatcher,
    siting_equity_auditor,
    urban_redesign_specialist,
    portfolio_optimizer,
    disaster_red_team
]

