from pathlib import Path
import requests
import rasterio
from rasterio.mask import mask
import geopandas as gpd
import hashlib

URL = "https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map/ESA_WorldCover_10m_2021_v200_N00E102_Map.tif"
RAW = Path("ESA_WorldCover_10m_2021_v200_N00E102_Map.tif")
BOUNDARY = Path("JB_District_Boundary_MyGDI_WGS84.geojson")
CLIP = Path("JB_WorldCover_2021_v200_WGS84.tif")
SHA = Path("WorldCover_SHA256.txt")

def download():
    if RAW.exists() and RAW.stat().st_size > 1_000_000:
        print("Raw WorldCover tile already exists:", RAW)
        return
    with requests.get(URL, stream=True, timeout=120) as r:
        r.raise_for_status()
        total = int(r.headers.get("content-length", 0))
        done = 0
        with RAW.open("wb") as f:
            for chunk in r.iter_content(chunk_size=1024*1024):
                if chunk:
                    f.write(chunk)
                    done += len(chunk)
                    if total:
                        print(f"\r{done/total*100:6.2f}%  {done/1024/1024:.1f}/{total/1024/1024:.1f} MB", end="")
    print("\nDownloaded:", RAW)

def checksum():
    h = hashlib.sha256()
    with RAW.open("rb") as f:
        for b in iter(lambda: f.read(1024*1024), b""):
            h.update(b)
    SHA.write_text(h.hexdigest() + "  " + RAW.name + "\n", encoding="utf-8")
    print("SHA256:", h.hexdigest())

def clip():
    if not BOUNDARY.exists():
        print("Boundary file not found; download is complete but clip was skipped.")
        print("Expected boundary:", BOUNDARY)
        return
    b = gpd.read_file(BOUNDARY).to_crs("EPSG:4326")
    with rasterio.open(RAW) as src:
        arr, transform = mask(src, b.geometry, crop=True, nodata=src.nodata)
        meta = src.meta.copy()
        meta.update(
            height=arr.shape[1],
            width=arr.shape[2],
            transform=transform,
            compress="deflate",
            tiled=True
        )
        with rasterio.open(CLIP, "w", **meta) as dst:
            dst.write(arr)
    print("Clipped:", CLIP)

if __name__ == "__main__":
    download()
    checksum()
    clip()
    print("WorldCover built-up class code = 50.")
    print("Do not aggregate to 500 m until Step 5A-3.")
