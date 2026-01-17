import json, base64, io, audioop
from fastapi import APIRouter, Form, WebSocket
from fastapi.responses import Response
from twilio.twiml.voice_response import VoiceResponse, Connect
from pydub import AudioSegment

from app.voice import voice_manager
from app.agents import get_agent_by_phone
from app.config import get_settings

router = APIRouter()
settings = get_settings()

@router.post("/incoming-call")
async def incoming_call(From: str = Form(...), CallSid: str = Form(...)):
    vr = VoiceResponse()
    connect = Connect()
    connect.stream(url=settings.stream_url)
    vr.append(connect)
    return Response(str(vr), media_type="application/xml")

def mp3_to_mulaw_chunks(mp3_bytes: bytes, chunk_ms: int = 100):
    seg = AudioSegment.from_file(io.BytesIO(mp3_bytes), format="mp3")
    seg = seg.set_channels(1).set_frame_rate(8000).set_sample_width(2)
    chunks = []
    for i in range(0, len(seg), chunk_ms):
        raw = seg[i:i+chunk_ms].raw_data
        mulaw = audioop.lin2ulaw(raw, 2)
        chunks.append(base64.b64encode(mulaw).decode())
    return chunks

@router.websocket("/media")
async def media(ws: WebSocket):
    await ws.accept()
    stream_sid = None

    try:
        while True:
            event = json.loads(await ws.receive_text())

            if event["event"] == "start":
                stream_sid = event["streamSid"]
                from_number = event["start"].get("from", "")
                agent = get_agent_by_phone(from_number)
                mp3 = voice_manager.text_to_speech(agent.greeting, agent.voice_id)
                for payload in mp3_to_mulaw_chunks(mp3):
                    await ws.send_text(json.dumps({
                        "event": "media",
                        "streamSid": stream_sid,
                        "media": {"payload": payload}
                    }))

            elif event["event"] == "stop":
                break

    except Exception as e:
        print("WS error:", e)
    finally:
        await ws.close()
