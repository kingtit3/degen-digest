"""Advanced structured logging configuration for Degen Digest.

This centralises log formatting so every module can simply do::

    from utils.advanced_logging import get_logger, configure_logging
    configure_logging(json=True)  # typically called once from main entry-point
    logger = get_logger(__name__)

The helper produces **JSON** logs by default when the environment variable
`LOG_FORMAT=json` is present (e.g. inside Docker) and colourful rich logs during
local development.  All standard-library ``logging`` calls are captured and
forwarded to *structlog* so third-party libraries continue to work.

Key features
------------
* Optional per-request or per-task context (``request_id``) bound via
  ``structlog.contextvars``.
* ISO8601 UTC timestamps.
* Easy to switch between human and machine format via env or parameter.
* Adds ``exc_info`` rendering only at *ERROR* level.
"""

from __future__ import annotations

import logging
import os
import sys
from typing import Any, Dict

# ---------------------------------------------------------------------------
# Optional structlog import.  If the dependency isn't available (e.g. in a
# minimal CI environment) we fall back to stdlib logging so that unit-tests do
# not crash with ``ModuleNotFoundError``.
# ---------------------------------------------------------------------------

import sys, types, logging

try:
    import structlog  # type: ignore
    _STRUCTLOG_AVAILABLE = True
except ModuleNotFoundError:  # pragma: no cover
    # ------------------------------------------------------------------
    # Create a minimal stub so the rest of this module can be imported even
    # when structlog isn't installed (e.g. in lightweight CI environments).
    # ------------------------------------------------------------------
    structlog = types.ModuleType("structlog")  # type: ignore

    def _noop(*_a, **_kw):  # noqa: D401
        return None

    structlog.get_logger = lambda name=None, **kw: logging.getLogger(name)  # type: ignore[attr-defined]
    structlog.configure = _noop  # type: ignore[attr-defined]
    structlog.PrintLoggerFactory = lambda: None  # type: ignore[attr-defined]
    structlog.processors = types.SimpleNamespace(
        TimeStamper=lambda *a, **kw: _noop,
        StackInfoRenderer=_noop,
        format_exc_info=_noop,
        UnicodeDecoder=_noop,
        JSONRenderer=_noop,
    )
    # Provide a real sub-module so that "import structlog.contextvars as ctx"
    # succeeds when structlog is absent.
    contextvars_mod = types.ModuleType("structlog.contextvars")
    contextvars_mod.merge_contextvars = _noop  # type: ignore[attr-defined]
    sys.modules["structlog.contextvars"] = contextvars_mod
    structlog.contextvars = contextvars_mod  # type: ignore[attr-defined]

    sys.modules["structlog"] = structlog  # type: ignore[arg-type]
    _STRUCTLOG_AVAILABLE = False

# ---------------------------------------------------------------------------
# Real structured implementation when structlog is present
# ---------------------------------------------------------------------------

if _STRUCTLOG_AVAILABLE:
    # ---------------------------------------------------------------------------
    # Public helpers
    # ---------------------------------------------------------------------------

    def configure_logging(*, json: bool | None = None, level: str | int = "INFO") -> None:
        """Configure structlog + stdlib logging.

        Args:
            json: Force JSON output.  If *None* (default) we choose JSON when the
                environment variable ``LOG_FORMAT`` is set to ``json`` *or* when
                stdout is *not* a TTY (i.e. running in containers / CI).
            level: Root logging level as string (e.g. ``"DEBUG"``) or numeric.
        """

        # ------------------------------------------------------------------
        # Decide on output format
        # ------------------------------------------------------------------
        if json is None:
            json = os.getenv("LOG_FORMAT", "console").lower() == "json" or not sys.stdout.isatty()

        timestamper = structlog.processors.TimeStamper(fmt="iso", utc=True)

        # Shared processors for both chains
        shared_processors: list[structlog.typing.Processor] = [
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,  # Adds tracebacks to event dict on error.
            timestamper,
        ]

        if json:
            renderer: structlog.typing.Processor = structlog.processors.JSONRenderer()
        else:
            try:
                from rich.console import Console
                from rich.syntax import Syntax
                from rich.traceback import Traceback

                console = Console(force_terminal=True, color_system="auto")

                def _rich_renderer(_: str, __: str, event_dict: Dict[str, Any]) -> str:  # type: ignore[override]
                    level = event_dict.pop("level", "info").upper()
                    ts = event_dict.pop("timestamp", "-")
                    msg = event_dict.pop("event", "")
                    rest = " ".join(f"{k}={v!r}" for k, v in event_dict.items())
                    console.print(f"[bold cyan]{ts}[/] | [bold]{level:<8}[/] | {msg} {rest}")
                    return ""

                renderer = _rich_renderer  # type: ignore[assignment]
            except Exception:  # pragma: no cover – rich is optional
                renderer = structlog.dev.ConsoleRenderer()

        structlog.configure(
            processors=[
                structlog.contextvars.merge_contextvars,
                *shared_processors,
                structlog.processors.UnicodeDecoder(),
                renderer,
            ],
            wrapper_class=structlog.make_filtering_bound_logger(getattr(logging, str(level).upper(), level)),
            logger_factory=structlog.PrintLoggerFactory(),
            cache_logger_on_first_use=True,
        )

        # Stdlib -> structlog bridge – simple setup: format messages via structlog
        logging.basicConfig(level=level, format="%(message)s")

    def get_logger(name: str):
        """Return a structlog logger bound with module name."""
        return structlog.get_logger(name=name)

# ---------------------------------------------------------------------------
# Fallback implementation when structlog is absent
# ---------------------------------------------------------------------------

if not _STRUCTLOG_AVAILABLE:
    # ---------------------------------------------------------------------------
    # Public helpers
    # ---------------------------------------------------------------------------

    def configure_logging(*, json: bool | None = None, level: str | int = "INFO") -> None:  # type: ignore[override]
        """Fallback basicConfig when structlog is absent."""

        logging.basicConfig(
            level=level,
            format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    def get_logger(name: str):  # type: ignore[override]
        """Return stdlib logger in structlog-less environments."""

        return logging.getLogger(name) 