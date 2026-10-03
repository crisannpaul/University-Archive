"""Shared structured logger for the Smart Library engine.

Every op imports `get_logger` so log format stays consistent. Per the spec's
Logging section, normal flow goes to INFO, per-step detail to DEBUG. DEBUG is
off by default — flip on with `set_verbose(True)` from the CLI / UI.
"""

import logging
import sys

_LOG_FORMAT = "%(asctime)s %(levelname)s [%(name)s] %(message)s"
_DATE_FORMAT = "%H:%M:%S"

_root_configured = False


def _configure_root() -> None:
    global _root_configured
    if _root_configured:
        return
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT))
    root = logging.getLogger("smart_library")
    root.handlers = [handler]
    root.setLevel(logging.INFO)
    root.propagate = False
    _root_configured = True


def get_logger(name: str) -> logging.Logger:
    """Return a logger under the `smart_library` namespace."""
    _configure_root()
    if not name.startswith("smart_library"):
        name = f"smart_library.{name}"
    return logging.getLogger(name)


def set_verbose(verbose: bool) -> None:
    """Toggle DEBUG-level emission for the whole engine namespace."""
    _configure_root()
    logging.getLogger("smart_library").setLevel(logging.DEBUG if verbose else logging.INFO)


def step(logger: logging.Logger, op: str, clip_filename: str, action: str, elapsed_s: float | None = None) -> None:
    """Emit a per-step transition line in the spec's canonical format.

    Format: `[{op}] {clip_filename}: {action} ({elapsed_s}s)`
    """
    if elapsed_s is None:
        logger.info("[%s] %s: %s", op, clip_filename, action)
    else:
        logger.info("[%s] %s: %s (%.2fs)", op, clip_filename, action, elapsed_s)


def step_error(logger: logging.Logger, op: str, clip_filename: str, error: str) -> None:
    """Emit a failure line in the spec's canonical format."""
    logger.error("[%s] %s: ERROR — %s", op, clip_filename, error)
