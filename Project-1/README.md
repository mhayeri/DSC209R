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
| `plot1_aisle_price.png` | In 37 of 47 aisles, the least processed third of items costs more per calorie than the most processed third |
| `plot2_organic_mix.png` | 56% of products with "organic" in the name are still ultra-processed (vs 79% of the rest) |
| `plot3_aisle_strip.png` | In 16 of the 20 biggest aisles, at least 80% of products are ultra-processed |

## Data notes

- The CSV has 26,250 products from Walmart, Target and Whole Foods.
- Plot 1 uses aisles with 60+ priced items whose least and most processed thirds
  differ by at least 0.1 in median score, and leaves out coffee beans (listed at
  about 0 kcal).
- Plot 2 counts a product as organic when its name contains "organic" or
  "organics". Each grid uses largest-remainder rounding so its cells add up to 100.
- Plot 3 shows every product in the 20 aisles with the most items. Vertical
  position inside a row is random jitter with a fixed seed.
