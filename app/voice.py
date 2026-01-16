import os, io
from pydub import AudioSegment

class VoiceManager:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def text_to_speech(self, text: str, voice_id: str) -> bytes:
        # Placeholder: silencio válido (no rompe Twilio)
        silence = AudioSegment.silent(duration=1200)
        buf = io.BytesIO()
        silence.export(buf, format="mp3")
        return buf.getvalue()

voice_manager = VoiceManager(
    api_key=os.getenv("ELEVENLABS_API_KEY", "")
)
