"""Loading and transforming the GroceryDB table for each chart."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from project1.config import DATA_PATH, EXCLUDED_CATEGORIES, MIN_AISLE_ITEMS, MIN_THIRDS_GAP

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

# Product names matching this are counted as organic.
ORGANIC_PATTERN: str = r"\borganics?\b"
ORGANIC_GROUP: str = "Name says organic"
OTHER_GROUP: str = "Everything else"

# An aisle needs this many organic and this many other items to compare the two.
MIN_ORGANIC_COMPARE_ITEMS: int = 15

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
    """Lay out each group's processing-class mix as a square grid of cells.

    Each group (organic vs everything else) gets ``side * side`` cells, one per
    percent when ``side`` is 10. Cell counts per class use largest-remainder
    rounding so they always add up to the full grid. Cells are filled row by
    row from the top, least processed class first.

    Args:
        df: Raw GroceryDB table.
        side: Cells per row and column.

    Returns:
        One row per cell with ``group``, ``row``, ``col``, ``nova`` (class
        number), ``class_label``, ``n_items`` (group size) and ``pct_ultra``.
    """
    cells_total = side * side
    groups = df.assign(group=np.where(is_organic(df), ORGANIC_GROUP, OTHER_GROUP))
    rows: list[dict[str, float | int | str]] = []
    for group in (ORGANIC_GROUP, OTHER_GROUP):
        classes = groups.loc[groups["group"] == group, "FPro_class"].astype(int)
        shares = classes.value_counts(normalize=True).reindex(range(4), fill_value=0)
        exact = shares * cells_total
        cells = np.floor(exact).astype(int)
        leftover = cells_total - cells.sum()
        cells[(exact - cells).sort_values(ascending=False).index[:leftover]] += 1
        sequence = [nova for nova in range(4) for _ in range(cells[nova])]
        for i, nova in enumerate(sequence):
            rows.append(
                {
                    "group": group,
                    "row": i // side,
                    "col": i % side,
                    "nova": nova,
                    "class_label": CLASS_LABELS[nova].replace("\n", " "),
                    "n_items": len(classes),
                    "pct_ultra": shares[3] * 100,
                }
            )
    return pd.DataFrame(rows)


def organic_within_aisle_gap(
    df: pd.DataFrame, min_items: int = MIN_ORGANIC_COMPARE_ITEMS
) -> tuple[float, int]:
    """How much lower organic items score than other items in the same aisle.

    Args:
        df: Raw GroceryDB table.
        min_items: Items each side of the comparison needs within an aisle.

    Returns:
        The median, across aisles, of (other median score - organic median
        score), and the number of aisles compared.
    """
    flagged = df.assign(organic=is_organic(df))
    counts = flagged.groupby(["category", "organic"]).size().unstack(fill_value=0)
    medians = flagged.groupby(["category", "organic"])["FPro"].median().unstack()
    usable = (counts[True] >= min_items) & (counts[False] >= min_items)
    gaps = (medians[False] - medians[True])[usable]
    return float(gaps.median()), int(usable.sum())


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
