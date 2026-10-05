"""Plot 1: price per calorie of each aisle's least and most processed thirds."""
from __future__ import annotations

import altair as alt
import pandas as pd

from project1.config import MIN_AISLE_ITEMS, MIN_THIRDS_GAP
from project1.theme import ACCENT, CONTEXT, DARK, SUBTITLE, apply_theme

LEAST: str = "Least processed third"
MOST: str = "Most processed third"

ROW_HEIGHT: int = 15
PLOT_WIDTH: int = 560

# Gap between the plot's right edge and the ratio column, in pixels.
RATIO_COLUMN_OFFSET: int = 14


def build_aisle_price_plot(thirds: pd.DataFrame) -> alt.TopLevelMixin:
    """Draw one row per aisle with a dot for each third, joined by a line.

    A ratio column on the right repeats the gap as a number, and a divider
    separates aisles where the less processed third costs more from those
    where it costs less.

    Args:
        thirds: Output of :func:`project1.data.aisle_price_thirds`, sorted by ratio.

    Returns:
        A themed Altair chart ready to be saved.
    """
    thirds = thirds.assign(
        ratio_text=thirds["ratio"].map(lambda r: f"{r:.2f}×"),
        pricier=thirds["ratio"] > 1,
    )
    n_pricier = int(thirds["pricier"].sum())
    n_aisles = len(thirds)
    order = list(thirds["label"])
    long = pd.concat(
        [
            thirds.assign(third=MOST, cents=thirds["cents_high"]),
            thirds.assign(third=LEAST, cents=thirds["cents_low"]),
        ]
    )
    y = alt.Y("label:N", sort=order, title=None, axis=alt.Axis(ticks=False, domain=False))
    x_scale = alt.Scale(type="log", domain=[10, 400])

    links = (
        alt.Chart(thirds)
        .mark_rule(color="#c9c9c9", strokeWidth=2)
        .encode(y=y, x=alt.X("cents_high:Q", scale=x_scale), x2="cents_low:Q")
    )
    dots = (
        alt.Chart(long)
        .mark_circle(size=70, opacity=1)
        .encode(
            y=y,
            x=alt.X(
                "cents:Q",
                scale=x_scale,
                title="Median price per 100 kcal (US cents, log scale)",
                axis=alt.Axis(values=[10, 20, 50, 100, 200, 400], grid=True, gridColor="#eeeeee"),
            ),
            color=alt.Color(
                "third:N",
                scale=alt.Scale(domain=[LEAST, MOST], range=[ACCENT, CONTEXT]),
                legend=alt.Legend(title=None, orient="top", direction="horizontal", labelFontSize=12),
            ),
            tooltip=["label", "third", alt.Tooltip("cents:Q", format=".0f"), "n"],
        )
    )
    ratio_x = alt.value(PLOT_WIDTH + RATIO_COLUMN_OFFSET)
    ratios = (
        alt.Chart(thirds)
        .mark_text(align="left", fontSize=11)
        .encode(
            y=y,
            x=ratio_x,
            text="ratio_text:N",
            color=alt.condition("datum.pricier", alt.value(ACCENT), alt.value(SUBTITLE)),
        )
    )
    ratio_header = (
        alt.Chart(pd.DataFrame({"text": [["Least ÷ most", "processed price"]]}))
        .mark_text(align="left", baseline="bottom", fontSize=10, color=SUBTITLE, lineHeight=11)
        .encode(x=ratio_x, y=alt.value(-12), text="text")
    )
    divider_y = ROW_HEIGHT * n_pricier
    divider = (
        alt.Chart(pd.DataFrame({"y": [divider_y]}))
        .mark_rule(color=DARK, strokeDash=[4, 3], strokeWidth=1)
        .encode(y=alt.value(divider_y), x=alt.value(0), x2=alt.value(PLOT_WIDTH + 70))
    )
    above_note = _divider_note(
        f"↑ {n_pricier} aisles: less processed costs more", divider_y - 5, "bottom", ACCENT
    )
    below_note = _divider_note(
        f"↓ {n_aisles - n_pricier} aisles: less processed costs the same or less", divider_y + 5, "top", SUBTITLE
    )
    median_ratio = thirds["ratio"].median()
    title = alt.TitleParams(
        "In most aisles, the less processed option costs more per calorie",
        subtitle=[
            f"In {n_pricier} of {n_aisles} aisles, the least processed third of items costs more per "
            f"100 kcal than the most processed third (median aisle: {median_ratio:.1f}× as much).",
            "Within each aisle, priced items are split into thirds by Food Processing Score; "
            "each dot is the median price of one third.",
            f"Aisles shown have {MIN_AISLE_ITEMS}+ priced items and thirds at least "
            f"{MIN_THIRDS_GAP} apart in median score; coffee beans (listed at ~0 kcal) are left out. "
            "(WF) = Whole Foods-only category.",
        ],
        color=DARK,
    )
    chart = alt.layer(links, divider, dots, ratios, ratio_header, above_note, below_note).properties(
        width=PLOT_WIDTH, height=ROW_HEIGHT * n_aisles, title=title
    )
    return apply_theme(chart)


def _divider_note(text: str, y_px: float, baseline: str, color: str) -> alt.Chart:
    """Italic caption pinned to the left end of the divider, above or below it."""
    return (
        alt.Chart(pd.DataFrame({"text": [text]}))
        .mark_text(align="left", baseline=baseline, fontSize=11, fontStyle="italic", color=color)
        .encode(x=alt.value(6), y=alt.value(y_px), text="text:N")
    )
