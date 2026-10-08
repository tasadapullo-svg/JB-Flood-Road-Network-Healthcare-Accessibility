# Step 6 — Historical Flood Zones × Observed Road Disruption Validation v1.0

## Purpose
Test whether the frozen historical flood-zone geography corresponds to documented transport consequences.

This is NOT an independent validation of where flooding occurred:
2023 and 2025 historical evidence contributed to the historical evidence archive.
Step 6 instead asks whether the frozen flood geography is associated with independently documented
road-impact consequences such as inundation, trapped vehicles, closure, or access restriction.

## 2023 result
The frozen layer contains 8 road-type historical zones:
F05, F07, F09, F10, F11, F12, F13 and F14.

All 8/8 have a same-road observed 2023 impact record:
- Jalan Kolam Ayer: explicit closure.
- Jalan Ayer Molek: vehicle trapped and road inundation.
- Jalan Sungai Chat, Jalan Tun Abdul Razak, Jalan Tebrau, Jalan Stulang Darat,
  Jalan Yahya Awal and Jalan Mahmoodiah: reported inundation.

This is strong operational-consequence correspondence, but not an independent flood-location test.

Two explicit closures were reported in 2023:
1. Jalan Kolam Ayer: directly corresponds to F07 at the named-road level.
2. Jalan Gertak Merah approach toward Wisma Persekutuan: source-limited.
   Candidate road-name segments geometrically cross F05/F11, but the exact affected approach/edge subset
   is unresolved; those crossings are NOT counted as exact closure-zone matches.

## 2025 result
Four JKR disruption sections have authorized spatial geometry:
- FT003 km 9.1–10.0
- FT01 km 19.6–20.0
- J105 km 7.0–7.5
- J46 km 2.0–2.3

Direct polygon intersection with the frozen F01–F19 layer:
0/4.

Nearest-zone distances are reported continuously rather than converted into a post-hoc proximity threshold.

Interpretation:
The frozen historical zones are localized evidence-support areas, not an exhaustive flood-disruption footprint.
The 2025 JKR event therefore demonstrates road impacts both near and outside the recurrent historical-zone layer.

## Scientific use
Supported claim:
"Frozen historical flood zones correspond strongly with documented 2023 road-impact consequences on the same roads,
while spatially authorized 2025 JKR disruptions extend beyond the localized historical-zone footprints."

Not supported:
"All observed road disruptions occur inside the historical flood zones."
