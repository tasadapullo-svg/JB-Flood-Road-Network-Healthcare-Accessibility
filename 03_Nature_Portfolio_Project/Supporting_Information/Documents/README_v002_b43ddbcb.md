# Flood-Induced Road Disruption, Healthcare Accessibility, and Recovery Prioritization in Johor Bahru

Reproducible data products and analytical outputs for an event-based urban flood-road-healthcare accessibility resilience study.

## Overview

This repository supports a Scientific Reports / Nature Portfolio manuscript project on Johor Bahru, Malaysia. The analytical chain links rainfall and flood evidence to road disruption, healthcare-accessibility loss, spatial inequality, healthcare-critical road identification, and recovery prioritization.

## Study Area

Johor Bahru District, Johor, Malaysia.

## Analytical Objectives

- Reconstruct the March 2025 flood event.
- Quantify modelled healthcare-accessibility loss associated with documented road closures.
- Test sensitivity to closure-location uncertainty.
- Identify flood-susceptible healthcare-critical roads.
- Evaluate recovery sequences and spatial-equity benefits.

## Data Sources

The project uses administrative, transport, terrain, population, rainfall, flood-evidence, and healthcare facility inputs, including MyGeoportal / MyGDI, OpenStreetMap / Geofabrik, Copernicus GLO-30, WorldPop 2026, NASA GPM IMERG V07, MET Malaysia / Senai, JKR / official flood records, and healthcare facility records. Third-party datasets remain subject to their original providers' terms.

## Repository Structure

See [REPOSITORY_STRUCTURE.md](REPOSITORY_STRUCTURE.md).

## Key Derived Data Products

- D06R: corrected official baseline healthcare-accessibility products.
- D07: flood-event, rainfall, road-rain alignment, and closure-spatialization products.
- D08: observed-closure accessibility impact and uncertainty/sensitivity products.
- D09: flood-susceptible healthcare-critical road priority products.
- D10: recovery-order and spatial-equity benefit products.
- D11: result architecture, claim-evidence, figure/table freeze, and audit support.

## Important Baseline Correction

The original D06 baseline contained an identified one-way origin-departure direction logic issue. D06R is the corrected and authoritative baseline for all subsequent D08-D10 comparisons. The old D06 is retained only for provenance and comparison.

## Minimal Modelled Result Context

The nominal March-20 scenario indicates approximately 4,961 modelled newly unreachable population, with sensitivity values of approximately 2,554-5,079. The modelled Tebrau share is 85.4-94.4%. The nominal J105-first recovery scenario accounts for 64.9% recovery, and J105 + FT01 accounts for 90.7%. These values are modelled and scenario-specific, not direct census facts.

## Reproducibility

Large upstream datasets are not necessarily stored directly in GitHub. Derived analytical products, quality-control outputs, metadata, provenance files, and external-data references are included. See [DATA_AVAILABILITY.md](DATA_AVAILABILITY.md).

## Limitations

This is an event-based March 2025 analysis. Closure timing is incomplete, closure spatialization includes uncertainty, susceptibility is not calibrated probability, CRPI is a preparedness screening index, D06R uses a reference/free-flow speed model, and population origins are spatially dependent. See [docs/KNOWN_LIMITATIONS.md](docs/KNOWN_LIMITATIONS.md).

## Citation

See [CITATION.cff](CITATION.cff).

## License

License pending author confirmation. See [LICENSE_PENDING.md](LICENSE_PENDING.md).
