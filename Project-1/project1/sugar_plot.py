"""Plot 3: sugar content by processing class."""
from __future__ import annotations

import altair as alt
import pandas as pd

from project1.theme import ACCENT, GREY, apply_theme

BAR_SIZE: int = 60


def build_sugar_plot(summary: pd.DataFrame) -> alt.TopLevelMixin:
    """Draw each class as an interquartile bar with a median tick.

    Args:
        summary: Output of :func:`project1.data.sugar_by_class`.

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
    title = alt.TitleParams(
        "Ultra-processed foods carry several times more sugar than minimally processed ones",
        subtitle="Grey bar = middle 50% of items; red tick = median.",
    )
    return apply_theme((iqr + median).properties(width=560, height=380, title=title))
