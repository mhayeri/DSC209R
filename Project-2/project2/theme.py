"""Colors, matplotlib styling and the shared title/source/inset helpers."""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402  (backend must be set first)
from matplotlib.axes import Axes  # noqa: E402
from matplotlib.figure import Figure  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402

from project2.config import END, START  # noqa: E402

DARK: str = "#22313f"       # titles, labels, reference lines
SUBTITLE: str = "#555555"
MUTED: str = "#8a949e"      # the "before" bar and secondary marks
PANEL: str = "#f5f6f8"      # background behind the inset
QUARTER_COLORS: dict[str, str] = {
    "Q1": "#c0392b",
    "Q2": "#e08e45",
    "Q3": "#4a90b8",
    "Q4": "#1f3b57",
}

# Same figure size for both charts so they sit side by side on the page at one scale.
FIG_SIZE: tuple[float, float] = (9.0, 6.4)

SOURCE: str = (f"Source: World Bank, GDP per capita (constant 2010 US$) and population. "
               f"162 countries with GDP data in both {START} and {END};\n"
               f"quarters rank countries by {START} GDP per capita (about 40 countries each).")

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.edgecolor": "#555555",
    "axes.labelcolor": DARK,
    "xtick.color": "#444444",
    "ytick.color": "#444444",
})


def money(value: float, _pos: int | None = None) -> str:
    """Tick formatter: 12500 -> "$12,500"."""
    return f"${value:,.0f}"


def new_figure(top: float = 0.79, bottom: float = 0.15, left: float = 0.1,
               right: float = 0.97) -> tuple[Figure, Axes]:
    """A figure with room above the axes for the title, subtitle and legend."""
    fig, ax = plt.subplots(figsize=FIG_SIZE)
    fig.subplots_adjust(left=left, right=right, top=top, bottom=bottom)
    return fig, ax


def add_titles(fig: Figure, title: str, subtitle: str) -> None:
    """Left-aligned bold title, grey subtitle and the two-line source note."""
    fig.suptitle(title, x=0.06, y=0.975, ha="left", fontsize=16, fontweight="bold", color=DARK)
    fig.text(0.06, 0.905, subtitle, fontsize=10.5, color=SUBTITLE, ha="left", va="top")
    fig.text(0.06, 0.012, SOURCE, fontsize=7.8, color="#666666", ha="left")


def share_inset(fig: Figure, rect: tuple[float, float, float, float], start: float, end: float,
                title: str) -> Axes:
    """Two-bar inset: the lower group's income as a share of the richest quarter.

    Both charts draw this inset with the same scale and style so a reader can
    compare them directly; only the countries behind the numbers differ.

    Args:
        fig: Figure to draw on.
        rect: ``(left, bottom, width, height)`` in figure coordinates.
        start: Share in ``START`` as a fraction (0.064 = 6.4%).
        end: Share in ``END`` as a fraction.
        title: Two- or three-line heading above the bars.

    Returns:
        The inset axes.
    """
    left, bottom, width, height = rect
    # Light panel behind the inset and its title, so it reads as a separate chart.
    fig.patches.append(FancyBboxPatch(
        (left - 0.018, bottom - 0.065), width + 0.036, height + 0.165, transform=fig.transFigure,
        boxstyle="round,pad=0,rounding_size=0.01", facecolor=PANEL, edgecolor="#dde1e6", zorder=1))  # above the main axes
    ins = fig.add_axes(rect, zorder=2)
    ins.bar([str(START), str(END)], [start * 100, end * 100], color=[MUTED, QUARTER_COLORS["Q1"]], width=0.6)
    for i, value in enumerate((start, end)):
        ins.text(i, value * 100 + 0.4, f"{value * 100:.1f}%", ha="center", fontsize=9, color=DARK)
    ins.set_ylim(0, 14)
    ins.set_yticks([])
    ins.spines["left"].set_visible(False)
    ins.tick_params(axis="x", labelsize=8.5, length=0)
    ins.set_title(title, fontsize=8, loc="left", color=DARK, pad=6)
    ins.patch.set_alpha(0)
    return ins
