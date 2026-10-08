@echo off
setlocal
echo ============================================================
echo STEP 5A-2 / WorldCover
echo ============================================================
python -m pip install --upgrade requests rasterio geopandas
python download_and_clip_worldcover.py
pause
