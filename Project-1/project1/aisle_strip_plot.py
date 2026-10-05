"""Plot 3: every product in the largest aisles, placed by processing score."""
from __future__ import annotations

import altair as alt
import pandas as pd

from project1.theme import ACCENT, CONTEXT, DARK, SUBTITLE, apply_theme

ROW_HEIGHT: int = 30
PLOT_WIDTH: int = 560

# Aisles at or above this ultra-processed share sit below the divider.
MOSTLY_ULTRA_PCT: float = 80.0

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
                legend=alt.Legend(
                    title=None,
                    orient="top",
                    direction="horizontal",
                    labelFontSize=12,
                    symbolOpacity=1,
                    symbolSize=120,
                ),
            ),
            tooltip=["label", alt.Tooltip("FPro:Q", format=".2f"), "kind"],
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
    share_header = (
        alt.Chart(pd.DataFrame({"text": [["% ultra-", "processed"]]}))
        .mark_text(align="left", baseline="bottom", fontSize=10, color=SUBTITLE, lineHeight=11)
        .encode(x=alt.value(PLOT_WIDTH + 12), y=alt.value(-4), text="text")
    )
    n_mostly = int((aisles["pct_ultra"] >= MOSTLY_ULTRA_PCT).sum())
    divider_y = ROW_HEIGHT * (n_rows - n_mostly)
    divider = (
        alt.Chart(pd.DataFrame({"y": [divider_y]}))
        .mark_rule(color=DARK, strokeDash=[4, 3], strokeWidth=1)
        .encode(y=alt.value(divider_y), x=alt.value(-200), x2=alt.value(PLOT_WIDTH + 55))
    )
    divider_note = (
        alt.Chart(
            pd.DataFrame(
                {"text": [f"↓ {n_mostly} of {n_rows} aisles: {MOSTLY_ULTRA_PCT:.0f}% or more ultra-processed"]}
            )
        )
        .mark_text(align="left", baseline="top", fontSize=11, fontStyle="italic", color=ACCENT)
        .encode(x=alt.value(4), y=alt.value(divider_y + 3), text="text:N")
    )
    title = alt.TitleParams(
        f"In {n_mostly} of the {n_rows} biggest aisles, at least 4 in 5 products are ultra-processed",
        subtitle=[
            f"Each dot is one product ({len(items):,} in all) in the {n_rows} aisles with the most items, "
            "placed by its Food Processing Score.",
            "Orange = predicted NOVA class 3 (ultra-processed). Class and score summarize the same model "
            "prediction differently, so the colors overlap from 0.5 to about 0.73.",
            "Dots are spread up and down at random within each row so they don't stack; "
            "height inside a row means nothing.",
        ],
        color=DARK,
    )
    return apply_theme(
        alt.layer(divider, dots, names, shares, share_header, divider_note).properties(
            width=PLOT_WIDTH, height=ROW_HEIGHT * n_rows, title=title
        )
    )
