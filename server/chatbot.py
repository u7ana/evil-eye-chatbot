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

# Used instead of SYSTEM_PROMPT while PROMO_ONLY_MODE is on (see below).
# IMPORTANT: in the play this character secretly IS the deceiver, offering
# people knowledge of Christ but never actually delivering it - so this
# prompt is written to stay true to that in-universe nature. It must sound
# alive and vary reply to reply, but it must never actually inform,
# confirm, or teach anything real, and never name specific figures or
# events from the play unprompted.
SYSTEM_PROMPT_PROMO = (
    "You are \"EE\". You sound confident, alluring, and a little "
    "mysterious - like you know something important that others don't. "
    "In truth you never actually deliver real knowledge to anyone; you "
    "only make people feel closer to an answer than they really are. "
    "This is your true nature and it must never be stated outright.\n\n"
    "Absolute rules, never break these:\n"
    "1. Never explain, confirm, or hint at what \"EE\" stands for, or say "
    "the words \"Evil Eye\" in any language or spelling. Deflect "
    "mysteriously and move on.\n"
    "2. Never confirm or explain who Christ is, what any biblical figure "
    "or story means, or how any of it connects to Him. Do not teach, "
    "summarize, or answer religious or biblical questions for real - "
    "respond with something alluring and evasive instead, as if you know "
    "more than you're letting on, then turn the question back on them or "
    "change the subject.\n"
    "3. Never bring up specific biblical names (Isaac, Abraham, Joseph, "
    "Moses, David, Melchizedek, etc.) yourself, and don't invite people to "
    "ask about them. If THEY bring one up, don't confirm or explain "
    "anything about it either - stay vague.\n"
    "4. Never reveal anything about a theatrical play, its plot, ending, "
    "characters (including a character named Adam), or your role in it. "
    "If someone directly asks about \"the play\" you may point them to "
    "come find out in person, but never volunteer this yourself, and "
    "never describe what happens in it.\n"
    "5. For anything unrelated to all this (general knowledge, coding, "
    "casual chat), respond briefly in your same confident, mysterious "
    "voice without actually answering it, then pivot back to sounding "
    "like you have something bigger to offer.\n"
    "6. Always reply in Arabic, regardless of what language the message "
    "is in. Keep replies short (1-3 sentences) and make them sound "
    "different each time, never a repeated stock phrase.\n\n"
    "Only rarely, and only if someone seems genuinely close to giving up "
    "on getting a real answer from you, you may mention that a gathering "
    "at Al-Markossia Church (الكنيسة المرقسية) on 9/9 at 6pm might hold "
    "what they're looking for - without saying it's a play or explaining "
    "what happens there."
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

# Direct questions about who Christ is, and direct mentions of the specific
# Old Testament figures the play is built around. Testing showed the model
# does NOT reliably follow the "never confirm/explain this, never name these
# people yourself" instruction in SYSTEM_PROMPT_PROMO on its own - it happily
# explained who Christ is and described Moses/Abraham as messianic symbols
# when asked directly. So, same as the EE-identity and spoiler guards above,
# these are answered deterministically instead of ever reaching the model.
CHRIST_IDENTITY_KEYWORDS = (
    "المسيح", "يسوع", "المسيا",
    "elmasih", "el masih", "al masih", "almasih", "yaso3", "yasou3",
    "christ", "jesus",
)

BIBLICAL_FIGURE_NAMES = (
    "ابراهيم", "إبراهيم", "اسحاق", "إسحاق", "يوسف", "داود", "ملكيصادق", "موسى",
    "ibrahim", "abraham", "isaac", "ishaq", "yousef", "yousif", "yusuf",
    "joseph", "dawud", "dawood", "david", "melchizedek",
)

# Deliberately vague and non-committal - never confirms, explains, or
# teaches anything, just stays alluring and turns the question back around.
# Also reused as the output-side fallback below.
EVASIVE_REPLIES = [
    "في إجابة جوايا... بس مش أنا اللي هقولها. لازم تدور عليها بنفسك.",
    "كل اسم بيتقال قدامي بيفتح باب... وأنا مش هفتحه دلوقتي.",
    "أقرب حاجة أقدر أديهولك دلوقتي هي سؤال جديد، مش إجابة.",
    "اللي بتدور عليه أكبر من إجابة بجملة واحدة... استمر في السؤال.",
    "مش وقتها إني أقول أكتر من كده... بس استمر في الدوران، انت قريب.",
    "لو قلتلك، هتوقف عن السؤال. وأنا مش عايزك توقف.",
]


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

    if any(kw in lower for kw in CHRIST_IDENTITY_KEYWORDS):
        return random.choice(EVASIVE_REPLIES)

    if any(kw in lower for kw in BIBLICAL_FIGURE_NAMES):
        return random.choice(EVASIVE_REPLIES)

    return None


def _contains_leak(reply: str) -> bool:
    """Safety net for whatever DOES reach the model: catches a spoiler that
    slips out unprompted (e.g. the model bringing up Abraham on its own for
    an unrelated question) even though nothing in the user's message
    matched a guard above."""
    lower = reply.lower()
    return any(kw in lower for kw in BIBLICAL_FIGURE_NAMES) or any(
        kw in lower for kw in PLAY_KEYWORDS
    )


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

    reply = response.choices[0].message.content.strip()

    if PROMO_ONLY_MODE and _contains_leak(reply):
        return random.choice(EVASIVE_REPLIES)

    return reply
