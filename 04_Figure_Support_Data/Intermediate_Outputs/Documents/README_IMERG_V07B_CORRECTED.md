# IMERG V07B acquisition — corrected freeze

NASA currently documents GPM IMERG Final V07 as ending on 2025-09-30.

Therefore the Step 5A-2 primary climatology is corrected to complete calendar years:

- PRIMARY: 2016-01-01 to 2024-12-31
- Daily expected: 3288
- Monthly expected: 108

Optional recent extension:
- 2025-01-01 to 2025-09-30
- Daily expected: 273
- This partial year must NOT be used as a complete annual climatology year.

Why:
Using Jan-Sep 2025 as if it were a full year would bias annual rainfall summaries.
The period correction is made because of source availability, not because of F01-F19 performance.

## GES DISC subset settings

Dataset:
GPM_3IMERGDF_07

Primary date range:
2016-01-01 to 2024-12-31

Spatial bounding box:
W 103.5352318143
E 104.0278971763
S 1.2880318215
N 1.6730875531

Variable:
precipitation

Output:
NetCDF4

Procedure:
1. Sign in to NASA Earthdata.
2. Open GPM_3IMERGDF_07.
3. Choose Subset / Get Data.
4. Enter the frozen date range and bounding box.
5. Select only precipitation plus coordinate/time dimensions.
6. Generate and download the links-list TXT file.
7. Run download_gesdisc_links.py from this folder.

Do not send Earthdata username/password/token to ChatGPT.
