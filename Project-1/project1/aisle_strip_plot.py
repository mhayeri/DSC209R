"""Plot 3: every product in the largest aisles, placed by processing score."""
from __future__ import annotations

import altair as alt
import pandas as pd

from project1.theme import ACCENT, CONTEXT, DARK, SUBTITLE, apply_theme

ROW_HEIGHT: int = 30
PLOT_WIDTH: int = 560

ULTRA: str = "Ultra-processed (class 3)"
NOT_ULTRA: str = "Classes 0-2"


def build_aisle_strip_plot(items: pd.DataFrame, aisles: pd.DataFrame) -> alt.TopLevelMixin:
    """Draw one jittered row of dots per aisle with its ultra-processed share.

    Args:
        items: Product rows from :func:`project1.data.aisle_strip`.
        aisles: Aisle rows from :func:`project1.data.aisle_strip`.

    Returns:
        A themed Altair chart ready to be saved.
    """
    n_rows = len(aisles)
    y_scale = alt.Scale(domain=[-0.5, n_rows - 0.5], reverse=True, nice=False, zero=False)
    no_axis = alt.Axis(labels=False, ticks=False, domain=False, grid=False, title=None)
    items = items.assign(kind=items["ultra"].map({True: ULTRA, False: NOT_ULTRA}))

    dots = (
        alt.Chart(items)
        .mark_circle(size=9, opacity=0.35)
        .encode(
            x=alt.X(
                "FPro:Q",
                title="Food Processing Score (0 = least, 1 = most processed)",
                scale=alt.Scale(domain=[0, 1]),
            ),
            y=alt.Y("y:Q", scale=y_scale, axis=no_axis),
            color=alt.Color(
                "kind:N",
                scale=alt.Scale(domain=[NOT_ULTRA, ULTRA], range=[CONTEXT, ACCENT]),
                legend=alt.Legend(title=None, orient="top", direction="horizontal", labelFontSize=12),
            ),
        )
    )
    names = (
        alt.Chart(aisles)
        .mark_text(align="right", fontSize=12, color=DARK)
        .encode(x=alt.value(-10), y=alt.Y("row:Q", scale=y_scale, axis=no_axis), text="label:N")
    )
    shares = (
        alt.Chart(aisles.assign(share_text=aisles["pct_ultra"].map(lambda p: f"{p:.0f}%")))
        .mark_text(align="left", fontSize=12, fontWeight="bold", color=ACCENT)
        .encode(x=alt.value(PLOT_WIDTH + 12), y=alt.Y("row:Q", scale=y_scale, axis=no_axis), text="share_text:N")
    )
    title = alt.TitleParams(
        "In most big aisles, almost everything is ultra-processed",
        subtitle="Each dot is one product in one of the 20 largest aisles; right column: share ultra-processed.",
        color=DARK,
    )
    return apply_theme(
        alt.layer(dots, names, shares).properties(width=PLOT_WIDTH, height=ROW_HEIGHT * n_rows, title=title)
    )
