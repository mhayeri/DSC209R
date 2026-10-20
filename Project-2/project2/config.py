"""Paths and constants shared across the Project 2 modules."""
from __future__ import annotations

from pathlib import Path

PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent
RAW_DIR: Path = PROJECT_ROOT / "data" / "raw"
PANEL_PATH: Path = PROJECT_ROOT / "data" / "panel.csv"
# The report page and its two images sit together at the project root.
PAGE_DIR: Path = PROJECT_ROOT

# Window compared in both charts. Every country in the panel has GDP per capita
# in both end years, so the two charts describe exactly the same countries.
START: int = 1990
END: int = 2019

# Countries left out of the lower group in the AGAINST chart's inset.
EXCLUDED_FROM_INSET: tuple[str, ...] = ("CHN", "IND")

# Saved PNGs use this many pixels per inch of figure size.
DPI: int = 200

# Raw World Bank column names (cleaned files from light-and-salt/World-Bank-Data-by-Indicators).
GDP_COLUMN: str = "average_value_GDP per capita (constant 2010 US$)"
POP_COLUMN: str = "average_value_Population, total"
