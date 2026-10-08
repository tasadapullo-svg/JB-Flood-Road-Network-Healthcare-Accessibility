# QA Report

- Total original files: 809
- Total original directories: 230
- Total original size bytes: 6657771614
- Canonical unique files copied: 893
- Exact duplicates identified: 763
- Duplicate original copies quarantined: 170
- GIS/geospatial canonical files preserved: 146
- GIS sidecar groups detected and preserved: 0
- Files exceeding 20 MiB in organized copy: 35
- Files split for GitHub_Ready: 35
- Reconstruction verification failures: 0
- GitHub_Ready total files: 1113
- GitHub_Ready total size bytes: 5635876548
- GitHub file-size compliance: True
- Copy verification failures: 0
- QA status: PASS_WITH_REPORTED_ARCHIVE_EXCEPTIONS

## Unresolved Issues

- 3 archives were not extracted; see Archive_Report.csv.

## Remote Verification

- Repository: https://github.com/tasadapullo-svg/JB-Flood-Road-Network-Healthcare-Accessibility
- Target branch: main
- Git push status: SUCCESS
- Remote verification method: `git fetch origin main`, `git ls-remote --heads origin main`, and remote tree comparison with `git ls-tree -r origin/main`.
- Data upload commit verified: a059fa2fbfa4d05036cee194ad951a30ce0c8d2f
- Remote file count verified before this QA-report update: 1113
- Required top-level directories verified: 01_Historical_Flood_2016_2026, 02_GIS_Baseline_Data, 03_Nature_Portfolio_Project, 04_Figure_Support_Data, 90_Organization_Reports, tools.
- Required reports verified: File_Inventory.csv, Rename_Mapping.csv, Duplicate_Report.csv, Large_File_Report.csv, Archive_Report.csv, Publication_Exclusions.csv, QA_Report.md.
- Large-file metadata verified remotely: 35 restore metadata files and 207 split part files present.
- Remote verification status: PASS.

## Summary JSON

```json
{
  "total_original_files": 809,
  "total_original_directories": 230,
  "total_original_size_bytes": 6657771614,
  "files_organized": 893,
  "files_renamed": 16,
  "exact_duplicates_identified": 763,
  "exact_duplicates_quarantined": 170,
  "unique_files_preserved": 893,
  "archives_processed": 47,
  "gis_datasets_preserved": 146,
  "gis_sidecar_groups_preserved": 0,
  "files_exceeding_20mib": 35,
  "files_split": 35,
  "reconstruction_verification_failures": 0,
  "github_ready_total_files": 1113,
  "github_ready_total_size_bytes": 5635876548,
  "github_file_size_compliance": true,
  "copy_verification_failures": 0,
  "archive_unresolved": 3
}
```
