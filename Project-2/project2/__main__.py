"""Render the Project 2 charts: ``python -m project2`` (add ``--rebuild`` to remake the panel)."""
from __future__ import annotations

import sys

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from project2.against_plot import build_against_plot
from project2.config import DPI, END, EXCLUDED_FROM_INSET, PAGE_DIR, PANEL_PATH, START
from project2.data import build_panel, country_table, load_panel, quarter_medians, trend_line, weighted_share
from project2.for_plot import build_for_plot


def save(fig: Figure, name: str) -> None:
    """Write ``fig`` next to the report page as a PNG."""
    fig.savefig(PAGE_DIR / name, dpi=DPI)
    plt.close(fig)
    print(f"saved {name}")


def main() -> None:
    """Load (or rebuild) the panel and render both charts."""
    panel = build_panel() if "--rebuild" in sys.argv or not PANEL_PATH.exists() else load_panel()
    table = country_table(panel)
    print(f"{len(table)} countries, quarter sizes {table['quarter'].value_counts().sort_index().tolist()}")

    share_all = (weighted_share(panel, table, START), weighted_share(panel, table, END))
    share_ex = (weighted_share(panel, table, START, EXCLUDED_FROM_INSET),
                weighted_share(panel, table, END, EXCLUDED_FROM_INSET))
    print(f"weighted share, all: {share_all[0]:.3f} -> {share_all[1]:.3f}; "
          f"without {', '.join(EXCLUDED_FROM_INSET)}: {share_ex[0]:.3f} -> {share_ex[1]:.3f}")

    save(build_for_plot(table, trend_line(table), *share_all), "for.png")
    excluded = " and ".join(table.loc[list(EXCLUDED_FROM_INSET), "name"])
    save(build_against_plot(quarter_medians(table), *share_ex, excluded), "against.png")


if __name__ == "__main__":
    main()
