"""Loading and transforming the GroceryDB table for each chart."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from project1.config import DATA_PATH, EXCLUDED_CATEGORIES, MIN_CATEGORY_ITEMS

# Display order and names for the store panels, top to bottom.
STORE_ORDER: tuple[str, ...] = ("WholeFoods", "Walmart", "Target")
STORE_LABELS: dict[str, str] = {"WholeFoods": "Whole Foods", "Walmart": "Walmart", "Target": "Target"}

# price percal is dollars per kcal; the chart reports cents per 100 kcal.
DOLLARS_PER_KCAL_TO_CENTS_PER_100KCAL: int = 100 * 100


def load_grocerydb(path: Path = DATA_PATH) -> pd.DataFrame:
    """Read the GroceryDB CSV.

    Args:
        path: Location of ``grocerydb.csv``.

    Returns:
        One row per product with processing score, price and nutrition columns.
    """
    return pd.read_csv(path)


def category_price_summary(
    df: pd.DataFrame,
    min_items: int = MIN_CATEGORY_ITEMS,
    excluded: tuple[str, ...] = EXCLUDED_CATEGORIES,
) -> pd.DataFrame:
    """Aggregate products to one row per food category.

    Only products with a price per calorie are used. Categories with fewer than
    ``min_items`` such products, and any category in ``excluded``, are dropped.

    Args:
        df: Raw GroceryDB table.
        min_items: Minimum number of priced products a category needs.
        excluded: Category names to remove regardless of size.

    Returns:
        Columns ``category``, ``label``, ``n``, ``fpro`` (median processing score)
        and ``cents`` (median price in US cents per 100 kcal).
    """
    priced = df.dropna(subset=["price percal"])
    summary = (
        priced.groupby("category")
        .agg(n=("FPro", "size"), fpro=("FPro", "median"), ppc=("price percal", "median"))
        .reset_index()
    )
    summary = summary[(summary["n"] >= min_items) & ~summary["category"].isin(excluded)].copy()
    summary["cents"] = summary["ppc"] * DOLLARS_PER_KCAL_TO_CENTS_PER_100KCAL
    summary["label"] = (
        summary["category"].str.replace("-wf", "", regex=False).str.replace("-", " ")
    )
    return summary.drop(columns="ppc").reset_index(drop=True)


def log_linear_trend(summary: pd.DataFrame, n_points: int = 50) -> tuple[pd.DataFrame, float]:
    """Fit log10(price) against processing score across categories.

    Args:
        summary: Output of :func:`category_price_summary`.
        n_points: Number of evenly spaced points to return for drawing the line.

    Returns:
        A tuple of the fitted line (columns ``fpro`` and ``cents``) and the
        multiplicative change in price for each +0.1 of processing score.
    """
    slope, intercept = np.polyfit(summary["fpro"], np.log10(summary["cents"]), 1)
    xs = np.linspace(summary["fpro"].min(), summary["fpro"].max(), n_points)
    line = pd.DataFrame({"fpro": xs, "cents": 10 ** (intercept + slope * xs)})
    return line, float(10 ** (slope * 0.1))


def store_histogram(df: pd.DataFrame, n_bins: int = 20) -> pd.DataFrame:
    """Bin the processing score within each store.

    Counts are converted to a share of that store's items so stores with very
    different catalog sizes can be compared on one scale.

    Args:
        df: Raw GroceryDB table.
        n_bins: Number of equal-width bins between 0 and 1.

    Returns:
        Columns ``store_label``, ``lo``, ``hi`` (bin edges) and ``share`` (percent).
    """
    edges = np.linspace(0, 1, n_bins + 1)
    rows: list[dict[str, float | str]] = []
    for store in STORE_ORDER:
        counts, _ = np.histogram(df.loc[df["store"] == store, "FPro"], bins=edges)
        for lo, hi, count in zip(edges[:-1], edges[1:], counts):
            rows.append(
                {
                    "store_label": STORE_LABELS[store],
                    "lo": lo,
                    "hi": hi,
                    "share": count / counts.sum() * 100,
                }
            )
    return pd.DataFrame(rows)
