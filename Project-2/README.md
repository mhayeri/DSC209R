# Project 2: Persuasive or Deceptive Visualization?

Two charts built from the same World Bank data, one arguing FOR and one AGAINST the
proposition "Poorer countries are catching up with richer ones," with scored design
decisions and a reflection, for DSC 209R.

Report page: `index.html` (served at `mhayeri.github.io/DSC209R/Project-2/`).

## Layout

```
Project-2/
  index.html             the report (course template)
  for.png, against.png   the two charts, next to the page
  data/panel.csv         162 countries x 1990-2019: GDP per capita and population
  data/raw/              raw World Bank files (not committed, see below)
  project2/              plotting and verification code
  outputs/               checkpoint PDF
```

## Setup

```
pip install -r requirements.txt
```

## Usage

From this folder:

```
python -m project2            # render for.png and against.png from data/panel.csv
python -m project2 --rebuild  # rebuild data/panel.csv from data/raw/ first
python -m project2.verify     # recompute every quoted number from data/raw/ and check the page
```

`verify` uses its own code path from the raw files, so it catches mistakes in the
chart pipeline. It exits non-zero if any number on the page is wrong or missing.

## Data notes

- Source: the cleaned files in
  [light-and-salt/World-Bank-Data-by-Indicators](https://github.com/light-and-salt/World-Bank-Data-by-Indicators).
  Put `economy-and-growth/economy-and-growth.csv`, `health/health.csv` and the health
  folder's `Metadata_Country_...csv` (renamed `country_metadata.csv`) in `data/raw/`.
- Income is GDP per capita in constant 2010 US$; population is the total population.
- The panel keeps real countries only (rows with a Region in the metadata, which drops
  regional and income aggregates) that report GDP per capita in both 1990 and 2019: 162.
- Quarters rank those countries by 1990 GDP per capita (41, 40, 40, 41 countries).
- The weighted share is the population-weighted mean GDP per capita of the lower three
  quarters divided by that of the richest quarter, in the same year.
