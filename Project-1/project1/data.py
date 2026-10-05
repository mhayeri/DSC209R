"""Loading and transforming the GroceryDB table for each chart."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from project1.config import DATA_PATH, EXCLUDED_CATEGORIES, MIN_AISLE_ITEMS, MIN_THIRDS_GAP

# Display order and names for the store panels, top to bottom.
STORE_ORDER: tuple[str, ...] = ("WholeFoods", "Walmart", "Target")
STORE_LABELS: dict[str, str] = {"WholeFoods": "Whole Foods", "Walmart": "Walmart", "Target": "Target"}

# Sugar per 100 g of product cannot exceed 100 g, so larger values are entry errors.
MAX_SUGAR_G_PER_100G: float = 100.0

# Class names follow the course's description of the NOVA classification.
# A newline in a name wraps the axis label onto two lines.
CLASS_LABELS: dict[int, str] = {
    0: "0: unprocessed or\nminimally processed",
    1: "1: processed culinary\ningredients",
    2: "2: processed\nfoods",
    3: "3: ultra-processed\nfood and drink",
}

# Readable aisle names. Categories ending in -wf exist only in the Whole Foods data
# and overlap a general category, so they say "(WF)" to keep the two apart.
AISLE_NAMES: dict[str, str] = {
    "baby-food": "Baby food",
    "baking": "Baking",
    "bread": "Bread",
    "breakfast": "Breakfast foods",
    "cakes": "Cakes",
    "cereal": "Cereal",
    "cheese": "Cheese",
    "coffee-beans-wf": "Coffee beans (WF)",
    "cookies-biscuit": "Cookies & biscuits",
    "culinary-ingredients": "Oils, vinegar & cooking basics",
    "dairy-yogurt-drink": "Yogurt & dairy drinks",
    "dressings": "Dressings",
    "drink-coffee": "Coffee drinks",
    "drink-juice": "Juice",
    "drink-juice-wf": "Juice (WF)",
    "drink-shakes-other": "Shakes & other drinks",
    "drink-soft-energy-mixes": "Soda, energy & drink mixes",
    "drink-tea": "Tea",
    "drink-water-wf": "Water (WF)",
    "eggs-wf": "Eggs (WF)",
    "ice-cream-dessert": "Ice cream & frozen dessert",
    "jerky": "Jerky",
    "mac-cheese": "Mac & cheese",
    "meat-packaged": "Packaged meat",
    "meat-poultry-wf": "Fresh meat & poultry (WF)",
    "milk-milk-substitute": "Milk & milk substitutes",
    "muffins-bagels": "Muffins & bagels",
    "nuts-seeds-wf": "Nuts & seeds (WF)",
    "pasta-noodles": "Pasta & noodles",
    "pastry-chocolate-candy": "Pastry, chocolate & candy",
    "pizza": "Pizza",
    "prepared-meals-dishes": "Prepared meals",
    "produce-beans-wf": "Produce & beans (WF)",
    "produce-packaged": "Packaged produce",
    "pudding-jello": "Pudding & jello",
    "rice-grains-packaged": "Packaged rice & grains",
    "rice-grains-wf": "Rice & grains (WF)",
    "rolls-buns-wraps": "Rolls, buns & wraps",
    "salad": "Salad",
    "sauce-all": "Sauces",
    "sausage-bacon": "Sausage & bacon",
    "seafood": "Seafood",
    "seafood-wf": "Seafood (WF)",
    "snacks-bars": "Snack bars",
    "snacks-chips": "Chips",
    "snacks-dips-salsa": "Dips & salsa",
    "snacks-mixes-crackers": "Crackers & snack mixes",
    "snacks-nuts-seeds": "Snack nuts & seeds",
    "snacks-popcorn": "Popcorn",
    "soup-stew": "Soup & stew",
    "spices-seasoning": "Spices & seasoning",
    "spread-squeeze": "Spreads",
}

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


def aisle_label(category: str) -> str:
    """Readable aisle name for a GroceryDB category, falling back to the raw name."""
    return AISLE_NAMES.get(category, category.replace("-", " "))


def aisle_price_thirds(
    df: pd.DataFrame,
    min_items: int = MIN_AISLE_ITEMS,
    min_gap: float = MIN_THIRDS_GAP,
    excluded: tuple[str, ...] = EXCLUDED_CATEGORIES,
) -> pd.DataFrame:
    """Compare the cheapest-to-eat end of each aisle with its least processed end.

    Within each category, priced items are split by Food Processing Score into
    the least processed third and the most processed third, and the median
    price per 100 kcal of each third is taken.

    Args:
        df: Raw GroceryDB table.
        min_items: Minimum number of priced items an aisle needs.
        min_gap: Minimum difference in median processing score between the two thirds.
        excluded: Category names to remove regardless of size.

    Returns:
        One row per aisle with ``category``, ``label``, ``n``, ``fpro_low``,
        ``fpro_high`` (median score of each third), ``cents_low``, ``cents_high``
        (median US cents per 100 kcal of each third) and ``ratio`` (low / high).
    """
    priced = df[(df["price percal"] > 0) & ~df["category"].isin(excluded)]
    rows: list[dict[str, float | str | int]] = []
    for category, items in priced.groupby("category"):
        if len(items) < min_items:
            continue
        low = items[items["FPro"] <= items["FPro"].quantile(1 / 3)]
        high = items[items["FPro"] >= items["FPro"].quantile(2 / 3)]
        rows.append(
            {
                "category": category,
                "label": aisle_label(category),
                "n": len(items),
                "fpro_low": low["FPro"].median(),
                "fpro_high": high["FPro"].median(),
                "cents_low": low["price percal"].median() * DOLLARS_PER_KCAL_TO_CENTS_PER_100KCAL,
                "cents_high": high["price percal"].median() * DOLLARS_PER_KCAL_TO_CENTS_PER_100KCAL,
            }
        )
    thirds = pd.DataFrame(rows)
    thirds = thirds[thirds["fpro_high"] - thirds["fpro_low"] >= min_gap].copy()
    thirds["ratio"] = thirds["cents_low"] / thirds["cents_high"]
    return thirds.sort_values("ratio", ascending=False).reset_index(drop=True)


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


def store_medians(df: pd.DataFrame) -> pd.DataFrame:
    """Median processing score for each store.

    Args:
        df: Raw GroceryDB table.

    Returns:
        Columns ``store_label``, ``med`` and ``text`` (a ready-made annotation).
    """
    meds = df.groupby("store")["FPro"].median().round(2)
    out = pd.DataFrame(
        {
            "store_label": [STORE_LABELS[s] for s in STORE_ORDER],
            "med": [meds[s] for s in STORE_ORDER],
        }
    )
    out["text"] = "median " + out["med"].astype(str)
    return out


def sugar_by_class(
    df: pd.DataFrame, max_sugar: float = MAX_SUGAR_G_PER_100G
) -> tuple[pd.DataFrame, int]:
    """Summarize sugar content within each processing class.

    Args:
        df: Raw GroceryDB table.
        max_sugar: Rows with more sugar than this (g per 100 g) are removed as errors.

    Returns:
        A tuple of the summary and the number of rows removed. The summary has
        columns ``label``, ``q1``, ``med``, ``q3`` and ``n``, one row per class.
    """
    valid = df[df["Sugars, total"].notna() & (df["Sugars, total"] <= max_sugar)]
    summary = (
        valid.groupby("FPro_class")["Sugars, total"]
        .agg(
            q1=lambda v: v.quantile(0.25),
            med="median",
            q3=lambda v: v.quantile(0.75),
            n="size",
        )
        .reset_index()
    )
    summary["label"] = summary["FPro_class"].astype(int).map(CLASS_LABELS)
    return summary, len(df) - len(valid)
