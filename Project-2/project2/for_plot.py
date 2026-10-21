"""FOR the proposition: growth rate against starting income, with a weighted-share inset."""
from __future__ import annotations

import numpy as np
import pandas as pd
from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter

from project2.config import END, START
from project2.data import QUARTER_NAMES, QUARTERS
from project2.theme import DARK, QUARTER_COLORS, add_titles, money, new_figure, share_inset

# Countries named on the chart, with label offsets in points (dx, dy).
LABELS: dict[str, tuple[int, int]] = {
    "CHN": (10, 8),
    "IND": (8, -16),
    "VNM": (8, 6),
    "POL": (-8, 8),
    "IRL": (8, -14),
    "COD": (8, -3),
}

# Bubble area in points^2 grows with the square root of population.
BUBBLE_SCALE: float = 1 / 22


def build_for_plot(table: pd.DataFrame, trend: tuple[float, float],
                   share_start: float, share_end: float) -> Figure:
    """Scatter of each country's growth rate against its starting income.

    Args:
        table: Output of :func:`project2.data.country_table`.
        trend: ``(slope, intercept)`` from :func:`project2.data.trend_line`.
        share_start: Weighted share of the lower three quarters in ``START``, all countries.
        share_end: The same share in ``END``.

    Returns:
        The finished figure.
    """
    fig, ax = new_figure()
    # Largest bubbles first, so small countries are drawn on top and stay visible.
    by_size = table.sort_values("pop_end", ascending=False)
    ax.scatter(by_size["gdp_start"], by_size["cagr"], s=np.sqrt(by_size["pop_end"]) * BUBBLE_SCALE,
               c=by_size["quarter"].map(QUARTER_COLORS), alpha=0.65, edgecolor="white", linewidth=0.5)
    for q in QUARTERS:  # legend entries only
        ax.scatter([], [], s=120, c=QUARTER_COLORS[q], alpha=0.65, label=QUARTER_NAMES[q])

    slope, intercept = trend
    xs = np.linspace(np.log10(table["gdp_start"].min()), np.log10(table["gdp_start"].max()), 50)
    ax.plot(10 ** xs, intercept + slope * xs, color=DARK, lw=1.8, ls="--")
    ax.axhline(0, color="#999999", lw=0.8)
    ax.set_ylim(-2.4, 12.5)  # headroom above the data for the inset

    ax.set_xscale("log")
    ax.set_xticks([300, 1000, 3000, 10000, 30000, 100000])
    ax.xaxis.set_major_formatter(FuncFormatter(money))
    ax.set_xlabel(f"GDP per capita in {START} (log scale)", fontsize=10.5)
    ax.set_ylabel(f"Average annual growth in GDP per capita, {START}-{END} (%)", fontsize=10)

    for code, (dx, dy) in LABELS.items():
        ax.annotate(table.loc[code, "name"], (table.loc[code, "gdp_start"], table.loc[code, "cagr"]),
                    xytext=(dx, dy), textcoords="offset points", fontsize=8.5, color=DARK,
                    ha="right" if dx < 0 else "left")

    ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=4, frameon=False, fontsize=9,
              handletextpad=0.3, columnspacing=1.6)
    share_inset(fig, (0.68, 0.535, 0.17, 0.14), share_start, share_end,
                "Income of the other three quarters\nas a share of the richest quarter\n(population-weighted)")
    add_titles(fig, "Countries that started poorer have grown faster",
               f"Average annual growth in GDP per capita, {START}-{END}, against each country's "
               f"{START} level.\nBubble size shows population; the dashed line is the trend across all "
               f"{len(table)} countries.")
    return fig
