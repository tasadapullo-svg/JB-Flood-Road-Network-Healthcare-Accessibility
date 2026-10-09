# Method alignment and limitations of equivalence

These are methods extracted from the study description and the archived QC files; this project implements them in *new code*.

| Step | Frozen documented method | Current source | Residual uncertainty |
|---|---|---|---|
| D02 | OSM 2026-10-03 road snapshot; 10 km buffer; Malaysia routing context excluding Singapore cross-border shortcuts | Existing routing arc CSV is required | Exact D02 graph-builder parameters and duplicate subedge IDs must match |
| D05C | All 75,149 positive WorldPop cells; projected to subedges with chainage; snap offsets excluded from travel times | `D06_Origin_Access_to_RoutingGraph_Mapping.csv` joined to population table | A standalone joined canonical origins CSV is not yet included |
| D06R | One-way departure: `to_u = code != 1`, `to_v = code != -1`. Corrected baseline replaces D06. | SciPy reversed multi-sink directed Dijkstra | Endpoint hospital access flags and graph closure splitting may differ |
| D08 | Four 2025 documented restrictions, binary graph stress tests, MAR20 and MAR21, all-vehicle equivalence where B3 | Archived D08 closure-subedge/interval records | Ambiguous partial-edge treatment remains producer-sensitive |
| D10 | All six orders with stagewise graph reconstruction | Calculated by all closure subsets; population-weighted loss | Repair costs/times not modelled; geographic rank sensitivity depends on archived shifted-geometry members |
| D09 | Ordinal flood-evidence × health dependency percentile, diagnostic index separate from D08/D10 | intentionally out of primary route package | D09 was not used to derive Table 2 restoration tiers |

## Travel impedance

Time for subedge/partial connector: `minutes = length_metres / 1000 / speed_kmh × 60`.

Reference speed hierarchy (km/h) from archived D06 QC: motorway 90; trunk 80; primary 60; secondary 50; tertiary 40; unclassified 35; residential 30; service 20; living_street 15. Use actual archived directed arc weights wherever possible rather than regenerating them from modern OSM.

## Important numerical reference values (comparison only)

- D06R: reachable 1,900,604.087722 people; weighted mean 7.21085593 min; 30-min coverage 99.62533094%.
- MAR20: 544 newly unreachable origins / 4,961.0454786 people; 30-min coverage change -0.26031868 percentage points.
- MAR21/J46: zero newly unreachable in frozen model.
- FT003: 11,143.0427432 people delayed at least one minute.
- Nominal recovery: J105 3,219.757497; FT01 1,278.999497; FT003 462.288485 people.
- The J105 first-place ranking is sensitive to closure geometry and is **not** a universal policy order.

**All these numeric values are stored in `spec.py` as reference targets and are never used as simulated results.**

## No clinical or real traffic outcomes are claimed

The outputs describe conditional reference-network connectivity under all-vehicle closure-equivalent stress tests. There is no data on hospital capacity, real patient travel, floodwater depth at tested roads, patient mortality, repair duration, or traffic-congestion redistribution. Report none of these as experimentally measured.
