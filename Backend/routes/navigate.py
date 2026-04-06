import asyncio, base64, json
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from models.request import NavigateRequest
from services import vision, voice, classifier, session as sess
from services.language import get_fallback
from utils.image import compress

router = APIRouter()

@router.post("/navigate/stream")
async def navigate(body: NavigateRequest):
    return StreamingResponse(
        _stream(body),
        media_type="text/event-stream",
        headers={
            "Cache-Control":     "no-cache",
            "Connection":        "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )

async def _stream(body: NavigateRequest):

    lang = body.lang_hint

    def sse(event: str, data: dict) -> str:
        return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"

    try:
        # Compress screenshot
        screenshot = compress(body.screenshot)

        # Phase 1: STT + session load in parallel
        stt_task  = asyncio.create_task(_stt(body))
        sess_task = asyncio.create_task(sess.get(body.session_id))
        stt_result, session = await asyncio.gather(stt_task, sess_task)

        transcript = stt_result.get("transcript", "")
        lang       = stt_result.get("detected_lang", body.lang_hint)
        query      = transcript or body.query or ""

        if not query:
            yield sse("error", _err_payload(lang, "NO_AUDIO"))
            yield sse("done", {})
            return

        # Use established preferred language from session
        if session:
            lang = session.get("preferred_lang") or lang

        yield sse("transcript", {"text": transcript, "lang": lang})

        # Classify: simple vs complex
        task_type = await classifier.classify(screenshot, query)

        # Phase 2: Gemini vision analysis
        history      = (session or {}).get("history", [])
        dom_snapshot = body.dom_snapshot.model_dump() if body.dom_snapshot else {}

        analysis = await vision.analyze(
            screenshot_b64=screenshot,
            query=query,
            url=body.url,
            lang=lang,
            history=history,
            dom_snapshot=dom_snapshot,
            task_type=task_type,
        )

        lang = analysis.language or lang

        # Send action immediately — extension executes while TTS generates
        if analysis.action.type not in ("none", "done", "stuck"):
            yield sse("action", {"action": analysis.action.model_dump()})

        # Phase 3: TTS + session save in parallel
        tts_task  = asyncio.create_task(
            voice.synthesize(
                text=analysis.speech_response,
                lang=lang,
                gender=body.voice_gender,
                rate=body.speech_rate,
            )
        )
        save_task = asyncio.create_task(
            sess.append_turn(
                sid=body.session_id,
                user_text=query,
                model_text=analysis.speech_response,
                detected_lang=lang,
            )
        )

        audio_bytes, _ = await asyncio.gather(tts_task, save_task)

        yield sse("response", {
            "text":        analysis.speech_response,
            "audio":       base64.b64encode(audio_bytes).decode(),
            "lang":        lang,
            "confidence":  analysis.confidence,
            "screen_desc": analysis.screen_description,
        })

        yield sse("done", {})

    except asyncio.TimeoutError:
        payload = _err_payload(lang, "TIMEOUT")
        yield sse("error", await _with_audio(payload, lang))
        yield sse("done", {})

    except Exception:
        import traceback; traceback.print_exc()
        payload = _err_payload(lang, "DEFAULT")
        yield sse("error", await _with_audio(payload, lang))
        yield sse("done", {})


async def _stt(body: NavigateRequest) -> dict:
    if body.audio_buffer:
        return await voice.transcribe(body.audio_buffer, body.lang_hint)
    return {"transcript": body.query or "", "detected_lang": body.lang_hint}


def _err_payload(lang: str, code: str = "DEFAULT") -> dict:
    MESSAGES = {
        "NO_AUDIO": {
            "en": "I couldn't hear anything. Please speak clearly.",
            "hi": "मुझे कुछ सुनाई नहीं दिया। स्पष्ट बोलें।",
            "gu": "મને કંઈ સંભળાયું નહીં. સ્પષ્ટ બોલો.",
            "ta": "எனக்கு எதுவும் கேட்கவில்லை. தெளிவாக பேசுங்கள்.",
        },
        "TIMEOUT": {
            "en": "Taking too long. Please try again.",
            "hi": "बहुत समय लग रहा है। दोबारा कोशिश करें।",
            "gu": "ઘણો સમય લાગી રહ્યો છે. ફરી પ્રયાસ કરો.",
        },
    }
    msgs = MESSAGES.get(code, {})
    text = msgs.get(lang) or msgs.get("en") or get_fallback(lang)
    return {"text": text, "audio": None}


async def _with_audio(payload: dict, lang: str) -> dict:
    try:
        audio = await voice.synthesize(payload["text"], lang)
        payload["audio"] = base64.b64encode(audio).decode()
    except Exception:
        pass
    return payload