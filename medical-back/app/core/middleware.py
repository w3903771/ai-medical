import uuid
from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.utils.request_context import request_id_ctx_var, trace_id_ctx_var
from app.core.logging import get_request_logger


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        rid = str(uuid.uuid4())
        tid = str(uuid.uuid4())
        request_id_ctx_var.set(rid)
        trace_id_ctx_var.set(tid)
        logger = get_request_logger()
        logger.info(f"Incoming request {request.method} {request.url}")
        response = await call_next(request)
        logger.info(f"Completed request {response.status_code}")
        response.headers["X-Request-ID"] = rid
        response.headers["X-Trace-ID"] = tid
        return response


def setup_middleware(app: FastAPI) -> None:
    app.add_middleware(RequestContextMiddleware)