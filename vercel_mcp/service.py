import base64
from typing import Any

import httpx

from .config import (
    ALLOWED_HTTP_METHODS,
    DEFAULT_TIMEOUT_SECONDS,
    MAX_RESPONSE_BODY_CHARS,
    VERCEL_API_BASE_URL,
)
from .schemas import VercelResponseData


def _serialize_headers(headers: dict[str, Any] | None) -> dict[str, str]:
    if not headers:
        return {}
    return {str(key): str(value) for key, value in headers.items()}


def _serialize_text_body(content: str, max_response_chars: int) -> dict[str, Any]:
    is_truncated = len(content) > max_response_chars
    body = content[:max_response_chars] if is_truncated else content
    payload: dict[str, Any] = {
        "kind": "text",
        "content": body,
        "truncated": is_truncated,
        "original_length": len(content),
    }
    return payload


def _serialize_binary_body(content: bytes, max_response_chars: int) -> dict[str, Any]:
    is_truncated = len(content) > max_response_chars
    body = content[:max_response_chars] if is_truncated else content
    payload: dict[str, Any] = {
        "kind": "base64",
        "content": base64.b64encode(body).decode("ascii"),
        "truncated": is_truncated,
        "original_length": len(content),
    }
    return payload


def _serialize_response_body(
    response: httpx.Response,
    max_response_chars: int,
) -> dict[str, Any]:
    content_type = response.headers.get("content-type", "").lower()

    if "application/json" in content_type:
        parsed_json: Any | None
        try:
            parsed_json = response.json()
        except ValueError:
            parsed_json = None

        text_payload = _serialize_text_body(response.text, max_response_chars)
        if parsed_json is not None:
            text_payload["json"] = parsed_json
        return text_payload

    if content_type.startswith("text/") or "xml" in content_type or "html" in content_type:
        return _serialize_text_body(response.text, max_response_chars)

    return _serialize_binary_body(response.content, max_response_chars)


def _normalize_and_validate_method(method: str) -> str:
    normalized_method = method.upper().strip()
    if normalized_method not in ALLOWED_HTTP_METHODS:
        raise ValueError(
            "method must be one of: " + ", ".join(sorted(ALLOWED_HTTP_METHODS))
        )
    return normalized_method


def _normalize_and_validate_path(path: str) -> str:
    normalized_path = path.strip()
    if not normalized_path.startswith("/"):
        raise ValueError("path must start with '/'")
    if " " in normalized_path:
        raise ValueError("path cannot contain whitespace")
    return normalized_path


def _build_authorized_headers(
    auth_token: str,
    headers: dict[str, Any] | None,
) -> dict[str, str]:
    token = auth_token.strip()
    if not token:
        raise ValueError("auth_token is required and cannot be empty")

    request_headers = _serialize_headers(headers)
    request_headers["Authorization"] = f"Bearer {token}"
    request_headers.setdefault("Accept", "application/json")
    request_headers.setdefault("User-Agent", "cl-mcp-vercel/1.0")
    return request_headers


def execute_vercel_request(
    method: str,
    path: str,
    auth_token: str,
    headers: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
    json_body: Any | None = None,
    body: str | None = None,
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
    follow_redirects: bool = True,
    max_response_chars: int = MAX_RESPONSE_BODY_CHARS,
) -> VercelResponseData:
    normalized_method = _normalize_and_validate_method(method)
    normalized_path = _normalize_and_validate_path(path)

    if json_body is not None and body is not None:
        raise ValueError("Provide only one of 'json_body' or 'body'")

    if timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be greater than 0")

    if max_response_chars <= 0:
        raise ValueError("max_response_chars must be greater than 0")

    url = f"{VERCEL_API_BASE_URL}{normalized_path}"
    request_headers = _build_authorized_headers(auth_token=auth_token, headers=headers)

    try:
        with httpx.Client(
            follow_redirects=follow_redirects,
            timeout=timeout_seconds,
        ) as client:
            response = client.request(
                method=normalized_method,
                url=url,
                headers=request_headers,
                params=params,
                json=json_body,
                content=body,
            )
    except httpx.HTTPError as exc:
        raise RuntimeError(f"Vercel API request failed: {exc}") from exc

    return {
        "request": {
            "method": normalized_method,
            "path": normalized_path,
            "url": url,
            "headers": request_headers,
            "params": params or {},
            "timeout_seconds": timeout_seconds,
            "follow_redirects": follow_redirects,
            "max_response_chars": max_response_chars,
        },
        "response": {
            "url": str(response.url),
            "status_code": response.status_code,
            "reason_phrase": response.reason_phrase,
            "headers": dict(response.headers),
            "elapsed_ms": round(response.elapsed.total_seconds() * 1000, 2),
            "body": _serialize_response_body(response, max_response_chars),
        },
    }
