"""Paths and tunable constants shared across the Project 1 modules."""
from __future__ import annotations

from pathlib import Path

PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent
DATA_PATH: Path = PROJECT_ROOT / "data" / "grocerydb.csv"
OUTPUT_DIR: Path = PROJECT_ROOT / "outputs"

# Rendered PNGs are saved at this multiple of the chart's pixel size.
SCALE_FACTOR: int = 2

# Aisles with fewer priced items than this are too thin to split into thirds.
MIN_AISLE_ITEMS: int = 60

# An aisle's least- and most-processed thirds must differ by at least this much in
# median processing score, or there is no real processing contrast to compare.
MIN_THIRDS_GAP: float = 0.1

# Coffee beans are sold with ~0 kcal listed, which makes price per calorie meaningless.
EXCLUDED_CATEGORIES: tuple[str, ...] = ("coffee-beans-wf",)
