"""Render the Project 1 charts: ``python -m project1``."""
from __future__ import annotations

import altair as alt

from project1.aisle_price_plot import build_aisle_price_plot
from project1.aisle_strip_plot import build_aisle_strip_plot
from project1.checkpoint import build_checkpoint_pdf
from project1.config import OUTPUT_DIR, PROJECT_ROOT, SCALE_FACTOR
from project1.data import (
    aisle_price_thirds,
    aisle_strip,
    load_grocerydb,
    organic_class_grid,
    organic_within_aisle_gap,
)
from project1.organic_plot import build_organic_plot


def save(chart: alt.TopLevelMixin, name: str) -> None:
    """Write ``chart`` to ``outputs/<name>`` as a PNG."""
    OUTPUT_DIR.mkdir(exist_ok=True)
    chart.save(str(OUTPUT_DIR / name), scale_factor=SCALE_FACTOR)
    print(f"saved {name}")


def main() -> None:
    """Load the data and render every chart."""
    df = load_grocerydb()
    thirds = aisle_price_thirds(df)
    print(f"least processed third costs more in {(thirds['ratio'] > 1).sum()} of {len(thirds)} aisles")
    save(build_aisle_price_plot(thirds), "plot1_aisle_price.png")
    aisle_gap, n_compared = organic_within_aisle_gap(df)
    save(build_organic_plot(organic_class_grid(df), aisle_gap, n_compared), "plot2_organic_mix.png")
    items, aisles = aisle_strip(df)
    save(build_aisle_strip_plot(items, aisles), "plot3_aisle_strip.png")

    paragraph = PROJECT_ROOT / "writeup" / "checkpoint_paragraph.md"
    if paragraph.exists():
        build_checkpoint_pdf(
            [
                ("Plot A", OUTPUT_DIR / "plot1_aisle_price.png"),
                ("Plot B", OUTPUT_DIR / "plot2_organic_mix.png"),
                ("Plot C", OUTPUT_DIR / "plot3_aisle_strip.png"),
            ],
            paragraph,
            OUTPUT_DIR / "checkpoint_submission.pdf",
        )
        print("saved checkpoint_submission.pdf")


if __name__ == "__main__":
    main()
