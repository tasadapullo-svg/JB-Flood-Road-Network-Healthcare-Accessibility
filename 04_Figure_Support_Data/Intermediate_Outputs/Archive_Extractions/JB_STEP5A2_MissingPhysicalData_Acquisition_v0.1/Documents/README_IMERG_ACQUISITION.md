# NASA IMERG acquisition specification

## Frozen period
2016-01-01 through 2025-12-31.

This gives:
- 120 complete monthly steps,
- 3653 complete daily steps,
- 175,344 half-hourly steps if the optional high-frequency sensitivity archive is used.

## Frozen Johor Bahru bounding box
- west: 103.5352318143
- east: 104.0278971763
- south: 1.2880318215
- north: 1.6730875531

## Products
1. GPM_3IMERGM_07 — Final monthly, mandatory.
2. GPM_3IMERGDF_07 — Final daily, mandatory.
3. GPM_3IMERGHH_07 — Final half-hourly, optional sensitivity only.

## Important acquisition rule
Use GES DISC spatial subsetting to the frozen JB bounding box.
Do not bulk-download the global half-hourly archive.

## Authentication
Earthdata/GES DISC authentication is required for the subset workflow.
The project does not store usernames, passwords or tokens.

## Historical-label firewall
F01–F19, D09, official hotspots and historical flood records are not used to choose
the rainfall period, variables, thresholds or spatial subset.
