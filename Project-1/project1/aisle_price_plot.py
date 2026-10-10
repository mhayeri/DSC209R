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

# Snack bars get the callout because the gap holds per calorie and per gram; the
# longest bar (soup) flips per gram because soup is mostly water and few calories.
CALLOUT_AISLE: str = "snacks-bars"


def build_aisle_price_plot(thirds: pd.DataFrame, n_pricier_per_gram: int) -> alt.TopLevelMixin:
    """Draw one row per everyday aisle with a dot for each third, joined by a line.

    Args:
        thirds: Output of :func:`project1.data.aisle_price_thirds`, sorted by ratio.
        n_pricier_per_gram: Aisles where the less processed third also costs more
            per gram, from :func:`project1.data.count_pricier_per_gram`.

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
    y = alt.Y("label:N", sort=order, title="Grocery aisle", axis=alt.Axis(ticks=False, domain=False, labelFontSize=13))
    x_scale = alt.Scale(domain=[0, 220])
    x_axis = alt.Axis(values=list(range(0, 221, 40)))

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
            x=alt.X("cents:Q", scale=x_scale, title="Median price per 100 calories (US cents)", axis=x_axis),
            color=alt.Color(
                "third:N",
                scale=alt.Scale(domain=[LEAST, MOST], range=[ACCENT, CONTEXT]),
                legend=alt.Legend(title=None, orient="top", direction="horizontal", labelFontSize=13),
            ),
        )
    )
    top = shown[shown["category"] == CALLOUT_AISLE].iloc[0]
    callout = (
        alt.Chart(pd.DataFrame({"x": [top["cents_low"]], "label": [top["label"]], "text": [f"{top['ratio']:.1f}× the price of the most processed"]}))
        .mark_text(align="left", dx=12, fontSize=12, fontWeight="bold", color=ACCENT)
        .encode(x=alt.X("x:Q", scale=x_scale), y=y, text="text:N")
    )
    n_products = int(thirds["n"].sum())
    title = alt.TitleParams(
        f"Less processed food costs more per calorie in {n_pricier_all} of {n_all} aisles",
        subtitle=[
            "Products in each aisle are ranked by Food Processing Score (0 to 1, higher = more processed) and split into thirds.",
            "Each dot is the median price of the top or bottom third, in US cents per 100 kcal.",
            f"Based on {n_products:,} products with a price and calorie count in the {n_all} aisles with 60+ such products.",
            f"Coffee beans excluded. 12 aisles shown. Per 100 g instead, the less processed third costs more in {n_pricier_per_gram} of {n_all}.",
            "Source: GroceryDB (Walmart, Target and Whole Foods products).",
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
