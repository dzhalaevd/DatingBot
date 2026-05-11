from typing import Any
from collections.abc import Callable

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
