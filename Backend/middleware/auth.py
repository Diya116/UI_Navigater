from fastapi import Request, HTTPException
from core.firebase import firebase_auth


async def verify_token(request: Request) -> str:
    """
    Verify Firebase ID token from Authorization header.
    Returns uid on success, raises 401 on failure.

    Chrome extension users: anonymous Firebase tokens (auto-generated)
    SDK users: full Firebase Auth tokens
    """
    auth_header = request.headers.get("Authorization", "")

    if not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Missing or invalid Authorization header"
        )

    token = auth_header.replace("Bearer ", "").strip()

    try:
        decoded = firebase_auth.verify_id_token(token)
        return decoded["uid"]
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid Firebase token: {str(e)}"
        )