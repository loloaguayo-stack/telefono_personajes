import os
import requests

class VoiceManager:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.elevenlabs.io/v1"
        
        # IDs de voces reales de ElevenLabs
        self.voices = {
            "VOICE_1": "iEjYawvKyFDB2gblp41T",  # Sarah (femenina, cálida)
            "VOICE_2": "7UzGhQ9CKdPWkWZoA5Cx"   # Arnold (masculina, amigable)
        }

    def text_to_speech(self, text: str, voice_id: str) -> bytes:
        """
        Convierte texto a audio MP3 usando ElevenLabs API
        """
        if not self.api_key:
            raise ValueError("ElevenLabs API key not configured")
        
        # Usar ID real de voz o fallback a primera voz disponible
        actual_voice_id = self.voices.get(voice_id, self.voices["VOICE_1"])
        
        url = f"{self.base_url}/text-to-speech/{actual_voice_id}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }
        
        payload = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as e:
            print(f"ElevenLabs API error: {e}")
            # Fallback: retornar silencio para no romper la llamada
            from pydub import AudioSegment
            import io
            silence = AudioSegment.silent(duration=1200)
            buf = io.BytesIO()
            silence.export(buf, format="mp3")
            return buf.getvalue()

voice_manager = VoiceManager(
    api_key=os.getenv("ELEVENLABS_API_KEY", "")

)

