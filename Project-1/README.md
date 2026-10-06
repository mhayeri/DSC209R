# Project 1: Expository Visualization

Expository visualizations built from the GroceryDB dataset (Walmart, Target and
Whole Foods products with a Food Processing Score, price and nutrition per 100 g)
for DSC 209R.

## Layout

```
Project-1/
  data/grocerydb.csv     raw dataset
  project1/              plotting code
  outputs/               rendered charts
  writeup/               checkpoint paragraph
```

## Setup

```
pip install -r requirements.txt
```

## Usage

From this folder:

```
python -m project1
```

This renders the three charts and the checkpoint PDF into `outputs/`:

| File | Takeaway |
|---|---|
| `plot1_aisle_price.png` | Less processed food usually costs more per calorie (37 of 47 aisles; 12 familiar aisles shown) |
| `plot2_organic_mix.png` | 56% of products with "organic" in the name are still ultra-processed (vs 79% of the rest) |
| `plot3_aisle_ultra_share.png` | In 16 of the 20 biggest aisles, at least 80% of products are ultra-processed |

## Data notes

- The CSV has 26,250 products from Walmart, Target and Whole Foods.
- Plot 1 splits each aisle's priced items into thirds by Food Processing Score. The
  "37 of 47" count uses aisles with 60+ priced items whose two thirds differ by at
  least 0.1 in median score, and leaves out coffee beans (listed at about 0 kcal).
- Plot 2 counts a product as organic when its name contains "organic" or "organics".
- Plot 3 uses the 20 aisles with the most products; ultra-processed means predicted
  NOVA class 3.
