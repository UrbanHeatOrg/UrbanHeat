import asyncio
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from track3_forestry.agent import root_agent

async def main():
    session_service = InMemorySessionService()
    runner = Runner(app_name="track3_forestry", agent=root_agent, session_service=session_service)
    session = await session_service.create_session(
        app_name=runner.app_name,
        user_id="cli_planner",
    )

    prompt = "Where does tree planting buy the most relief per dollar across Dallas corridors this decade? Show the top tracts, BigQuery ML attribution drivers, person-°F ROI, and specific planting sites."
    print("=" * 80)
    print(f"TRACK 3 PROMPT: {prompt}")
    print("=" * 80 + "\n")

    msg = types.Content(role="user", parts=[types.Part.from_text(text=prompt)])
    async for event in runner.run_async(
        user_id="cli_planner",
        session_id=session.id,
        new_message=msg,
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    print(part.text, end="", flush=True)
                elif part.function_call:
                    print(f"\n[Tool Invocation: {part.function_call.name}({part.function_call.args})]\n", flush=True)

    print("\n\n" + "=" * 80)
    await runner.close()

if __name__ == "__main__":
    asyncio.run(main())
