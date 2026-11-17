# Urban Heat Island Resilience & Cooling Center Allocation — Workspace Guidelines

## Agent Architecture & Guidelines

### 1. Frontend Design & UI Craft (Anthropic Standard)
- All UI work must adhere strictly to the guidelines defined in [`.agents/rules/frontend_design.md`](.agents/rules/frontend_design.md).
- Avoid generic "AI Slop" aesthetic defaults (Inter/Roboto, purple gradients, unstyled cards).
- Use curated typography pairings: **Plus Jakarta Sans / Outfit** for UI headings and **JetBrains Mono** for telemetry data, coordinates, and Census IDs.
- Leverage modern Tailwind CSS, dark command-center aesthetics, glassmorphic translucency (`backdrop-blur-md`, `border-white/10`), and accessible shadcn/Radix primitives.
- Use Playwright MCP to inspect live visual rendering and validate responsive breakpoints.

### 2. Backend & BigQuery ML Integrations
- Leverage the **Google MCP Toolbox for Databases** (`mcp.json` / `mcp/tools.yaml`) to run parameterized predictions against `qwiklabs-gcp-04-4753f87c7a64.a4i_climate.heat_offset_model`.
- Maintain Model Armor security filtering (`agent/model_armor.py`) for all AI-generated spatial and allocation reasoning.
- Validate REST API endpoints against `test_system_endpoints.py`.
