"""Plot 2: share of organic-named products that are ultra-processed, as unit grids."""
from __future__ import annotations

import altair as alt
import pandas as pd

from project1.data import GRID_SIDE, ORGANIC_GROUP, OTHER_GROUP
from project1.theme import ACCENT, CONTEXT, DARK, SUBTITLE, apply_theme

ULTRA: str = "Ultra-processed (NOVA class 3)"
NOT_ULTRA: str = "Not ultra-processed (classes 0-2)"

CELL_PX: int = 24
CELL_AREA: int = 400


def build_organic_plot(grid: pd.DataFrame) -> alt.TopLevelMixin:
    """Draw one 10 x 10 grid per group, each cell one percent of its items.

    Args:
        grid: Output of :func:`project1.data.organic_class_grid`.

    Returns:
        A themed horizontal concatenation of the two grids.
    """
    grid = grid.assign(kind=grid["ultra"].map({True: ULTRA, False: NOT_ULTRA}))
    color = alt.Color(
        "kind:N",
        scale=alt.Scale(domain=[ULTRA, NOT_ULTRA], range=[ACCENT, CONTEXT]),
        legend=alt.Legend(
            title=None,
            orient="bottom",
            direction="horizontal",
            labelFontSize=13,
            labelLimit=0,
            symbolType="square",
            symbolSize=200,
        ),
    )
    panels = [_grid_panel(grid[grid["group"] == group], color) for group in (ORGANIC_GROUP, OTHER_GROUP)]
    title = alt.TitleParams(
        "More than half of “organic” groceries are still ultra-processed",
        subtitle="Each square is 1% of a group's products. Organic = the product name contains "
        "“organic” or “organics”.",
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
        .encode(x=alt.X("col:O", axis=axis), y=alt.Y("row:O", axis=axis), color=color)
        .properties(
            width=CELL_PX * GRID_SIDE,
            height=CELL_PX * GRID_SIDE,
            title=alt.TitleParams(
                f"{pct_ultra:.0f}% ultra-processed",
                subtitle=f"{group} ({n_items:,} products)",
                fontSize=26,
                color=ACCENT,
                subtitleFontSize=14,
                subtitleColor=SUBTITLE,
                anchor="start",
            ),
        )
    )
