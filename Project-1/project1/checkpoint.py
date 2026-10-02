"""Assemble the checkpoint PDF: three plots, one per page, then the paragraph."""
from __future__ import annotations

import textwrap
from pathlib import Path
from typing import Sequence

import matplotlib

matplotlib.use("Agg")  # render to files only; no display needed
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

PAGE_WIDTH_IN: float = 11.0
WRAP_COLUMNS: int = 88


def build_checkpoint_pdf(
    plots: Sequence[tuple[str, Path]], paragraph_path: Path, out_path: Path
) -> None:
    """Write the checkpoint submission PDF.

    Args:
        plots: ``(page label, PNG path)`` pairs, one page each, in order.
        paragraph_path: Text file with the paragraph explaining the preferred plot.
        out_path: Where to write the PDF.
    """
    paragraph = paragraph_path.read_text(encoding="utf-8").strip()
    with PdfPages(out_path) as pdf:
        for label, image_path in plots:
            pdf.savefig(_image_page(label, image_path))
        pdf.savefig(_text_page("Preferred plot", paragraph))
    plt.close("all")


def _image_page(label: str, image_path: Path) -> plt.Figure:
    """Return a figure sized to the image's aspect ratio, with a page label."""
    image = mpimg.imread(image_path)
    height_px, width_px = image.shape[:2]
    fig = plt.figure(figsize=(PAGE_WIDTH_IN, PAGE_WIDTH_IN * height_px / width_px + 0.6))
    ax = fig.add_axes([0.02, 0.02, 0.96, 0.92])
    ax.imshow(image)
    ax.axis("off")
    fig.text(0.02, 0.975, label, fontsize=13, weight="bold", va="top")
    return fig


def _text_page(heading: str, body: str) -> plt.Figure:
    """Return a letter-size figure holding a heading and a wrapped paragraph."""
    fig = plt.figure(figsize=(8.5, 11))
    fig.text(0.1, 0.93, heading, fontsize=16, weight="bold")
    fig.text(
        0.1,
        0.89,
        textwrap.fill(body, WRAP_COLUMNS),
        fontsize=11,
        va="top",
        linespacing=1.5,
    )
    return fig
