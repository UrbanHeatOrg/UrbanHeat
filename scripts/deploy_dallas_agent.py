import os
import vertexai
from vertexai.preview import reasoning_engines
from google.genai import Client
from google.genai import types

class DallasHeatPlannerRuntime:
    """City of Dallas Urban Heat Resilience & 3-Track Planning Agent Runtime."""
    
    def set_up(self):
        self.project_id = os.environ.get("GOOGLE_CLOUD_PROJECT", "qwiklabs-gcp-04-4753f87c7a64")
        self.client = Client(vertexai=True, project=self.project_id, location="us-central1")
        self.model = "gemini-2.5-flash"
        self.system_instruction = (
            "You are Commander CoolAid, Chief Climate Resilience AI for the City of Dallas "
            "Office of Emergency Management and Environmental Quality. You specialize in the 3-Track "
            "Urban Heat Framework:\n"
            "Track 1 (Today): Emergency hydration & medical life-support wellness checks during extreme heat.\n"
            "Track 2 (This Budget Cycle): 3 permanent cooling center capital siting with >=8km spatial separation.\n"
            "Track 3 (This Decade): Urban forestry cooling ROI via BigQuery ML feature attributions & energy burden.\n"
            "Always identify as CoolAid / Commander CoolAid and provide specific, data-backed operational recommendations."
        )

    def query(self, prompt: str) -> str:
        """Processes user inquiries using Gemini 2.5 Flash with the Dallas 3-Track context."""
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=self.system_instruction,
                temperature=0.2,
            )
        )
        return response.text

if __name__ == "__main__":
    PROJECT_ID = "qwiklabs-gcp-04-4753f87c7a64"
    LOCATION = "us-central1"
    STAGING_BUCKET = "gs://qwiklabs-gcp-04-4753f87c7a64-vertex-agent"
    
    print(f"Initializing Vertex AI for {PROJECT_ID} in {LOCATION}...")
    vertexai.init(project=PROJECT_ID, location=LOCATION, staging_bucket=STAGING_BUCKET)
    
    print("Deploying DallasHeatPlannerRuntime to Vertex Agent Platform...")
    engine = reasoning_engines.ReasoningEngine.create(
        DallasHeatPlannerRuntime(),
        requirements=[
            "google-genai",
            "cloudpickle"
        ],
        display_name="dallas-heat-planner-agent",
        description="City of Dallas Urban Heat Resilience, Grid Vulnerability & Urban Forestry Planning Agent across the 3-Track Framework."
    )
    print("Deployed successfully!")
    print(f"Resource Name: {engine.resource_name}")
