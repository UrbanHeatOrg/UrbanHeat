# 🧰 HeatShield AI: Google MCP Toolbox for Databases

This directory provides the official **[MCP Toolbox for Databases](https://github.com/googleapis/mcp-toolbox)** (`googleapis/mcp-toolbox`, formerly *Gen AI Toolbox*) integration for **HeatShield AI**.

It exposes our Google Cloud BigQuery climate resilience warehouse (`a4i_climate`) and Vertex AI / BigQuery ML models (`heat_offset_model`) as standardized **Model Context Protocol (MCP)** endpoints.

---

## 🚀 Quickstart

### 1. Run MCP Toolbox Server via NPX (Stdio)
```bash
export GOOGLE_CLOUD_PROJECT="qwiklabs-gcp-04-4753f87c7a64"

# Run custom HeatShield AI climate resilience tools
npx -y @toolbox-sdk/server --tools-file=mcp/tools.yaml --stdio

# Run generic BigQuery schema explorer (list_tables, describe_table)
npx -y @toolbox-sdk/server --prebuilt=bigquery --stdio
```

### 2. Run via Official Docker Image
```bash
docker run -i --rm \
  -e GOOGLE_CLOUD_PROJECT="qwiklabs-gcp-04-4753f87c7a64" \
  -v $(pwd)/mcp/tools.yaml:/config/tools.yaml \
  us-central1-docker.pkg.dev/database-toolbox/toolbox/toolbox:latest \
  toolbox --tools-file=/config/tools.yaml --stdio
```

---

## 🛠️ Exposed MCP Tools

All tools are declaratively defined in [`mcp/tools.yaml`](tools.yaml) with strictly typed parameters and parameterized SQL statements to ensure least-privilege security and eliminate SQL injection risks:

| Tool Name | Source | Description | Parameters |
|:---|:---:|:---|:---|
| **`explain_heat_offset_bqml`** | BigQuery ML | Runs `ML.EXPLAIN_PREDICT` on `heat_offset_model` returning predicted offset and top 4 feature attributions. | `latitude`, `longitude`, `total_pop`, `pop_density_per_sqmi`, `poverty_rate`, `no_vehicle_rate`, `dist_to_park_m` |
| **`get_tract_resilience_profile`** | BigQuery | Queries `dallas_resilience_master` for multi-dimensional vulnerability (CDC SVI, HHS emPOWER, DOE energy burden, LST). | `geo_id` (11-digit FIPS) |
| **`rank_cooling_centers_mcp`** | BigQuery | Ranks top priority cooling facilities by equity index (`poverty_rate * 0.4 + no_vehicle_rate * 0.4 + density * 0.2`). | `limit_count` (int) |
| **`query_climate_trace_emitters`** | BigQuery | Filters Climate TRACE point-source GHG emitters with annual CO2e tonnes and abatement costs. | `min_emissions_tonnes` (float) |
| **`get_noaa_station_extremes`** | BigQuery | Analyzes historical extreme heat frequency (annual days > 95°F and > 100°F). | `start_year` (int) |

---

## 🔌 Connecting to MCP Clients

To use these tools within **Google Antigravity**, **Gemini CLI**, **Claude Code**, or **Cursor**, reference the root [`mcp.json`](../mcp.json):

```json
{
  "mcpServers": {
    "urban-heat-toolbox": {
      "command": "npx",
      "args": [
        "-y",
        "@toolbox-sdk/server",
        "--tools-file=mcp/tools.yaml",
        "--stdio"
      ],
      "env": {
        "GOOGLE_CLOUD_PROJECT": "qwiklabs-gcp-04-4753f87c7a64"
      }
    }
  }
}
```
