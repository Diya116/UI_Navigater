import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig
from core.config import get_settings

settings = get_settings()

vertexai.init(
    project=settings.gcp_project_id,
    location=settings.gcp_region,
)

# Pro — complex multi-step tasks, high accuracy needed
gemini_pro = GenerativeModel(
    model_name=settings.gemini_model_pro,
    generation_config=GenerationConfig(
        response_mime_type="application/json",
        temperature=0.1,
        max_output_tokens=1024,
    ),
)

# Flash — simple actions, 15x cheaper, fast
gemini_flash = GenerativeModel(
    model_name=settings.gemini_model_flash,
    generation_config=GenerationConfig(
        response_mime_type="application/json",
        temperature=0.1,
        max_output_tokens=1024,
    ),
)

# Classifier — ultra cheap, 20 tokens max
gemini_classifier = GenerativeModel(
    model_name=settings.gemini_model_flash,
    generation_config=GenerationConfig(
        response_mime_type="application/json",
        temperature=0.0,
        max_output_tokens=20,
    ),
)