"""Standardized API response helpers.

All successful responses follow:
{
  "success": true,
  "data": <payload>,
  "message": "optional human readable message",
  "meta": { "path": "/api/v1/...", "timestamp": "...", "request_id": "uuid" }
}

All error responses follow:
{
  "success": false,
  "error": {
     "code": "ERROR_CODE",
     "message": "Primary error message",
     "details": <list|dict|None>
  },
  "meta": { ... }
}
"""

from __future__ import annotations
from typing import Any, Dict, Iterable, Mapping
from flask import request
from datetime import datetime, timezone
import uuid
import os


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _camel_case(key: str) -> str:
    if '_' not in key:
        return key
    parts = key.split('_')
    return parts[0] + ''.join(p.capitalize() for p in parts[1:])


def _transform_keys(obj: Any) -> Any:
    """Recursively transform dict keys to camelCase when enabled.

    Controlled by env RESPONSE_CAMELCASE=true
    """
    if os.getenv('RESPONSE_CAMELCASE', 'true').lower() != 'true':
        return obj
    if isinstance(obj, Mapping):
        return { _camel_case(k): _transform_keys(v) for k, v in obj.items() }
    if isinstance(obj, list):
        return [_transform_keys(v) for v in obj]
    return obj


def _meta() -> Dict[str, Any]:
    return {
        "path": request.path if request else None,
        "request_id": str(uuid.uuid4()),
        "timestamp": _now_iso(),
    }


def success_response(data: Any = None, message: str | None = None, status: int = 200, meta: Dict[str, Any] | None = None):
    payload = {
        "success": True,
        "data": _transform_keys(data) if data is not None else None,
        "message": message,
        "meta": {**_meta(), **(meta or {})}
    }
    # Remove null message for compactness
    if message is None:
        payload.pop("message", None)
    return payload, status


def error_response(code: str, message: str, details: Any = None, status: int = 400, meta: Dict[str, Any] | None = None):
    payload = {
        "success": False,
        "error": {
            "code": code,
            "message": message,
        },
        "meta": {**_meta(), **(meta or {})}
    }
    if details is not None and details != []:
        payload["error"]["details"] = _transform_keys(details)
    return payload, status


def paginated_response(items: Iterable, total: int, page: int, page_size: int, message: str | None = None):
    return success_response({
        "items": list(items),
        "pagination": {
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": (total + page_size - 1) // page_size
        }
    }, message=message)
