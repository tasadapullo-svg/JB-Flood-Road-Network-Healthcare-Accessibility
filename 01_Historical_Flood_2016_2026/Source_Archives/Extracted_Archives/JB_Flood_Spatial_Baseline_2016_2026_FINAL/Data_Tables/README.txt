JB Flood Spatial Baseline 2016–2026 FINAL
Generated: 2026-10-06

FROZEN RULE
1) Evidence-supported spatial location -> complete coordinate / retain traceable evidence -> PLOT.
2) Insufficient spatial evidence -> retain historical event -> UNRESOLVED / DO NOT PLOT.
3) Do not substitute nearby schools, estates, same-name localities, administrative centroids, or arbitrary buffered polygons.
4) Closed Polygon_ID is an analysis/community/facility boundary and is NOT automatically an observed inundation footprint.
5) Roads are not converted to flood polygons without evidence for the affected start/end segment.

CORE QA
- Event-location records: 346
- Annual spatial-object records: 297
- GIS-ready annual point records: 241
- Blank-coordinate unresolved annual records: 43
- Coordinates present but non-strict annual records: 13
- Fixed baseline points: 45 / 45 PASS
- Formal closed polygons: 14 / 14 PASS
- Consolidated master locations: 211
- 2026 data are partial through 2026-10-06.

TRACEABILITY CHAIN
Event -> Year -> Standardized Location -> Point -> Area -> Polygon -> Evidence -> Plot Status

DIRECTORY
01_Master/
  JB_Flood_Master_2016_2026.xlsx
  GIS_Plot_Ready.xlsx
  Unresolved_Do_Not_Plot.xlsx
02_Points/
  All_Validated_Points.xlsx
  All_Validated_Points.geojson
  All_Annual_Plot_Ready_Points.geojson
  Fixed45_Validated_Points.geojson
03_Areas/
  All_Area_Objects.xlsx
  Area_Status.xlsx
04_Closed_Polygons/
  All_Validated_Polygons.xlsx
  All_Validated_Polygons.geojson
  Polygon_QA.xlsx
05_By_Year/
  2016 ... 2026 standardized workbooks
06_Event_Location_Link/
  Event_Location_Polygon_Link.xlsx
07_QA/
  Spatial_Completeness_QA.xlsx
  Unresolved_List.xlsx
08_Source_Archive/
  Frozen annual source package, v001 45-point baseline, and final coordinate audit.

IMPORTANT
- Frequency classes (1–3 / 4–6 / >=7) in the consolidated master are based on the 2016–2026 event-location inventory after cross-year consolidation.
- Fixed45 evidence is retained as a separate baseline layer and is not added again to event counts, preventing double-counting.
- Unresolved records remain valid historical event evidence but are excluded from the formal point map.
