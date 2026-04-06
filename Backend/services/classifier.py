import json, re, base64, logging
from vertexai.generative_models import Part, Content
from core.vertex import gemini_classifier

logger = logging.getLogger(__name__)

PROMPT = """You are a classifier. Screenshot + user query provided.
Classify as simple or complex.

simple = one action: click, fill one field, scroll, describe screen
complex = multi-step goal: fill entire form, complete purchase, search then navigate

Reply ONLY with valid JSON: {"type":"simple"} or {"type":"complex"}
No markdown, no explanation, just the JSON."""

async def classify(screenshot_b64: str, query: str) -> str:
    try:
        img         = Part.from_data(data=base64.b64decode(screenshot_b64), mime_type="image/jpeg")
        prompt_part = Part.from_text(PROMPT)
        query_part  = Part.from_text(f'Query: "{query}"')

        result = await gemini_classifier.generate_content_async(
            [prompt_part, img, query_part]  # pass list directly, not wrapped in Content
        )

        # Guard: check candidates exist
        if not result.candidates:
            logger.warning("Classifier: no candidates returned (blocked?), defaulting to simple")
            return "simple"

        # Guard: check parts exist
        parts = result.candidates[0].content.parts
        if not parts:
            logger.warning("Classifier: empty parts in response, defaulting to simple")
            return "simple"

        raw = parts[0].text.strip()

        # Strip markdown fences if model ignores instructions
        raw = re.sub(r"```json|```", "", raw).strip()

        return json.loads(raw).get("type", "simple")

    except json.JSONDecodeError as e:
        logger.warning("Classifier returned non-JSON (%s), defaulting to simple", e)
        return "simple"
    except Exception as e:
        logger.warning("Classifier failed (%s), defaulting to simple", e)
        return "simple"