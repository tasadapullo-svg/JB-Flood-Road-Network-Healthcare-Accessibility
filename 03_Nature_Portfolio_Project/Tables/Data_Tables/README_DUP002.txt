D09 Flood Susceptibility / Critical Road Priority Index v1.0

PURPOSE
1) Network-wide preparedness screening:
   flood susceptibility evidence × healthcare-network structural criticality.
2) Observed March-2025 recovery priority:
   explicit D08 accessibility consequences for documented road closures.

PRIMARY NETWORK-WIDE INDEX
CRPI = 100 × flood evidence score × healthcare criticality percentile.

Flood evidence score (primary balanced mapping):
A Observed road disruption = 1.00
B High-evidence susceptibility = 0.75
C Potential susceptibility = 0.40
D Background = 0.00

Priority tiers among A/B/C roads with positive healthcare dependency:
P1 Critical   >=95th percentile
P2 High       80th–<95th
P3 Moderate   50th–<80th
P4 Watchlist  <50th
P0            background or zero healthcare dependency

IMPORTANT
CRPI is NOT flood probability and NOT expected annual loss.
It is a relative preparedness screening index.

OBSERVED 2025 RECOVERY PRIORITY
Group 1: J105 + FT01
Group 2: FT003
Group 4: J46

The exact D08 4,961-person nominal result remains sensitivity-dependent.
Use the D08 uncertainty range rather than treating the nominal value as universal.

GIS
Both EPSG:3375 and WGS84 GeoPackages are provided.
Use:
- all_core_roads_CRPI
- P1_critical_recovery_segments
- P1_P2_priority_segments
- observed_2025_closure_sections
- official_recurrent_hotspots
- historical_recurrent_locations
- district_reference

SCIENTIFIC LIMIT
Do not label B/C roads as "high flood probability."
Use "high-evidence flood susceptibility" and "potential flood susceptibility."

STATUS
D09 Network-wide preparedness CRPI: PASS
D09 Observed-2025 recovery priority: PASS
CRPI score-mapping robustness: PASS
GIS priority layers: PASS
Quantitative flood probability interpretation: NOT AUTHORIZED
