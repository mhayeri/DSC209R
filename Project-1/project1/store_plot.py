"""Plot 2: distribution of the processing score at each store."""
from __future__ import annotations

import altair as alt
import pandas as pd

from project1.data import STORE_LABELS, STORE_ORDER
from project1.theme import DARK, GREY, apply_theme


def build_store_plot(histogram: pd.DataFrame, n_items: int) -> alt.TopLevelMixin:
    """Stack one histogram per store, sharing the processing-score axis.

    Args:
        histogram: Output of :func:`project1.data.store_histogram`.
        n_items: Number of products behind the histograms, quoted in the subtitle.

    Returns:
        A themed vertical concatenation of three bar charts.
    """
    labels = [STORE_LABELS[s] for s in STORE_ORDER]
    panels: list[alt.Chart] = []
    for i, label in enumerate(labels):
        is_last = i == len(labels) - 1
        panel = (
            alt.Chart(histogram[histogram["store_label"] == label])
            .mark_bar(color=GREY)
            .encode(
                x=alt.X(
                    "lo:Q",
                    bin="binned",
                    title="Food Processing Score (0 = least, 1 = most processed)" if is_last else None,
                ),
                x2="hi:Q",
                y=alt.Y("share:Q", title="% of items"),
            )
            .properties(
                width=640,
                height=130,
                title=alt.TitleParams(label, anchor="start", fontSize=14, color=DARK),
            )
        )
        panels.append(panel)
    title = alt.TitleParams(
        "Whole Foods stocks far more minimally processed food than Walmart or Target",
        subtitle=f"Histogram of Food Processing Score per store (20 bins, all {n_items:,} items).",
    )
    return apply_theme(alt.vconcat(*panels).properties(title=title))
