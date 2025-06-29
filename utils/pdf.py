"""Markdown → PDF conversion helper (uses Pandoc via pypandoc)."""

from pathlib import Path
import logging
import pypandoc

logger = logging.getLogger(__name__)


def md_to_pdf(input_md: Path, output_pdf: Path):
    """Convert a markdown file to PDF.

    Requires `pandoc` binary to be installed. If not found, logs warning.
    """
    try:
        logger.info("Converting %s to %s", input_md, output_pdf)
        pypandoc.convert_file(str(input_md), "pdf", outputfile=str(output_pdf))
    except OSError as exc:
        logger.warning("Pandoc not installed or conversion failed: %s", exc) 