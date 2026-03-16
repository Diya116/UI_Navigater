from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    gcp_project_id:      str
    gcp_region:          str  = "us-central1"
    gemini_model_pro:    str  = "gemini-1.5-pro"
    gemini_model_flash:  str  = "gemini-1.5-flash"
    firebase_project_id: str
    rate_limit_rpm:      int  = 30
    max_screenshot_kb:   int  = 300
    environment:         str  = "production"

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()