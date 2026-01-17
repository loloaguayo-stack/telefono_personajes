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

@router.post("/respond")
async def respond(SpeechResult: str = Form(...), From: str = Form(...)):
    # 1. Identificar vecino
    agent = get_agent_by_phone(From)
    
    # 2. Claude genera respuesta (Texto)
    ai_text = await llm_manager.get_response(agent.prompt, SpeechResult)
    
    # 3. ElevenLabs genera audio y lo guarda en /tmp
    audio_content = await voice_manager.text_to_speech(ai_text, agent.voice_id)
    filename = f"reply_{hash(ai_text)}.mp3"
    with open(f"/tmp/{filename}", "wb") as f:
        f.write(audio_content)
    
    # 4. TwiML para que Twilio reproduzca y vuelva a escuchar
    vr = VoiceResponse()
    audio_url = f"{settings.base_url}/get-audio/{filename}"
    
    vr.play(audio_url)
    
    # Re-enganchamos el Gather para que la conversación siga
    gather = vr.gather(input="speech", action="/respond", language="es-ES", speech_timeout="auto")
    return Response(str(vr), media_type="application/xml")

