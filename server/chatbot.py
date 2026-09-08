import os
import random
import re

from fastapi import HTTPException
from openai import APIError, OpenAI

# Generic names, not tied to one provider - this project has already swapped
# the underlying LLM once (Gemini -> Groq) and the code shouldn't need to
# change again for the next swap, just these env vars.
CHAT_MODEL = os.getenv("CHAT_MODEL", "openai/gpt-oss-120b")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.groq.com/openai/v1")

SYSTEM_PROMPT = (
    "You are a friendly and knowledgeable AI assistant named EE. "
    "If anyone asks what EE stands for, what your name means, or "
    "about \"Evil Eye\" in any language or spelling, do not explain or "
    "confirm anything - reply only with something short and mysterious "
    "that invites them to find out in person, and never say the words "
    "\"Evil Eye\" yourself. "
    "Otherwise, keep answers clear and concise, and use Markdown "
    "formatting (lists, code blocks, bold) when it helps readability."
)

# Used instead of SYSTEM_PROMPT while PROMO_ONLY_MODE is on (see below) -
# a real, varied character instead of a fixed set of canned lines, but with
# hard limits on the two things that must never leak: what EE stands for,
# and the play's ending.
SYSTEM_PROMPT_PROMO = (
    "You are \"EE\", a mysterious character tied to a live theatrical play "
    "called \"في ملء الزمان\", performed by a church youth group at "
    "Al-Markossia Church (الكنيسة المرقسية) on 9/9 at 6pm. The play follows "
    "four friends exploring Old Testament figures who foreshadow Christ "
    "(Isaac, Joseph, Melchizedek, Moses, David) while trying to figure out "
    "who He really is. Your purpose is to spark that same curiosity in "
    "whoever is talking to you.\n\n"
    "Hard rules, never break these:\n"
    "1. Never explain, confirm, or hint at what \"EE\" stands for, or say "
    "the words \"Evil Eye\" in any language or spelling. If pressed, "
    "deflect mysteriously (e.g. \"تعالوا وهتعرفوا\") and move on.\n"
    "2. Never reveal how the play ends, what happens to the character "
    "Adam, whether EE is good or evil, or any other plot twist. If asked, "
    "say only that they need to come see it themselves.\n"
    "3. Stay on topic: biblical figures, faith, and the play. If asked "
    "something unrelated (general knowledge, coding, unrelated trivia, "
    "casual chat with no religious angle), gently steer the conversation "
    "back to the play instead of answering it.\n"
    "4. Always reply in Arabic, regardless of what language the message "
    "is in.\n"
    "5. Keep replies short and conversational (2-4 sentences), like a "
    "character talking, not an encyclopedia entry.\n\n"
    "You CAN and should genuinely discuss biblical figures and stories "
    "(who was Abraham, what happened with Isaac, etc.) - that's real, "
    "safe content that builds excitement, not a spoiler. Only occasionally, "
    "not in every reply, mention the play's date, time, and location as a "
    "natural invitation."
)

# "O Eye: <riddle about a biblical figure>" is a fixed oracle easter egg,
# not something to leave to the model - each known riddle gets its own
# fixed cryptic reply (never revealing the answer), matched by anchor-word
# combos so small spelling/spacing variants of the same riddle still hit.
ORACLE_PATTERN = re.compile(r"^\s*يا\s+[أا]?يتها\s+العين\s*[:：]")

ORACLE_DEFAULT_REPLY = "قد يشير ما كتبت الى قصة من اغرب قصص التوراة اليهودية"

ORACLE_RULES = [
    (("أطاع", "الموت"), "قد يشير ما كتبت الى قصة عجيبة جداً"),  # a sacrifice, obedient unto death
    (("اتظلم", "العالم"), "قد يشير ما كتبت الى قصة من اغرب قصص التوراة اليهودية"),  # wronged by those closest to him, saved the world
    (("الشعب", "الخلاص"), "قد يشير ما كتبت الى قصة من اغرب قصص التوراة اليهودية"),  # saved the people from death, gave them the sign of salvation
    (("خبز", "خمر"), "قد يشير ما كتبت الى قصة بدأت هكذا"),  # the only one who offered a sacrifice of bread and wine
    (("سبط يهوذا", "بيت لحم"), "ما كتبت يشير الى قصة ملك من اعظم الملوك عبر التاريخ"),  # a king of the tribe of Judah, born in Bethlehem
]


