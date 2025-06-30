"""Utility to configure rich, rotating, and hierarchical logging for Degen Digest.

Usage:
    from utils.logger import setup_logging
    setup_logging()

After calling, modules can simply do:
    import logging
    logger = logging.getLogger(__name__)
"""

import logging
import logging.handlers
from pathlib import Path

# New structured logging backend
try:
    from utils.advanced_logging import configure_logging as _advanced_config

    # Expose alias for downstream modules that still import setup_logging
    def setup_logging(log_dir: Path | str = "logs", level: int = logging.INFO):  # type: ignore[override]
        """Backward-compat wrapper that now delegates to advanced structured logging.

        The original behaviour (rotating file + console) is retained *if* the
        environment variable ``LOG_FORMAT`` is not set to ``json``.  Otherwise
        we switch to the JSON/structlog pipeline configured in
        ``utils.advanced_logging``.
        """

        # If JSON logging requested we ignore the local file handler logic and
        # let advanced logging handle everything via stdout.
        if str(level).upper() == "DEBUG":
            # When debugging we prefer human-readable console regardless.
            import os

            os.environ.setdefault("LOG_FORMAT", "console")

        _advanced_config(json=None, level=level)

except Exception:  # pragma: no cover – structlog not available during installation
    # Fallback to legacy simple logging when structlog isn't installed yet.
    def setup_logging(log_dir: Path | str = "logs", level: int = logging.INFO):  # type: ignore[override]
        """Legacy formatter (console + rotating file)."""

        log_dir_path = Path(log_dir)
        log_dir_path.mkdir(parents=True, exist_ok=True)

        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)

        file_handler = logging.handlers.RotatingFileHandler(
            log_dir_path / "degen_digest.log", maxBytes=5 * 1024 * 1024, backupCount=5
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)

        root_logger = logging.getLogger()
        if not root_logger.handlers:
            root_logger.setLevel(level)
            root_logger.addHandler(console_handler)
            root_logger.addHandler(file_handler) 