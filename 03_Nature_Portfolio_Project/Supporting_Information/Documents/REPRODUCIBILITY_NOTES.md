# Reproducibility Notes

The project data pipeline follows:

D01 Study Area -> D02 Road Network -> D03 Terrain -> D04 Healthcare -> D05 Population -> D06R Baseline -> D07 Flood Event -> D08 Accessibility Impact -> D09 Critical Road Priority -> D10 Recovery Equity -> D11 Results Architecture.

D06R replaces D06 for all downstream scientific comparisons. The original D06 baseline is retained only as provenance for the correction.

Large upstream datasets are referenced through the external data manifest, while compact derived products and quality-control outputs are prepared for GitHub review.
