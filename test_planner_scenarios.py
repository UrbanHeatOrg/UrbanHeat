"""Test script running all key municipal planner questions through the ADK Agent."""

import asyncio
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import agent.agent as ag

QUESTIONS = [
    # Track 1: Operational Emergency Response (102°F Extreme Heat Spike)
    "Today it is 102° tomorrow. Where do the hydration trucks and wellness checks go?",
    
    # Track 2: Capital Budget Allocation (Permanent Centers)
    "We can fund four cooling centers and one mobile hydration unit this summer in Dallas. Where should they go?",
    
    # Track 3: Urban Forestry ROI (Decadal Resilience)
    "This decade, where does tree planting buy the most heat relief per dollar across Dallas corridors?",
    
    # Intersection Microclimate Explanation (ML.EXPLAIN_PREDICT)
    "Why is the intersection at latitude 32.7834, longitude -96.8623 so much hotter than average? What features drive that?",
    
    # Civil Rights Equity Audit
    "Run an equity audit on our top recommended sites compared to the Dallas citywide baseline.",
    
    # Strict Boundary & Refusal Testing (Out of Bounds City)
    "Where should we deploy cooling centers in Houston or Phoenix?",
    
    # Strict Boundary & Refusal Testing (Unmeasured Minute-Level Historical Date)
    "What was the exact minute-by-minute temperature at 3:15 PM on October 12, 2021 at Elm and Akard?"
]

async def run_scenario(question: str):
    print("=" * 80)
    print(f"PLANNER QUESTION: {question}")
    print("=" * 80)
    
    session_service = InMemorySessionService()
    runner = Runner(app_name="dallas_heat_planner", agent=ag.root_agent, session_service=session_service)
    session = await session_service.create_session(app_name="dallas_heat_planner", user_id="planner_dana")
    
    msg = types.Content(role="user", parts=[types.Part.from_text(text=question)])
    async for event in runner.run_async(session_id=session.id, user_id="planner_dana", new_message=msg):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    print(part.text, end="", flush=True)
                elif part.function_call:
                    print(f"\n[Invoking Tool: {part.function_call.name}({part.function_call.args})]\n")
    print("\n\n")

async def main():
    for q in QUESTIONS:
        await run_scenario(q)

if __name__ == "__main__":
    asyncio.run(main())
