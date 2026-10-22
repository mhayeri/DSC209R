"""Recompute every number quoted on the charts and in the report: ``python -m project2.verify``.

Works from the raw World Bank files with its own code (it does not import
``project2.data``), so a bug in the chart pipeline cannot hide here. Each quoted
string must match the recomputed value and appear in ``index.html``.
"""
from __future__ import annotations

import sys

import numpy as np
import pandas as pd

from project2.config import GDP_COLUMN, PAGE_DIR, POP_COLUMN, RAW_DIR


def main() -> int:
    """Print each check and return a non-zero exit code if any fails."""
    meta = pd.read_csv(RAW_DIR / "country_metadata.csv", encoding="utf-8-sig", index_col=False)
    real = set(meta.loc[meta["Region"].notna(), "Country Code"])
    eco = pd.read_csv(RAW_DIR / "economy-and-growth.csv", low_memory=False)
    hea = pd.read_csv(RAW_DIR / "health.csv", low_memory=False)
    eco = eco[eco["Country Code"].isin(real)]
    gdp = eco.pivot(index="Country Code", columns="Year", values=GDP_COLUMN)
    pop = hea.pivot(index="Country Code", columns="Year", values=POP_COLUMN)

    def panel(a: int, b: int) -> pd.DataFrame:
        return gdp[[a, b]].dropna()

    p = panel(1990, 2019)
    q = pd.qcut(p[1990], 4, labels=False)  # 0 = poorest
    cagr = ((p[2019] / p[1990]) ** (1 / 29) - 1) * 100
    med = p.groupby(q).median()
    change = med[2019] - med[1990]

    def corr(a: int, b: int) -> float:
        d = panel(a, b)
        g = (d[b] / d[a]) ** (1 / (b - a)) - 1
        return float(np.corrcoef(np.log10(d[a]), g)[0, 1])

    def slope(a: int, b: int) -> float:
        d = panel(a, b)
        g = ((d[b] / d[a]) ** (1 / (b - a)) - 1) * 100
        return float(np.polyfit(np.log10(d[a]), g, 1)[0])

    def share(year: int, drop: tuple[str, ...] = ()) -> float:
        lower = [c for c in p.index if q[c] < 3 and c not in drop]
        rich = [c for c in p.index if q[c] == 3]
        w = lambda cs: np.average(gdp.loc[cs, year], weights=pop.loc[cs, year])  # noqa: E731
        return float(w(lower) / w(rich))

    s_all = share(2019) - share(1990)
    s_no_chn = share(2019, ("CHN",)) - share(1990, ("CHN",))
    s_no_ind = share(2019, ("IND",)) - share(1990, ("IND",))
    q1 = cagr[q == 0]
    slope_all, intercept = np.polyfit(np.log10(p[1990]), cagr, 1)

    # (quoted text, recomputed value formatted the same way)
    checks: list[tuple[str, str]] = [
        ("162 countries", f"{len(p)} countries"),
        ("6.4%", f"{share(1990) * 100:.1f}%"),
        ("10.8%", f"{share(2019) * 100:.1f}%"),
        ("10.3%", f"{share(1990, ('CHN', 'IND')) * 100:.1f}%"),
        ("10.7%", f"{share(2019, ('CHN', 'IND')) * 100:.1f}%"),
        ("+$554", f"+${change[0]:,.0f}"),
        ("+$13,906", f"+${change[3]:,.0f}"),
        ("25 times", f"{change[3] / change[0]:.0f} times"),
        ("$29,100", f"${round((med.loc[3, 1990] - med.loc[0, 1990]) / 100) * 100:,.0f}"),
        ("$42,500", f"${round((med.loc[3, 2019] - med.loc[0, 2019]) / 100) * 100:,.0f}"),
        ("2.3%", f"{q1.median():.1f}%"),
        ("1.4%", f"{cagr[q == 3].median():.1f}%"),
        ("-0.25", f"{corr(1990, 2019):.2f}"),
        ("-0.07", f"{corr(1970, 2019):.2f}"),
        ("-0.39", f"{corr(2000, 2019):.2f}"),
        ("109 countries", f"{len(panel(1970, 2019))} countries"),
        ("6 of the 41", f"{int((q1 < 0).sum())} of the {len(q1)}"),
        ("three-quarters", "three-quarters" if 0.7 <= 1 - s_no_chn / s_all <= 0.8 else
         f"{1 - s_no_chn / s_all:.0%}"),
        ("accounts for none of it", "accounts for none of it" if s_no_ind >= s_all else "India removes some"),
        ("55 of 217", f"{len(gdp) - len(p)} of {len(gdp)}"),
        ("Afghanistan, Somalia, South Sudan, Syria and Yemen",
         "Afghanistan, Somalia, South Sudan, Syria and Yemen"
         if {"AFG", "SOM", "SSD", "SYR", "YEM"}.isdisjoint(p.index) else "one of them is in the panel"),
        ("$563", f"${med.loc[0, 1990]:,.0f}"),
        ("$1,117", f"${med.loc[0, 2019]:,.0f}"),
        ("nearly doubled", "nearly doubled" if 1.9 <= med.loc[0, 2019] / med.loc[0, 1990] < 2
         else f"x{med.loc[0, 2019] / med.loc[0, 1990]:.2f}"),
        ("grew by about half", "grew by about half" if 1.4 <= med.loc[3, 2019] / med.loc[3, 1990] <= 1.6
         else f"x{med.loc[3, 2019] / med.loc[3, 1990]:.2f}"),
        ("$29,700", f"${round(med.loc[3, 1990], -2):,.0f}"),
        ("$43,600", f"${round(med.loc[3, 2019], -2):,.0f}"),
        ("China (8.7% a year)", f"China ({cagr['CHN']:.1f}% a year)"),
        ("India (4.6%)", f"India ({cagr['IND']:.1f}%)"),
        ("China, at 8.7% a year", f"China, at {cagr['CHN']:.1f}% a year"),
        ("about $200", f"about ${round(p[1990].min(), -2):,.0f}"),
        ("about $125,000", f"about ${round(p[1990].max(), -3):,.0f}"),
        ("about 2.8 billion", f"about {(pop.loc['CHN', 2019] + pop.loc['IND', 2019]) / 1e9:.1f} billion"),
        ("about 2.6% growth", f"about {intercept + slope_all * np.log10(p[1990].min()):.1f}% growth"),
        ("about 0.9% for the richest", f"about {intercept + slope_all * np.log10(p[1990].max()):.1f}% for the richest"),
        ("over two thousand years", "over two thousand years"
         if 2000 < (med.loc[3, 2019] - med.loc[0, 2019]) / (change[0] / 29) < 3000 else "wrong"),
        ("more than a quarter of the chart", "more than a quarter of the chart"
         if change[3] / (52000 + 1500) > 0.25 else "less than a quarter"),
    ]
    print(f"1990-2000 slope {slope(1990, 2000):+.2f} (positive = richer countries grew faster then)")
    print(f"dropping India alone removes {1 - s_no_ind / s_all:.0%} of the narrowing")

    page = (PAGE_DIR / "index.html").read_text(encoding="utf-8") if (PAGE_DIR / "index.html").exists() else ""
    page = " ".join(page.split())  # HTML line wrapping must not hide a phrase
    failures = 0
    for quoted, actual in checks:
        ok_value = quoted == actual
        ok_page = not page or quoted in page
        failures += not (ok_value and ok_page)
        status = "ok" if ok_value and ok_page else ("WRONG VALUE" if not ok_value else "NOT ON PAGE")
        print(f"{status:12} {quoted:18} recomputed: {actual}")
    if slope(1990, 2000) <= 0:
        failures += 1
        print("WRONG VALUE  1990-2000 should slope the other way")
    print("all checks passed" if not failures else f"{failures} check(s) failed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
