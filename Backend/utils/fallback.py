from services.language import (
    get_fallback,
    get_no_audio_msg,
    get_timeout_msg,
)

# ── Per-error-code messages in supported languages ─────────

_RATE_LIMIT_MSGS = {
    "en": "Too many requests. Please slow down and try again.",
    "hi": "बहुत अधिक अनुरोध। कृपया थोड़ा रुककर दोबारा कोशिश करें।",
    "gu": "ઘણી બધી વિનંતીઓ. કૃપા કરીને થોડી રાહ જોઈને ફરી પ્રયાસ કરો.",
    "ta": "அதிகமான கோரிக்கைகள். கொஞ்சம் காத்து மீண்டும் முயற்சிக்கவும்.",
    "te": "చాలా అభ్యర్థనలు. దయచేసి కొంచెం ఆగి మళ్ళీ ప్రయత్నించండి.",
    "bn": "অনেক বেশি অনুরোধ। একটু অপেক্ষা করুন এবং আবার চেষ্টা করুন।",
}

_QUOTA_MSGS = {
    "en": "Daily limit reached. Please try again tomorrow.",
    "hi": "आज की सीमा समाप्त हो गई। कल पुनः प्रयास करें।",
    "gu": "આજની મર્યાદા પૂરી થઈ ગઈ. કાલે ફરી પ્રયાસ કરો.",
    "ta": "இன்றைய வரம்பு முடிந்தது. நாளை மீண்டும் முயற்சிக்கவும்.",
    "te": "ఈరోజు పరిమితి అయిపోయింది. రేపు మళ్ళీ ప్రయత్నించండి.",
    "bn": "আজকের সীমা শেষ হয়েছে। আগামীকাল আবার চেষ্টা করুন।",
}

_SCREENSHOT_MSGS = {
    "en": "I couldn't capture the screen. Please try pressing Alt+N again.",
    "hi": "स्क्रीन कैप्चर नहीं हो सकी। Alt+N दोबारा दबाएँ।",
    "gu": "સ્ક્રીન કૅપ્ચર થઈ શકી નહીં. Alt+N ફરી દબાવો.",
    "ta": "திரையை படம் எடுக்க முடியவில்லை. Alt+N மீண்டும் அழுத்தவும்.",
    "te": "స్క్రీన్ క్యాప్చర్ అవ్వలేదు. Alt+N మళ్ళీ నొక్కండి.",
}

_LOW_CONFIDENCE_MSGS = {
    "en": "I'm not sure what to do. Could you describe what you want more clearly?",
    "hi": "मुझे समझ नहीं आया। क्या आप थोड़ा स्पष्ट बता सकते हैं?",
    "gu": "મને સ્પષ્ટ ન થયું. શું તમે વધુ સ્પષ્ટ રીતે કહી શકો?",
    "ta": "என்ன செய்வது என்று தெரியவில்லை. தெளிவாக சொல்ல முடியுமா?",
    "te": "ఏం చేయాలో అర్థం కాలేదు. మరింత స్పష్టంగా చెప్పగలరా?",
}

# ── Map error codes to message dicts ───────────────────────

_MESSAGE_MAP: dict[str, dict[str, str]] = {
    "NO_AUDIO":       {
        "en": "I couldn't hear anything. Please speak clearly and try again.",
        "hi": "मुझे कुछ सुनाई नहीं दिया। स्पष्ट बोलकर दोबारा कोशिश करें।",
        "gu": "મને કંઈ સંભળાયું નહીં. સ્પષ્ટ બોલીને ફરી પ્રયાસ કરો.",
        "ta": "எனக்கு எதுவும் கேட்கவில்லை. தெளிவாக பேசி மீண்டும் முயற்சிக்கவும்.",
        "te": "నాకు ఏమీ వినిపించలేదు. స్పష్టంగా మాట్లాడి మళ్ళీ ప్రయత్నించండి.",
    },
    "TIMEOUT":        {
        "en": "Taking too long. Please try again.",
        "hi": "बहुत समय लग रहा है। दोबारा कोशिश करें।",
        "gu": "ઘણો સમય લાગી રહ્યો છે. ફરી પ્રયાસ કરો.",
        "ta": "அதிக நேரம் ஆகிறது. மீண்டும் முயற்சிக்கவும்.",
        "te": "చాలా సేపు పడుతోంది. మళ్ళీ ప్రయత్నించండి.",
    },
    "RATE_LIMIT":     _RATE_LIMIT_MSGS,
    "QUOTA_EXCEEDED": _QUOTA_MSGS,
    "SCREENSHOT":     _SCREENSHOT_MSGS,
    "LOW_CONFIDENCE": _LOW_CONFIDENCE_MSGS,
    "DEFAULT":        {},   # falls through to get_fallback()
}


def build_error_payload(lang: str, error_code: str = "DEFAULT") -> dict:
    """
    Build SSE error payload with message in user's language.
    The audio field is None — the caller synthesises TTS if needed.

    Args:
        lang:       ISO 639-1 language code (e.g. 'gu', 'hi', 'en')
        error_code: one of NO_AUDIO | TIMEOUT | RATE_LIMIT |
                    QUOTA_EXCEEDED | SCREENSHOT | LOW_CONFIDENCE | DEFAULT

    Returns:
        {"text": "<localised message>", "audio": None}
    """
    messages = _MESSAGE_MAP.get(error_code, {})
    text = (
        messages.get(lang)
        or messages.get("en")
        or get_fallback(lang)
    )
    return {"text": text, "audio": None}