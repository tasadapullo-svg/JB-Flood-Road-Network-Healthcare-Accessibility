"""
Extract independent physical hydrography from the existing Geofabrik PBF.

Inputs expected in the same folder or edit paths below:
- malaysia-singapore-brunei-261003.osm.pbf
- JB_District_Boundary_MyGDI_WGS84.geojson

Outputs:
- JB_OSM_Hydrography_WGS84.gpkg
- JB_OSM_Hydrography_EPSG3377.gpkg
- JB_OSM_Hydrography_QC.csv

No historical flood points/zones and no D09 are used.
"""

from pathlib import Path
import pandas as pd
import geopandas as gpd
from pyrosm import OSM
from shapely.geometry import box

PBF = Path("malaysia-singapore-brunei-261003.osm.pbf")
BOUNDARY = Path("JB_District_Boundary_MyGDI_WGS84.geojson")
OUT_WGS = Path("JB_OSM_Hydrography_WGS84.gpkg")
OUT_3377 = Path("JB_OSM_Hydrography_EPSG3377.gpkg")

if not PBF.exists():
    raise SystemExit(f"Missing PBF: {PBF}")
if not BOUNDARY.exists():
    raise SystemExit(f"Missing boundary: {BOUNDARY}")

boundary = gpd.read_file(BOUNDARY).to_crs("EPSG:4326")
minx, miny, maxx, maxy = boundary.total_bounds

# Small context margin is physical/data-processing context only.
pad = 0.03
bbox_geom = box(minx-pad, miny-pad, maxx+pad, maxy+pad)

osm = OSM(str(PBF), bounding_box=bbox_geom)

water = osm.get_data_by_custom_criteria(
    custom_filter={"waterway":["river","stream","canal","drain","ditch"]},
    filter_type="keep",
    keep_nodes=False,
    keep_ways=True,
    keep_relations=True
)

coast = osm.get_data_by_custom_criteria(
    custom_filter={"natural":["coastline"]},
    filter_type="keep",
    keep_nodes=False,
    keep_ways=True,
    keep_relations=True
)

def clean(gdf, role):
    if gdf is None or len(gdf) == 0:
        return gpd.GeoDataFrame(columns=["name","waterway","natural","osm_type","id","role","geometry"],
                                geometry="geometry", crs="EPSG:4326")
    gdf = gdf.to_crs("EPSG:4326").copy()
    gdf = gdf[gdf.geometry.notna() & ~gdf.geometry.is_empty].copy()
    gdf = gpd.clip(gdf, boundary)
    keep = [c for c in ["name","waterway","natural","osm_type","id","geometry"] if c in gdf.columns]
    gdf = gdf[keep].copy()
    for c in ["name","waterway","natural","osm_type","id"]:
        if c not in gdf.columns:
            gdf[c] = None
    gdf["role"] = role
    return gdf[["name","waterway","natural","osm_type","id","role","geometry"]]

water = clean(water, "HYDROGRAPHY")
coast = clean(coast, "COASTLINE")

major = water[water["waterway"].isin(["river","stream","canal"])].copy()
drain = water[water["waterway"].isin(["drain","ditch"])].copy()

for p in [OUT_WGS, OUT_3377]:
    if p.exists():
        p.unlink()

for name, gdf in [("major_hydrography",major),("osm_drain_baseline",drain),("coastline",coast)]:
    gdf.to_file(OUT_WGS, layer=name, driver="GPKG")
    gdf.to_crs("EPSG:3377").to_file(OUT_3377, layer=name, driver="GPKG")

qc = pd.DataFrame([
    ["major_hydrography_features",len(major)],
    ["river",int((major.waterway=="river").sum())],
    ["stream",int((major.waterway=="stream").sum())],
    ["canal",int((major.waterway=="canal").sum())],
    ["osm_drain_baseline_features",len(drain)],
    ["drain",int((drain.waterway=="drain").sum())],
    ["ditch",int((drain.waterway=="ditch").sum())],
    ["coastline_features",len(coast)],
    ["all_major_valid",bool(major.geometry.is_valid.all()) if len(major) else True],
    ["all_drain_valid",bool(drain.geometry.is_valid.all()) if len(drain) else True],
    ["all_coast_valid",bool(coast.geometry.is_valid.all()) if len(coast) else True],
], columns=["metric","value"])
qc.to_csv("JB_OSM_Hydrography_QC.csv", index=False)

print(qc.to_string(index=False))
print("Saved:", OUT_WGS, OUT_3377)
