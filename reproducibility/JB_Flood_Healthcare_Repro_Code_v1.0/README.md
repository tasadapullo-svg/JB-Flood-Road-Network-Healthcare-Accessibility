# Johor Bahru Flood–Healthcare Accessibility: Independent Reference Code

**Status: independently reconstructed reference implementation — NOT the original D06R/D08/D10 author execution scripts; original experimental results have NOT been independently reproduced by this package yet.**

This project contains Python code implementing the mathematical and directed-routing methods described in the Scientific Reports manuscript and the existing archived data/QC materials. It is intended to make new runs and independent checking possible **once the actual normalized graph and access mappings are provided**. Its synthetic unit tests are useful for software correctness; they do not validate the study's reported numerical findings.

## Research methods included

| Module | Implemented | Requirements / limitations |
|---|---|---|
| D06R | Directed graph, correct one-way origin departure, off-node origin/hospital positions, 14 hospital sinks, shortest reference road travel times | Need original subedge-to-arc mapping and origin population/subdistrict join |
| D08 | Single- and multiple-road full arc-removal equivalents; partial closure intervals for connectors; population-weighted coverage, newly unreachable and delays | Need exact archived D07F/D08 subedge indices; partial boundary behavior may differ from historical producer implementation |
| D10 | All six restoration permutations; first-stage and cumulative connectivity recovery | Need confirmed D06R/D08 numerical agreement first |
| D08 shifted geometry | Optional 27-position combinations | Requires *full shifted subedge/interval mappings*, not only the existing count-only shift-definitions table |
| D09 screening | Not included in the core model | Screening index is separate from direct route-removal and restoration decisions |

**Critical caution:** The paper uses archived results. Do not claim this software reproduces the paper unless you run the full data and obtain a `PASS` on the frozen reference comparison, followed by checking the remaining audit outputs and geographic mappings.

## Install / quick test (Windows PowerShell)

```powershell
cd JB_Flood_Healthcare_Repro_Code_v1.0
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[test]"
python -m pytest -q
```

Linux / macOS: use `python3 -m venv .venv && source .venv/bin/activate`.

## Prepare archived data

1. Clone the published data archive: `https://github.com/tasadapullo-svg/JB-Flood-Road-Network-Healthcare-Accessibility`.
2. Restore split files **from that repository root**:

```powershell
python tools/restore_large_files.py
```

3. Inspect available CSV headers and schema:

```powershell
jb-repro inspect --repo-root "C:\path\to\JB-Flood-Road-Network-Healthcare-Accessibility"
```

4. First try the strict archive adapter (it joins data by unique `origin_id`, does not guess missing edge IDs):

```powershell
jb-repro prepare --repo-root "C:\path\to\JB-Flood-Road-Network-Healthcare-Accessibility" --outdir local_inputs
```

If it reports ambiguous/missing source columns, follow the manual normalization steps below. A `prepare` schema PASS is not a verified full-data numerical match.

4. Create **four joined, normalized CSVs** documented in `docs/INPUT_SCHEMA.md` and `docs/ADAPTER_AND_VALIDATION.md`. Not all required canonical fields are necessarily in a single original table. In particular, the mapping table may need a join to the WorldPop origin table to obtain each `population` and `subdistrict`.
5. If the source headers match the recognized aliases, use strict canonical normalization:

```powershell
jb-repro normalize --edges "C:\path\to\directed_arcs.csv" --origins "C:\path\to\joined_origins.csv" --hospitals "C:\path\to\hospital_mapping.csv" --closures "C:\path\to\D08_Closure_Subedge_Intervals.csv" --outdir local_inputs
```

If the CLI explicitly reports missing input fields, supply them from the archived source tables and rerun. **Never use a fabricated value or replace a missing field with a guessed default.**

## Run actual tests

```powershell
jb-repro run --edges local_inputs/edges.csv --origins local_inputs/origins.csv --hospitals local_inputs/hospitals.csv --closures local_inputs/closures.csv --outdir run_outputs --require-match
```

Results created by computation (not copied from the paper):

- `S0_origin_accessibility.csv`
- `scenario_summary.csv`
- `subdistrict_summary.csv`
- `six_restoration_orders.csv`
- `frozen_reference_comparison.json` (PASS/FAIL per metric)
- `run_metadata.json`

`--require-match` forces a nonzero exit if frozen targets differ. A failed run is scientific feedback, not a number to patch manually. Add `--full-origin-results` for scenario-level origin outputs.

## Graph and scenario interpretation

- The historical D06 baseline had a one-way origin departure error and is superseded by **D06R**. Our rule is: origin may depart to endpoint **u if `oneway_code != 1`**, and to **v if `oneway_code != -1`**.
- Map-matching/off-network snap distances are **not** added to network travel time.
- Edge costs are non-negative time in minutes, recorded speeds or documented road-class speed fallbacks.
- J105 and J46 have documented heavy-vehicle B3 restrictions; treating either as all-vehicle road closure is a **hypothetical stricter stress test**, not a claim of actual total closure. FT01 and FT003 are documented T closures.
- MAR20 is an analytical three-road simultaneous closure-equivalent scenario. It is not an event traffic observation.
- Closure position can change the road ranking. J105-first is a **nominal**, not universally robust priority.
- Each `subedge_idx` in `edges.csv` must identify every directed arc representing that road subedge; closing the subedge removes those arcs.
- In incomplete/ambiguous boundary intervals, the tool conservatively uses whole-subedge blocking. If origins/hospitals map to such edges, validate geometry details instead of treating the calculated figures as validated.

## Provenance and research ethics

The figures hard-coded in `src/jb_repro/spec.py` are **archived audit targets only**, and are never substituted for computed results. This implementation was prepared with AI assistance in October 2026 based on existing manuscript methods and archived QC. It is not a recovered original historical analysis script, and has not been confirmed to run on the full study files. Research authors are responsible for validating computation, outputs and attribution.

See `docs/METHOD_ALIGNMENT.md`, `docs/INPUT_SCHEMA.md`, `docs/ADAPTER_AND_VALIDATION.md`, and `docs/LIMITATIONS_AND_RELEASE.md`.
