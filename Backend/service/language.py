VOICE_MAP = {
    "en": {"code": "en-US", "f": "en-US-Neural2-F",  "m": "en-US-Neural2-D"},
    "hi": {"code": "hi-IN", "f": "hi-IN-Wavenet-A",  "m": "hi-IN-Wavenet-B"},
    "gu": {"code": "gu-IN", "f": "gu-IN-Wavenet-A",  "m": "gu-IN-Wavenet-B"},
    "ta": {"code": "ta-IN", "f": "ta-IN-Wavenet-A",  "m": "ta-IN-Wavenet-B"},
    "te": {"code": "te-IN", "f": "te-IN-Standard-A", "m": "te-IN-Standard-B"},
    "bn": {"code": "bn-IN", "f": "bn-IN-Wavenet-A",  "m": "bn-IN-Wavenet-B"},
    "mr": {"code": "mr-IN", "f": "mr-IN-Wavenet-A",  "m": "mr-IN-Wavenet-B"},
    "kn": {"code": "kn-IN", "f": "kn-IN-Wavenet-A",  "m": "kn-IN-Wavenet-B"},
    "ml": {"code": "ml-IN", "f": "ml-IN-Wavenet-A",  "m": "ml-IN-Wavenet-B"},
    "pa": {"code": "pa-IN", "f": "pa-IN-Wavenet-A",  "m": "pa-IN-Wavenet-B"},
    "ar": {"code": "ar-XA", "f": "ar-XA-Wavenet-A",  "m": "ar-XA-Wavenet-B"},
    "es": {"code": "es-ES", "f": "es-ES-Neural2-A",  "m": "es-ES-Neural2-B"},
    "fr": {"code": "fr-FR", "f": "fr-FR-Neural2-A",  "m": "fr-FR-Neural2-B"},
    "de": {"code": "de-DE", "f": "de-DE-Neural2-A",  "m": "de-DE-Neural2-B"},
    "pt": {"code": "pt-BR", "f": "pt-BR-Neural2-A",  "m": "pt-BR-Neural2-B"},
    "zh": {"code": "zh-CN", "f": "cmn-CN-Wavenet-A", "m": "cmn-CN-Wavenet-B"},
    "ja": {"code": "ja-JP", "f": "ja-JP-Neural2-B",  "m": "ja-JP-Neural2-C"},
}

STT_ALTERNATIVES = [
    "hi-IN","gu-IN","ta-IN","te-IN","bn-IN",
    "mr-IN","kn-IN","ml-IN","en-US","ar-XA",
]

FALLBACKS = {
    "en": "Something went wrong. Please try again.",
    "hi": "कुछ गलत हो गया। कृपया दोबारा कोशिश करें।",
    "gu": "કંઈક ખોટું થઈ ગયું. ફરી પ્રયાસ કરો.",
    "ta": "ஏதோ தவறாகிவிட்டது. மீண்டும் முயற்சிக்கவும்.",
    "te": "ఏదో తప్పు జరిగింది. మళ్ళీ ప్రయత్నించండి.",
    "bn": "কিছু ভুল হয়েছে। আবার চেষ্টা করুন।",
    "mr": "काहीतरी चुकले. पुन्हा प्रयत्न करा.",
    "kn": "ಏನೋ ತಪ್ಪಾಗಿದೆ. ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ.",
    "ml": "എന്തോ തെറ്റ് സംഭവിച്ചു. വീണ്ടും ശ്രമിക്കുക.",
    "pa": "ਕੁਝ ਗਲਤ ਹੋ ਗਿਆ। ਦੁਬਾਰਾ ਕੋਸ਼ਿਸ਼ ਕਰੋ।",
    "ar": "حدث خطأ ما. يرجى المحاولة مرة أخرى.",
    "es": "Algo salió mal. Inténtalo de nuevo.",
    "fr": "Quelque chose s'est mal passé. Réessayez.",
}

def get_voice(lang: str, gender: str = "FEMALE") -> tuple[str, str]:
    v = VOICE_MAP.get(lang, VOICE_MAP["en"])
    return v["code"], v["f"] if gender.upper() == "FEMALE" else v["m"]

def get_fallback(lang: str) -> str:
    return FALLBACKS.get(lang, FALLBACKS["en"])

def lang_to_bcp47(lang: str) -> str:
    v = VOICE_MAP.get(lang, VOICE_MAP["en"])
    return v["code"]