from typing import Callable, Any

import structlog

SerializerType = Callable[[dict[str, Any]], str | bytes]

ProcessorType = Callable[
    [
        structlog.types.WrappedLogger,
        str,
        structlog.types.EventDict,
    ],
    str | bytes,
]
