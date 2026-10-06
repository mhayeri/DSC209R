"""Loading and transforming the GroceryDB table for each chart."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from project1.config import DATA_PATH, EXCLUDED_CATEGORIES, MIN_AISLE_ITEMS, MIN_THIRDS_GAP

# Plot 3 shows this many of the largest aisles.
STRIP_AISLES: int = 20

# Products are spread up to this fraction of a row above and below its center.
JITTER_HALF_HEIGHT: float = 0.32
JITTER_SEED: int = 209

# Class names follow the course's description of the NOVA classification.
# A newline marks where a long name may wrap.
CLASS_LABELS: dict[int, str] = {
    0: "0: unprocessed or\nminimally processed",
    1: "1: processed culinary\ningredients",
    2: "2: processed\nfoods",
    3: "3: ultra-processed\nfood and drink",
}

# Product names matching this are counted as organic.
ORGANIC_PATTERN: str = r"\borganics?\b"
ORGANIC_GROUP: str = "Name says organic"
OTHER_GROUP: str = "Everything else"

# Cells per side of each unit chart grid; 10 gives one cell per percent.
GRID_SIDE: int = 10

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


def is_organic(df: pd.DataFrame) -> pd.Series:
    """Flag products whose name says "organic" or "organics" (any case)."""
    return df["name"].str.contains(ORGANIC_PATTERN, case=False, regex=True)


def organic_class_grid(df: pd.DataFrame, side: int = GRID_SIDE) -> pd.DataFrame:
    """Lay out each group's ultra-processed share as a square grid of cells.

    Each group (organic vs everything else) gets ``side * side`` cells, one per
    percent when ``side`` is 10. Cells are filled row by row from the top,
    with the ultra-processed cells last so they collect at the bottom.

    Args:
        df: Raw GroceryDB table.
        side: Cells per row and column.

    Returns:
        One row per cell with ``group``, ``row``, ``col``, ``ultra`` (bool),
        ``n_items`` (group size) and ``pct_ultra``.
    """
    cells_total = side * side
    organic = is_organic(df)
    rows: list[dict[str, float | int | str | bool]] = []
    for group, members in ((ORGANIC_GROUP, df[organic]), (OTHER_GROUP, df[~organic])):
        pct_ultra = (members["FPro_class"] == 3).mean() * 100
        n_ultra = round(pct_ultra * cells_total / 100)
        for i in range(cells_total):
            rows.append(
                {
                    "group": group,
                    "row": i // side,
                    "col": i % side,
                    "ultra": i >= cells_total - n_ultra,
                    "n_items": len(members),
                    "pct_ultra": pct_ultra,
                }
            )
    return pd.DataFrame(rows)


def aisle_strip(
    df: pd.DataFrame, n_aisles: int = STRIP_AISLES, seed: int = JITTER_SEED
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Every product in the largest aisles, ready to draw as a jittered strip.

    Aisles are ordered from the lowest to the highest share of ultra-processed
    items. Each product gets a fixed random vertical offset so dots with the
    same score spread out instead of stacking.

    Args:
        df: Raw GroceryDB table.
        n_aisles: How many of the largest aisles (by item count) to keep.
        seed: Seed for the vertical jitter, so the chart renders the same every time.

    Returns:
        A tuple of ``items`` (one row per product: ``label``, ``row``, ``y``,
        ``FPro``, ``ultra``) and ``aisles`` (one row per aisle: ``label``,
        ``row``, ``n``, ``pct_ultra``).
    """
    largest = df["category"].value_counts().head(n_aisles).index
    kept = df[df["category"].isin(largest)].assign(ultra=lambda d: d["FPro_class"] == 3)
    aisles = (
        kept.groupby("category")
        .agg(n=("FPro", "size"), pct_ultra=("ultra", "mean"))
        .sort_values("pct_ultra")
        .reset_index()
    )
    aisles["pct_ultra"] *= 100
    aisles["row"] = range(len(aisles))
    aisles["label"] = aisles["category"].map(aisle_label)
    rng = np.random.default_rng(seed)
    items = kept.merge(aisles[["category", "row", "label"]], on="category")
    items["y"] = items["row"] + rng.uniform(-JITTER_HALF_HEIGHT, JITTER_HALF_HEIGHT, len(items))
    return items[["label", "row", "y", "FPro", "ultra"]], aisles.drop(columns="category")
