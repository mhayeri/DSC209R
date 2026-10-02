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
| `plot1_price_vs_processing.png` | The more processed the food, the cheaper its calories |
| `plot2_processing_by_store.png` | Whole Foods stocks far more minimally processed food than Walmart or Target |
| `plot3_sugar_by_class.png` | Sugar jumps only in the ultra-processed class |

## Data notes

- The CSV has 26,250 products. Several nutrient columns contain impossible values
  (for example sodium above 500,000 per 100 g), so each chart states what it filters.
- Plot 1 uses category medians for categories with 20+ items that have a price per
  calorie, and leaves out coffee beans (listed with about 0 kcal).
- Plot 3 removes 38 rows with more than 100 g of sugar per 100 g.
