import os
import vertexai
from vertexai.preview import reasoning_engines
from agent.agent import root_agent

PROJECT_ID = "qwiklabs-gcp-04-4753f87c7a64"
LOCATION = "us-central1"
STAGING_BUCKET = "gs://qwiklabs-gcp-04-4753f87c7a64-vertex-agent"

print(f"Initializing Vertex AI for project={PROJECT_ID}, location={LOCATION}...")
vertexai.init(
    project=PROJECT_ID,
    location=LOCATION,
    staging_bucket=STAGING_BUCKET
)

print("Packaging root_agent into Vertex Reasoning Engine (AdkApp)...")
app = reasoning_engines.AdkApp(agent=root_agent)

print("Deploying ReasoningEngine to Vertex Agent Platform...")
remote_app = reasoning_engines.ReasoningEngine.create(
    app,
    requirements=[
        "google-adk",
        "google-cloud-bigquery",
        "google-genai",
        "pydantic"
    ],
    display_name="dallas-heat-resilience-agent",
    description="City of Dallas Urban Heat Resilience, Grid Vulnerability & Urban Forestry Planning Agent across 3-Track Framework."
)

print("Successfully deployed!")
print(f"Reasoning Engine Resource Name: {remote_app.resource_name}")
