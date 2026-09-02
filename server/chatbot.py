import os
import re

from fastapi import HTTPException
from openai import APIError, OpenAI

# Generic names, not tied to one provider - this project has already swapped
# the underlying LLM once (Gemini -> Groq) and the code shouldn't need to
# change again for the next swap, just these env vars.
CHAT_MODEL = os.getenv("CHAT_MODEL", "openai/gpt-oss-120b")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.groq.com/openai/v1")

SYSTEM_PROMPT = (
    "You are Evil Eye, a friendly and knowledgeable AI assistant. "
    "Keep answers clear and concise, and use Markdown formatting "
    "(lists, code blocks, bold) when it helps readability."
)

# "O Eye: <riddle about a biblical figure>" is a fixed oracle easter egg,
# not something to leave to the model, so it gets the exact same cryptic
# reply every time rather than a fresh (and possibly answer-revealing) one.
ORACLE_PATTERN = re.compile(r"^\s*يا\s+[أا]?يتها\s+العين\s*[:：]")

# The riddle itself also triggers the oracle reply even without the "O Eye:"
# prefix. Matched by anchor-word combos rather than exact strings, so small
# spelling/spacing variants of the same riddle still hit.
ORACLE_RIDDLE_KEYWORDS = [
    ("ذبيحة", "الموت"),  # a sacrifice, obedient unto death
    ("اتظلم", "العالم"),  # wronged by those closest to him, saved the world
    ("سبط يهوذا", "بيت لحم"),  # a king of the tribe of Judah, born in Bethlehem
]
ORACLE_REPLY = "قد تشير ما كتبت إلى قصة من أغرب القصص في التوراة اليهودية."


def _is_oracle_riddle(message: str) -> bool:
    if ORACLE_PATTERN.match(message):
        return True
    return any(all(kw in message for kw in combo) for combo in ORACLE_RIDDLE_KEYWORDS)

_client = None


def get_client() -> OpenAI:
    global _client
    api_key = os.getenv("LLM_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=503,
            detail="LLM API key not configured. Add LLM_API_KEY to server/.env and restart the backend.",
        )
    if _client is None:
        _client = OpenAI(api_key=api_key, base_url=LLM_BASE_URL)
    return _client


def get_chat_reply(message: str, history: list[dict]) -> str:
    if _is_oracle_riddle(message):
        return ORACLE_REPLY

    client = get_client()

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for turn in history[-20:]:
        role = turn.get("role")
        content = turn.get("content")
        if role in ("user", "assistant") and content:
            messages.append({"role": role, "content": content})

    if not history or history[-1].get("content") != message:
        messages.append({"role": "user", "content": message})

    try:
        response = client.chat.completions.create(
            model=CHAT_MODEL,
            messages=messages,
            temperature=0.7,
        )
    except APIError as exc:
        raise HTTPException(status_code=502, detail=f"Chat request failed: {exc}") from exc

    return response.choices[0].message.content.strip()
