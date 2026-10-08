# JB Historical Flood Spatial Framework — Step 2 Analysis Grid Freeze v1.0

The outer study boundary was already frozen as the MyGDI/JUPEM Johor Bahru District polygon.
This step freezes the spatial analysis lattice before historical flood evidence is introduced.

## Frozen common origin
- X = **-3000.000 m**
- Y = **-84000.000 m**
- CRS = **EPSG:3377**

The origin is aligned to a 1 km anchor so the 250 m, 500 m, and 1000 m grids are perfectly nested.

## Grids
- **500 m × 500 m**: primary analysis grid.
- **250 m × 250 m**: fine-scale sensitivity grid.
- **1000 m × 1000 m**: coarse-scale sensitivity grid.

Each scale contains:
- full square cells intersecting the study boundary;
- clipped cells for exact in-boundary area calculations;
- permanent Grid_ID;
- row/column identifiers;
- metric coordinates;
- WGS84 centroid;
- coverage fraction;
- edge-cell flag.

## Freeze rule
Do not shift the origin, renumber cells, or regenerate the lattice using a new local bounding box after historical events are added.
