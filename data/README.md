# Dataset — Newfoundland cod fishery landings (1955–2024)

`cod_landings_nl.csv` — one row per year, 1955 through 2024 (70 rows).

## Columns

| Column | Type | Description |
|---|---|---|
| `year` | INT | Calendar year, 1955–2024. |
| `landings_tonnes` | DOUBLE | Reported cod landings for that year, in tonnes. |
| `licensed_fishers` | INT | Number of licensed cod fishers that year. |
| `fishery_status` | VARCHAR | Short status label (see below). |

### `fishery_status` values

| Label | Period | Meaning |
|---|---|---|
| `commercial` | 1955–1963 | Established commercial fishery. |
| `peak` | 1964–1971 | The high-landings years (foreign offshore fleets). |
| `declining` | 1972–1991 | Long decline after the late-1960s peak. |
| `moratorium declared` | 1992 | The July 1992 cod moratorium — the collapse year. |
| `moratorium` | 1993–2006 | Fishery closed. |
| `limited stewardship fishery` | 2007–2024 | Small, tightly managed fishery. |

## The shape of the data (what the chart shows)

- ~260k tonnes in the mid-1950s, rising as offshore fleets expand.
- A peak of ~**810k tonnes in 1968**.
- A steep decline through the 1970s; partial recovery in the 1980s.
- The **1992 moratorium** — landings collapse to near zero.
- A small, slowly rising stewardship fishery in recent years.

## Provenance — please read

This is a **realistic synthetic reconstruction built for teaching**, not official
statistics. The values follow the real, well-documented history of the Northern
cod fishery (the late-1960s peak and the 1992 moratorium are real events) but the
exact year-by-year numbers are generated, not sourced from Fisheries and Oceans
Canada (DFO).

The series is produced deterministically by
[`scripts/generate_dataset.py`](../scripts/generate_dataset.py) — re-running it
reproduces this file byte-for-byte. To use **real** figures instead, replace this
CSV with your own file keeping the same four column names and types; everything
downstream (the SQL, the notebooks, the chart) will work unchanged.
