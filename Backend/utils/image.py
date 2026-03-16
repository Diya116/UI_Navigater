import base64
import io
from PIL import Image

MAX_WIDTH    = 1280    # pixels — Gemini doesn't need more resolution
JPEG_QUALITY = 80      # good balance: quality vs file size
MAX_SIZE_KB  = 300     # reject screenshots larger than this after decode


def compress(b64: str) -> str:
    """
    Resize screenshot to max 1280px wide and re-encode as JPEG 80%.

    Why this matters:
      Before: 600KB PNG  → expensive to upload, slow Gemini processing
      After:   85KB JPEG → 7× faster upload, lower token cost

    Args:
        b64: base64-encoded PNG or JPEG (data URL prefix optional)

    Returns:
        base64-encoded JPEG string (no data URL prefix)
    """
    # Strip data URL prefix if present (e.g. "data:image/png;base64,...")
    if "," in b64:
        b64 = b64.split(",")[1]

    raw = base64.b64decode(b64)
    img = Image.open(io.BytesIO(raw)).convert("RGB")

    # Resize if wider than max — maintain aspect ratio
    if img.width > MAX_WIDTH:
        ratio  = MAX_WIDTH / img.width
        height = int(img.height * ratio)
        img    = img.resize((MAX_WIDTH, height), Image.LANCZOS)

    # Re-encode as JPEG
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=JPEG_QUALITY, optimize=True)
    compressed_bytes = buf.getvalue()

    return base64.b64encode(compressed_bytes).decode("utf-8")


def validate_size(b64: str, max_kb: int = MAX_SIZE_KB) -> bool:
    """
    Return True if raw decoded size is within allowed limit.
    Called before compression to reject absurdly large inputs.
    """
    try:
        # Strip prefix if present
        raw_b64 = b64.split(",")[-1]
        raw_bytes = len(base64.b64decode(raw_b64))
        return (raw_bytes / 1024) <= max_kb
    except Exception:
        return False


def get_dimensions(b64: str) -> tuple[int, int]:
    """
    Return (width, height) of a base64-encoded image.
    Used for logging and analytics.
    """
    try:
        if "," in b64:
            b64 = b64.split(",")[1]
        raw = base64.b64decode(b64)
        img = Image.open(io.BytesIO(raw))
        return img.width, img.height
    except Exception:
        return 0, 0