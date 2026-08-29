import edge_tts
from fastapi import HTTPException

# Windows only ships one Arabic system voice (Hoda, female), so Arabic
# speech goes through edge-tts instead: free, no API key, and it has a
# real male Egyptian-Arabic neural voice to match how the app is spoken to.
ARABIC_VOICE = "ar-EG-ShakirNeural"


async def synthesize_arabic(text: str) -> bytes:
    communicate = edge_tts.Communicate(text[:4000], ARABIC_VOICE)
    chunks = []
    try:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                chunks.append(chunk["data"])
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Arabic voice request failed: {exc}") from exc

    if not chunks:
        raise HTTPException(status_code=502, detail="Arabic voice request returned no audio.")

    return b"".join(chunks)
