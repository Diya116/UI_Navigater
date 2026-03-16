import base64


# webm/opus at 16kHz mono encodes at roughly 6-8 KB per second
# 6 seconds of speech ≈ 36-48 KB raw, ≈ 48-64 KB as base64
_BYTES_PER_SECOND = 8000
_MIN_SPEECH_BYTES = 800    # less than this = silence or noise only


def validate_audio(b64: str, max_seconds: int = 8) -> bool:
    """
    Return True if audio is present and within allowed duration.
    Does not decode audio — estimates from base64 string length.
    """
    if not b64:
        return False
    try:
        raw_bytes = len(base64.b64decode(b64))
        max_bytes = max_seconds * _BYTES_PER_SECOND
        return _MIN_SPEECH_BYTES <= raw_bytes <= max_bytes
    except Exception:
        return False


def is_empty_audio(b64: str) -> bool:
    """
    Return True if audio buffer is too small to contain real speech.
    Used to decide whether to run STT or use text query fallback.
    """
    if not b64:
        return True
    try:
        raw_bytes = len(base64.b64decode(b64))
        return raw_bytes < _MIN_SPEECH_BYTES
    except Exception:
        return True


def get_audio_duration_estimate(b64: str) -> float:
    """
    Estimate audio duration in seconds from base64 buffer size.
    Used for logging and analytics only — not for billing.
    """
    if not b64:
        return 0.0
    try:
        raw_bytes = len(base64.b64decode(b64))
        return raw_bytes / _BYTES_PER_SECOND
    except Exception:
        return 0.0