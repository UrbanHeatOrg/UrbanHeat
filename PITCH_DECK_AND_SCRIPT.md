# HeatShield AI — Pitch Deck & 3-Minute Video Script
**Challenge**: Agents for Impact Hackathon 2026 — Challenge 1: Walkability & Urban Heat Island Resilience  
**Team**: UrbanHeatOrg / HeatShield AI  
**Deployment**: [https://dallas-heat-app-447063751013.us-central1.run.app](https://dallas-heat-app-447063751013.us-central1.run.app)  
**Repository**: [https://github.com/UrbanHeatOrg/UrbanHeat](https://github.com/UrbanHeatOrg/UrbanHeat)  
**Deliverable**: 10-Slide Pitch Deck Structure, 3-Minute Video Script, and Rubric Alignment  

---

## 📽️ PART 1: 3-Minute Video Walkthrough Script

**Target Duration**: 02:55 - 03:00  
**Tone**: Authoritative, energetic, civic-tech command center narrative.

```
00:00 - 00:30 | SCENE 1: THE HOOK & DANA'S URGENT PROBLEM
---------------------------------------------------------------------------------
Visual: Full-screen screen-capture of the HeatShield AI Dark Command Center 
        (http://localhost:8000), showing the 3D Dallas skyline with glowing orange
        and crimson heat observation points across Oak Cliff and Bachman Lake.

Voiceover (Dana / Narrator):
"It’s July in Dallas. We've just endured eleven consecutive days over 100°F.
I'm Dana, Chief Climate Resilience Officer. We have capital funding for four permanent 
cooling centers and one mobile hydration unit, but City Council votes in three weeks. 
Where do they go?

Legacy planning relies on citywide averages or slow spreadsheets. But heat doesn't 
kill on average—it kills at specific, unshaded transit stops and low-income apartment 
complexes. Meet HeatShield AI: an autonomous climate resilience engine powered by 
Google ADK, Gemini 2.5 Flash on Vertex AI, and BigQuery ML."
```

```
00:30 - 01:15 | SCENE 2: LIVE SITING & THE 4TH & MARSALIS BENCHMARK
---------------------------------------------------------------------------------
Visual: Screen cursor zooms into the interactive map. The user selects 'Track 2: Siting'.
        5 prioritized sites appear with 1,200m walking catchments.
        Cursor clicks on Oak Cliff, highlighting '4th & Marsalis' vs 'Lake Cliff Park'.

Voiceover:
"HeatShield AI evaluated over 782 candidate civic facilities across Dallas County.
Instead of guesswork, it queries our custom BigQuery ML linear regression model 
trained on 19,491 NOAA Heat Watch campaign observations.

Watch this: One of the classic questions planners ask is: 
'Why is 4th and Marsalis so much hotter than two blocks north?'

Our contrast tool pulls empirical ground truth in real time: 4th & Marsalis hit 
107.8°F—a blistering 109.4°F heat index. Just two blocks north near Lake Cliff Park, 
temperatures drop to 105.7°F—over two degrees cooler. 
Using BigQuery ML's ML.EXPLAIN_PREDICT, our agent diagnoses the exact physical cause: 
4th and Marsalis is an asphalt-choked commercial corridor with zero tree canopy, 
while Lake Cliff Park provides mature vegetative shade and water-body cooling."
```

```
01:15 - 01:55 | SCENE 3: TITLE VI EQUITY AUDIT & DEFENSIVE RIGOR
---------------------------------------------------------------------------------
Visual: Screen transitions to the 'Equity & Civil Rights Audit' modal.
        A bar chart pops up comparing the 5 selected sites against the Dallas baseline:
        Poverty (36.6% vs 12.2%), Zero-Vehicle (34.4% vs 5.3%).

Voiceover:
"In public policy, data ethics is not optional. We built HeatShield AI around 
the federal civil rights standard: 'Strip the variable, audit the outcome.'
We strictly stripped race and ethnicity from model training features to prevent 
algorithmic redlining. Then, we ran a post-hoc Title VI equity audit.

The result? Our recommended cooling centers serve neighborhoods with three times 
higher poverty and 6.5 times higher zero-vehicle transit rates than the city average. 
100% of sites fall inside federal Disadvantaged Community tracts under Justice40. 
We also protect all user interactions with Google Cloud Model Armor to prevent 
prompt injection and SQL manipulation."
```

```
01:55 - 02:30 | SCENE 4: NATIONAL SCALE & THE $50M PARETO FRONTIER
---------------------------------------------------------------------------------
Visual: Cursor switches to the 'National Climate Investment Simulator'.
        Slider shifts budget to $50M. A dynamic Pareto Frontier curve renders,
        contrasting lives shielded against Climate TRACE CO2e tonnes abated.

Voiceover:
"Extreme heat doesn't stop at city limits. For municipal leaders managing $50 million 
climate bonds, HeatShield AI integrates Climate TRACE version 5.12 point-source emissions.
Our multi-objective Pareto optimizer solves the capital trade-off between adaptation 
and mitigation.

A pure heat adaptation approach protects 310,000 residents but abates zero emissions. 
A pure decarbonization approach cuts 840,000 tonnes of CO2e at industrial facilities 
without protecting a single pedestrian. Our agent delivers the balanced Pareto sweet-spot: 
235,000 frontline residents protected, plus 365,000 tonnes of CO2e abated annually 
by capturing landfill methane at McCommas Bluff and electrifying bus transit."
```

```
02:30 - 03:00 | SCENE 5: COUNCIL RESOLUTION & CALL TO ACTION
---------------------------------------------------------------------------------
Visual: The agent exports 'City Council Resolution No. 2026-HEAT-01', complete 
        with $10M line-item appropriations. Final title card displays:
        - Live Cloud Run URL
        - GitHub Repository
        - Google MCP Toolbox Ready

Voiceover:
"By 9:00 AM, Dana isn't presenting vague ideas—she is placing City Council Resolution 
No. 2026-HEAT-01 on the mayor's desk, backed by empirical BigQuery ML evidence, 
defensible licensing, and verified pedestrian walkability.

Deployed live on Google Cloud Run. Integrated with Google's MCP Toolbox for Databases.
This is HeatShield AI: Turning unmeasured urban heat into lifesaving capital infrastructure.
Thank you."
```

---

## 📊 PART 2: 10-Slide Pitch Deck Structure

### Slide 1: Title & Executive Vision
- **Header**: HeatShield AI — Autonomous Climate Resilience & Capital Siting Engine
- **Subheader**: From Unmeasured Microclimates to Life-Saving Municipal Infrastructure
- **Visuals**: Dark command center UI screenshot + Google Cloud Run verified badge + BigQuery ML badge
- **Key Points**:
  - Built for Agents for Impact 2026 (Challenge 1: Walkability & Urban Heat).
  - Autonomous Multi-Agent Hierarchy powered by Google ADK & Gemini 2.5 Flash on Vertex AI.
  - Deployed in production on Cloud Run: `dallas-heat-app-447063751013.us-central1.run.app`.

### Slide 2: The Urban Heat Crisis & Dana's Dilemma
- **Header**: The Municipal Challenge: July in Dallas
- **Subheader**: Extreme heat kills more Americans annually than hurricanes and tornadoes combined.
- **Visuals**: Climatology chart showing 65 days > 100°F in recent peak summers; max temperature 111.9°F.
- **Dana's Mandate**:
  - $10M capital allocation for 4 permanent cooling centers + 1 mobile hydration unit.
  - 782 candidate public facilities across Dallas County.
  - Council vote in 3 weeks; decisions must withstand legal, civil rights, and public scrutiny.

### Slide 3: Three Tracks, One Coherent Architecture
- **Header**: Synchronizing Three Municipal Clocks
- **Subheader**: From emergency hours to decadal master planning.
- **Architecture Diagram**:
  - **Track 1 (Hours / Days)**: Emergency Dispatcher — Real-time 104°F mobile tanker dispatch to unshaded bus stops.
  - **Track 2 (Months / Year — PRIMARY TRACK)**: Siting & Title VI Auditor — 4 permanent hubs with 1,200m walking catchments.
  - **Track 3 (Years / Decades)**: Urban Redesign Specialist — Native shade canopy and high-albedo cool pavement corridors.
  - **National Engine**: Portfolio Optimizer — $50M Pareto multi-objective capital allocation.

### Slide 4: Data Engineering & BigQuery ML Rigor
- **Header**: Ground-Truth Science in Google BigQuery
- **Subheader**: Moving beyond regional satellite estimates to hyper-local street physics.
- **Data Pipeline**:
  - 19,491 empirical NOAA Heat Watch mobile campaign observations ingested into BigQuery.
  - BigQuery ML Linear Regression (`a4i_climate.heat_offset_model`) predicting hyper-local thermal risk offsets.
  - Explainable AI via `ML.EXPLAIN_PREDICT`: Quantifying feature attributions for park distance, building density, and median structure age.
  - Zero ODbL license contamination: 100% Public Domain (NOAA, Census, EPA, CDC, HHS, DOE) and CC BY 4.0 (Climate TRACE).

### Slide 5: The Benchmark: "Why is 4th & Marsalis So Much Worse?"
- **Header**: Resolving Canonical Microclimate Contrasts
- **Subheader**: Real-time diagnostic contrast between 4th & Marsalis vs. Lake Cliff Park (Oak Cliff).
- **Comparative Metrics**:
  - 4th & Marsalis: **107.8°F** observed (**109.4°F Heat Index**).
  - Lake Cliff Park (2 blocks north): **105.7°F** observed (**107.0°F Heat Index**).
  - **Thermal Delta**: **+2.1°F ambient / +2.4°F heat index**.
  - **BigQuery ML Attribution Diagnosis**: 4th & Marsalis is an unshaded asphalt commercial strip with high thermal mass, while Lake Cliff Park provides mature canopy shade and water-body cooling.

### Slide 6: Priority Siting & 1,200m Pedestrian Catchments
- **Header**: The Recommended Allocation Portfolio
- **Subheader**: Selecting 4 permanent resilience hubs and 1 mobile staging depot from 782 assets.
- **Selected Facilities**:
  1. *Igelisia de Cristo Elim Church* (Tract `48113020500`) — 45.2% zero-vehicle households; acute pedestrian corridor.
  2. *Saints of Zion Baptist Church* (Tract `48113008704`) — 52.2% concentrated poverty; energy burden relief.
  3. *Education Outreach & Vocational Center* (Tract `48113020300`) — 38.5% no-car rate; Fair Park community nexus.
  4. *Bon Air Baptist Church* (Tract `48113011401`) — 506m park distance; severe shade desert.
  5. *Hillview Terrace Assembly of God* (Tract `48113012302`) — Mobile hydration fleet staging for East Dallas.

### Slide 7: Title VI Equity Audit: "Strip the Variable, Audit the Outcome"
- **Header**: Algorithmic Fairness & Civil Rights Compliance
- **Subheader**: Verifying environmental justice under Title VI and Justice40 standards.
- **Audit Findings Table**:
  - Poverty Concentration: **36.6%** in target tracts vs. **12.2%** Dallas baseline (**3.0x higher**).
  - Zero-Vehicle Transit Burden: **34.4%** vs. **5.3%** Dallas baseline (**6.49x higher**).
  - Direct Population Shielded: **20,864 residents**.
  - Justice40 Disadvantaged Community (DAC) Share: **100% of sites inside federal DAC tracts**.
  - Methodology: Demographic race stripped from model training; audited post-hoc to guarantee equity.

### Slide 8: National Scale: The $50M Climate Pareto Simulator
- **Header**: Balancing Extreme Heat Adaptation vs. Climate TRACE Decarbonization
- **Subheader**: Multi-objective Pareto frontier for mayors and municipal finance directors.
- **Optimization Trade-off Curve**:
  - *Option A (Pure Heat)*: $50M -> 310,000 residents shielded, 0 t CO2e abated.
  - *Option B (Balanced Pareto)*: $50M -> 235,000 residents shielded, 365,000 t CO2e abated (McCommas Bluff landfill gas + bus electrification).
  - *Option C (Pure Mitigation)*: $50M -> 0 residents shielded, 840,000 t CO2e abated.

### Slide 9: Full-Stack Google Cloud Architecture
- **Header**: Enterprise-Grade Open Architecture
- **Subheader**: Built with Google's latest AI and cloud native technologies.
- **Architecture Highlights**:
  - **Google ADK & Gemini 2.5 Flash on Vertex AI**: Hierarchical 5-agent advisory swarm.
  - **Google Cloud Model Armor**: Real-time prompt injection, jailbreak, and SQL injection sanitization.
  - **Google MCP Toolbox for Databases**: Declarative `mcp/tools.yaml` & `mcp.json` for BigQuery ML.
  - **Google Maps Platform**: Dark Vector Tiles, Routes API walking durations, Places API civic lookups, Solar API rooftop solar flux.
  - **Cloud Run Deployment**: Containerized, auto-scaling, production HTTPS endpoint.

### Slide 10: Deliverables, Council Resolution & Call to Action
- **Header**: Municipal Governance Ready
- **Subheader**: Immediate path to adoption for City Council.
- **Key Deliverables**:
  - Council Resolution No. 2026-HEAT-01 with $10M line-item appropriations.
  - Live interactive dashboard: `https://dallas-heat-app-447063751013.us-central1.run.app`.
  - Comprehensive GitHub codebase: `https://github.com/UrbanHeatOrg/UrbanHeat`.
  - 100% verified test suite covering all 19 system endpoints.

---

## 🏆 PART 3: Evaluation Rubric Alignment Matrix

| Rubric Dimension | Weight | Hackathon Requirement | HeatShield AI Implementation |
| :--- | :---: | :--- | :--- |
| **Impact & Insight** | **30%** | Actionable recommendations for Dana; clear decisions and rationale. | Evaluates 782 facilities down to 4 permanent hubs and 1 mobile unit; answers all 7 of Dana's canonical scenario questions with exact coordinates, budgets, and walking catchments. |
| **Technical Execution** | **30%** | Meaningful use of ADK, BigQuery ML (`ML.EXPLAIN_PREDICT`), and Cloud Run. | Multi-agent ADK swarm with Gemini 2.5 Flash on Vertex AI; BigQuery ML linear regression model with feature attributions; Model Armor security; live Cloud Run deployment. |
| **Rigor & Judgment** | **25%** | Defensible data licensing, validation, bias handling, honest model limitations. | 9 public domain/CC BY datasets (zero ODbL trap); "Strip the variable, audit the outcome" Title VI equity audit; explicitly acknowledges that model predicts relative offsets and cannot physically simulate post-planting delta; principled refusal for non-Dallas queries. |
| **Craft & Communication** | **15%** | Pitch deck, video script, clean executive dashboard, council resolution. | Command center dashboard with Google Maps dark mode; 10-slide pitch deck; 3-minute video script; formal City Council Resolution No. 2026-HEAT-01. |
| **Bonus: Range** | **+10 pts** | Technical breadth: MCP Toolbox, Climate TRACE, multi-objective optimization. | Integration with official `googleapis/mcp-toolbox`; Climate TRACE v5.12 point-source emissions; $50M Multi-Objective Pareto Frontier simulator. |
