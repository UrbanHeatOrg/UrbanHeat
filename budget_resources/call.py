import asyncio
from google.adk.runners import InMemoryRunner
from google.genai import types
from agent import root_agent

async def main():
    runner = InMemoryRunner(agent=root_agent)
    session = await runner.session_service.create_session(
        app_name=runner.app_name,
        user_id="local",
    )

    async for event in runner.run_async(
        user_id="local",
        session_id=session.id,
        new_message=types.Content(
            role="user",
            parts=[types.Part(text="Execute your instructions.")],
        ),
    ):
        if event.is_final_response() and event.content:
            for part in event.content.parts:
                if part.text:
                    print(part.text)

    await runner.close()

if __name__ == "__main__":
    asyncio.run(main())
    