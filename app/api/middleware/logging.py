from time import time
from typing import Any
from uuid import uuid4

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from app.tooling.ioc import ioc_container_type
from app.tooling.logging import AppLogger


def route_logger(**logger_kwargs: Any):
    def dependency(
        request: Request,
    ) -> AppLogger:
        return ioc_container_type().logger(request.url.path, **logger_kwargs)

    return dependency


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        logger = ioc_container_type().logger(LoggingMiddleware.__name__)
        type(logger).add_to_context(_request_id=str(uuid4()), _path=request.url.path)

        start_time = time()
        response = await call_next(request)
        duration_ms = (time() - start_time) * 1000
        logger.info("request_processed", status_code=response.status_code, duration_ms=round(duration_ms, 2))

        return response
