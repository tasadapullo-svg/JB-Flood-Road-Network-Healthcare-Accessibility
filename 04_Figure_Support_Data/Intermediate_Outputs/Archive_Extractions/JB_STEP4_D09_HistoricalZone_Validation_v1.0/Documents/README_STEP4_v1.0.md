# Step 4 — Historical Flood Zones × D09 Susceptibility Audit v1.0

## Critical methodological finding
The current D09 susceptibility layer cannot be used as a fully independent validation target
for JB_Historical_Flood_Zones_v1.0.

Reason:
D09's A/B/C screening classes were constructed partly from:
- documented 2025 road disruption;
- official flood-hotspot proximity;
- historical recurrent-location proximity;
- terrain low-lying evidence.

The frozen historical-zone layer is derived from overlapping historical evidence families.
Therefore a simple "D09 hit rate" contains circularity.

## Exact D09 terminology
A = Observed Road Disruption
B = High-Evidence Susceptibility
C = Potential Susceptibility
D = Background

A is NOT called "Very High probability", and B is NOT a calibrated flood probability.

For this audit:
- Strong-evidence coverage = A or B.
- Any susceptibility coverage = A, B, or C.

## Descriptive retrospective coverage
Strict polygon × road-segment intersection:
- All 19: A/B = 6/19 (31.6%);
  A/B/C = 12/19 (63.2%).
- Excluding four LOW-confidence proxies: A/B = 6/15 (40.0%);
  A/B/C = 11/15 (73.3%).

## Class-stratified coverage
- Severe: A/B 3/9 (33.3%);
  A/B/C 4/9 (44.4%).
- Recurrent: A/B 3/8 (37.5%);
  A/B/C 8/8 (100.0%).
- Mild: A/B 0/2 (0.0%);
  A/B/C 0/2 (0.0%).

## Recurrence robustness
- 3/3 core-year locations: A/B 0/2;
  A/B/C 0/2.
- 2/3 core-year locations: A/B 6/15 (40.0%);
  A/B/C 12/15 (80.0%).

## Circularity audit
Zones spatially exposed to D09's own encoded historical/official inputs:
- n = 11
- A/B strict = 6/11 (54.5%)
- A/B/C strict = 11/11 (100.0%)

D09-input-unexposed holdout:
- n = 8
- A/B strict = 0/8 (0.0%)
- A/B/C strict = 1/8 (12.5%)

This contrast is why the full-sample overlap must not be described as independent validation.

## Independent terrain-component support
Across all 19 zones:
- >=25% low-lying road-terrain flag: 5/19 (26.3%)
- >=50% low-lying road-terrain flag: 3/19 (15.8%)

These values show limited independent physical support from the D09 terrain component.

## Scientific decision
- Retrospective D09 concordance: REPORTABLE.
- Independent validation of current D09 using the same historical evidence family: NOT AUTHORIZED.
- Strong claim that "D09 successfully validates historical flood hotspots": NOT SUPPORTED.
- The honest finding is that D09 covers its input-exposed recurrent evidence well, but generalization to
  input-unexposed frozen historical zones is weak.

## Recommended manuscript use
Treat this as a leakage-controlled validation audit and a limitation/result, not as a failed study.
A future susceptibility model intended for independent validation should be rebuilt using physical predictors
only (e.g., terrain, drainage, rainfall, river/tide, imperviousness) and reserve historical flood zones strictly
as held-out validation labels.
