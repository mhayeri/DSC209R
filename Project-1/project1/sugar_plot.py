"""Plot 3: sugar content by processing class."""
from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

import altair as alt
import pandas as pd

from project1.theme import ACCENT, CONTEXT, DARK, apply_theme

BAR_SIZE: int = 60


def _one_decimal(value: float) -> str:
    """Format ``value`` to one decimal, rounding half up like the chart's own labels."""
    return str(Decimal(str(value)).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))


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
        title="Processing class (predicted NOVA classification)",
        axis=alt.Axis(labelAngle=0, labelLineHeight=14, labelExpr="split(datum.label, '\\n')"),
    )
    iqr = (
        alt.Chart(summary)
        .mark_bar(size=BAR_SIZE, opacity=0.7)
        .encode(
            x=x,
            y=alt.Y("q1:Q", title="Sugar (g per 100 g of product)"),
            y2="q3:Q",
            color=alt.condition("datum.FPro_class == 3", alt.value(ACCENT), alt.value(CONTEXT)),
        )
    )
    median = (
        alt.Chart(summary)
        .mark_tick(color=DARK, thickness=4, size=BAR_SIZE)
        .encode(x=x, y="med:Q")
    )
    median_labels = (
        alt.Chart(summary)
        .mark_text(dx=48, align="left", color=DARK, fontSize=13, fontWeight="bold")
        .encode(x=x, y="med:Q", text=alt.Text("med:Q", format=".1f"))
    )
    top_median = summary["med"].max()
    other_median = summary["med"].drop(summary["med"].idxmax()).max()
    title = alt.TitleParams(
        "Sugar jumps only in the ultra-processed class",
        subtitle=[
            "Bar = middle 50% of items (25th-75th percentile); dark tick = median, labeled "
            f"({_one_decimal(top_median)} g in class 3 vs {_one_decimal(other_median)} g or less elsewhere).",
            f"Items with sugar > 100 g/100 g (data errors, {n_removed} rows) removed.",
        ],
    )
    return apply_theme((iqr + median + median_labels).properties(width=560, height=380, title=title))
