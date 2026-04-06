from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    gcp_project_id:                  str
    gcp_region:                      str   = "asia-southeast1"
    vertex_region:                   str   = "asia-southeast1"
    gemini_model_pro:                str   = "gemini-1.5-pro"
    gemini_model_flash:              str   = "gemini-1.5-flash"
    firebase_project_id:             str
    rate_limit_rpm:                  int   = 30
    max_screenshot_kb:               int   = 300
    max_audio_sec:                   int   = 8
    environment:                     str   = "development"
    google_application_credentials:  str   = ""

    class Config:
        env_file = ".env"
        extra   = "ignore"          # ← ignore any extra .env variables


@lru_cache()
def get_settings() -> Settings:
    return Settings()