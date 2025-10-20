"""Minimal HTTP server exposing FunctionGraph-compatible endpoints."""

from __future__ import annotations

import importlib
import json
import logging
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from types import SimpleNamespace
from typing import Any, Callable, Dict, Optional, Tuple

logging.basicConfig(level=logging.INFO)
_LOGGER = logging.getLogger("functiongraph.sample")

_DEFAULT_HANDLER = "app.handler"
_HANDLER: Optional[Callable[[Any, Any], Dict[str, Any]]] = None


def _resolve_handler(
    handler_ref: str,
) -> Tuple[Optional[Callable[[Any, Any], Dict[str, Any]]], Optional[HTTPStatus], Optional[Dict[str, Any]]]:
    """Attempt to import and return the callable referenced by ``handler_ref``."""

    try:
        module_name, function_name = handler_ref.rsplit(".", 1)
    except ValueError:
        return None, HTTPStatus.BAD_REQUEST, {"message": "Handler must be in 'module.function' format"}

    try:
        module = importlib.import_module(module_name)
        candidate = getattr(module, function_name)
    except (ImportError, AttributeError) as exc:
        return None, HTTPStatus.BAD_REQUEST, {"message": "Unable to import handler", "details": str(exc)}

    if not callable(candidate):
        return None, HTTPStatus.BAD_REQUEST, {"message": "Handler attribute is not callable"}

    return candidate, None, None


class InvocationContext(SimpleNamespace):
    """Context object passed to the handler with a default logger."""

    def __init__(self, values: Dict[str, Any]):
        super().__init__(**values)
        if not hasattr(self, "logger"):
            self.logger = _LOGGER


class FunctionGraphHandler(BaseHTTPRequestHandler):
    server_version = "FunctionGraphSample/1.0"

    def do_POST(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
        if self.path == "/init":
            self._handle_init()
        elif self.path == "/invoke":
            self._handle_invoke()
        else:
            self._send_json(HTTPStatus.NOT_FOUND, {"message": "Unsupported path"})

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A003 - inherited name
        _LOGGER.info("%s - - %s", self.address_string(), format % args)

    def _read_json_body(self) -> Dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length) if length else b""
        if not raw_body:
            return {}
        try:
            return json.loads(raw_body.decode("utf-8"))
        except json.JSONDecodeError as exc:  # pragma: no cover - malformed payload
            self._send_json(
                HTTPStatus.BAD_REQUEST,
                {"message": "Invalid JSON payload", "details": str(exc)},
            )
            raise

    def _handle_init(self) -> None:
        global _HANDLER

        try:
            payload = self._read_json_body()
        except json.JSONDecodeError:
            return

        handler_ref = payload.get("handler", _DEFAULT_HANDLER)
        candidate, status, error_payload = _resolve_handler(handler_ref)

        if candidate is None:
            status = status or HTTPStatus.INTERNAL_SERVER_ERROR
            error_payload = error_payload or {"message": "Handler resolution failed"}
            self._send_json(status, error_payload)
            return

        _HANDLER = candidate
        _LOGGER.info("Handler initialized: %s", handler_ref)
        self._send_json(HTTPStatus.OK, {"message": "Handler initialized", "handler": handler_ref})

    def _handle_invoke(self) -> None:
        global _HANDLER

        if _HANDLER is None:
            candidate, status, error_payload = _resolve_handler(_DEFAULT_HANDLER)
            if candidate is None:
                status = status or HTTPStatus.INTERNAL_SERVER_ERROR
                error_payload = error_payload or {"message": "Handler resolution failed"}
                self._send_json(status, error_payload)
                return
            _HANDLER = candidate
            _LOGGER.info("Handler lazily initialized: %s", _DEFAULT_HANDLER)

        try:
            payload = self._read_json_body()
        except json.JSONDecodeError:
            return

        event = payload.get("event")
        context_values = payload.get("context")
        context_obj: Any
        if isinstance(context_values, dict):
            context_obj = InvocationContext(context_values)
        else:
            context_obj = InvocationContext({})

        try:
            result = _HANDLER(event, context_obj)
        except Exception as exc:  # pragma: no cover - handler level errors
            _LOGGER.exception("Handler raised an exception")
            self._send_json(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                {"message": "Handler raised an exception", "details": str(exc)},
            )
            return

        if not isinstance(result, dict):
            self._send_json(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                {"message": "Handler returned a non-dict response"},
            )
            return

        self._send_json(HTTPStatus.OK, result)

    def _send_json(self, status: HTTPStatus, payload: Dict[str, Any]) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status.value)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def run_server(host: str = "0.0.0.0", port: int = 8000) -> None:
    server = HTTPServer((host, port), FunctionGraphHandler)
    _LOGGER.info("Starting FunctionGraph HTTP server on %s:%s", host, port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:  # pragma: no cover - manual shutdown
        _LOGGER.info("Received interrupt, shutting down server")
    finally:
        server.server_close()


if __name__ == "__main__":
    run_server()
