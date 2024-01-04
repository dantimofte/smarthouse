import logging
import sys
from typing import Union

import structlog


class StdErrFilter(logging.Filter):
    """
    Filter for the stderr stream
    Doesn't print records below ERROR to stderr to avoid dupes
    """
    def filter(self, record):
        return 0 if record.levelno < logging.WARNING else 1


class StdOutFilter(logging.Filter):
    """
    Filter for the stdout stream
    Doesn't print records above WARNING to stdout to avoid dupes
    """
    def filter(self, record):
        return 1 if record.levelno < logging.WARNING else 0


def initlog(
    level: Union[int, str] = logging.INFO,
    force_console: bool = True
) -> None:

    common_processors = [
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.stdlib.ExtraAdder(),
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="ISO"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
        structlog.processors.CallsiteParameterAdder(
            {
                structlog.processors.CallsiteParameter.FILENAME,
                structlog.processors.CallsiteParameter.FUNC_NAME,
                structlog.processors.CallsiteParameter.LINENO,
            }
        ),
    ]
    structlog.configure(
        processors=common_processors
        + [
            # If log level is too low, abort pipeline and throw away log entry.
            structlog.stdlib.filter_by_level,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    mid_processors = [
        structlog.stdlib.ProcessorFormatter.remove_processors_meta
    ]
    # human-readable for console or structured for log aggregation systems
    if sys.stdout.isatty() or force_console:
        final_processors = [*mid_processors, structlog.dev.ConsoleRenderer()]
    else:
        final_processors = mid_processors + [
            structlog.processors.ExceptionRenderer(
                structlog.processors.ExceptionDictTransformer(
                    show_locals=False
                )
            ),
            structlog.processors.EventRenamer("message", "_event"),
            structlog.processors.JSONRenderer(),
        ]
    formatter = structlog.stdlib.ProcessorFormatter(
        processors=final_processors,
    )

    # Log everything up to the WARNING level to stdout.
    stdout_handler = logging.StreamHandler()
    stdout_handler.setFormatter(formatter)
    stdout_handler.stream = sys.stdout
    stdout_handler.level = logging.INFO
    stdout_handler.filter = StdOutFilter().filter

    # Log everything from the ERROR level to stderr.
    stderr_handler = logging.StreamHandler()
    stderr_handler.setFormatter(formatter)
    stderr_handler.stream = sys.stderr
    stderr_handler.level = logging.WARNING
    stderr_handler.filter = StdErrFilter().filter

    root_logger = logging.getLogger()
    root_logger.addHandler(stdout_handler)
    root_logger.addHandler(stderr_handler)
    root_logger.setLevel(level)
