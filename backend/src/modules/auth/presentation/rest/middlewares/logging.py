import time
from typing import (
    Awaitable,
    Callable,
)

from fastapi import (
    Request,
    Response,
)
import structlog


async def logging_middleware(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    req_id = request.headers.get("request-id")

    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(
        request_id=req_id,
    )

    start_time = time.time()

    response: Response = await call_next(request)

    end_time = time.time()
    response_time = end_time - start_time

    await structlog.get_logger().info(
        "Request processed",
        request_id=req_id,
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        response_time=response_time,
    )

    return response
