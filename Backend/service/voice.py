import asyncio, base64
from google.cloud import speech_v2, texttospeech
from services.language import STT_ALTERNATIVES, get_voice, lang_to_bcp47
from core.config import get_settings

settings    = get_settings()
_stt_client = speech_v2.SpeechAsyncClient()
_tts_client = texttospeech.TextToSpeechAsyncClient()

async def transcribe(audio_b64: str, lang_hint: str = "en") -> dict:
    audio_bytes = base64.b64decode(audio_b64)
    primary     = lang_to_bcp47(lang_hint)

    request = speech_v2.RecognizeRequest(
        recognizer=(
            f"projects/{settings.gcp_project_id}"
            "/locations/global/recognizers/_"
        ),
        config=speech_v2.RecognitionConfig(
            auto_decoding_config=speech_v2.AutoDetectDecodingConfig(),
            language_codes=[primary] + STT_ALTERNATIVES,
            model="chirp",
            features=speech_v2.RecognitionFeatures(
                enable_automatic_punctuation=True,
            ),
        ),
        content=audio_bytes,
    )

    response = await _stt_client.recognize(request=request)

    if not response.results:
        return {"transcript": "", "detected_lang": lang_hint}

    best = response.results[0].alternatives[0]
    lang = (response.results[0].language_code or primary).split("-")[0].lower()

    return {
        "transcript":    best.transcript,
        "detected_lang": lang,
        "confidence":    best.confidence,
    }


async def synthesize(
    text: str,
    lang: str     = "en",
    gender: str   = "FEMALE",
    rate: float   = 1.0,
) -> bytes:
    lang_code, voice_name = get_voice(lang, gender)

    ssml = (
        f'<speak><prosody rate="{_rate(rate)}">'
        f'{_esc(text)}'
        f'</prosody></speak>'
    )

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

def _rate(r):
    if r <= 0.7: return "slow"
    if r <= 1.2: return "medium"
    if r <= 1.6: return "fast"
    return "x-fast"

def _esc(t):
    return t.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")