from typing import Any

from typing_extensions import TypedDict


class VercelAuthData(TypedDict, total=False):
    token: str


class VercelRequestData(TypedDict, total=False):
    method: str
    path: str
    url: str
    headers: dict[str, str]
    params: dict[str, Any]
    timeout_seconds: float
    follow_redirects: bool
    max_response_chars: int


class VercelResponseData(TypedDict, total=False):
    request: VercelRequestData
    response: dict[str, Any]
