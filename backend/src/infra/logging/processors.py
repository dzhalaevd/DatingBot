from typing import Any
from uuid import UUID

import orjson
import structlog

from .types import SerializerType, ProcessorType


def make_json_safe(data: Any) -> Any:
    if isinstance(data, dict):
        return {
            str(k): make_json_safe(v)
            for k, v in data.items()
        }
    elif isinstance(data, (list, tuple, set)):
        return [make_json_safe(v) for v in data]
    elif isinstance(data, bytes):
        return data.decode(errors="ignore")
    elif isinstance(data, (str, int, float, bool)) or data is None:
        return data
    else:
        return str(data)


def additionally_serialize(obj: object) -> Any:
    if isinstance(obj, UUID):
        return str(obj)
    if isinstance(obj, bytes):
        return obj.decode(errors="ignore")

    return repr(obj)


def serialize_to_json(data: Any) -> str:
    safe_data = make_json_safe(data)
    return orjson.dumps(safe_data, default=additionally_serialize).decode()


def get_render_processor(
        serializer: SerializerType = serialize_to_json,
        *,
        render_json_logs: bool = False,
        colors: bool = True,
) -> ProcessorType:
    if render_json_logs:
        return structlog.processors.JSONRenderer(serializer=serializer)
    return structlog.dev.ConsoleRenderer(colors=colors)
