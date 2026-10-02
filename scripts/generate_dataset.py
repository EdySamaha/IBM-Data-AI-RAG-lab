#!/usr/bin/env python3
"""
Generate data/cod_landings_nl.csv — the Newfoundland cod-fishery dataset
used by both lab tracks.

The series is a *realistic synthetic reconstruction* built for teaching, not
official DFO statistics. It is deterministic (seeded) so re-running this
script always reproduces the same CSV. The shape follows the real history of
the Northern cod fishery:

    ~260k tonnes in the mid-1950s  ->  peak ~810k in 1968 (foreign fleets)
    ->  steep 1970s decline  ->  partial 1980s recovery  ->  late-'80s slide
    ->  the July 1992 moratorium (collapse)  ->  near-zero afterward, with a
        small recent uptick under a limited stewardship fishery.

Columns (exactly what the notebooks and SQL expect):
    year              INT      calendar year, 1955-2024
    landings_tonnes   DOUBLE   reported cod landings, tonnes
    licensed_fishers  INT      licensed cod fishers that year
    fishery_status    VARCHAR  short status label (see STATUS below)

Usage:
    python scripts/generate_dataset.py
"""
from __future__ import annotations

import csv
import random
from pathlib import Path

SEED = 1992  # deterministic output
YEAR_START, YEAR_END = 1955, 2024
MORATORIUM_YEAR = 1992

# (year, value) anchor points; values between anchors are linearly interpolated.
LANDINGS_ANCHORS = [
    (1955, 260_000), (1960, 350_000), (1965, 620_000), (1968, 810_000),
    (1972, 450_000), (1975, 300_000), (1977, 210_000), (1980, 230_000),
    (1985, 260_000), (1988, 240_000), (1990, 190_000), (1991, 170_000),
    (1992, 75_000),  (1993, 12_000),  (1995, 5_000),   (2000, 7_000),
    (2005, 10_000),  (2010, 13_000),  (2015, 16_000),  (2020, 18_000),
    (2024, 20_000),
]

FISHERS_ANCHORS = [
    (1955, 22_000), (1968, 31_000), (1980, 35_000), (1990, 28_000),
    (1992, 24_000), (1993, 6_000),  (2000, 4_500),  (2010, 3_800),
    (2024, 3_000),
]


def interpolate(anchors: list[tuple[int, int]], year: int) -> float:
    """Piecewise-linear value for `year` across the (year, value) anchors."""
    if year <= anchors[0][0]:
        return float(anchors[0][1])
    if year >= anchors[-1][0]:
        return float(anchors[-1][1])
    for (y0, v0), (y1, v1) in zip(anchors, anchors[1:]):
        if y0 <= year <= y1:
            frac = (year - y0) / (y1 - y0)
            return v0 + frac * (v1 - v0)
    return float(anchors[-1][1])  # unreachable


def status_for(year: int) -> str:
    """Short, human-readable status label for a given year."""
    if year <= 1963:
        return "commercial"
    if year <= 1971:
        return "peak"
    if year == MORATORIUM_YEAR:
        return "moratorium declared"
    if year < MORATORIUM_YEAR:
        return "declining"
    if year <= 2006:
        return "moratorium"
    return "limited stewardship fishery"


def main() -> None:
    rng = random.Random(SEED)
    out_path = Path(__file__).resolve().parents[1] / "data" / "cod_landings_nl.csv"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    for year in range(YEAR_START, YEAR_END + 1):
        base_landings = interpolate(LANDINGS_ANCHORS, year)
        # +/- ~3% deterministic jitter so the line looks like real data,
        # not a textbook curve. The moratorium year is left clean for clarity.
        jitter = 1.0 if year == MORATORIUM_YEAR else (1.0 + rng.uniform(-0.03, 0.03))
        landings = round(base_landings * jitter, 1)

        fishers = int(round(interpolate(FISHERS_ANCHORS, year)
                            * (1.0 + rng.uniform(-0.02, 0.02))))

        rows.append((year, landings, fishers, status_for(year)))

    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["year", "landings_tonnes", "licensed_fishers", "fishery_status"])
        writer.writerows(rows)

    peak = max(rows, key=lambda r: r[1])
    print(f"Wrote {len(rows)} rows to {out_path}")
    print(f"Peak: {peak[1]:,.0f} tonnes in {peak[0]}")
    print(f"1992 (moratorium): {next(r[1] for r in rows if r[0] == 1992):,.0f} tonnes")


if __name__ == "__main__":
    main()
