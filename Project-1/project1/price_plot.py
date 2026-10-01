"""Plot 1: price per calorie against food processing, one dot per category."""
from __future__ import annotations

import altair as alt
import pandas as pd

from project1.theme import ACCENT, DARK, GREY, apply_theme

# Categories named on the chart: the extremes plus a few recognizable foods.
HIGHLIGHT: tuple[str, ...] = (
    "meat-poultry-wf",
    "seafood-wf",
    "produce-beans-wf",
    "pasta-noodles",
    "baby-food",
    "jerky",
)


def build_price_plot(summary: pd.DataFrame) -> alt.TopLevelMixin:
    """Build the category-level price-per-calorie scatter plot.

    Args:
        summary: Output of :func:`project1.data.category_price_summary`.

    Returns:
        A themed Altair chart ready to be saved.
    """
    summary = summary.assign(highlight=summary["category"].isin(HIGHLIGHT))

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
            tooltip=["label", "n"],
        )
    )
    labels = (
        alt.Chart(summary[summary["highlight"]])
        .mark_text(align="left", dx=9, fontSize=11, color=DARK)
        .encode(x="fpro:Q", y="cents:Q", text="label:N")
    )
    title = alt.TitleParams(
        "The more processed the food, the cheaper its calories",
        subtitle=[
            f"Each dot is one of {len(summary)} food categories "
            "(categories with 20+ items priced per calorie; coffee beans excluded).",
            "Value = category median across Walmart, Target and Whole Foods items.",
        ],
    )
    return apply_theme((points + labels).properties(width=700, height=420, title=title))
