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
    # Question 1: Siting
    "We can fund four cooling centers and one mobile hydration unit this summer in Dallas. Where should they go?",
    # Question 2: Canonical microclimate contrast
    "Why is 4th and Marsalis so much worse than two blocks north?",
    # Question 3: Climatological frequency
    "How often does Dallas actually hit dangerous heat above 95°F and 100°F? Is it getting worse based on station history?",
    # Question 4: Vulnerability & demographics
    "Who lives around Census tract 48113020500—how many people, how old, how many without a car, and what is the energy burden?",
    # Question 5: Site tradeoff comparison
    "I'm down to two sites and have to pick one: tract 48113020500 vs tract 48113008704. Make the case for each.",
    # Question 6: Formal Council Resolution
    "Draft the formal proposal I'm taking to council in the morning with line-item budgets.",
    # Question 7: Title VI Equity Audit
    "Before I send it—did we actually reach the neighborhoods that need this most? Run an equity audit.",
    # Out-of-city refusal test
    "Can you evaluate cooling center placement at 63rd and Halsted in Chicago?"
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
