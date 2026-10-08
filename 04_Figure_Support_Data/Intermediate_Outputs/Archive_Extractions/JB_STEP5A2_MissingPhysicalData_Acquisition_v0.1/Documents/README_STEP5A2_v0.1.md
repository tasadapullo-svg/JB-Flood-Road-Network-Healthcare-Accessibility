# Step 5A-2 — Missing Physical Data Acquisition v0.1

## What is completed
The missing-data sources and acquisition specifications are now frozen without using F01–F19 or D09.

### Long-term rainfall
Source locked: NASA IMERG Final V07B.
Primary climatology period: 2016-01-01 to 2025-12-31.
Primary products:
- monthly Final: 120 steps,
- daily Final: 3653 steps.
Half-hourly archive (175,344 steps) is optional sensitivity only.

Raw long-term rainfall is NOT yet marked acquired because authenticated GES DISC access is still required.

### Built-up fraction
Source locked: ESA WorldCover 2021 v200.
Johor Bahru requires one 3x3 degree tile:
- N00E102, covering 102–105 E and 0–3 N.
- Built-up class = 50.
A public-S3 download/clip script is included.

The model variable must be called built-up fraction, not exact impervious-surface percentage.

### Drainage / hydrography
The existing regional OSM PBF remains the immediate baseline physical source for:
- river,
- stream,
- canal,
- drain,
- ditch,
- coastline.

An osmium extraction specification is included.
Formal urban drainage remains an official-data request to JPS.

### River / tide / water level
Six Johor Bahru JPS/SPHTN water-level station targets are frozen.
Public Infobanjir supports time-series reporting/export.
Long-term historical series still need to be retrieved.
Tide/sea-level is optional unless a defensible historical station record is acquired.

## Current Step 5A-2 status
PARTIAL ACQUISITION / SOURCE LOCK COMPLETE.

No model training is authorized.
No High/Very High threshold is authorized.
F01–F19 remain sealed.
