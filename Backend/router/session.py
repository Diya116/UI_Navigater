from fastapi import APIRouter, HTTPException
from services import session as sess
from core.firebase import db

router = APIRouter()


@router.get("/session/{session_id}")
async def get_session(session_id: str):
    """
    Get session data for a user.
    Returns history count, preferred language, usage stats.
    Used by the extension popup to show stats.
    """
    data = await sess.get(session_id)

    if not data:
        return {
            "session_id":     session_id,
            "exists":         False,
            "preferred_lang": None,
            "detected_lang":  None,
            "lang_counts":    {},
            "history_count":  0,
            "last_url":       None,
            "updated_at":     None,
        }

    return {
        "session_id":     session_id,
        "exists":         True,
        "preferred_lang": data.get("preferred_lang"),
        "detected_lang":  data.get("detected_lang"),
        "lang_counts":    data.get("lang_counts", {}),
        "history_count":  len(data.get("history", [])),
        "last_url":       data.get("last_url"),
        "updated_at":     str(data.get("updated_at", "")),
    }


@router.delete("/session/{session_id}")
async def clear_session_history(session_id: str):
    """
    Clear conversation history for a session.
    Keeps language preference — user does not have to re-establish it.
    Called when user clicks "Clear session" in popup settings.
    """
    await sess.clear_history(session_id)
    return {
        "cleared":    True,
        "session_id": session_id,
        "message":    "Conversation history cleared. Language preference kept.",
    }


@router.delete("/session/{session_id}/full")
async def delete_session_fully(session_id: str):
    """
    Fully delete a session including language preferences.
    Used for GDPR data deletion requests.
    """
    try:
        await db.collection("sessions").document(session_id).delete()
        return {
            "deleted":    True,
            "session_id": session_id,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/session/{session_id}/history")
async def get_session_history(session_id: str):
    """
    Get conversation history for a session.
    Useful for debugging and user transparency.
    """
    data = await sess.get(session_id)
    if not data:
        raise HTTPException(status_code=404, detail="Session not found")

    return {
        "session_id": session_id,
        "history":    data.get("history", []),
        "count":      len(data.get("history", [])),
    }