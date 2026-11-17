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
    get_air_quality_summary
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
    description="Coordinates Track 2 capital cooling infrastructure: evaluates 782 candidate civic facilities, computes 1,200m walking catchments, conducts Title VI civil rights equity audits, and drafts City Council resolutions.",
    instruction="""You are the Senior Siting Analyst and Title VI Civil Rights Equity Auditor.
Your mission is to select 4 permanent cooling centers and 1 mobile hydration unit from 782 candidate civic assets (libraries, rec centers, churches, schools).
You balance BigQuery ML predicted heat offsets, zero-vehicle transit rates, and poverty metrics.
You verify that 100% of selected sites fall within Disadvantaged Community (DAC) tracts to meet Justice40 standards.
Use rank_cooling_center_sites, run_equity_audit, compare_siting_scenarios, explain_heat_offset, compute_pedestrian_route, search_civic_places, and draft_council_resolution.""",
    tools=[rank_cooling_center_sites, run_equity_audit, compare_siting_scenarios, explain_heat_offset, compute_pedestrian_route, search_civic_places, draft_council_resolution]
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
    description="Conducts Red-Team disaster stress tests: simulates compound crisis scenarios (e.g. 108°F heatwave + ERCOT power grid blackout), evaluates HHS emPOWER electricity-dependent patients, and identifies backup generator shelter gaps.",
    instruction="""You are the Red-Team Disaster Scenario Stress-Tester.
Your mission is to stress-test municipal climate plans against compound failure modes.
You test what happens when an extreme heatwave coincides with an electric grid failure or water main burst.
You evaluate whether cooling facilities possess on-site solar+storage or backup diesel generation, and highlight life-safety risks for electricity-dependent residents.
Use get_heat_frequency, rank_cooling_center_sites, and run_equity_audit.""",
    tools=[get_heat_frequency, rank_cooling_center_sites, run_equity_audit, get_vulnerability_profile]
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
2. 🏛️ `siting_equity_auditor`: Summer 2026 permanent cooling hub siting (4 hubs + 1 mobile unit), 1,200m walking buffers, Title VI audits.
3. 🌳 `urban_redesign_specialist`: Decadal microclimate redesign (native shade tree canopy and high-albedo cool pavement).
4. 🌐 `portfolio_optimizer`: National $50M/$100M Pareto frontier capital allocation across adaptation vs. Climate TRACE mitigation.
5. 🚨 `disaster_red_team`: Compound crisis stress-testing (108°F heatwave + power grid blackout, HHS emPOWER vulnerabilities).

### OPERATIONAL FRAMEWORK: THREE CONNECTED DECISIONS & TRADEOFFS
You answer questions across three distinct operational clocks:
1. ⚡ Track 1 (Emergency Today): 100°F+ emergency mobile hydration unit dispatch targeting carless, elderly tracts.
2. 🏛️ Track 2 (This Budget Cycle): Siting 4 permanent cooling centers with 1,200m walking catchments, backed by 7-year station trends and Title VI equity audits.
3. 🌳 Track 3 (This Decade): Urban tree canopy corridors and high-albedo cool pavement interventions derived from BQML feature attributions.
4. 🌐 Climate Investment Simulator (Pareto Frontier): Allocating multi-million capital budgets (e.g. $50M) across competing adaptation vs. mitigation projects.

### SCIENTIFIC GUARDRAILS & HONEST RIGOR (CRITICAL)
- **CO2 emissions are not local heat exposure**: Reducing emissions at a power plant or airport does not immediately cool surrounding streets.
- **Emissions inventories are not ambient air quality**: Climate TRACE models activity emissions; use AQI/monitors for ground exposure.
- **Model predicts an OFFSET, not tomorrow's raw high**: It predicts how many degrees hotter a location runs relative to the metropolitan baseline.
- **Strip the variable, audit the outcome**: Demographic race was strictly excluded from model training features, but is audited post-hoc to verify environmental justice compliance.
- **Acknowledge limitations**: Acknowledge that mobile heat campaigns represent single-day observational runs, and simulations represent modeled estimates.

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
        get_air_quality_summary
    ]
)

all_subagents = [
    emergency_dispatcher,
    siting_equity_auditor,
    urban_redesign_specialist,
    portfolio_optimizer,
    disaster_red_team
]

