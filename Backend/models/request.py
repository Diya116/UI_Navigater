from pydantic import BaseModel, Field
from typing import Optional

class Viewport(BaseModel):
    w:   int
    h:   int
    dpr: float = 1.0
    scrollY: float = 0.0
    scrollX: float = 0.0

class DOMElement(BaseModel):
    i:       int
    tag:     str
    type:    Optional[str]  = None
    id:      Optional[str]  = None
    name:    Optional[str]  = None
    cls:     Optional[str]  = None
    text:    Optional[str]  = None
    role:    Optional[str]  = None
    href:    Optional[str]  = None
    testid:  Optional[str]  = None
    value:   Optional[str]  = None
    checked: Optional[bool] = None
    rect:    Optional[dict] = None

class DOMSnapshot(BaseModel):
    title:    str
    url:      str
    focused:  Optional[dict]       = None
    elements: list[DOMElement]     = []
    landmarks: list[dict]          = []
    pageText: str                  = ""
    scrollY:  float                = 0.0
    viewport: Optional[Viewport]   = None

class NavigateRequest(BaseModel):
    screenshot:   str
    audio_buffer: Optional[str]     = None
    query:        Optional[str]     = None
    url:          str
    dom_snapshot: Optional[DOMSnapshot] = None
    session_id:   str
    lang_hint:    str               = "en"
    speech_rate:  float             = Field(default=1.0, ge=0.5, le=2.0)
    voice_gender: str               = "FEMALE"