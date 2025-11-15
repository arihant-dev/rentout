from fastapi import APIRouter # type: ignore
from pydantic import BaseModel # type: ignore
from app.services.ai_service import call_text_model, call_text_to_speech # type: ignore

router = APIRouter()

class AIRequest(BaseModel):
    text: str

@router.post("/text")
async def text(req: AIRequest):
    return {"reply": await call_text_model(req.text)}

@router.post("/tts")
async def tts(req: AIRequest):
    return {"audio_url": await call_text_to_speech(req.text)}