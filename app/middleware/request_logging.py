import logging
import time
import uuid
from collections.abc import Awaitable, Callable

from fastapi import Request, Response

logger = logging.getLogger(__name__)


async def log_requests(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    correlation_id = str(uuid.uuid4())
    request.state.correlation_id = correlation_id
    start_time = time.perf_counter()

    logger.info(
        "Request started: %s %s | Correlation ID: %s",
        request.method,
        request.url.path,
        correlation_id,
    )

    response = await call_next(request)
    process_time = time.perf_counter() - start_time

    response.set_cookie(key="example", value="value")
    response.headers["X-Process-Time"] = str(process_time)
    response.headers["X-Correlation-ID"] = correlation_id

    logger.info(
        "Request completed: %s %s | Status: %s | Time: %.4f seconds | Correlation ID: %s",
        request.method,
        request.url.path,
        response.status_code,
        process_time,
        correlation_id,
    )

    return response
