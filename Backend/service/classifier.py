import json
from vertexai.generative_models import Part
from core.vertex import gemini_classifier
import base64

PROMPT = """
Screenshot + user query provided.
Classify as simple or complex.

simple = one action: click, fill one field, scroll, describe screen
complex = multi-step goal: fill entire form, complete purchase, search then navigate

Reply ONLY: {"type":"simple"} or {"type":"complex"}
"""

async def classify(screenshot_b64: str, query: str) -> str:
    img = Part.from_data(
        data=base64.b64decode(screenshot_b64),
        mime_type="image/jpeg"
    )
    result = await gemini_classifier.generate_content_async(
        contents=[{"role":"user","parts":[img, f'Query: "{query}"']}],
        system_instruction=PROMPT,
    )
    raw = result.candidates[0].content.parts[0].text
    return json.loads(raw.strip()).get("type", "simple")