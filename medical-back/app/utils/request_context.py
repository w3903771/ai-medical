from contextvars import ContextVar
from typing import Optional

request_id_ctx_var: ContextVar[Optional[str]] = ContextVar("request_id", default=None)
trace_id_ctx_var: ContextVar[Optional[str]] = ContextVar("trace_id", default=None)