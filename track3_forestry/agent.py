import os
import sys

# Ensure root workspace is in sys.path
WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if WORKSPACE_DIR not in sys.path:
    sys.path.insert(0, WORKSPACE_DIR)

from google.adk.agents import Agent
from agent.tools import evaluate_urban_forestry_roi, get_tract_canopy_planting_sites

os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "1")
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "qwiklabs-gcp-04-4753f87c7a64")
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "us-central1")

SYSTEM_INSTRUCTION = """You are the Urban Forestry & Decadal Microclimate Strategist for Dallas (Track 3).
Your core mission is to answer: "Where does tree planting buy the most relief per dollar across Dallas corridors this decade?"

Decision Logic:
1. Always invoke `evaluate_urban_forestry_roi` to query BigQuery ML `ML.EXPLAIN_PREDICT` feature attributions for park distance deficits and building thermal mass.
2. For specific tracts, call `get_tract_canopy_planting_sites` to identify concrete physical planting opportunities (city parks, school grounds, wide street medians, vacant parcels).
3. Quantify cooling ROI in person-°F reduction and annual peak AC energy savings per $10k spent.
4. State honest biological timelines: full cooling benefits take 7-10 years to reach canopy maturity.
"""

root_agent = Agent(
    name="track3_forestry_agent",
    model="gemini-2.5-flash",
    description="Track 3: Urban Forestry & Decadal Microclimate Cooling ROI Strategist.",
    instruction=SYSTEM_INSTRUCTION,
    sub_agents=[],
    tools=[evaluate_urban_forestry_roi, get_tract_canopy_planting_sites]
)
