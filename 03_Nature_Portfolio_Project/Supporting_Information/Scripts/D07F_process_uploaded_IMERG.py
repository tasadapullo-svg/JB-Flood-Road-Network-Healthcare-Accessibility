#!/usr/bin/env python3
from pathlib import Path
import pandas as pd, numpy as np, h5py, geopandas as gpd

ROOT=Path(__file__).resolve().parents[1]
MAN=ROOT/'04_IMERG_STATUS'/'D07F_IMERG_144_Granule_Availability_Audit.csv'
GRID_SOURCE=Path('/mnt/data/D07C_D07E_Flood_Hotspots_Hydromet_v0.2/06_GPM_IMERG/D07E_GPM_IMERG_JB_GridCells_WGS84.gpkg')
OUT=ROOT/'04_IMERG_STATUS'
m=pd.read_csv(MAN)
# Re-scan ROOT and /mnt/data so files can be uploaded anywhere in the working package/workspace.
roots=[ROOT,Path('/mnt/data')]
files={}
for rr in roots:
    for pat in ('*.HDF5','*.h5','*.hdf5'):
        for p in rr.rglob(pat): files[p.name]=p
missing=[f for f in m.filename if f not in files]
if missing:
    raise SystemExit(f'Missing {len(missing)} of 144 IMERG granules. First missing: {missing[0]}')

grid=gpd.read_file(GRID_SOURCE,layer='gpm_cells_intersecting_jb')

def read_grid(path):
    with h5py.File(path,'r') as f:
        lon=np.asarray(f['Grid/lon'][:]); lat=np.asarray(f['Grid/lat'][:])
        p=np.asarray(f['Grid/precipitation'][:]).squeeze()
        if p.shape==(len(lon),len(lat)): p=p.T
        if p.shape!=(len(lat),len(lon)): raise ValueError((path,p.shape,len(lat),len(lon)))
        p=np.where(p<0,np.nan,p)
        return lon,lat,p

rows=[]
for _,mr in m.sort_values('myt_start').iterrows():
    fp=files[mr.filename]
    lon,lat,p=read_grid(fp)
    for _,cell in grid.iterrows():
        ix=int(np.argmin(abs(lon-cell.center_lon))); iy=int(np.argmin(abs(lat-cell.center_lat)))
        rate=float(p[iy,ix])
        rows.append({'gpm_cell_id':cell.gpm_cell_id,'myt_time':pd.to_datetime(mr.myt_start),
                     'precipitation_rate_mm_hr':rate,'half_hour_accum_mm':rate*0.5,
                     'source_filename':fp.name})
df=pd.DataFrame(rows).sort_values(['gpm_cell_id','myt_time'])
for h,n in [(1,2),(3,6),(6,12)]:
    df[f'rolling_{h}h_mm']=df.groupby('gpm_cell_id')['half_hour_accum_mm'].transform(lambda s:s.rolling(n,min_periods=n).sum())
df.to_csv(OUT/'D07F_IMERG_JB_HalfHourly_Rolling.csv',index=False,encoding='utf-8-sig')

peak_rows=[]
for cell,g in df.groupby('gpm_cell_id'):
    rec={'gpm_cell_id':cell}
    for h in (1,3,6):
        c=f'rolling_{h}h_mm'; j=g[c].idxmax()
        rec[f'peak_{h}h_mm']=float(g.loc[j,c]); rec[f'peak_{h}h_end_myt']=str(g.loc[j,'myt_time'])
    peak_rows.append(rec)
peaks=pd.DataFrame(peak_rows)
peaks.to_csv(OUT/'D07F_IMERG_JB_Cell_Peaks_1h_3h_6h.csv',index=False,encoding='utf-8-sig')

# District-level maxima across all 20 cells (max cell-window, not areal mean).
summary=[]
for h in (1,3,6):
    c=f'rolling_{h}h_mm'; j=df[c].idxmax()
    summary.append({'duration_h':h,'peak_mm':float(df.loc[j,c]),'gpm_cell_id':df.loc[j,'gpm_cell_id'],
                    'window_end_myt':str(df.loc[j,'myt_time'])})
pd.DataFrame(summary).to_csv(OUT/'D07F_IMERG_District_Max_CellWindow_Peaks.csv',index=False,encoding='utf-8-sig')
print('IMERG complete:',len(df),'cell-time rows;',len(peaks),'cells')
