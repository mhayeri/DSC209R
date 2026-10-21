"""AGAINST the proposition: dollars added per quarter, with a weighted-share inset."""
from __future__ import annotations

import pandas as pd
from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter

from project2.config import END, START
from project2.data import QUARTER_NAMES, QUARTERS
from project2.theme import DARK, QUARTER_COLORS, add_titles, money, new_figure, share_inset

# Vertical position of each quarter's row, richest at the top.
ROW: dict[str, int] = {"Q4": 3, "Q3": 2, "Q2": 1, "Q1": 0}


def round_to(value: float, step: int) -> int:
    """Round to the nearest ``step`` (e.g. 29,124 -> 29,100 for step 100)."""
    return int(round(value / step) * step)


def build_against_plot(medians: pd.DataFrame, share_start: float, share_end: float,
                       excluded_names: str) -> Figure:
    """Dumbbell chart of each quarter's median income in the start and end years.

    Args:
        medians: Output of :func:`project2.data.quarter_medians`.
        share_start: Weighted share of the lower three quarters in ``START``,
            without the excluded countries.
        share_end: The same share in ``END``.
        excluded_names: Readable names of the excluded countries, for the inset title.

    Returns:
        The finished figure.
    """
    fig, ax = new_figure(left=0.17)
    for q in QUARTERS:
        start, end, y = medians.loc[q, "gdp_start"], medians.loc[q, "gdp_end"], ROW[q]
        ax.plot([start, end], [y, y], color=QUARTER_COLORS[q], lw=3.2, solid_capstyle="round", zorder=2)
        ax.scatter([start], [y], s=80, facecolor="white", edgecolor=QUARTER_COLORS[q], lw=2, zorder=3)
        ax.scatter([end], [y], s=80, color=QUARTER_COLORS[q], zorder=3)
        ax.text(end + 900, y, f"+${medians.loc[q, 'change']:,.0f}", va="center", fontsize=11.5,
                fontweight="bold", color=QUARTER_COLORS[q])

    ax.set_yticks([ROW[q] for q in QUARTERS])
    ax.set_yticklabels([QUARTER_NAMES[q] for q in QUARTERS], fontsize=10.5)
    ax.set_ylim(-0.5, 3.5)
    ax.set_xlim(-1500, 52000)
    ax.xaxis.set_major_formatter(FuncFormatter(money))
    ax.set_xlabel("Median GDP per capita (constant 2010 US dollars)", fontsize=10.5)
    ax.grid(axis="x", color="#e5e5e5")
    ax.set_axisbelow(True)

    # Key for the two dot styles, in the same spot as the FOR chart's legend.
    ax.scatter([], [], s=80, facecolor="white", edgecolor=DARK, lw=2, label=str(START))
    ax.scatter([], [], s=80, color=DARK, label=str(END))
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=2, frameon=False, fontsize=9.5,
              handletextpad=0.3, columnspacing=1.6)

    share_inset(fig, (0.68, 0.3, 0.17, 0.14), share_start, share_end,
                f"Income of the other three quarters\nas a share of the richest quarter\n"
                f"(population-weighted, without\n{excluded_names})")
    gap_start = medians.loc["Q4", "gdp_start"] - medians.loc["Q1", "gdp_start"]
    gap_end = medians.loc["Q4", "gdp_end"] - medians.loc["Q1", "gdp_end"]
    usd = "\\$"  # escaped so matplotlib does not read paired dollar signs as math mode
    add_titles(fig, f"Median income per person by starting-income quarter, {START}-{END}",
               f"Median GDP per capita of each quarter of countries, {START} and {END}. The gap between "
               f"the richest and\npoorest quarters' medians grew from {usd}{round_to(gap_start, 100):,} "
               f"to {usd}{round_to(gap_end, 100):,}.")
    return fig
