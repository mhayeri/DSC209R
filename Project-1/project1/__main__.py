"""Render the Project 1 charts: ``python -m project1``."""
from __future__ import annotations

import altair as alt

from project1.config import OUTPUT_DIR, SCALE_FACTOR
from project1.data import (
    category_price_summary,
    load_grocerydb,
    log_linear_trend,
    store_histogram,
    store_medians,
)
from project1.price_plot import build_price_plot
from project1.store_plot import build_store_plot


def save(chart: alt.TopLevelMixin, name: str) -> None:
    """Write ``chart`` to ``outputs/<name>`` as a PNG."""
    OUTPUT_DIR.mkdir(exist_ok=True)
    chart.save(str(OUTPUT_DIR / name), scale_factor=SCALE_FACTOR)
    print(f"saved {name}")


def main() -> None:
    """Load the data and render every chart."""
    df = load_grocerydb()
    summary = category_price_summary(df)
    trend, price_ratio = log_linear_trend(summary)
    print(f"each +0.1 processing score multiplies price per calorie by {price_ratio:.2f}")
    save(build_price_plot(summary, trend), "plot1_price_vs_processing.png")
    save(build_store_plot(store_histogram(df), store_medians(df), len(df)), "plot2_processing_by_store.png")


if __name__ == "__main__":
    main()
