import asyncio, base64, logging
from google.api_core.exceptions import ServiceUnavailable, DeadlineExceeded, InvalidArgument
from google.cloud import speech_v2, texttospeech
from services.language import get_voice, lang_to_bcp47
from core.config import get_settings

logger   = logging.getLogger(__name__)
settings = get_settings()

# Languages verified to work with model="long" at location="global"
_SUPPORTED_LANGS = {
    "en-US", "hi-IN", "gu-IN", "ta-IN",
    "te-IN", "mr-IN", "kn-IN", "ml-IN",
}

_RETRYABLE      = (ServiceUnavailable, DeadlineExceeded, ConnectionResetError)
_MAX_RETRIES    = 3
_BASE_BACKOFF   = 1.0


def _make_stt_client():
    return speech_v2.SpeechAsyncClient()

def _make_tts_client():
    return texttospeech.TextToSpeechAsyncClient()

_stt_client = _make_stt_client()
_tts_client = _make_tts_client()


async def transcribe(audio_b64: str, lang_hint: str = "en") -> dict:
    global _stt_client

    audio_bytes = base64.b64decode(audio_b64)

    if len(audio_bytes) < 100:
        logger.warning("Audio too small (%d bytes), skipping STT", len(audio_bytes))
        return {"transcript": "", "detected_lang": lang_hint, "confidence": 0.0}

    primary = lang_to_bcp47(lang_hint)

    # Fall back to en-US if primary language not supported by "long" model
    if primary not in _SUPPORTED_LANGS:
        logger.warning("Language %s not supported by long model, falling back to en-US", primary)
        primary = "en-US"

    # Build alternatives: other supported langs excluding primary, max 2
    alternatives = [l for l in _SUPPORTED_LANGS if l != primary][:2]
    language_codes = [primary] + alternatives

    request = speech_v2.RecognizeRequest(
        recognizer=(
            f"projects/{settings.gcp_project_id}"
            "/locations/global/recognizers/_"
        ),
        config=speech_v2.RecognitionConfig(
            auto_decoding_config=speech_v2.AutoDetectDecodingConfig(),
            language_codes=language_codes,
            model="long",
        ),
        content=audio_bytes,
    )

    last_exc = None
    for attempt in range(1, _MAX_RETRIES + 1):
        try:
            response = await _stt_client.recognize(request=request)
            break
        except _RETRYABLE as exc:
            last_exc = exc
            logger.warning("STT attempt %d/%d failed (%s)", attempt, _MAX_RETRIES, exc)
            if attempt == _MAX_RETRIES:
                logger.warning("Reinitialising STT client after repeated failures")
                _stt_client = _make_stt_client()
                raise
            await asyncio.sleep(_BASE_BACKOFF * (2 ** (attempt - 1)))
        except InvalidArgument as exc:
            # Config error — no point retrying
            logger.error("STT config error (will not retry): %s", exc)
            raise

    if not response.results:
        return {"transcript": "", "detected_lang": lang_hint, "confidence": 0.0}

    best   = response.results[0].alternatives[0]
    lang   = (response.results[0].language_code or primary).split("-")[0].lower()

    return {
        "transcript":    best.transcript,
        "detected_lang": lang,
        "confidence":    getattr(best, "confidence", 0.0),
    }


async def synthesize(
    text:   str,
    lang:   str   = "en",
    gender: str   = "FEMALE",
    rate:   float = 1.0,
) -> bytes:
    global _tts_client

    lang_code, voice_name = get_voice(lang, gender)

    ssml = (
        f'<speak><prosody rate="{_rate(rate)}">'
        f'{_esc(text)}'
        f'</prosody></speak>'
    )

    for attempt in range(1, _MAX_RETRIES + 1):
        try:
            response = await _tts_client.synthesize_speech(
                request=texttospeech.SynthesizeSpeechRequest(
                    input=texttospeech.SynthesisInput(ssml=ssml),
                    voice=texttospeech.VoiceSelectionParams(
                        language_code=lang_code,
                        name=voice_name,
                        ssml_gender=(
                            texttospeech.SsmlVoiceGender.FEMALE
                            if gender.upper() == "FEMALE"
                            else texttospeech.SsmlVoiceGender.MALE
                        ),
                    ),
                    audio_config=texttospeech.AudioConfig(
                        audio_encoding=texttospeech.AudioEncoding.MP3,
                        volume_gain_db=2.0,
                        speaking_rate=rate,
                    ),
                )
            )
            return response.audio_content
        except _RETRYABLE as exc:
            logger.warning("TTS attempt %d/%d failed (%s)", attempt, _MAX_RETRIES, exc)
            if attempt == _MAX_RETRIES:
                _tts_client = _make_tts_client()
                raise
            await asyncio.sleep(_BASE_BACKOFF * (2 ** (attempt - 1)))


def _rate(r: float) -> str:
    if r <= 0.7: return "slow"
    if r <= 1.2: return "medium"
    if r <= 1.6: return "fast"
    return "x-fast"

def _esc(t: str) -> str:
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")