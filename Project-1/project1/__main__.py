"""Render the Project 1 charts: ``python -m project1``."""
from __future__ import annotations

import altair as alt

from project1.config import OUTPUT_DIR, SCALE_FACTOR
from project1.data import category_price_summary, load_grocerydb
from project1.price_plot import build_price_plot


def save(chart: alt.TopLevelMixin, name: str) -> None:
    """Write ``chart`` to ``outputs/<name>`` as a PNG."""
    OUTPUT_DIR.mkdir(exist_ok=True)
    chart.save(str(OUTPUT_DIR / name), scale_factor=SCALE_FACTOR)
    print(f"saved {name}")


def main() -> None:
    """Load the data and render every chart."""
    df = load_grocerydb()
    save(build_price_plot(category_price_summary(df)), "plot1_price_vs_processing.png")


if __name__ == "__main__":
    main()