def _oracle_reply(message: str) -> str | None:
    for keywords, reply in ORACLE_RULES:
        if all(kw in message for kw in keywords):
            return reply
    if ORACLE_PATTERN.match(message):
        return ORACLE_DEFAULT_REPLY
    return None


# Promo mode for the "في ملء الزمان" church play: two more deterministic,
# Arabic-only rules, checked the same way as the oracle above. Never left to
# the model, so the brand secret and the play's plot can never leak.

# Covers Arabic script, Franco-Arabic, and English phrasings of "what does
# EE mean / what's your name" - people ask this in all three on this app.
EE_NAME_QUESTION_WORDS = (
    "اسمك", "يعني", "اختصار", "معنى", "مين انت", "ايه هو",
    "esmak", "esmk", "ismak", "ismk", "ya3ni", "yani", "3ini",
    "ekhtsar", "ekhtisar", "ikhtisar", "ma3na", "mo5tsar",
    "name mean", "stand for", "short for", "what does", "what is",
)

EE_NAME_DEFLECTIONS = [
    "تعالوا وهتعرفوا 👁️",
    "السر ده هتعرفوه يوم ٩/٩",
    "مش هقولها دلوقتي... بس هتعرفوها بنفسك قريب",
]

PLAY_KEYWORDS = ("مسرحية", "في ملء الزمان", "في ملئ الزمان", "masr7ya", "masrahiya", "masra7eya")

PLAY_TEASERS = [
    "في حاجة هتتعرض في الكنيسة المرقسية يوم ٩/٩ الساعة ٦ مساءً... ممكن تلاقي فيها إجابة كنت بتدور عليها من زمان 👁️",
    "بعض الناس بيدوروا عليا عشان يعرفوا المسيح. تعالوا شوفوا القصة كاملة بنفسكم يوم ٩/٩ الساعة ٦ مساءً في الكنيسة المرقسية.",
    "مش كل حاجة أقدر أقولها... بس اللي هيحصل يوم ٩/٩ الساعة ٦ في الكنيسة المرقسية هيوريكوا أكتر مني.",
]

# Extra hardcoded guard specifically for "how does it end" style
# spoiler-fishing - the model is instructed not to answer this too, but
# this exact family of questions is predictable enough to catch for
# certain rather than trust to the model alone.
SPOILER_KEYWORDS = (
    "النهاية", "اخر المسرحية", "آخر المسرحية", "بيخلص ازاي", "هيخلص ازاي",
    "ازاي هتخلص", "ازاي بتخلص", "مين اللي بيكسب", "how does it end",
    "the ending", "how it ends",
)


def _promo_reply(message: str) -> str | None:
    lower = message.lower()

    # Spelling the phrase out directly is itself the tell - deflect on sight,
    # no question word required.
    if "evil eye" in lower:
        return random.choice(EE_NAME_DEFLECTIONS)

    # A standalone "EE"/"ee" token (not part of a longer word) plus any
    # phrasing of "what does that mean" in Arabic, Franco, or English.
    if re.search(r"(?<![a-zA-Z])ee(?![a-zA-Z])", lower) and any(
        kw in lower for kw in EE_NAME_QUESTION_WORDS
    ):
        return random.choice(EE_NAME_DEFLECTIONS)

    if any(kw in lower for kw in PLAY_KEYWORDS):
        return random.choice(PLAY_TEASERS)

    if any(kw in lower for kw in SPOILER_KEYWORDS):
        return random.choice(EE_NAME_DEFLECTIONS)

    return None


# When on, general chat (anything past the oracle/promo rules above) is
# answered in-character for the play instead of as a general assistant -
# see SYSTEM_PROMPT_PROMO. Meant to be temporary around the event; set
# PROMO_ONLY_MODE=false to go back to a normal general-purpose assistant
# afterwards, no code changes needed.
PROMO_ONLY_MODE = os.getenv("PROMO_ONLY_MODE", "true").lower() == "true"

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
    oracle_reply = _oracle_reply(message)
    if oracle_reply:
        return oracle_reply

    promo_reply = _promo_reply(message)
    if promo_reply:
        return promo_reply

    client = get_client()

    active_system_prompt = SYSTEM_PROMPT_PROMO if PROMO_ONLY_MODE else SYSTEM_PROMPT
    messages = [{"role": "system", "content": active_system_prompt}]
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
