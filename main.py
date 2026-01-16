from fastapi import FastAPI
from app.twilio_handler import router as twilio_router

app = FastAPI(title="AI Companion Phone")

app.include_router(twilio_router)

@app.get("/")
async def root():
    return {"status": "ok", "service": "AI Companion Phone"}
