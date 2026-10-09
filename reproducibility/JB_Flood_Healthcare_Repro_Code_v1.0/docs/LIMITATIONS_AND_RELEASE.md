# Scope, release note, and responsible Code availability language

## This is not an original-code recovery

The study archive contains extensive experimental output tables, frozen QC reports, metadata and data-integrity checks. The exact original producer scripts for D06R, D08 and D10 were not available for verification when this package was drafted. The scripts in this release are a freshly written independent algorithmic reimplementation based on documented analysis specifications.

### Conditions **not** yet satisfied automatically

1. No production study run against the full normalized graph/origin/closure tables has been performed by this generated package.
2. No numerical or origin-level parity with D06R/D08/D10 has yet been demonstrated by this software.
3. Historical producer behavior for partial closure intervals, graph splitting and edge-index mapping is not completely known.
4. Shifted-geometry tables currently available in the public archive include *counts*, which do not identify the affected subedge ID sets for the 27 cases.
5. The public source archive is large and some files are split; restoring and checking them is essential.
6. This package does not create hydraulic flood-hazard data or actual observed hospital-care outcomes.
7. A successful `pytest` run demonstrates only that small synthetic software tests passed.

## Suggested temporary disclosure for GitHub README

> The repository includes an independent, AI-assisted reference reimplementation of the directed-road healthcare accessibility, road-disruption and reopening analyses. It was derived from archived method descriptions and frozen outputs and should not be treated as the original experimental execution code. Reproduction against the full archived input data remains to be verified. Generated outputs are audited against the frozen reference metrics; differences are retained and disclosed.

## When full numerical parity has been established

Only after running the complete data and recording the results, software versions, input hashes and checks, the manuscript Code availability statement may be strengthened to say the new executable reconstruction and validation resources are available. Do not claim original scripts existed in the archive if they did not.

## Publishing guidance

Place this folder under `reproducibility/JB_Flood_Healthcare_Repro_Code_v1.0/` in the same repository, or keep a dedicated code repository linked from the data archive. Keep large raw data in their existing tracked paths. Do not store credentials, private paths, or personal contact details in script configuration. Distinguish code authorship/AI assistance and archived scientific result authorship. The MIT license in this package applies **only to newly authored source code**, not automatically to third-party GIS/source datasets.
