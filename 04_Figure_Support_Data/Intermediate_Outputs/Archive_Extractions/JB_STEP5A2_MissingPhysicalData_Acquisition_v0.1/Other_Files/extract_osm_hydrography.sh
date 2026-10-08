#!/usr/bin/env bash
set -euo pipefail

# Input already exists in the project/local archive:
INPUT="malaysia-singapore-brunei-261003.osm.pbf"

# Extract physical hydrography/coastline only.
osmium tags-filter "$INPUT" \
  w/waterway=river,stream,canal,drain,ditch \
  w/natural=coastline \
  -o JB_hydrography_source.osm.pbf \
  --overwrite

echo "Created JB_hydrography_source.osm.pbf"
echo "Next: clip to JB_Study_Boundary_v1.0 + context and convert to GPKG."
echo "Do not use historical flood hotspots during extraction."
