from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import Response
from pydantic import BaseModel, Field

from chatbot import get_chat_reply
from transcribe import transcribe_audio
from tts import synthesize_arabic

router = APIRouter()


class HistoryTurn(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    history: list[HistoryTurn] = Field(default_factory=list)


class ChatResponse(BaseModel):
    reply: str


class TranscribeResponse(BaseModel):
    text: str


class SpeakRequest(BaseModel):
    text: str


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest):
    if not payload.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    history = [turn.model_dump() for turn in payload.history]
    reply = get_chat_reply(payload.message, history)

    return ChatResponse(reply=reply)


@router.post("/transcribe", response_model=TranscribeResponse)
async def transcribe(audio: UploadFile = File(...), language: str | None = Form(None)):
    audio_bytes = await audio.read()
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="No audio received.")

    text = transcribe_audio(audio_bytes, language=language)
    return TranscribeResponse(text=text)


@router.post("/speak-arabic")
async def speak_arabic(payload: SpeakRequest):
    if not payload.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")

    audio_bytes = await synthesize_arabic(payload.text)
    return Response(content=audio_bytes, media_type="audio/mpeg")
