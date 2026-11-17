"""FastAPI Backend Server for Dallas Urban Heat Resilience Planning Dashboard."""

import os
import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import agent.tools as tools
import agent.agent as ag
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

app = FastAPI(title="Dallas Urban Heat Resilience Planning System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

session_service = InMemorySessionService()
runner = Runner(app_name="dallas_heat_planner", agent=ag.root_agent, session_service=session_service)

class ChatRequest(BaseModel):
    message: str
    session_id: str = "web_session"

@app.get("/api/sites")
def get_sites():
    return tools.rank_cooling_center_sites(top_n=5, prioritize_vulnerability=True)

@app.get("/api/audit")
def get_audit():
    return tools.run_equity_audit()

@app.get("/api/frequency")
def get_frequency():
    return tools.get_heat_frequency()

@app.get("/api/explain")
def explain(lat: float, lon: float):
    return tools.explain_heat_offset(lat, lon)

@app.get("/api/compare")
def compare(tract_a: str = "48113020500", tract_b: str = "48113008704"):
    return tools.compare_siting_scenarios(tract_a, tract_b)

@app.get("/api/dispatch")
def dispatch(temp: float = 104.5, trucks: int = 2):
    return tools.dispatch_emergency_units(temp, trucks)

@app.get("/api/retrofits")
def retrofits(tract_id: str = "48113020500", budget: float = 1000000.0):
    return tools.recommend_urban_retrofits(tract_id, budget)

@app.get("/api/resolution")
def resolution(budget: float = 10000000.0):
    return tools.draft_council_resolution(budget_dollars=budget)

@app.get("/api/climate-trace/assets")
def climate_assets(city: str = "Dallas", sector: str = None, min_emissions: float = 0.0):
    return tools.get_emission_sources(city, sector, min_emissions)

@app.get("/api/climate-trace/city-emissions")
def city_emissions(city: str = "Dallas"):
    return tools.get_city_emissions(city)

@app.get("/api/climate-trace/strategies")
def strategies(sector: str = None):
    return tools.get_reduction_strategies(sector)

@app.get("/api/portfolio/optimize")
def optimize_portfolio(budget: float = 50.0, adaptation_weight: float = 0.5, mitigation_weight: float = 0.5):
    return tools.optimize_climate_portfolio(budget, adaptation_weight, mitigation_weight)


from agent.model_armor import inspect_prompt_armor

@app.get("/api/armor/status")
def armor_status():
    return {
        "status": "ACTIVE",
        "service": "Google Cloud Model Armor",
        "features": [
            "Prompt Injection Sanitization",
            "Jailbreak Prevention",
            "System Prompt Leak Shield",
            "SQL/DDL Injection Interception"
        ]
    }

@app.post("/api/chat")
async def chat(req: ChatRequest):
    try:
        # 1. Google Cloud Model Armor Inspection
        armor = inspect_prompt_armor(req.message)
        if not armor["safe"]:
            return {
                "session_id": req.session_id,
                "response": armor["rejection_message"],
                "model_armor_blocked": True,
                "model_armor_status": armor["sanitization_status"],
                "violation_type": armor["violation_type"],
                "tool_calls": []
            }
            
        session = await session_service.get_session(app_name="dallas_heat_planner", user_id="planner_web", session_id=req.session_id)
        if not session:
            session = await session_service.create_session(app_name="dallas_heat_planner", user_id="planner_web")
            session_id = session.id
        else:
            session_id = req.session_id
            
        msg = types.Content(role="user", parts=[types.Part.from_text(text=armor["sanitized_prompt"])])
        response_text = ""
        tool_calls = []
        
        async for event in runner.run_async(
            session_id=session_id,
            user_id="planner_web",
            new_message=msg
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        response_text += part.text
                    elif part.function_call:
                        tool_calls.append({
                            "tool": part.function_call.name,
                            "args": part.function_call.args
                        })

                        
        return {
            "session_id": session_id,
            "response": response_text,
            "tool_calls": tool_calls
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

@app.get("/")
def serve_index():
    return FileResponse(static_dir / "index.html")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
