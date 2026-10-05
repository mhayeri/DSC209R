"""Plot 1: price per calorie of each aisle's least and most processed thirds."""
from __future__ import annotations

import altair as alt
import pandas as pd

from project1.theme import ACCENT, CONTEXT, DARK, apply_theme

LEAST: str = "Least processed third"
MOST: str = "Most processed third"

ROW_HEIGHT: int = 15


def build_aisle_price_plot(thirds: pd.DataFrame) -> alt.TopLevelMixin:
    """Draw one row per aisle with a dot for each third, joined by a line.

    Args:
        thirds: Output of :func:`project1.data.aisle_price_thirds`, sorted by ratio.

    Returns:
        A themed Altair chart ready to be saved.
    """
    order = list(thirds["label"])
    long = pd.concat(
        [
            thirds.assign(third=LEAST, cents=thirds["cents_low"]),
            thirds.assign(third=MOST, cents=thirds["cents_high"]),
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
                legend=alt.Legend(title=None, orient="top", direction="horizontal"),
            ),
            tooltip=["label", "third", alt.Tooltip("cents:Q", format=".0f")],
        )
    )
    title = alt.TitleParams(
        "In most aisles, the less processed option costs more per calorie",
        subtitle=[
            "Within each aisle, priced items are split into thirds by Food Processing Score; "
            "each dot is the median price of one third.",
        ],
        color=DARK,
    )
    return apply_theme(
        (links + dots).properties(width=560, height=ROW_HEIGHT * len(thirds), title=title)
    )
