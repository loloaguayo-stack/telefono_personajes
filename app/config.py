import os
from dataclasses import dataclass

@dataclass
class Settings:
    port: int = int(os.getenv("PORT", 8000))
    stream_url: str = os.getenv("STREAM_URL", "")
    max_call_duration_seconds: int = int(os.getenv("MAX_CALL_DURATION", 900))

def get_settings() -> Settings:
    return Settings()
