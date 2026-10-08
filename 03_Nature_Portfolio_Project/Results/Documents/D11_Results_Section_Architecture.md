# D11 Final Results Architecture / Figure–Table Freeze v1.0

## Recommended Results Structure

### 3.1 Event reconstruction and observed road disruption
**Question:** Was the March 2025 episode sufficiently strong and coherent to support an event-based road-disruption analysis?

Use **Figure 1** and **Table 1**.

Core numerical anchors:
- JB 72-h area-weighted rainfall: 271.33 mm.
- 20 Mar area-weighted rainfall: 156.47 mm.
- Local 6-h maximum: 97.51 mm.
- Senai gauge: 176.2 mm/day; nearest IMERG grid: 143.23 mm/day.
- Primary accessibility event: J105 + FT01 + FT003 on 20 Mar.

Result logic:
**hydrometeorological trigger → observed road disruption**.

### 3.2 Healthcare accessibility loss
**Question:** What was the consequence of the observed closures for population access to acute hospitals?

Use **Figure 2** and **Table 2**.

Core result:
- Nominal newly unreachable population: 4961.
- Sensitivity-supported range: 2554–5079.
- 30-min coverage change: -0.260 percentage points.
- Population-weighted mean delay among common reachable origins: 0.009 min.

Narrative rule:
The dominant effect is **network disconnection**, not citywide mean delay.

### 3.3 Robustness and spatial inequality
**Question:** Are the results robust, and which communities absorb the loss?

Use **Figure 3**.

Core result:
- Tebrau share of newly unreachable across sensitivity: 85.4–94.4%.
- Mukim Tebrau is the stable dominant affected area.
- J105 is high-impact but location-sensitive.
- FT01 has a lower but highly stable accessibility-isolation effect.

Narrative rule:
Report **nominal + sensitivity range**, never a single universal 4,961-person claim.

### 3.4 Flood susceptibility and critical-road preparedness
**Question:** Which flood-susceptible roads are also structurally important for healthcare access?

Use **Figure 4** and **Table 3**.

Core result:
- 1,458 A/B/C flood-susceptible core segments also have positive healthcare dependency.
- 74 P1 Critical segments.
- 218 P2 High segments.
- CRPI score-mapping robustness: Spearman 0.991–0.999.
- 99 of 101 distinct top-100 candidates are common across all score mappings.

Narrative rule:
CRPI is a **preparedness screening index**, not flood probability.

### 3.5 Recovery benefit and spatial-equity restoration
**Question:** Which restoration sequence recovers healthcare access most efficiently and reduces the spatially concentrated burden?

Use **Figure 5** and **Table 4**.

Core result:
- Nominal J105-first restores 3220 people (64.9%).
- J105 + FT01 restore 4499 (90.7%).
- Robust recovery policy: **Tier 1 = J105 + FT01; Tier 2 = FT003**.

Narrative rule:
Use J105-first as the **nominal** sequence, not a universal ordering under all spatial uncertainty.
