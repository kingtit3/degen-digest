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


def setup_logging(log_dir: Path | str = "logs", level: int = logging.INFO):
    """Configure logging with console + rotating file handlers.

    Args:
        log_dir: Directory where log files will be stored.
        level: Root logging level.
    """
    log_dir_path = Path(log_dir)
    log_dir_path.mkdir(parents=True, exist_ok=True)

    # Formatters
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)

    # Rotating file handler keeps 5 files of 5 MB each
    file_handler = logging.handlers.RotatingFileHandler(
        log_dir_path / "degen_digest.log", maxBytes=5 * 1024 * 1024, backupCount=5
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)

    # Configure root logger only once
    root_logger = logging.getLogger()
    if not root_logger.handlers:
        root_logger.setLevel(level)
        root_logger.addHandler(console_handler)
        root_logger.addHandler(file_handler) 