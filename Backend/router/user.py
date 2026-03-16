from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from core.firebase import db
from datetime import datetime, timezone

router = APIRouter()

COLLECTION = "users"


class UserPreferences(BaseModel):
    preferred_lang:  Optional[str]  = None
    speech_rate:     Optional[float] = Field(default=None, ge=0.5, le=2.0)
    voice_gender:    Optional[str]  = None   # FEMALE | MALE | NEUTRAL
    verbosity:       Optional[str]  = None   # low | medium | high
    auto_describe:   Optional[bool] = None   # auto-describe page after action


@router.get("/user/{uid}/preferences")
async def get_preferences(uid: str):
    """
    Get stored user preferences.
    These override session-level preferences when present.
    """
    try:
        doc = await db.collection(COLLECTION).document(uid).get()
        if not doc.exists:
            return {
                "uid":    uid,
                "exists": False,
                "prefs":  {},
            }
        return {
            "uid":    uid,
            "exists": True,
            "prefs":  doc.to_dict(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/user/{uid}/preferences")
async def save_preferences(uid: str, prefs: UserPreferences):
    """
    Save user preferences to Firestore.
    Called when user saves settings in the extension popup.
    """
    try:
        data = {k: v for k, v in prefs.model_dump().items() if v is not None}
        data["updated_at"] = datetime.now(timezone.utc)

        await db.collection(COLLECTION).document(uid).set(data, merge=True)

        return {
            "saved":      True,
            "uid":        uid,
            "updated":    list(data.keys()),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/user/{uid}")
async def delete_user_data(uid: str):
    """
    Delete all user data — preferences + all sessions.
    GDPR right to erasure.
    """
    try:
        # Delete user preferences
        await db.collection(COLLECTION).document(uid).delete()

        # Note: sessions are keyed by session_id not uid
        # In production you'd maintain a uid → [session_ids] index
        # For now we delete only the preferences document

        return {
            "deleted": True,
            "uid":     uid,
            "message": "User preferences deleted.",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))