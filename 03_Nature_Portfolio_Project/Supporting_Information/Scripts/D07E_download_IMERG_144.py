#!/usr/bin/env python3
from pathlib import Path
import sys, subprocess

def ensure_packages():
    missing=[]
    for p in ['earthaccess','pandas']:
        try: __import__(p)
        except Exception: missing.append(p)
    if missing:
        subprocess.check_call([sys.executable,'-m','pip','install',*missing])
ensure_packages()
import earthaccess
import pandas as pd
ROOT=Path(__file__).resolve().parent
RAW=ROOT/'RAW_AUTHENTICATED'
RAW.mkdir(parents=True,exist_ok=True)
BBOX=(103.5352318142566,1.2880318214880526,104.02789717628242,1.6730875530604803)
UTC_START='2025-03-18T16:00:00Z'
UTC_END='2025-03-21T15:59:59Z'
print('D07-E NASA IMERG authenticated download')
print('UTC window:',UTC_START,'to',UTC_END)
auth=earthaccess.login()
if not getattr(auth,'authenticated',False):
    auth=earthaccess.login(strategy='interactive',persist=True)
if not getattr(auth,'authenticated',False):
    raise RuntimeError('NASA Earthdata authentication failed.')
results=earthaccess.search_data(short_name='GPM_3IMERGHH',version='07',temporal=(UTC_START,UTC_END),bounding_box=BBOX)
print('Granules returned by CMR:',len(results))
files=earthaccess.download(results,RAW)
paths=[Path(x) for x in files]
hdf=[p for p in paths if p.suffix.lower() in {'.hdf5','.h5'} or '3IMERG' in p.name]
rows=[{'filename':p.name,'size_bytes':p.stat().st_size if p.exists() else None,'path':str(p.resolve())} for p in sorted(hdf)]
pd.DataFrame(rows).to_csv(ROOT/'D07E_Downloaded_IMERG_Inventory.csv',index=False,encoding='utf-8-sig')
print('Expected: 144; actual IMERG-like files:',len(hdf))
print('STATUS:', 'PASS' if len(hdf)==144 else 'REVIEW')
print('Upload the RAW_AUTHENTICATED folder as a ZIP to ChatGPT. Do not upload credentials.')
