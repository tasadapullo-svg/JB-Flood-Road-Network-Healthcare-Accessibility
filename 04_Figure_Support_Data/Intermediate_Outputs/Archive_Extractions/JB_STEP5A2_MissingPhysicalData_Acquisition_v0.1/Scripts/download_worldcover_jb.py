"""
Download/clip ESA WorldCover 2021 v200 for Johor Bahru.

Requires:
    pip install rasterio geopandas
The public WorldCover S3 bucket does not require credentials.

Frozen source tile:
    N00E102 = 102E–105E, 0N–3N
"""

from pathlib import Path
import os
import rasterio
from rasterio.windows import from_bounds
from rasterio.windows import transform as window_transform

URL = "https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map/ESA_WorldCover_10m_2021_v200_N00E102_Map.tif"
OUT = Path("JB_ESA_WorldCover_10m_2021_v200_bbox.tif")

WEST  = 103.5352318143
SOUTH = 1.2880318215
EAST  = 104.0278971763
NORTH = 1.6730875531

os.environ["GDAL_DISABLE_READDIR_ON_OPEN"] = "EMPTY_DIR"
os.environ["AWS_NO_SIGN_REQUEST"] = "YES"
os.environ["CPL_VSIL_CURL_ALLOWED_EXTENSIONS"] = ".tif"

with rasterio.Env():
    with rasterio.open(URL) as src:
        win = from_bounds(WEST, SOUTH, EAST, NORTH, src.transform)
        win = win.round_offsets().round_lengths()
        data = src.read(1, window=win)
        profile = src.profile.copy()
        profile.update(
            width=data.shape[1],
            height=data.shape[0],
            transform=window_transform(win, src.transform),
            compress="deflate",
            tiled=True
        )
        with rasterio.open(OUT, "w", **profile) as dst:
            dst.write(data, 1)

print("saved:", OUT)
print("built-up class code = 50")
print("Do not calculate final 500 m fractions until Step 5A-3 harmonization.")
