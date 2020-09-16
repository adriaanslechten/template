"""Mostly sets up structlog as the catch-all logging handler"""
import logging
import sys
from typing import Any, Callable

import structlog
from pyrus import PyrusRenderer


class StructlogHandler(logging.Handler):
    """Feeds all events back into structlog"""

    def __init__(self, *args: Any, **kw: Any) -> None:
        super(StructlogHandler, self).__init__(*args, **kw)
        self._log = structlog.get_logger()

    def emit(self, record: logging.LogRecord) -> None:
        kw = {}
        if record.args:
            kw["positional_args"] = record.args
        self._log.log(
            record.levelno,
            record.msg,
            name=record.name,
            exc_info=record.exc_info,
            **kw,
        )


def level_filter(log_level: str) -> Callable:
    """Log levels for structlog"""
    limit = getattr(logging, log_level)
    lut = structlog.stdlib._NAME_TO_LEVEL  # pylint:disable=protected-access

    def inner(_: Any, __: Any, event: dict) -> dict:
        """Filter function"""
        if (lut.get(event["level"], 0)) < limit:
            raise structlog.DropEvent
        return event

    return inner


def setup_logging(log_level: str = "INFO") -> None:
    """Sets logging up"""
    processors = [
        structlog.stdlib.add_log_level,
        level_filter(log_level),
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        PyrusRenderer(),
    ]

    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(file=sys.stderr),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    root = logging.getLogger()
    root.setLevel(log_level)
    root.addHandler(StructlogHandler())
    logging.getLogger("asyncio").setLevel(logging.CRITICAL)
