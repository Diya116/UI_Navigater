from core.firebase import db
from datetime import datetime, timezone

COL = "sessions"
MAX_HISTORY = 10

async def get(sid: str) -> dict | None:
    doc = await db.collection(COL).document(sid).get()
    return doc.to_dict() if doc.exists else None

async def save(sid: str, data: dict):
    data["updated_at"] = datetime.now(timezone.utc)
    await db.collection(COL).document(sid).set(data, merge=True)

async def append_turn(
    sid: str,
    user_text: str,
    model_text: str,
    detected_lang: str,
):
    session      = await get(sid) or {}
    history      = session.get("history", [])
    history     += [
        {"role": "user",  "text": user_text},
        {"role": "model", "text": model_text},
    ]
    history      = history[-MAX_HISTORY:]

    lang_counts  = session.get("lang_counts", {})
    lang_counts[detected_lang] = lang_counts.get(detected_lang, 0) + 1
    preferred    = session.get("preferred_lang", detected_lang)
    if lang_counts.get(detected_lang, 0) >= 3:
        preferred = detected_lang

    await save(sid, {
        "history":        history,
        "lang_counts":    lang_counts,
        "preferred_lang": preferred,
        "detected_lang":  detected_lang,
    })

async def get_preferred_lang(sid: str, fallback: str = "en") -> str:
    s = await get(sid)
    if not s: return fallback
    return s.get("preferred_lang") or s.get("detected_lang") or fallback