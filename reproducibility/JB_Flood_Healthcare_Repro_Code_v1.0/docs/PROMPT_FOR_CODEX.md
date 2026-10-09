# Prompt for local Codex (optional)

Read `README.md`, `docs/INPUT_SCHEMA.md`, `docs/ADAPTER_AND_VALIDATION.md`, and all QC records in my JB flood-healthcare GitHub repository. This `reproducibility/JB_Flood_Healthcare_Repro_Code_v1.0` package is a newly written independent reference implementation, **not** the original experimental code.

Do the following locally, without modifying scientific source files:
1. Run the original repository's large-file restoration tool and verify hashes.
2. Inspect headers/dtypes of D06 directed arcs, D06 origin mapping, D05 WorldPop cell origins, D05C road snapping, D06 hospital mapping, D08 interval rows. Document exact join keys and direction/index conventions.
3. Attempt `jb-repro prepare`. If it fails, locate the correct graph subedge index bridge and implement an **auditable** adapter, with assertions for no duplicate origin IDs, 75,149 origins, 14 hospitals, and exact population sum.
4. Do not invent geocoordinates, full closure intervals, missing arc IDs, reference speeds, or historic observations. Preserve both original and corrected D06R data; use only corrected D06R for analysis.
5. Run pytest and a baseline-only real-data analysis, compare D06R summaries and origin-level baseline.
6. Run all D08 scenarios and D10 six restoration orders, and compare numeric results against frozen reference files. Save deviations and stack traces; do NOT hard-code frozen study results into computed output.
7. Obtain full shifted interval sets for 27 combinations from real source files only. If unavailable, mark the feature `NOT_VERIFIED`.
8. Update `REPRODUCTION_STATUS.md` with precise command, git commit hash, input SHA-256, environment versions, numerical deviations, verification status, and known limitations. Do not claim overall PASS unless both calculations and the relevant geometry checks pass.
9. Commit the new code and audit notes via a branch / PR, not an unreviewed forced push.

Goal: transform a documented independent reference implementation into an independently VERIFIED replication if and only if the archived inputs support such a claim.
