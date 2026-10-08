# JB Flood Healthcare Accessibility Research Data

This repository contains the GitHub-ready research data archive for a study on flood disturbance, transportation-network resilience, healthcare accessibility, and spatial equity in Johor Bahru, Malaysia.

The files in this repository are an organized publication copy. The original source files were inventoried, renamed into ASCII English paths, checked with SHA-256 hashes, deduplicated by exact checksum, and prepared so that every file in this GitHub-ready copy is no larger than 20 MiB.

## Repository Purpose

This repository is intended for scientific data archiving and reproducible file sharing. It is a file-management and data-preservation archive, not a recalculated analysis output. No scientific values, spreadsheet cells, coordinates, geometries, raster values, manuscripts, references, or figures were edited during organization.

## Top-Level Structure

```text
GitHub_Ready/
|-- 01_Historical_Flood_2016_2026/
|-- 02_GIS_Baseline_Data/
|-- 03_Nature_Portfolio_Project/
|-- 04_Figure_Support_Data/
|-- 90_Organization_Reports/
|-- tools/
|   `-- restore_large_files.py
`-- README.md
```

## Directory Guide

### 01_Historical_Flood_2016_2026

Historical flood records and supporting spatial materials for 2016 through 2026. Files are organized into annual records, event evidence, flood locations, flood polygons, master datasets, source archives, and unclassified support files where needed.

### 02_GIS_Baseline_Data

Baseline geospatial inputs used to support the research framework. This includes administrative boundaries, road-network data, DEM/elevation data, population data, healthcare-facility data, rainfall data, satellite imagery, spatial layers, GIS project files, and related unclassified GIS support materials.

### 03_Nature_Portfolio_Project

Project materials prepared around the manuscript and journal-style research workflow. This includes manuscript materials, section-specific files, figures, tables, references, submission materials, supporting information, and archive extractions where applicable.

### 04_Figure_Support_Data

Data and outputs supporting figure preparation. The directory includes figure-specific materials, shared GIS assets, intermediate outputs, final exports, and unclassified support files.

### 90_Organization_Reports

Traceability and quality-assurance reports generated during organization:

- `File_Inventory.csv`: complete original-file inventory with paths, extensions, file sizes, timestamps, SHA-256 hashes, archive flags, and duplicate-name indicators.
- `Rename_Mapping.csv`: source-to-destination mapping for every original and extracted file, including final classification, final English filename, checksum, and canonical/duplicate status.
- `Duplicate_Report.csv`: exact duplicate records verified by matching file size and SHA-256 checksum.
- `Large_File_Report.csv`: GitHub file-size preparation report, including copied files, split files, part counts, original checksums, and reconstruction verification status.
- `Archive_Report.csv`: archive inspection and extraction status, including skipped archives and reasons.
- `Publication_Exclusions.csv`: public-publication screening result and exclusion notes.
- `QA_Report.md`: final quality-assurance summary and unresolved issues.
- `summary.json`: machine-readable measured summary of organization results.

## Measured Archive Summary

```text
Total original files inventoried: 809
Total original directories inventoried: 230
Total original source size: 6,657,771,614 bytes

Unique canonical files preserved: 893
Files renamed into English/ASCII paths: 16
Exact duplicates identified: 763
Duplicate original copies quarantined outside this repository: 170

Archives extracted: 47
Unresolved archives: 3
GIS/geospatial canonical files preserved: 146
Files originally exceeding 20 MiB: 35
Files split for GitHub: 35
Reconstruction verification failures: 0

GitHub-ready total files: 1,113
GitHub-ready total size: 5,635,876,548 bytes
GitHub file-size compliance: all files are no larger than 20 MiB
```

## Large File Restoration

Files larger than 20 MiB were split into lossless binary parts. Split files use sequential part names such as:

```text
Example_File.ext.part001
Example_File.ext.part002
Example_File.ext.restore.json
```

Each `.restore.json` file records:

- original relative path
- original filename
- original file size
- original SHA-256 checksum
- part-size limit
- part filenames and part SHA-256 checksums

To restore all split files after cloning or downloading this repository, run:

```bash
python tools/restore_large_files.py
```

The restore script verifies each part checksum and then verifies the reconstructed file against the original SHA-256 checksum. If a checksum mismatch occurs, the script stops and reports the affected file.

## Integrity and Deduplication Method

Duplicate detection used a two-step exact-match rule:

1. Compare file size.
2. Confirm identical SHA-256 checksum.

Only files with verified identical SHA-256 hashes were treated as exact duplicates. Filename similarity alone was not used for deduplication. Unique versions were preserved even when names were similar.

## Naming and Path Rules

All publication paths in this repository use ASCII English names. Filenames preserve original file extensions. When the original meaning was not safely inferable from the filename and folder context, a neutral English name was assigned and the original path was recorded in `Rename_Mapping.csv`.

## Archive Handling Notes

Supported archives were inspected for metadata and unsafe path traversal before extraction. One large archive was safely inspected but not extracted because its uncompressed size exceeded the configured extraction safety threshold. Two additional archives were skipped because they were exact duplicate archives already represented elsewhere. See `90_Organization_Reports/Archive_Report.csv` for details.

## Data Protection Notes

This archive was prepared without:

- modifying spreadsheet or CSV cell values
- editing GeoJSON, shapefile geometry, raster values, or coordinates
- changing flood-event identifiers
- recalculating statistics or accessibility metrics
- regenerating maps or figures
- editing manuscript or reference content
- deleting unique research files from the publication copy

## Recommended Use

For audit and traceability, begin with:

1. `90_Organization_Reports/QA_Report.md`
2. `90_Organization_Reports/summary.json`
3. `90_Organization_Reports/Rename_Mapping.csv`
4. `90_Organization_Reports/Large_File_Report.csv`

For full local reconstruction of large files, run `tools/restore_large_files.py` before opening datasets that were split into `.part###` files.

## Known Limitations

This repository is large for standard GitHub hosting, even after per-file splitting. For long-term scientific distribution, consider pairing this GitHub repository with Git LFS, Zenodo, Figshare, OSF, institutional storage, or another research-data repository.
