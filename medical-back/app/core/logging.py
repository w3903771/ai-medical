from loguru import logger
import sys
from app.utils.request_context import request_id_ctx_var, trace_id_ctx_var


def configure_logging(settings) -> None:
    logger.remove()
    logger.add(
        sys.stdout,
        level=settings.log_level,
        format=(
            settings.log_format
            or "{time:YYYY-MM-DD HH:mm:ss} | {level} | {extra[request_id]} | {extra[trace_id]} | {message}"
        ),
        enqueue=True,
        backtrace=True,
        diagnose=True,
    )


def get_request_logger():
    rid = request_id_ctx_var.get(None) or "-"
    tid = trace_id_ctx_var.get(None) or "-"
    return logger.bind(request_id=rid, trace_id=tid)