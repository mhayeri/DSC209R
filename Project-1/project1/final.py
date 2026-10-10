"""Assemble the final PDF: the chart on page 1 and the write-up on page 2.

Run ``python -m project1.final``. This is separate from ``python -m project1`` so
that re-rendering the final chart never overwrites the checkpoint PDF.
"""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")  # render to files only; no display needed
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from project1.aisle_price_plot import build_aisle_price_plot
from project1.checkpoint import TEXT_LEFT, TEXT_WIDTH_IN, _image_page, _wrap_to_width
from project1.config import OUTPUT_DIR, PROJECT_ROOT, SCALE_FACTOR
from project1.data import aisle_price_thirds, count_pricier_per_gram, load_grocerydb

CHART_PATH = OUTPUT_DIR / "final_plot.png"
WRITEUP_PATH = PROJECT_ROOT / "writeup" / "final_writeup.md"
# No name or PID in the file name, as the assignment requires.
BODY_FONTSIZE: int = 10
LINE_SPACING: float = 1.35
PDF_PATH = OUTPUT_DIR / "project1_final_submission.pdf"


def _writeup_page(paragraphs: list[str]) -> plt.Figure:
    """Letter-size page with a heading and the write-up, one wrapped block per paragraph."""
    fig = plt.figure(figsize=(8.5, 11))
    fig.text(TEXT_LEFT, 0.95, "Design rationale", fontsize=15, weight="bold")
    body = "\n\n".join(_wrap_to_width(fig, para, TEXT_WIDTH_IN, BODY_FONTSIZE) for para in paragraphs)
    fig.text(TEXT_LEFT, 0.92, body, fontsize=BODY_FONTSIZE, va="top", linespacing=LINE_SPACING)
    return fig


def main() -> None:
    """Render the chart, then write the two-page submission PDF."""
    df = load_grocerydb()
    thirds = aisle_price_thirds(df)
    chart = build_aisle_price_plot(thirds, count_pricier_per_gram(df, thirds["category"]))
    OUTPUT_DIR.mkdir(exist_ok=True)
    chart.save(str(CHART_PATH), scale_factor=SCALE_FACTOR)
    paragraphs = WRITEUP_PATH.read_text(encoding="utf-8").strip().split("\n\n")
    with PdfPages(PDF_PATH) as pdf:
        pdf.savefig(_image_page("", CHART_PATH))
        pdf.savefig(_writeup_page(paragraphs))
    plt.close("all")
    print(f"saved {PDF_PATH.name}")


if __name__ == "__main__":
    main()
