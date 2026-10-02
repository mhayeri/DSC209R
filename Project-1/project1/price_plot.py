"""Plot 1: price per calorie against food processing, one dot per category."""
from __future__ import annotations

import altair as alt
import pandas as pd

from project1.theme import ACCENT, DARK, GREY, apply_theme

# Cheap, heavily processed staples called out together in a shaded box.
CLUSTER: tuple[str, ...] = (
    "cookies-biscuit",
    "cakes",
    "bread",
    "snacks-chips",
    "cereal",
)

# Categories named on the chart: the extremes plus a few recognizable foods.
HIGHLIGHT: tuple[str, ...] = (
    "meat-poultry-wf",
    "produce-beans-wf",
    "pasta-noodles",
    "baby-food",
    "jerky",
)


def build_price_plot(summary: pd.DataFrame, trend: pd.DataFrame) -> alt.TopLevelMixin:
    """Build the category-level price-per-calorie scatter plot.

    Args:
        summary: Output of :func:`project1.data.category_price_summary`.
        trend: Fitted line from :func:`project1.data.log_linear_trend`.

    Returns:
        A themed Altair chart ready to be saved.
    """
    summary = summary.assign(highlight=summary["category"].isin(HIGHLIGHT + CLUSTER))

    points = (
        alt.Chart(summary)
        .mark_circle(opacity=0.75)
        .encode(
            x=alt.X(
                "fpro:Q",
                title="Median Food Processing Score of category (0 = least, 1 = most processed)",
                scale=alt.Scale(domain=[0, 1]),
            ),
            y=alt.Y(
                "cents:Q",
                title="Median price per 100 kcal (US cents, log scale)",
                scale=alt.Scale(type="log", domain=[10, 500]),
            ),
            size=alt.Size(
                "n:Q",
                title="Items in category",
                scale=alt.Scale(domain=[20, 2000], range=[40, 700]),
                legend=alt.Legend(values=[100, 500, 1000, 2000]),
            ),
            color=alt.condition("datum.highlight", alt.value(ACCENT), alt.value(GREY)),
            tooltip=["category", "n"],
        )
    )
    labels = (
        alt.Chart(summary[summary["category"].isin(HIGHLIGHT)])
        .mark_text(align="left", dx=9, fontSize=11, color=DARK)
        .encode(x="fpro:Q", y="cents:Q", text="label:N")
    )
    trend_line = (
        alt.Chart(trend)
        .mark_line(color=DARK, strokeDash=[5, 4])
        .encode(x="fpro:Q", y="cents:Q")
    )
    callout = _cluster_callout()
    title = alt.TitleParams(
        "The more processed the food, the cheaper its calories",
        subtitle=[
            f"Each dot is one of {len(summary)} food categories "
            "(categories with 20+ items priced per calorie; coffee beans excluded).",
            "Value = category median across Walmart, Target and Whole Foods items. Dashed line: log-linear fit.",
            "Red dots are the categories named or boxed on the chart; grey dots are the rest.",
        ],
    )
    return apply_theme((callout[0] + trend_line + points + labels + callout[1]).properties(width=700, height=420, title=title))


def _cluster_callout() -> tuple[alt.Chart, alt.Chart]:
    """Build the shaded box and caption around the cheap, processed cluster.

    Returns:
        A ``(box, caption)`` pair; the box is drawn under the dots, the caption on top.
    """
    box = (
        alt.Chart(pd.DataFrame({"x0": [0.84], "x1": [1.0], "y0": [20], "y1": [48]}))
        .mark_rect(color=ACCENT, opacity=0.10)
        .encode(x="x0:Q", x2="x1:Q", y="y0:Q", y2="y1:Q")
    )
    caption = (
        alt.Chart(
            pd.DataFrame(
                {
                    "x": [0.995],
                    "y": [16.5],
                    "text": ["Cookies, cakes, bread, cereal, chips: ~30 cents per 100 kcal"],
                }
            )
        )
        .mark_text(align="right", fontSize=12, fontWeight="bold", color=ACCENT)
        .encode(x="x:Q", y="y:Q", text="text:N")
    )
    return box, caption
