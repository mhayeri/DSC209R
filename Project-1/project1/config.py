"""Paths and tunable constants shared across the Project 1 modules."""
from __future__ import annotations

from pathlib import Path

PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent
DATA_PATH: Path = PROJECT_ROOT / "data" / "grocerydb.csv"
OUTPUT_DIR: Path = PROJECT_ROOT / "outputs"

# Rendered PNGs are saved at this multiple of the chart's pixel size.
SCALE_FACTOR: int = 2

# Categories with fewer priced items than this are too thin for a stable median.
MIN_CATEGORY_ITEMS: int = 20

# Coffee beans are sold with ~0 kcal listed, which makes price per calorie meaningless.
EXCLUDED_CATEGORIES: tuple[str, ...] = ("coffee-beans-wf",)
