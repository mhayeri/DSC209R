"""Plot 2: distribution of the processing score at each store."""
from __future__ import annotations

import altair as alt
import pandas as pd

from project1.data import STORE_LABELS, STORE_ORDER
from project1.theme import ACCENT, DARK, GREY, apply_theme

# Scores at or above this are drawn in the accent color as "heavily processed".
HEAVY_THRESHOLD: float = 0.8


def build_store_plot(
    histogram: pd.DataFrame, medians: pd.DataFrame, n_items: int
) -> alt.TopLevelMixin:
    """Stack one histogram per store, sharing the processing-score axis.

    Args:
        histogram: Output of :func:`project1.data.store_histogram`.
        medians: Output of :func:`project1.data.store_medians`.
        n_items: Number of products behind the histograms, quoted in the subtitle.

    Returns:
        A themed vertical concatenation of three bar charts.
    """
    labels = [STORE_LABELS[s] for s in STORE_ORDER]
    panels: list[alt.Chart] = []
    for i, label in enumerate(labels):
        is_last = i == len(labels) - 1
        bars = (
            alt.Chart(histogram[histogram["store_label"] == label])
            .mark_bar()
            .encode(
                x=alt.X(
                    "lo:Q",
                    bin="binned",
                    title="Food Processing Score (0 = least, 1 = most processed)" if is_last else None,
                ),
                x2="hi:Q",
                y=alt.Y("share:Q", title="% of items"),
                color=alt.condition(
                    f"datum.lo >= {HEAVY_THRESHOLD}", alt.value(ACCENT), alt.value(GREY)
                ),
            )
        )
        median = medians[medians["store_label"] == label]
        rule = (
            alt.Chart(median)
            .mark_rule(color=DARK, strokeWidth=2)
            .encode(x="med:Q")
        )
        caption = (
            alt.Chart(median)
            .mark_text(align="right", dx=-5, baseline="top", color=DARK, fontSize=12)
            .encode(x="med:Q", y=alt.value(4), text="text:N")
        )
        panels.append(
            alt.layer(bars, rule, caption).properties(
                width=640,
                height=130,
                title=alt.TitleParams(label, anchor="start", fontSize=14, color=DARK),
            )
        )
    title = alt.TitleParams(
        "Whole Foods stocks far more minimally processed food than Walmart or Target",
        subtitle=(
            f"Histogram of Food Processing Score per store (20 bins, all {n_items:,} items); "
            f"red = score {HEAVY_THRESHOLD} or higher (heavily processed)."
        ),
    )
    return apply_theme(alt.vconcat(*panels).properties(title=title))
