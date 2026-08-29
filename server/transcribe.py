import os

from fastapi import HTTPException

WHISPER_MODEL_SIZE = os.getenv("WHISPER_MODEL", "small")

# Lazy-loaded: the model (100s of MB) only gets pulled into memory the
# first time someone actually uses the mic, not at server startup.
_model = None


def _get_model():
    global _model
    if _model is None:
        from faster_whisper import WhisperModel

        _model = WhisperModel(WHISPER_MODEL_SIZE, device="cpu", compute_type="int8")
    return _model


def transcribe_audio(audio_bytes: bytes, language: str | None = None) -> str:
    import io

    try:
        model = _get_model()
    except Exception as exc:  # first-run model download/load failure, etc.
        raise HTTPException(
            status_code=503,
            detail=f"Whisper model could not be loaded: {exc}",
        ) from exc

    segments, _info = model.transcribe(
        io.BytesIO(audio_bytes),
        language=language,
        vad_filter=True,
    )
    return " ".join(segment.text.strip() for segment in segments).strip()
