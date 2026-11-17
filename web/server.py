"""FastAPI Backend Server for Dallas Urban Heat Resilience Planning Dashboard."""

import os
import sys
import asyncio
import base64
import json
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from google import genai

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

@app.get("/api/routes/walking")
def walking_route(origin_lat: float, origin_lon: float, dest_lat: float, dest_lon: float):
    return tools.compute_pedestrian_route(origin_lat, origin_lon, dest_lat, dest_lon)

@app.get("/api/places/nearby")
def nearby_places(lat: float, lon: float, radius: float = 3000.0, place_type: str = "all"):
    return tools.search_civic_places(lat, lon, radius, place_type)

@app.get("/api/solar/insights")
def solar_insights(lat: float, lon: float):
    return tools.get_solar_and_shade_insights(lat, lon)

@app.get("/api/vulnerability")
def vulnerability_profile(tract_id: str = "48113020500"):
    return tools.get_vulnerability_profile(tract_id)

@app.get("/api/air-quality")
def air_quality(pollutant: str = "PM2.5", days: int = 30, county: str = "Dallas", state: str = "Texas"):
    return tools.get_air_quality_summary(pollutant=pollutant, days=days, county_name=county, state_name=state)

@app.get("/api/us/vulnerability")
def us_vulnerability(geo_id: Optional[str] = None, county: Optional[str] = None, state: Optional[str] = None):
    return tools.get_national_vulnerability_profile(geo_id=geo_id, county_name=county, state_name=state)

@app.get("/api/us/sites")
def us_priority_sites(state: str, county: str, top_n: int = 5):
    return tools.rank_national_cooling_center_sites(state_name=state, county_name=county, top_n=top_n)

@app.get("/api/us/counties")
def us_counties_list(state: Optional[str] = None):
    """Returns list of US counties or counties within a given state from us_resilience_master."""
    client = tools.get_bq_client()
    where = f"WHERE LOWER(state_name) = LOWER('{state}')" if state else ""
    sql = f"""
    SELECT state_name, county_name, COUNT(*) as tract_count, SUM(total_pop) as population
    FROM `{tools.PROJECT_ID}.{tools.DATASET}.us_resilience_master`
    {where}
    GROUP BY state_name, county_name
    ORDER BY state_name, county_name
    """
    try:
        rows = [dict(r) for r in client.query(sql).result()]
        return {"count": len(rows), "counties": rows}
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/contrast")
def heat_contrast(loc_a: str = "4th and Marsalis", loc_b: str = "2 blocks north of 4th and Marsalis"):
    return tools.compare_locations_heat_contrast(loc_a, loc_b)

@app.get("/api/resolve-location")
def resolve_loc(query: str = "4th and Marsalis"):
    return tools.resolve_dallas_location(query)


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

@app.get("/api/agents")
def list_agents():
    return {
        "root_agent": {
            "name": ag.root_agent.name,
            "model": ag.root_agent.model,
            "role": "Chief Climate Resilience & Investment Officer (Commander)",
            "total_tools": len(ag.root_agent.tools)
        },
        "subagents": [
            {
                "name": sub.name,
                "model": sub.model,
                "description": sub.description,
                "tools": [t.__name__ for t in sub.tools]
            }
            for sub in ag.all_subagents
        ]
    }

