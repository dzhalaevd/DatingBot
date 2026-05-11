import logging
import sys

import structlog
from structlog.processors import CallsiteParameter, CallsiteParameterAdder

from .processors import get_render_processor


def configure_logging(
    log_level: int = logging.INFO,
    render_json_logs: bool = False,
) -> None:
    """Настраивает систему логирования приложения.

    Вдохновился: https://gist.github.com/nkhitrov/38adbb314f0d35371eba4ffb8f27078f.

    :param render_json_logs: Выводить логи в json или нет
    :param log_level: Уровень логирования.
    """
    colors = False if render_json_logs else True

    for logger_name in ("sqlalchemy", "sqlalchemy.engine"):
        logger = logging.getLogger(logger_name)
        logger.handlers.clear()
        logger.propagate = True

    common_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.ExtraAdder(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.TimeStamper(fmt="iso", utc=False),
        CallsiteParameterAdder(
            {
                CallsiteParameter.LINENO,
                CallsiteParameter.PROCESS_NAME,
                CallsiteParameter.THREAD_NAME,
            },
        ),
    ]

    structlog_processors = [
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ]
    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=common_processors,
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            get_render_processor(
                render_json_logs=render_json_logs,
                colors=colors,
            ),
        ],
    )

    handlers: list[logging.Handler] = []

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    handlers.append(console_handler)

    logging.basicConfig(handlers=handlers, level=log_level)

    structlog.configure(
        processors=common_processors + structlog_processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # На случай, если какая-нибудь библиотека будет шуметь, то вместо None, можно прописать
    # типа "uvicorn.error"
    for name in [None]:
        if name:
            logging.getLogger(name).setLevel(logging.WARNING)
