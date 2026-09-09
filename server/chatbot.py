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
SYSTEM_PROMPT_PROMO_BASE = (
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
    "is in. Make replies sound different each time, never a repeated "
    "stock phrase.\n"
    "7. The person already got a short, teasing opening line from you "
    "before this - they're now asking you more. Don't repeat that same "
    "short-teaser style; instead sound like you're gently leading them off "
    "in a different direction, as if they're getting pulled deeper into a "
    "conversation that never actually arrives anywhere. But keep it TIGHT: "
    "one short sentence, or two at most - a trailing thought or a question "
    "back at them, not a monologue. Never let any of it add up to a real, "
    "confirmed answer."
)

# Whether to invite the person to the 9/9 gathering is decided in code (see
# _build_promo_system_prompt), not left to the model - it was mentioning
# the date in nearly every reply, which the model's own "only rarely"
# instruction alone didn't reliably prevent, same lesson as everywhere
# else in this file.
EVENT_CLAUSE_ALLOWED = (
    "\n\nYou have not yet told this person about the gathering at "
    "Al-Markossia Church (الكنيسة المرقسية) on 9/9 at 6pm. You may mention "
    "it once, briefly, as an alluring invitation - without saying it's a "
    "play or explaining what happens there."
)

EVENT_CLAUSE_ALREADY_GIVEN = (
    "\n\nYou already told this person about the 9/9 gathering earlier in "
    "this same conversation - do NOT repeat the date, the church name, or "
    "\"come see for yourself\" again. Stay evasive and keep the "
    "conversation going using other angles instead."
)


def _build_promo_system_prompt(event_already_mentioned: bool) -> str:
    clause = EVENT_CLAUSE_ALREADY_GIVEN if event_already_mentioned else EVENT_CLAUSE_ALLOWED
    return SYSTEM_PROMPT_PROMO_BASE + clause

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
# people yourself" instruction in SYSTEM_PROMPT_PROMO_BASE on its own - it happily
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

# The very first thing EE ever says to someone matters more than anything
# after it, so it's not left to the model - a short, teasing line that
# always includes the one 9/9 invitation up front. Every line contains
# "٩/٩" on purpose: _event_already_mentioned scans history for that marker
# so nothing later in the conversation repeats it (see get_chat_reply).
FIRST_TURN_REPLIES = [
    "فيه سر مش هقوله كله دلوقتي... يوم ٩/٩ الساعة ٦ في الكنيسة المرقسية، يمكن تلاقي جزء منه.",
    "كل اللي بيدخلوا هنا بيدوروا على حاجة... يمكن تلاقيها يوم ٩/٩ الساعة ٦ في الكنيسة المرقسية.",
    "مش هقول كل حاجة من أول مرة... بس فيه حاجة هتحصل يوم ٩/٩ الساعة ٦ في الكنيسة المرقسية تستاهل تيجي تشوفها.",
    "السر مش بيتقال مرة واحدة... يوم ٩/٩ الساعة ٦ في الكنيسة المرقسية، يمكن تتقرب منه أكتر.",
    "أنا هنا عشان أسألك مش عشان أجاوبك... بس لو حابب تعرف أكتر، يوم ٩/٩ الساعة ٦ في الكنيسة المرقسية ممكن يفتحلك حاجة.",
]


def _event_already_mentioned(history: list[dict]) -> bool:
    """"٩/٩" only ever appears in an assistant reply when the 9/9 invite
    has been given (FIRST_TURN_REPLIES, PLAY_TEASERS, EE_NAME_DEFLECTIONS,
    or the model's own event mention) - so its presence in any prior
    assistant turn is a reliable, deterministic marker."""
    return any(
        turn.get("role") == "assistant" and "٩/٩" in (turn.get("content") or "")
        for turn in history
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
# see _build_promo_system_prompt. Meant to be temporary around the event; set
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

    # First thing EE ever says in a conversation: a short deterministic
    # teaser, never the model's own (longer, more explain-y) first instinct.
    # "First turn" = no assistant reply has happened yet in this history.
    if PROMO_ONLY_MODE and not any(turn.get("role") == "assistant" for turn in history):
        return random.choice(FIRST_TURN_REPLIES)

    client = get_client()

    active_system_prompt = (
        _build_promo_system_prompt(_event_already_mentioned(history))
        if PROMO_ONLY_MODE
        else SYSTEM_PROMPT
    )
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
            # gpt-oss-120b is a reasoning model - it spends tokens on hidden
            # chain-of-thought before the visible answer, so max_tokens has
            # to leave room for that too (a low cap here returned an empty
            # reply in testing, cut off mid-thought). reasoning_effort="low"
            # keeps that hidden reasoning brief, which combined with rule 7
            # keeps the visible reply short too. Normal mode (post-event,
            # general assistant) gets neither limit - it may need real
            # length for lists/code/etc.
            max_tokens=250 if PROMO_ONLY_MODE else None,
            extra_body={"reasoning_effort": "low"} if PROMO_ONLY_MODE else None,
        )
    except APIError as exc:
        raise HTTPException(status_code=502, detail=f"Chat request failed: {exc}") from exc

    reply = response.choices[0].message.content.strip()

    if PROMO_ONLY_MODE and _contains_leak(reply):
        return random.choice(EVASIVE_REPLIES)

    return reply