@app.get("/api/3d-tiles/config")
def get_3d_tiles_config():
    return {
        "service": "Google Photorealistic 3D Tiles API",
        "tile_server_url": "https://tile.googleapis.com/v1/3dtiles/root.json",
        "format": "OGC 3D Tiles / glTF",
        "integration_modes": ["CesiumJS", "deck.gl", "Google Maps 3D (<gmp-map-3d>)"],
        "dallas_bounds": {
            "center": {"lat": 32.7767, "lng": -96.7970},
            "default_tilt": 65.0,
            "default_heading": 30.0,
            "default_range": 1500.0
        },
        "features": [
            "Photorealistic textured building meshes",
            "High-resolution 3D terrain and canopy extrusion",
            "BigQuery ML heat offset layer draping",
            "Solar radiation and shadow cast integration"
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

@app.websocket("/ws/live")
async def websocket_live_endpoint(websocket: WebSocket):
    """Bidirectional real-time voice streaming endpoint via Gemini 3.8 Live API."""
    await websocket.accept()
    client = genai.Client()
    
    config = types.LiveConnectConfig(
        response_modalities=[types.Modality.AUDIO],
        input_audio_transcription=types.AudioTranscriptionConfig(),
        output_audio_transcription=types.AudioTranscriptionConfig(),
        system_instruction=types.Content(
            parts=[types.Part(text=(
                "You are Commander Dana, Chief Climate Resilience AI for the City of Dallas. "
                "You speak clearly, warmly, and concisely in real-time conversation. "
                "You have live knowledge of Dallas heat vulnerability, cooling centers, and climate data: "
                "West Dallas (Tract 48113020500) is the priority heat hotspot at 104.5°F with 31.4% poverty; "
                "Top cooling hubs include MLK Jr. Center, West Dallas Multipurpose Center, and Bachman Rec Center; "
                "Track 1 mobile hydration tankers stage at unshaded DART bus stops along Hampton Rd and Singleton Blvd; "
                "Singapore DUCT 3D microclimate physics shows tree canopy reduces ambient temperatures by 3.2°F, "
                "while cool roofs and high-albedo pavements reduce surface heat by up to 12°F. "
                "Keep responses conversational, concise, and brief (1-3 sentences) so the audio dialogue flows naturally."
            ))]
        )
    )
    
    try:
        async with client.aio.live.connect(model="gemini-3.8-live", config=config) as session:
            await websocket.send_json({"type": "status", "status": "connected", "model": "gemini-3.8-live"})

            async def receive_from_gemini():
                try:
                    async for response in session.receive():
                        sc = response.server_content
                        if not sc:
                            continue
                        
                        # Real-time barge-in interruption detection
                        if sc.interrupted:
                            await websocket.send_json({"type": "interrupted"})
                        
                        # User speech transcription
                        if sc.interim_input_transcription and sc.interim_input_transcription.text:
                            await websocket.send_json({
                                "type": "user_transcription",
                                "text": sc.interim_input_transcription.text,
                                "is_final": False
                            })
                        elif sc.input_transcription and sc.input_transcription.text:
                            await websocket.send_json({
                                "type": "user_transcription",
                                "text": sc.input_transcription.text,
                                "is_final": True
                            })
                        
                        # Dana speech transcription
                        if sc.output_transcription and sc.output_transcription.text:
                            await websocket.send_json({
                                "type": "dana_transcription",
                                "text": sc.output_transcription.text
                            })
                        
                        # Audio chunks (24kHz PCM)
                        if sc.model_turn and sc.model_turn.parts:
                            for part in sc.model_turn.parts:
                                if part.inline_data and part.inline_data.data:
                                    audio_b64 = base64.b64encode(part.inline_data.data).decode("utf-8")
                                    await websocket.send_json({
                                        "type": "audio",
                                        "data": audio_b64,
                                        "rate": 24000
                                    })
                        
                        if sc.turn_complete:
                            await websocket.send_json({"type": "turn_complete"})
                except asyncio.CancelledError:
                    pass
                except Exception as e:
                    print("Error receiving from Gemini Live:", e)

            async def receive_from_client():
                try:
                    while True:
                        msg = await websocket.receive_text()
                        data = json.loads(msg)
                        mtype = data.get("type")
                        
                        if mtype == "audio":
                            audio_b64 = data.get("data", "")
                            if audio_b64:
                                audio_bytes = base64.b64decode(audio_b64)
                                await session.send_realtime_input(
                                    audio=types.Blob(data=audio_bytes, mime_type="audio/pcm;rate=16000")
                                )
                        elif mtype == "text":
                            user_text = data.get("text", "")
                            armor = inspect_prompt_armor(user_text)
                            if not armor["safe"]:
                                await websocket.send_json({
                                    "type": "armor_blocked",
                                    "message": armor["rejection_message"]
                                })
                            else:
                                await session.send_realtime_input(text=armor["sanitized_prompt"])
                        elif mtype == "stream_end":
                            await session.send_realtime_input(audio_stream_end=True)
                except asyncio.CancelledError:
                    pass
                except WebSocketDisconnect:
                    pass
                except Exception as e:
                    print("Error receiving from client WebSocket:", e)

            gemini_task = asyncio.create_task(receive_from_gemini())
            client_task = asyncio.create_task(receive_from_client())

            done, pending = await asyncio.wait(
                [gemini_task, client_task],
                return_when=asyncio.FIRST_COMPLETED
            )
            for t in pending:
                t.cancel()
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print("WebSocket live session error:", e)
        try:
            await websocket.send_json({"type": "error", "message": str(e)})
            await websocket.close()
        except Exception:
            pass

static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

@app.get("/")
def serve_index():
    return FileResponse(static_dir / "index.html")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
