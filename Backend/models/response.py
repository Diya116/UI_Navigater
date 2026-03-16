from pydantic import BaseModel
from typing import Optional
from models.action import Action


class TranscriptEvent(BaseModel):
    text: str
    lang: str


class ActionEvent(BaseModel):
    action: Action


class ResponseEvent(BaseModel):
    text:        str
    audio:       Optional[str] = None   # base64 MP3
    lang:        str
    confidence:  float
    screen_desc: str


class ErrorEvent(BaseModel):
    text:  str
    audio: Optional[str] = None         # base64 MP3


class SessionResponse(BaseModel):
    session_id:    str
    preferred_lang: Optional[str] = None
    history_count: int