import time
import logging
import os
import json
import uuid
from typing import Callable
from fastapi import HTTPException, Request, FastAPI
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request as StarletteRequest
from starlette.types import ASGIApp


httprequest = "HTTP REQUEST"

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "request_id": getattr(record, "request_id", None),
            "src_ip": getattr(record, "src_ip", None),
            "method": getattr(record, "method", None),
            "url": getattr(record, "url", None),
            "status_code": getattr(record, "status_code", None),
            "duration_ms": getattr(record, "duration_ms", None),
            "error_type": getattr(record, "error_type", None),
            "error_detail": getattr(record, "error_detail", None),
            "level": record.levelname,
            "message": record.getMessage(),
        }
        return json.dumps(log_record)

logger = logging.getLogger("app")

logger.propagate = False


log_level_name = os.getenv("LOG_LEVEL", "INFO").upper()
log_level = getattr(logging, log_level_name, logging.INFO)
logger.setLevel(log_level)

json_formatter = JsonFormatter()

_stream_exists = any(isinstance(h, logging.StreamHandler) for h in logger.handlers)
if not _stream_exists:
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(json_formatter)
    logger.addHandler(stream_handler)

class LogMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: StarletteRequest, call_next: Callable):
        start = time.time()
        request_id = str(uuid.uuid4())
        client_ip = request.headers.get("x-forwarded-for", request.client.host)

    
        request.state.request_id = request_id
        request.state.client_ip = client_ip
        request.state.start_time = start

        try:
            response = await call_next(request)
        except Exception as exc:
            duration = round((time.time() - start) * 1000, 2)
            logger.error(
                httprequest,
                extra={
                    "request_id": request_id,
                    "src_ip": client_ip,
                    "method": request.method,
                    "url": str(request.url),
                    "status_code": 500,
                    "duration_ms": duration,
                    "error_type": exc.__class__.__name__,
                    "error_detail": str(exc),
                },
            )
            return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})

        if getattr(request.state, "error_logged", False):
            return response

        duration = round((time.time() - start) * 1000, 2)

 
        error_type = None
        error_detail = None
        level_method = logger.info
        if response.status_code >= 400:
            level_method = logger.warning
            error_type = "HTTPError"
            try:
                if hasattr(response, "body") and response.body:
                    body_text = response.body.decode()
                    data = json.loads(body_text)
                    if isinstance(data, dict) and "detail" in data:
                        error_detail = data["detail"]
            except (UnicodeDecodeError, json.JSONDecodeError, AttributeError, TypeError):
                pass

        level_method(
            httprequest,
            extra={
                "request_id": request_id,
                "src_ip": client_ip,
                "method": request.method,
                "url": str(request.url),
                "status_code": response.status_code,
                "duration_ms": duration,
                "error_type": error_type,
                "error_detail": error_detail,
            },
        )
        return response


def setup_error_logging(app: FastAPI):
 
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
   
        start = getattr(request.state, "start_time", None)
        duration = round((time.time() - start) * 1000, 2) if start else None
        request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
        client_ip = getattr(request.state, "client_ip", request.client.host)
        logger.warning(
            httprequest,
            extra={
                "request_id": request_id,
                "src_ip": client_ip,
                "method": request.method,
                "url": str(request.url),
                "status_code": exc.status_code,
                "duration_ms": duration,
                "error_type": "HTTPException",
                "error_detail": str(exc.detail),
            },
        )

        request.state.error_logged = True
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        start = getattr(request.state, "start_time", None)
        duration = round((time.time() - start) * 1000, 2) if start else None
        request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
        client_ip = getattr(request.state, "client_ip", request.client.host)
        logger.error(
            httprequest,
            extra={
                "request_id": request_id,
                "src_ip": client_ip,
                "method": request.method,
                "url": str(request.url),
                "status_code": 500,
                "duration_ms": duration,
                "error_type": exc.__class__.__name__,
                "error_detail": str(exc),
            },
        )
        request.state.error_logged = True
        return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})

    return app

