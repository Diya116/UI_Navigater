from pydantic import BaseModel
from typing import Optional, List
from enum import Enum

class ActionType(str, Enum):
    CLICK    = "click"
    FILL     = "fill"
    SCROLL   = "scroll"
    NAVIGATE = "navigate"
    SELECT   = "select"
    CHECK    = "check"
    FOCUS    = "focus"
    KEY      = "key"
    NONE     = "none"
    DONE     = "done"
    STUCK    = "stuck"

class ActionTarget(BaseModel):
    id:         Optional[str]   = None  # element id
    selector:   Optional[str]   = None  # css selector
    testid:     Optional[str]   = None  # data-testid
    aria_label: Optional[str]   = None
    text:       Optional[str]   = None  # visible text
    rect: Optional[dict]        = None  # {x,y,w,h} from getBoundingClientRect

class FormField(BaseModel):
    id:         Optional[str]  = None
    selector:   Optional[str]  = None
    text:       Optional[str]  = None
    rect:       Optional[dict] = None
    value:      str
    field_type: Optional[str]  = None

class Action(BaseModel):
    type:         ActionType
    # targeting — executor tries these in order
    id:           Optional[str]        = None
    selector:     Optional[str]        = None
    testid:       Optional[str]        = None
    aria_label:   Optional[str]        = None
    text:         Optional[str]        = None
    rect:         Optional[dict]       = None
    # action-specific
    value:        Optional[str]        = None
    direction:    Optional[str]        = None
    url:          Optional[str]        = None
    key:          Optional[str]        = None
    fields:       List[FormField]      = []
    submit_after: bool                 = False
    checked:      Optional[bool]       = None

class GeminiAnalysis(BaseModel):
    screen_description: str
    user_intent:        str
    speech_response:    str
    action:             Action
    language:           str
    confidence:         float