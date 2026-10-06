"""Plot 3: share of ultra-processed products in the largest aisles."""
from __future__ import annotations

import altair as alt
import pandas as pd

from project1.theme import ACCENT, CONTEXT, DARK, apply_theme

# Aisles at or above this share are drawn in the accent color.
MOSTLY_ULTRA_PCT: float = 80.0

ROW_HEIGHT: int = 24
PLOT_WIDTH: int = 520


def build_aisle_share_plot(shares: pd.DataFrame, n_products: int) -> alt.TopLevelMixin:
    """Sorted horizontal bars, one per aisle, with an 80% reference line.

    Args:
        shares: Output of :func:`project1.data.aisle_ultra_share`.
        n_products: Products across the aisles shown, quoted in the subtitle.

    Returns:
        A themed Altair chart ready to be saved.
    """
    shares = shares.assign(
        mostly=shares["pct_ultra"] >= MOSTLY_ULTRA_PCT,
        text=shares["pct_ultra"].map(lambda p: f"{p:.0f}%"),
    )
    n_mostly = int(shares["mostly"].sum())
    y = alt.Y("label:N", sort=list(shares["label"]), title=None, axis=alt.Axis(ticks=False, domain=False, labelFontSize=12))
    x = alt.X(
        "pct_ultra:Q",
        title="Products that are ultra-processed (%)",
        scale=alt.Scale(domain=[0, 100]),
        axis=alt.Axis(values=[0, 20, 40, 60, 80, 100]),
    )
    color = alt.condition("datum.mostly", alt.value(ACCENT), alt.value(CONTEXT))

    bars = alt.Chart(shares).mark_bar(height=ROW_HEIGHT - 6).encode(y=y, x=x, color=color)
    values = (
        alt.Chart(shares)
        .mark_text(align="right", dx=-5, fontSize=11, fontWeight="bold", color="white")
        .encode(y=y, x=x, text="text:N")
    )
    reference = pd.DataFrame({"pct_ultra": [MOSTLY_ULTRA_PCT], "note": ["4 in 5"]})
    rule = alt.Chart(reference).mark_rule(color=DARK, strokeDash=[4, 3]).encode(x=x)
    rule_label = (
        alt.Chart(reference)
        .mark_text(align="right", dx=-4, baseline="bottom", fontSize=11, fontStyle="italic", color=DARK)
        .encode(x=x, y=alt.value(-3), text="note:N")
    )
    title = alt.TitleParams(
        f"In {n_mostly} of the {len(shares)} biggest aisles, at least 4 in 5 products are ultra-processed",
        subtitle=[
            f"The {len(shares)} aisles with the most products ({n_products:,} products). "
            "Ultra-processed = predicted NOVA class 3.",
            f"Orange bars: {MOSTLY_ULTRA_PCT:.0f}% or more. Only cheese and fresh produce are mostly "
            "not ultra-processed.",
        ],
        color=DARK,
    )
    return apply_theme(
        alt.layer(rule, bars, values, rule_label).properties(
            width=PLOT_WIDTH, height=ROW_HEIGHT * len(shares), title=title
        )
    )
