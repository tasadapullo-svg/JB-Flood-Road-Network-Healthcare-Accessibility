# Explicit canonical input schema

Use CSV with header row and UTF-8 text. Large source files may first need reconstruction from `.part###` files. Arc and origin identifiers must retain their original exact values across tables. Missing fields are errors, **not** candidates for zero filling.

## 1. `edges.csv`: directed road arcs

| Column | Unit | Meaning |
|---|---|---|
| `subedge_idx` | stable ID | Undirected subedge identifier for pairing opposite directed arcs and closure mapping |
| `from_node` | stable ID | Permitted travel direction start |
| `to_node` | stable ID | Permitted travel direction end |
| `time_min` | minutes | Non-negative reference travel time for this directed arc |

One line **per permitted directed arc**, not one line per undirected road segment. Exclude prohibited links before building this table. Keep every valid OSM vertex/subedge. Multiple arcs between the same node pair are resolved by minimum travel time. `subedge_idx` must be shared with site snapping and closure-interval tables, otherwise access effects cannot be attributed to individual closures.

The published D06 graph QC describes **390,090 routing nodes** and **775,374 directed arcs after minimum-time duplicate pair resolution**; verify how the archived arc CSV labels its subedges before normalizing. If the arc data **does not include a subedge identifier**, reconstruct it from an audited, unique one-to-one mapping, not from nearest visual lines or guessed row positions.

## 2. `origins.csv`: population origins snapped on directed graph

| Column | Unit | Meaning |
|---|---|---|
| `origin_id` | text | Unique WorldPop pixel/cell ID |
| `population` | estimated people | Strictly positive, fractional values preserved |
| `subdistrict` | text | Original 8 administrative units |
| `route_subedge_idx` | ID | ID matching `edges.subedge_idx` |
| `route_node_u` | ID | Geometric subedge endpoint u |
| `route_node_v` | ID | Geometric subedge endpoint v |
| `route_edge_length_m` | metres | Metric length of projected subedge |
| `chainage_from_u_m` | metres | Projected distance along subedge from u |
| `oneway_code` | -1, 0, +1 | +1 permits u→v, -1 permits v→u, 0 permits both |
| `speed_kmh` | km/h | Speed for along-subedge approach cost |

The D06 origin mapping may need joining to D05A/D05C by **unique `origin_id`** to obtain `population` and `subdistrict`. Never aggregate the **75,149** origin cells into road segments: distinct chainages determine the one-way and closure-boundary effects. Total published weighted population: **1,905,758.5713106135**.

## 3. `hospitals.csv`: eligible hospital access points

| Column | Unit | Meaning |
|---|---|---|
| `facility_id` | ID | Unique eligible hospital ID |
| `route_subedge_idx` | ID | Graph subedge ID |
| `route_node_u`, `route_node_v` | IDs | Subedge endpoints |
| `route_edge_length_m` | m | Subedge length |
| `chainage_from_u_m` | m | Projected hospital point |
| `oneway_code` | -1,0,+1 | Same as origins |
| `speed_kmh` | km/h | Same as origins |

There are **14** eligible acute or emergency-care hospital locations in the frozen study (3 public and 11 private). Computational road projections are not necessarily the actual emergency entrances.

## 4. `closures.csv`: road blocked intervals

| Column | Unit | Meaning |
|---|---|---|
| `closure_id` | ID | Exact archived ID (e.g. `C2025_J105_7.0_7.5`) |
| `subedge_idx` | ID | Must match directed graph subedge index |
| `closure_a_from_u_m` | m or empty | Interval start in u-oriented chainage |
| `closure_b_from_u_m` | m or empty | Interval end in u-oriented chainage |

One row per affected subedge/interval. **Both endpoints empty** conservatively represents a whole-subedge block; it does **not** reconstruct unknown partial boundary sides. Archived table `D08_Closure_Subedge_Intervals.csv` contains `interval_method` and `requires_graph_split`; inspect ambiguous rows and their mapped origin populations manually. You must not claim exact replay when their side status differs from the original D08 producer handling.

## 5. Optional shifted-geometry tables

A proper 27-case sensitivity run needs `road`, `shift_label`, `subedge_idx`, `closure_a_from_u_m`, `closure_b_from_u_m` for every combination of J105 / FT01 / FT003 and shifts SIDE_A, NOMINAL, SIDE_B. The archive's `D08_Closure_Shift_Definitions.csv` contains **counts only** and cannot determine which precise edges were blocked. A new detailed interval-set reconstruction is required.

## Expected consistency gates before claiming a match

- 75,149 origins, population sum 1,905,758.5713, 14 hospitals.
- Corrected D06R reference (not deprecated D06).
- J105/FT01/FT003/J46 nominal affected-subedge counts 31/6/59/8.
- Reference arcs/nodes consistent with frozen D06 model.
- Every road closure matches exactly the correct subedge identifiers.
- A `PASS` after numerical frozen-reference comparisons plus independent checking of origin-level geometry and site assignments.
