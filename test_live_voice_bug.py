import asyncio
import json
import base64
import websockets
import time

async def test_live_voice_persistence():
    uri = "ws://localhost:8000/ws/live"
    print(f"Connecting to {uri}...")
    
    async with websockets.connect(uri) as ws:
        # 1. Wait for connection status
        initial_msg = await asyncio.wait_for(ws.recv(), timeout=10.0)
        status_data = json.loads(initial_msg)
        print(f"Received status message: {status_data}")
        assert status_data.get("type") == "status", f"Expected type=status, got {status_data}"
        print(f"Connected to model: {status_data.get('model')}")

        # 2. Send Turn 1: Spoken or text query
        print("\n--- Sending Turn 1 (Text query to Live model) ---")
        await ws.send(json.dumps({
            "type": "text",
            "text": "Hello Commander CoolAid, what is the temperature in West Dallas?"
        }))

        turn_1_completed = False
        coolaid_audio_chunks = 0
        coolaid_texts = []
        
        start_t = time.time()
        while time.time() - start_t < 15.0:
            try:
                msg = await asyncio.wait_for(ws.recv(), timeout=5.0)
                data = json.loads(msg)
                mtype = data.get("type")
                if mtype == "coolaid_transcription":
                    coolaid_texts.append(data.get("text"))
                    print(f"CoolAid Transcribing: {data.get('text')}")
                elif mtype == "audio":
                    coolaid_audio_chunks += 1
                elif mtype == "turn_complete":
                    print(f"Turn 1 Complete! Received {coolaid_audio_chunks} audio chunks.")
                    turn_1_completed = True
                    break
            except asyncio.TimeoutError:
                print("Timeout waiting for message in Turn 1")
                break

        assert turn_1_completed, "Turn 1 failed to complete!"
        assert coolaid_audio_chunks > 0, "No audio chunks received in Turn 1!"

        # 3. Simulate streaming PCM audio frames (16kHz mono silence/white noise) for 3 seconds
        print("\n--- Simulating Live Mic Audio Streaming for 3 seconds ---")
        dummy_pcm = b"\x00" * (4096 * 2)
        dummy_b64 = base64.b64encode(dummy_pcm).decode("utf-8")
        
        for i in range(12): # ~3 seconds of continuous audio frames
            await ws.send(json.dumps({
                "type": "audio",
                "data": dummy_b64
            }))
            await asyncio.sleep(0.25)
            assert ws.close_code is None, f"WebSocket closed prematurely during streaming chunk {i}!"

        print("Audio streaming completed without socket disconnect. Socket remains open!")

        # 4. Send Turn 2: Follow-up question to verify multi-turn persistence!
        print("\n--- Sending Turn 2 (Testing multi-turn persistence - verifying it does NOT close) ---")
        await ws.send(json.dumps({
            "type": "text",
            "text": "What cooling hubs are available?"
        }))

        turn_2_completed = False
        coolaid_audio_chunks_turn2 = 0
        
        start_t = time.time()
        while time.time() - start_t < 15.0:
            try:
                msg = await asyncio.wait_for(ws.recv(), timeout=5.0)
                data = json.loads(msg)
                mtype = data.get("type")
                if mtype == "coolaid_transcription":
                    print(f"CoolAid Turn 2 Transcribing: {data.get('text')}")
                elif mtype == "audio":
                    coolaid_audio_chunks_turn2 += 1
                elif mtype == "turn_complete":
                    print(f"Turn 2 Complete! Received {coolaid_audio_chunks_turn2} audio chunks.")
                    turn_2_completed = True
                    break
            except asyncio.TimeoutError:
                print("Timeout waiting for message in Turn 2")
                break

        assert turn_2_completed, "Turn 2 failed to complete - session may have closed after Turn 1!"
        assert coolaid_audio_chunks_turn2 > 0, "No audio chunks received in Turn 2!"

        print("\n>>> ALL VERIFICATIONS PASSED: Real-time voice session is stable, multi-turn, and non-terminating! <<<")

if __name__ == "__main__":
    asyncio.run(test_live_voice_persistence())
