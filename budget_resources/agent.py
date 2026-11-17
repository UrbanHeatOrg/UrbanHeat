import os
from google.adk.agents import Agent

os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "1")
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "qwiklabs-gcp-04-4753f87c7a64")
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "us-central1")

SYSTEM_INSTRUCTION = """
Which top-3 permanent cooling centers in Dallas do you recommend?
Print detailed reasoning for each, including equity and heat vulnerability considerations.
"""

root_agent = Agent(
    name="budget_resources",
    model="gemini-2.5-flash",
    description="Urban heat adaptation and resource allocation in Dallas.",
    instruction=SYSTEM_INSTRUCTION,
    sub_agents=[],
    tools=[]
)
