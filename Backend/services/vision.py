import json, re, base64, logging
from vertexai.generative_models import Part, Content
from core.vertex import gemini_pro, gemini_flash
from models.action import GeminiAnalysis

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an AI accessibility assistant helping blind users navigate websites by voice.
You receive a screenshot, a DOM snapshot of interactive elements, and the user's query.

Respond ONLY in this exact JSON — no markdown, no text outside JSON:

{
  "screen_description": "one sentence: what page is this",
  "user_intent": "what the user wants to do",
  "speech_response": "what to speak back — max 2 sentences — IN USER'S LANGUAGE",
  "action": {
    "type": "click|fill|scroll|navigate|select|check|focus|key|none",
    "id": "element id from DOM snapshot if available",
    "selector": "css selector if clearly available in DOM snapshot",
    "testid": "data-testid if available",
    "aria_label": "aria-label if available",
    "text": "visible text of target element",
    "rect": {"x":0,"y":0,"w":0,"h":0},
    "value": "for fill/select",
    "direction": "for scroll: up|down|top|bottom",
    "url": "for navigate",
    "key": "for key: Enter|Tab|Escape etc",
    "fields": [],
    "submit_after": false
  },
  "language": "ISO 639-1 code of language user spoke",
  "confidence": 0.0
}

RULES:
1. speech_response MUST be in the SAME language as the user's query.
2. For action targeting priority: id > selector > testid > aria_label > text > rect.
3. confidence < 0.75 → set action.type = "none", ask clarifying question in user's language.
4. Be natural in speech_response. Say "Clicking login" not "Executing click action".
5. For forms — name all visible fields before asking what to fill.
6. Cross-reference screenshot + DOM snapshot for best accuracy."""


def _format_dom(snapshot: dict) -> str:
    if not snapshot:
        return "No DOM snapshot available."
    lines = [f"Page: {snapshot.get('title', '')}"]
    lines.append(f"Scroll: {snapshot.get('scrollY', 0):.0f}px")
    lines.append("\nInteractive elements:")
    for el in snapshot.get("elements", []):
        parts = [f"[{el['i']}]", el["tag"]]
        if el.get("id"):     parts.append(f"id={el['id']}")
        if el.get("testid"): parts.append(f"testid={el['testid']}")
        if el.get("text"):   parts.append(f'"{el["text"]}"')
        if el.get("rect"):
            r = el["rect"]
            parts.append(f"at({r['x']},{r['y']} {r['w']}x{r['h']})")
        lines.append("  " + " ".join(str(p) for p in parts))
    lines.append("\nLandmarks:")
    for lm in snapshot.get("landmarks", []):
        lines.append(f"  {lm.get('tag', '')} {lm.get('text', '')[:50]}")
    lines.append(f"\nVisible text: {snapshot.get('pageText', '')[:300]}")
    return "\n".join(lines)


def _safe_json(raw: str) -> dict:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        cleaned = re.sub(r"```json\s*|\s*```", "", raw).strip()
        return json.loads(cleaned)


async def analyze(
    screenshot_b64: str,
    query:          str,
    url:            str,
    lang:           str,
    history:        list,
    dom_snapshot:   dict,
    task_type:      str = "simple",
) -> GeminiAnalysis:

    model = gemini_pro if task_type == "complex" else gemini_flash

    contents = []

    # Inject system prompt as first user turn
    contents.append(Content(
        role="user",
        parts=[Part.from_text(SYSTEM_PROMPT)]
    ))
    contents.append(Content(
        role="model",
        parts=[Part.from_text("Understood. I will respond only in the specified JSON format.")]
    ))

    # Conversation history
    for turn in history[-6:]:
        contents.append(Content(
            role=turn["role"],
            parts=[Part.from_text(turn["text"])]
        ))

    # Current turn: screenshot + DOM + query
    img_part  = Part.from_data(
        data=base64.b64decode(screenshot_b64),
        mime_type="image/jpeg",
    )
    text_part = Part.from_text(
        f"URL: {url}\n"
        f"Language: {lang}\n"
        f"User said: \"{query}\"\n\n"
        f"DOM SNAPSHOT:\n{_format_dom(dom_snapshot)}"
    )

    contents.append(Content(role="user", parts=[img_part, text_part]))

    try:
        result = await model.generate_content_async(contents=contents)
        raw    = result.candidates[0].content.parts[0].text
        data   = _safe_json(raw)
        return GeminiAnalysis(**data)
    except Exception as e:
        logger.error("Vision analysis failed: %s", e)
        # Return a safe fallback so the stream doesn't crash
        return GeminiAnalysis(
            screen_description="Unable to analyze screen",
            user_intent=query,
            speech_response="Sorry, I had trouble understanding the screen. Please try again.",
            action={"type": "none"},
            language=lang,
            confidence=0.0,
        )