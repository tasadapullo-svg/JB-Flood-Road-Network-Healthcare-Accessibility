# Step 5A-2 Execution Kit v0.2

This package converts Step 5A-2 from a source plan into a local execution kit.

## Important correction to rainfall freeze
NASA currently states IMERG Final V07 ends on 2025-09-30.
Therefore the PRIMARY climatology is now:
2016-01-01 through 2024-12-31 (3288 complete daily steps; 108 months).

2025-01-01 through 2025-09-30 is an optional extension only.
It must not be treated as a complete annual climatology year.

This correction is driven only by source availability and prevents annual-climatology bias.

## What can be completed without waiting for JPS
- WorldCover built-up source.
- IMERG long-term climatology.
- OSM river/stream/canal/drain/ditch/coastline baseline.

## JPS
The formal drainage/water-level request was submitted on 2026-10-05 at 18:49 MYT.
The analysis will not be blocked waiting for a reply.
Formal drainage can be added later as an optional enhanced version if received.

## Firewall
No F01-F19 and no D09 are used anywhere in these scripts.
