"""Plot 1: price per calorie of each aisle's least and most processed thirds."""
from __future__ import annotations

import altair as alt
import pandas as pd

from project1.config import EVERYDAY_AISLES
from project1.theme import ACCENT, CONTEXT, DARK, SUBTITLE, apply_theme

LEAST: str = "Least processed third"
MOST: str = "Most processed third"

ROW_HEIGHT: int = 32
PLOT_WIDTH: int = 560


def build_aisle_price_plot(thirds: pd.DataFrame) -> alt.TopLevelMixin:
    """Draw one row per everyday aisle with a dot for each third, joined by a line.

    Args:
        thirds: Output of :func:`project1.data.aisle_price_thirds`, sorted by ratio.

    Returns:
        A themed Altair chart ready to be saved.
    """
    n_pricier_all = int((thirds["ratio"] > 1).sum())
    n_all = len(thirds)
    shown = thirds[thirds["category"].isin(EVERYDAY_AISLES)].reset_index(drop=True)
    order = list(shown["label"])
    long = pd.concat(
        [
            shown.assign(third=MOST, cents=shown["cents_high"]),
            shown.assign(third=LEAST, cents=shown["cents_low"]),
        ]
    )
    y = alt.Y("label:N", sort=order, title=None, axis=alt.Axis(ticks=False, domain=False, labelFontSize=13))
    x_scale = alt.Scale(domain=[0, 220])

    n_cheaper = int((shown["ratio"] <= 1).sum())
    shade = (
        alt.Chart(pd.DataFrame({"y0": [ROW_HEIGHT * (len(shown) - n_cheaper)], "y1": [ROW_HEIGHT * len(shown)]}))
        .mark_rect(color="#eeeeee")
        .encode(y=alt.value(ROW_HEIGHT * (len(shown) - n_cheaper)), y2=alt.value(ROW_HEIGHT * len(shown)))
    )
    shade_note = _note(
        "Exceptions: here the less processed option is cheaper",
        PLOT_WIDTH - 6,
        ROW_HEIGHT * (len(shown) - n_cheaper) + 4,
        "right",
        "top",
        SUBTITLE,
    )
    links = (
        alt.Chart(shown)
        .mark_rule(color="#bdbdbd", strokeWidth=3)
        .encode(y=y, x=alt.X("cents_high:Q", scale=x_scale), x2="cents_low:Q")
    )
    dots = (
        alt.Chart(long)
        .mark_circle(size=150, opacity=1)
        .encode(
            y=y,
            x=alt.X("cents:Q", scale=x_scale, title="Median price per 100 calories (US cents)"),
            color=alt.Color(
                "third:N",
                scale=alt.Scale(domain=[LEAST, MOST], range=[ACCENT, CONTEXT]),
                legend=alt.Legend(title=None, orient="top", direction="horizontal", labelFontSize=13),
            ),
        )
    )
    top = shown.iloc[0]
    callout = (
        alt.Chart(pd.DataFrame({"x": [top["cents_low"]], "label": [top["label"]], "text": [f"{top['ratio']:.1f}× the price"]}))
        .mark_text(align="left", dx=12, fontSize=12, fontWeight="bold", color=ACCENT)
        .encode(x=alt.X("x:Q", scale=x_scale), y=y, text="text:N")
    )
    title = alt.TitleParams(
        "Less processed food usually costs more per calorie",
        subtitle=[
            "Items in each aisle are split into thirds by Food Processing Score; each dot is the median "
            "price of one third.",
            f"12 familiar aisles shown. Across all {n_all} aisles with 60+ priced items, the less "
            f"processed third costs more in {n_pricier_all}.",
        ],
        color=DARK,
    )
    chart = alt.layer(shade, links, dots, callout, shade_note).properties(
        width=PLOT_WIDTH, height=ROW_HEIGHT * len(shown), title=title
    )
    return apply_theme(chart)


def _note(text: str, x_px: float, y_px: float, align: str, baseline: str, color: str) -> alt.Chart:
    """A small italic note placed at a fixed pixel position."""
    return (
        alt.Chart(pd.DataFrame({"text": [text]}))
        .mark_text(align=align, baseline=baseline, fontSize=11, fontStyle="italic", color=color)
        .encode(x=alt.value(x_px), y=alt.value(y_px), text="text:N")
    )
