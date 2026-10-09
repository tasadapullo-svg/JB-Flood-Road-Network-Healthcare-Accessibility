# Practical integration with the existing public data repository

Code target: `https://github.com/tasadapullo-svg/JB-Flood-Road-Network-Healthcare-Accessibility` (`main` inspected 2026-10-09).

## Located archived files (names can be checked by `jb-repro inspect`)

- Raw routing arcs: `03_Nature_Portfolio_Project/Supporting_Information/Archive_Extractions/D06_Routing_Graph_Arcs_Time.csv/Data_Tables/D06_Routing_Graph_Arcs_Time.csv` (currently split; restore using existing tool).
- Origin mapping: `03_Nature_Portfolio_Project/Figures/Data_Tables/D06_Origin_Access_to_RoutingGraph_Mapping.csv`.
- Hospital mapping: `03_Nature_Portfolio_Project/Figures/Data_Tables/D06_Hospital_Access_to_RoutingGraph_Mapping.csv`.
- Population origins: `03_Nature_Portfolio_Project/Supporting_Information/Data_Tables/D05A_WorldPop_Origins.csv`.
- Alternate population/snap table: `03_Nature_Portfolio_Project/Supporting_Information/Data_Tables/D05C_WorldPop_Origins_RoadSnap.csv` (split).
- Closure intervals: `03_Nature_Portfolio_Project/Supporting_Information/Data_Tables/D08_Closure_Subedge_Intervals.csv`.
- Frozen baseline QC: `03_Nature_Portfolio_Project/Supporting_Information/Data_Tables/D06R_Accessibility_Global_Summary.csv`.
- Frozen impact QC: `03_Nature_Portfolio_Project/Supporting_Information/Data_Tables/D08_Global_Accessibility_Impact_Summary.csv`.
- Frozen restoration QC: `03_Nature_Portfolio_Project/Submission_Materials/Data_Tables/D10_All_6_Recovery_Orders.csv`.

## What to check on the local computer

Run `jb-repro inspect --repo-root ...` to print current CSV headers. The current archive has both large tables and intermediate tables with different headers. *Confirm* which field identifies the stable `subedge_idx` on every directed arc. Some published tables identify route subedges while the directed graph may use a different key; if so, retrieve the exact archived bridge map before running scenarios.

Join origin population and subdistrict to the origin mapping **by unique origin_id**; assert exactly 75,149 final origin rows, no nulls and unchanged total weight. If one table uses a different ID, do not use a positional/row-number join.

Do **not** assume all `D08_Closure_Subedge_Intervals.csv` rows correspond to a fully closed source edge. The original method explicitly distinguishes full and partial affected intervals. This code can calculate bounded intervals for on-edge access points; however, any ambiguous side geometry is a verification blocker when an origin uses that edge.

## Audit gate

The output `frozen_reference_comparison.json` must show `overall: PASS` on a production dataset and discrepancies need cause analysis. The initial comparison targets are a reduced set, so after its PASS, also audit:

- 390,090 graph nodes, 775,374 directed time arcs, 14 hospitals;
- 75,149 origin-level times versus D06R corrected table (not D06 old table);
- 31/6/59/8 matched subedges J105/FT01/FT003/J46;
- FT003 travel-time/hospital switch in original origin QA;
- remaining-by-mukim and all six restoration stages;
- 27 shifted-geometry combinations using exact archived subedge ID sets;
- full input-hash manifest and exact software versions.

Only after these checks should the release be described as a verified reproducibility package for the specific paper.
