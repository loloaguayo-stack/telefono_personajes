import json, base64, io
import numpy as np
from fastapi import APIRouter, Form, WebSocket
from fastapi.responses import Response
from twilio.twiml.voice_response import VoiceResponse, Connect
from pydub import AudioSegment

from app.voice import voice_manager
from app.agents import get_agent_by_phone
from app.config import get_settings

router = APIRouter()
settings = get_settings()

def lin2ulaw(pcm_val):
    """
    Convierte audio linear PCM a mu-law (reemplazo de audioop.lin2ulaw para Python 3.13+)
    """
    BIAS = 0x84
    CLIP = 32635
    
    # Convertir a numpy array si no lo es
    pcm_val = np.asarray(pcm_val, dtype=np.int16)
    
    # Aplicar el signo
    sign = (pcm_val < 0).astype(np.int16)
    pcm_val = np.abs(pcm_val)
    
    # Clip
    pcm_val = np.clip(pcm_val, 0, CLIP)
    pcm_val = pcm_val + BIAS
    
    # Calcular segmento y quantización
    seg = np.zeros_like(pcm_val, dtype=np.uint8)
    for i in range(7, -1, -1):
        if np.any(pcm_val >= (1 << (i + 8))):
            seg[pcm_val >= (1 << (i + 8))] = i
    
    uval = (seg << 4) | ((pcm_val >> (seg + 3)) & 0x0F)
    uval = (~uval) & 0xFF
    uval = np.where(sign, uval | 0x80, uval & 0x7F)
    
    return uval.astype(np.uint8).tobytes()

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
        # Convertir bytes a array de int16
        pcm_data = np.frombuffer(raw, dtype=np.int16)
        # Convertir a mu-law
        mulaw = lin2ulaw(pcm_data)
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
