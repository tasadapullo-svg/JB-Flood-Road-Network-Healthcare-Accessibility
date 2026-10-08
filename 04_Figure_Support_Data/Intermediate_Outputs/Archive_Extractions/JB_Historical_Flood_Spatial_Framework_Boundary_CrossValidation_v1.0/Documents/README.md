# JB Historical Flood Spatial Framework — Boundary Cross-Validation v1.0

This package freezes the outer GIS study boundary before any historical flood-zone classification.

## Decision
The final master outer boundary is the existing MyGDI/JUPEM Johor Bahru District polygon.
DOSM ADM2 is retained as an independent reproducibility cross-check.

## Evidence supporting the freeze
- High DOSM–MyGDI overlap.
- Small area difference.
- Boundary deviations are generally local and limited.
- Very high agreement between the MyGDI district polygon and the union of its 8 subdistrict units.

## Flood colours fixed now, polygons later
- Severe: red, 30% opacity.
- Recurrent: yellow, 30% opacity.
- Mild: blue, 30% opacity.

These internal flood polygons must NOT be drawn from administrative boundaries. They will be generated only after geocoding and validating historical flood evidence.

## Next analytical operation
Create a fixed 500 m × 500 m primary grid clipped to JB_Study_Boundary_v1.0, then create 250 m and 1000 m sensitivity grids using exactly the same grid origin.
