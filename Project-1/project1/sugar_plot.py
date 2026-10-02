"""Plot 3: sugar content by processing class."""
from __future__ import annotations

import altair as alt
import pandas as pd

from project1.theme import ACCENT, GREY, apply_theme

BAR_SIZE: int = 60


def build_sugar_plot(summary: pd.DataFrame, n_removed: int) -> alt.TopLevelMixin:
    """Draw each class as an interquartile bar with a median tick.

    Args:
        summary: Output of :func:`project1.data.sugar_by_class`.
        n_removed: Rows dropped for impossible sugar values, stated in the subtitle.

    Returns:
        A themed Altair chart ready to be saved.
    """
    x = alt.X(
        "label:N",
        sort=list(summary["label"]),
        title="Processing class (dataset's NOVA-style FPro_class)",
        axis=alt.Axis(labelAngle=0),
    )
    iqr = (
        alt.Chart(summary)
        .mark_bar(size=BAR_SIZE, color=GREY, opacity=0.6)
        .encode(x=x, y=alt.Y("q1:Q", title="Sugar (g per 100 g of product)"), y2="q3:Q")
    )
    median = (
        alt.Chart(summary)
        .mark_tick(color=ACCENT, thickness=4, size=BAR_SIZE)
        .encode(x=x, y="med:Q")
    )
    median_labels = (
        alt.Chart(summary)
        .mark_text(dx=48, align="left", color=ACCENT, fontSize=12)
        .encode(x=x, y="med:Q", text=alt.Text("med:Q", format=".1f"))
    )
    top_median = summary["med"].max()
    other_median = summary["med"].drop(summary["med"].idxmax()).max()
    title = alt.TitleParams(
        "Sugar jumps only in the ultra-processed class",
        subtitle=(
            "Grey bar = middle 50% of items (25th-75th percentile); red tick = median "
            f"(labeled; {top_median:.1f} g in class 3 vs {other_median:.1f} g or less elsewhere). "
            f"Items with sugar > 100 g/100 g (data errors, {n_removed} rows) removed."
        ),
    )
    return apply_theme((iqr + median + median_labels).properties(width=560, height=380, title=title))
