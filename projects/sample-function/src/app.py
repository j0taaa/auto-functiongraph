"""Sample FunctionGraph handler following Huawei Cloud patterns."""

from __future__ import annotations

import json
from typing import Any, Dict


def _extract_name(event: Any) -> str:
    """Attempt to pull a caller provided name from different event layouts."""

    default_name = "FunctionGraph"

    if isinstance(event, dict):
        if "name" in event and isinstance(event["name"], str):
            return event["name"]

        body = event.get("body")
        if isinstance(body, str) and body:
            try:
                body_json = json.loads(body)
            except json.JSONDecodeError:
                pass
            else:
                if isinstance(body_json, dict) and isinstance(body_json.get("name"), str):
                    return body_json["name"]
        elif isinstance(body, dict) and isinstance(body.get("name"), str):
            return body["name"]

    return default_name


def handler(event: Any, context: Any) -> Dict[str, Any]:
    """Return an HTTP style response expected by FunctionGraph."""

    name = _extract_name(event)
    message = {"message": f"Hello, {name}!", "event": event}

    logger = getattr(context, "logger", None)
    if logger is not None:
        try:
            logger.info("Responding with message for %s", name)
        except Exception:  # pragma: no cover - context logger is optional
            pass

    return {
        "statusCode": 200,
        "isBase64Encoded": False,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(message, ensure_ascii=False),
    }
