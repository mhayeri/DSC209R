"""Plot 2: processing-class mix of organic-named products, as unit grids."""
from __future__ import annotations

import altair as alt
import pandas as pd

from project1.data import GRID_SIDE, ORGANIC_GROUP, OTHER_GROUP
from project1.theme import ACCENT, DARK, SUBTITLE, apply_theme

# Least processed class darkest, fading toward class 2, then the accent for
# ultra-processed so the share the title talks about stands out.
CLASS_COLORS: tuple[str, ...] = ("#1f5f8b", "#5a9fd0", "#a8cfea", ACCENT)

CELL_PX: int = 24
CELL_AREA: int = 400


def build_organic_plot(
    grid: pd.DataFrame, aisle_gap: float, n_aisles_compared: int
) -> alt.TopLevelMixin:
    """Draw one 10 x 10 grid per group, each cell one percent of its items.

    Args:
        grid: Output of :func:`project1.data.organic_class_grid`.
        aisle_gap: Median within-aisle drop in processing score for organic items.
        n_aisles_compared: Aisles behind ``aisle_gap``.

    Returns:
        A themed horizontal concatenation of the two grids.
    """
    labels = list(grid.sort_values("nova")["class_label"].unique())
    color = alt.Color(
        "class_label:N",
        title="Processing class (predicted NOVA)",
        scale=alt.Scale(domain=labels, range=list(CLASS_COLORS)),
        legend=alt.Legend(
            orient="bottom",
            columns=2,
            labelFontSize=12,
            titleFontSize=12,
            labelLimit=0,
            titleLimit=0,
            symbolType="square",
            symbolSize=200,
        ),
    )
    panels = [_grid_panel(grid[grid["group"] == group], color) for group in (ORGANIC_GROUP, OTHER_GROUP)]
    title = alt.TitleParams(
        "More than half of “organic” groceries are still ultra-processed",
        subtitle=[
            "Each square is 1% of a group's items, filled from the least processed class (top) "
            "to ultra-processed (bottom).",
            "Organic = the product name contains “organic” or “organics”. Class is GroceryDB's "
            "predicted NOVA class.",
            "Part of the gap is mix: 19% of organic items are produce vs 7% of the rest. Within the same aisle, "
            f"organic items score only {aisle_gap:.2f} lower",
            f"on the 0-1 Food Processing Score (median across {n_aisles_compared} aisles with "
            "15+ items of each kind).",
        ],
        color=DARK,
    )
    return apply_theme(alt.hconcat(*panels, spacing=60).properties(title=title))


def _grid_panel(cells: pd.DataFrame, color: alt.Color) -> alt.Chart:
    """One group's grid, headed by its ultra-processed share and item count."""
    group = cells["group"].iloc[0]
    n_items = int(cells["n_items"].iloc[0])
    pct_ultra = cells["pct_ultra"].iloc[0]
    axis = alt.Axis(labels=False, ticks=False, domain=False, title=None)
    return (
        alt.Chart(cells)
        .mark_square(size=CELL_AREA, opacity=1)
        .encode(
            x=alt.X("col:O", axis=axis),
            y=alt.Y("row:O", axis=axis),
            color=color,
            tooltip=["class_label"],
        )
        .properties(
            width=CELL_PX * GRID_SIDE,
            height=CELL_PX * GRID_SIDE,
            title=alt.TitleParams(
                f"{pct_ultra:.0f}% ultra-processed",
                subtitle=f"{group} ({n_items:,} items)",
                fontSize=26,
                color=ACCENT,
                subtitleFontSize=14,
                subtitleColor=SUBTITLE,
                anchor="start",
            ),
        )
    )
