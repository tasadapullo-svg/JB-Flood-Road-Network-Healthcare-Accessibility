# Step 5 — Physical Context Validation v1.0

## Scope
This step does NOT build a new flood-susceptibility model.
It keeps the 19 frozen historical flood-zone polygons unchanged and overlays them with independent terrain context.

## GIS zones
- Severe: 9
- Recurrent: 8
- Mild: 2
- Total: 19

The polygons are the already-frozen historical evidence-support zones.
No polygon was moved, enlarged, reduced, merged or reclassified in Step 5.

## Physical context used
- Copernicus GLO-30 elevation.
- Terrain slope.
- Relative elevation at 500 m.
- Relative elevation at 1000 m.
- Strict low-lying terrain candidate.

## Outputs
1. A clean GIS map where every F01–F19 closed zone is visibly delineated.
2. A terrain-context map showing the same closed zones over the independent low-lying terrain screen.
3. Zone-level descriptive physical-context metrics.
4. GeoPackage/GeoJSON carrying the terrain attributes for GIS inspection.

## Interpretation rule
This is contextual validation, not a predictive flood model.
Terrain consistency may support interpretation of observed flood geography, but absence of a strict low-lying pixel does not invalidate a historical flood zone because urban drainage, rainfall intensity, river/tidal effects and local infrastructure can also influence inundation.

## Important exclusions
- D09 was not used.
- No High/Very High susceptibility threshold was created.
- No RF/XGBoost or weighted susceptibility model was trained.
- F01–F19 were not tuned to improve terrain agreement.
