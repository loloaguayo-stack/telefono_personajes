from fastapi import FastAPI
from app.twilio_handler import router as twilio_router
from fastapi.responses import FileResponse
import os

app = FastAPI(title="AI Companion Phone")

app.include_router(twilio_router)

@app.get("/")
async def root():
    return {"status": "ok", "service": "AI Companion Phone"}

@app.get("/get-audio/{filename}")
async def get_audio(filename: str):
    file_path = f"/tmp/{filename}"
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="audio/mpeg")
    return {"error": "File not found"}

