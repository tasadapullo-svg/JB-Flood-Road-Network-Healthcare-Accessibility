#!/usr/bin/env python
"""
D07-E authenticated NASA Earthdata IMERG downloader and Johor Bahru aggregator.

Prerequisites:
    pip install earthaccess h5py pandas numpy geopandas shapely pyproj

Authentication:
    Use NASA Earthdata credentials outside this script.
    Recommended environment/login mechanisms:
      earthaccess.login(strategy="environment")
    or run earthaccess.login() interactively on your own machine.

No credentials are embedded or written by this script.
"""
from pathlib import Path
import os
import numpy as np
import pandas as pd
import h5py
import earthaccess

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "06_GPM_IMERG" / "D07E_GPM_IMERG_V07B_20250319_21_MYT_144_Granule_Manifest.csv"
RAW = ROOT / "06_GPM_IMERG" / "RAW_AUTHENTICATED"
OUT = ROOT / "06_GPM_IMERG" / "D07E_GPM_IMERG_JB_HalfHourly_Aggregated.csv"
RAW.mkdir(parents=True, exist_ok=True)

m = pd.read_csv(MANIFEST)

# 1) Authenticate. The user controls credential provisioning.
try:
    auth = earthaccess.login(strategy="environment")
except Exception:
    auth = earthaccess.login()

# 2) Search exact temporal range. Final IMERG V07B.
results = earthaccess.search_data(
    short_name="GPM_3IMERGHH",
    version="07",
    temporal=("2025-03-18T16:00:00Z","2025-03-21T15:59:59Z"),
    bounding_box=(103.5352318,1.2880318,104.0278972,1.6730876),
)

# 3) Download. earthaccess may return 144 granules; validate against manifest.
files = earthaccess.download(results, RAW)

def read_precip(path):
    with h5py.File(path, "r") as f:
        # IMERG HDF5 expected groups: Grid/lon, Grid/lat, Grid/precipitation
        lon = np.asarray(f["Grid/lon"][:])
        lat = np.asarray(f["Grid/lat"][:])
        p = np.asarray(f["Grid/precipitation"][:])
        p = np.squeeze(p)
        # Handle either [lon,lat] or [lat,lon] storage defensively.
        if p.shape == (len(lon),len(lat)):
            p = p.T
        elif p.shape != (len(lat),len(lon)):
            raise ValueError(f"Unexpected precipitation shape {p.shape} in {path}")
        p = np.where(p < 0, np.nan, p)
        return lon, lat, p

# JB-relevant standard IMERG centers (district-intersecting cells).
grid = pd.read_file(ROOT / "06_GPM_IMERG" / "D07E_GPM_IMERG_JB_GridCells_WGS84.gpkg",
                    layer="gpm_cells_intersecting_jb")

rows=[]
for fp in sorted(map(Path, files)):
    # Match filename to manifest to obtain MYT timestamp.
    hit=m[m["filename"].eq(fp.name)]
    if hit.empty:
        continue
    t_myt=pd.to_datetime(hit.iloc[0]["myt_start"])
    lon,lat,p=read_precip(fp)
    for _,cell in grid.iterrows():
        ix=int(np.argmin(np.abs(lon-cell.center_lon)))
        iy=int(np.argmin(np.abs(lat-cell.center_lat)))
        rate=float(p[iy,ix])
        rows.append({
            "gpm_cell_id":cell.gpm_cell_id,
            "myt_time":t_myt,
            "precipitation_rate_mm_hr":rate,
            "half_hour_accum_mm":rate*0.5 if np.isfinite(rate) else np.nan,
            "source_filename":fp.name
        })

df=pd.DataFrame(rows).sort_values(["gpm_cell_id","myt_time"])
for hours,n in [(1,2),(3,6),(6,12)]:
    df[f"rolling_{hours}h_mm"]=(
        df.groupby("gpm_cell_id")["half_hour_accum_mm"]
          .transform(lambda s:s.rolling(n,min_periods=n).sum())
    )

df["data_qc_status"]="AUTHENTICATED_NASA_IMERG_V07B"
df.to_csv(OUT,index=False,encoding="utf-8-sig")
print(f"Wrote {len(df):,} grid-time rows to {OUT}")
