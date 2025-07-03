"""Markdown → PDF conversion helper (uses Pandoc via pypandoc)."""

import os
import shutil
from pathlib import Path

import pypandoc

from utils.advanced_logging import _STRUCTLOG_AVAILABLE, get_logger

logger = get_logger(__name__)


def md_to_pdf(input_md: Path, output_pdf: Path):
    """Convert a markdown file to PDF.

    Requires `pandoc` binary to be installed. If not found, logs warning.
    """
    # Allow callers to skip PDF (e.g. CI) via env var
    if os.getenv("SKIP_PDF"):
        logger.info("pdf convert skipped via SKIP_PDF env")
        return

    try:
        if _STRUCTLOG_AVAILABLE:
            logger.info("pdf convert", input=str(input_md), output=str(output_pdf))
        else:
            logger.info(f"pdf convert {input_md} -> {output_pdf}")

        # Prefer the lightweight 'tectonic' engine if present; otherwise let
        # Pandoc decide (usually pdflatex).
        extra_args: list[str] = []
        if not shutil.which("pdflatex") and shutil.which("tectonic"):
            extra_args += ["--pdf-engine", "tectonic"]

        # Professional page formatting
        extra_args += [
            "-V",
            "geometry:margin=0.75in",  # Slightly smaller margins for more content
            "-V",
            "fontsize=11pt",
            "-V",
            "mainfont=Times New Roman",  # Professional serif font
            "-V",
            "monofont=Consolas",  # Monospace font for code/links
            "-V",
            "colorlinks=true",  # Colored links
            "-V",
            "linkcolor=blue",
            "-V",
            "urlcolor=blue",
            "-V",
            "toccolor=gray",
            "-V",
            "numbersections=true",  # Numbered sections
            "-V",
            "papersize=letter",  # Standard letter size
            "-V",
            "linestretch=1.2",  # Better line spacing
            "--toc",  # Table of contents
            "--toc-depth=3",  # Include up to 3 levels
            "--pdf-engine-opt=-shell-escape",  # Allow shell commands for better font support
        ]

        # Optional emoji support: user can opt-in by setting PDF_EMOJI_FONT=1
        if os.getenv("PDF_EMOJI_FONT") == "1":
            # Ensure we use a Unicode‐capable engine (luatex/xelatex). Prefer lualatex.
            if not any(a.startswith("--pdf-engine") for a in extra_args):
                extra_args += ["--pdf-engine", "lualatex"]
            extra_args += ["-V", "mainfont=Noto Color Emoji"]

        # Add custom CSS for better styling
        css_content = """
        body { font-family: 'Times New Roman', serif; line-height: 1.4; }
        h1 { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
        h2 { color: #34495e; border-bottom: 1px solid #bdc3c7; padding-bottom: 5px; }
        h3 { color: #7f8c8d; }
        table { border-collapse: collapse; width: 100%; margin: 20px 0; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; font-weight: bold; }
        code { background-color: #f8f9fa; padding: 2px 4px; border-radius: 3px; }
        blockquote { border-left: 4px solid #3498db; margin: 0; padding-left: 20px; }
        .disclaimer { background-color: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; }
        """

        # Create temporary CSS file
        css_file = input_md.parent / "temp_styles.css"
        css_file.write_text(css_content)
        extra_args += ["--css", str(css_file)]

        pypandoc.convert_file(
            str(input_md),
            "pdf",
            outputfile=str(output_pdf),
            extra_args=extra_args or None,
        )

        # Clean up temporary CSS file
        if css_file.exists():
            css_file.unlink()

        logger.info("pdf done", path=str(output_pdf))
    except (OSError, RuntimeError) as exc:
        logger.warning("pdf convert failed", exc_info=exc)
