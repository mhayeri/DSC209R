"""Building the country panel and the transformations each chart uses."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from project2.config import END, GDP_COLUMN, PANEL_PATH, POP_COLUMN, RAW_DIR, START

QUARTERS: tuple[str, ...] = ("Q1", "Q2", "Q3", "Q4")
QUARTER_NAMES: dict[str, str] = {
    "Q1": "Poorest quarter",
    "Q2": "Lower-middle",
    "Q3": "Upper-middle",
    "Q4": "Richest quarter",
}


def build_panel(raw_dir: Path = RAW_DIR, out_path: Path = PANEL_PATH) -> pd.DataFrame:
    """Cut the raw World Bank files down to the countries and years the charts use.

    Keeps real countries only (regional and income aggregates have no Region in
    the metadata) that report GDP per capita in both ``START`` and ``END``.

    Args:
        raw_dir: Folder holding ``economy-and-growth.csv``, ``health.csv`` and
            ``country_metadata.csv``.
        out_path: Where to write the panel CSV.

    Returns:
        One row per country and year with ``code``, ``name``, ``year``, ``gdp``
        (GDP per capita, constant 2010 US$) and ``pop`` (total population).
    """
    meta = pd.read_csv(raw_dir / "country_metadata.csv", encoding="utf-8-sig", index_col=False)
    countries = set(meta.loc[meta["Region"].notna(), "Country Code"])
    eco = pd.read_csv(raw_dir / "economy-and-growth.csv", low_memory=False)
    hea = pd.read_csv(raw_dir / "health.csv", low_memory=False)
    eco = eco[["Country Code", "Country Name", "Year", GDP_COLUMN]].set_axis(
        ["code", "name", "year", "gdp"], axis=1)
    hea = hea[["Country Code", "Year", POP_COLUMN]].set_axis(["code", "year", "pop"], axis=1)
    panel = eco.merge(hea, on=["code", "year"], how="left")
    panel = panel[panel["code"].isin(countries) & panel["year"].between(START, END)]
    ends = panel.pivot(index="code", columns="year", values="gdp")[[START, END]].dropna()
    panel = panel[panel["code"].isin(ends.index)].sort_values(["code", "year"]).reset_index(drop=True)
    panel.to_csv(out_path, index=False)
    return panel


def load_panel(path: Path = PANEL_PATH) -> pd.DataFrame:
    """Read the panel CSV written by :func:`build_panel`."""
    return pd.read_csv(path)


def wide(panel: pd.DataFrame, column: str) -> pd.DataFrame:
    """Countries as rows, years as columns, for one panel column."""
    return panel.pivot(index="code", columns="year", values=column)


def country_table(panel: pd.DataFrame) -> pd.DataFrame:
    """One row per country with start and end income, growth rate and quarter.

    Returns:
        Indexed by country code, with ``name``, ``gdp_start``, ``gdp_end``,
        ``pop_end``, ``cagr`` (compound annual growth, percent) and ``quarter``
        (``Q1`` = poorest quarter of countries by ``START`` income).
    """
    gdp = wide(panel, "gdp")
    pop = wide(panel, "pop")
    table = pd.DataFrame({
        "name": panel.drop_duplicates("code").set_index("code")["name"],
        "gdp_start": gdp[START],
        "gdp_end": gdp[END],
        "pop_end": pop[END],
    })
    table["cagr"] = ((table["gdp_end"] / table["gdp_start"]) ** (1 / (END - START)) - 1) * 100
    table["quarter"] = pd.qcut(table["gdp_start"], 4, labels=list(QUARTERS)).astype(str)
    return table


def trend_line(table: pd.DataFrame) -> tuple[float, float]:
    """Least-squares fit of growth on log10 starting income: (slope, intercept)."""
    slope, intercept = np.polyfit(np.log10(table["gdp_start"]), table["cagr"], 1)
    return float(slope), float(intercept)


def quarter_medians(table: pd.DataFrame) -> pd.DataFrame:
    """Median start and end income of each quarter, and the change between them."""
    medians = table.groupby("quarter")[["gdp_start", "gdp_end"]].median().reindex(list(QUARTERS))
    medians["change"] = medians["gdp_end"] - medians["gdp_start"]
    return medians


def weighted_share(panel: pd.DataFrame, table: pd.DataFrame, year: int,
                   exclude: tuple[str, ...] = ()) -> float:
    """Income of the lower three quarters as a share of the richest quarter.

    Each side is a population-weighted mean of GDP per capita in ``year``, so a
    country counts in proportion to its people. Quarters stay fixed at their
    ``START`` membership.

    Args:
        panel: Output of :func:`load_panel`.
        table: Output of :func:`country_table`.
        year: Year to compare.
        exclude: Country codes dropped from the lower group.

    Returns:
        The ratio, e.g. 0.064 means the lower group averages 6.4% of the richest.
    """
    rows = panel[panel["year"] == year].set_index("code")[["gdp", "pop"]].dropna()
    lower = rows[rows.index.isin(table.index[table["quarter"] != "Q4"]) & ~rows.index.isin(exclude)]
    richest = rows[rows.index.isin(table.index[table["quarter"] == "Q4"])]
    return (np.average(lower["gdp"], weights=lower["pop"])
            / np.average(richest["gdp"], weights=richest["pop"]))
