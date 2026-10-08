# Step 5A-1 — Physical Predictor Data Readiness Audit v1.0

## Decision
No susceptibility model is trained in this step.
No High/Very High threshold is defined.
The frozen F01–F19 historical zones are not opened for predictor tuning.

## Current status
READY:
- Copernicus GLO-30 elevation.
- Slope.
- Relative elevation 500 m.
- Relative elevation 1000 m.
- Strict low-lying terrain derivative (sensitivity only).

NEED PROCESSING:
- Hydrologic terrain derivatives (flow accumulation / depression / TWI-like metrics).
- OSM major river/stream extraction.
- Distance to river/stream.
- Drainage density from extracted hydrography.
- Coastline and distance-to-coast.

MISSING:
- Long-term rainfall climatology.
- Independent impervious/built-up surface.
- Formal urban drainage network.
- Tide / river-water-level time series.
- Complete land-cover fractions for vegetation/open surface.

EXCLUDE FROM MODEL:
- Historical flood zones and points.
- Official hotspot lists.
- D09 susceptibility / CRPI.
- 2025 road closures.
- Population, hospitals, accessibility, traffic/FCD.
- March-2025 event rainfall as a static susceptibility predictor.

## Important CRS issue
The historical/grid framework is frozen in EPSG:3377, while existing D03 terrain products were processed in EPSG:3375.
Before any predictor stack is built, all physical predictors must be harmonized to the frozen EPSG:3377 analysis framework.

## Immediate next action
Only acquire the missing physical families:
1. long-term rainfall;
2. imperviousness / land cover;
3. formal drainage if available;
4. tide / water-level data.

OSM river/stream/coast extraction is processing, not new data acquisition.
