@echo off
setlocal
echo ============================================================
echo STEP 5A-2 / OSM Hydrography
echo ============================================================
python -m pip install --upgrade pyrosm geopandas pandas shapely pyogrio
python extract_osm_hydrography_pyrosm.py
pause
