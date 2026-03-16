from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request
import json


def get_rate_limit_key(request: Request) -> str:
    """
    Rate limit key resolution order:
      1. X-Session-Id header (SDK clients send this)
      2. Remote IP address (fallback for extension clients)
    """
    header_session = request.headers.get("X-Session-Id")
    if header_session:
        return header_session
    return get_remote_address(request)


# Global limiter instance — imported by main.py and routes
limiter = Limiter(key_func=get_rate_limit_key)