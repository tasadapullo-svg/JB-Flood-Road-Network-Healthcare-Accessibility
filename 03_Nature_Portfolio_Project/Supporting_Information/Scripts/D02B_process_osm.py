from __future__ import annotations

import csv
import hashlib
import json
import platform
import re
import shutil
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import networkx as nx
import osmium
import pandas as pd
import pyogrio
import shapely
from shapely.geometry import GeometryCollection, LineString, MultiLineString


ROOT = Path.cwd()
OSM_ROOT = ROOT / "06_Road_Network" / "OSM"
TEMP_ROOT = OSM_ROOT / "TEMP"
RUN_DIR = TEMP_ROOT / ("D02B_run_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
SNAPSHOT_DATE = "2026-10-03"
DATASET_ID = "D02"
METRIC_CRS = "EPSG:3375"
WORKING_CRS = "EPSG:4326"

RAW_PBF = OSM_ROOT / "RAW" / "malaysia-singapore-brunei-261003.osm.pbf"
RAW_MD5 = OSM_ROOT / "RAW" / "malaysia-singapore-brunei-261003.osm.pbf.md5"
BOUNDARY_WGS = ROOT / "01_Study_Area" / "Study_Area_Final" / "JB_Study_Area_Final.gpkg"
BOUNDARY_RSO = ROOT / "01_Study_Area" / "Study_Area_Final" / "JB_Study_Area_Final_RSO.gpkg"

FINAL_PATHS = {
    "clip_core": OSM_ROOT / "CLIPPED" / "CORE" / "JB_OSM_Core_20261003.osm.pbf",
    "clip_buffer": OSM_ROOT / "CLIPPED" / "ROUTING_BUFFER" / "JB_OSM_RoutingBuffer10km_20261003.osm.pbf",
    "core_wgs": OSM_ROOT / "PROCESSED" / "CORE" / "JB_OSM_RoadNetwork_Core_WGS84.gpkg",
    "core_rso": OSM_ROOT / "PROCESSED" / "CORE" / "JB_OSM_RoadNetwork_Core_RSO.gpkg",
    "buffer_wgs": OSM_ROOT / "PROCESSED" / "ROUTING_BUFFER" / "JB_OSM_RoadNetwork_RoutingBuffer10km_WGS84.gpkg",
    "buffer_rso": OSM_ROOT / "PROCESSED" / "ROUTING_BUFFER" / "JB_OSM_RoadNetwork_RoutingBuffer10km_RSO.gpkg",
    "qc_core": OSM_ROOT / "VALIDATION" / "D02_OSM_Core_RoadNetwork_QC.png",
    "qc_buffer": OSM_ROOT / "VALIDATION" / "D02_OSM_RoutingBuffer_QC.png",
    "metadata": OSM_ROOT / "METADATA" / "D02_OSM_Metadata.json",
    "dictionary": OSM_ROOT / "METADATA" / "D02_Road_Data_Dictionary.csv",
    "report": OSM_ROOT / "VALIDATION" / "D02_OSM_RoadNetwork_QC_Report.txt",
    "download_log": ROOT / "23_Metadata_Logs" / "Download_Log" / "D02_OSM_Download_Log.txt",
    "processing_log": ROOT / "23_Metadata_Logs" / "Processing_Log" / "D02_OSM_Processing_Log.txt",
}

MOTOR_HIGHWAYS = {
    "motorway",
    "motorway_link",
    "trunk",
    "trunk_link",
    "primary",
    "primary_link",
    "secondary",
    "secondary_link",
    "tertiary",
    "tertiary_link",
    "unclassified",
    "residential",
    "living_street",
    "service",
    "road",
}
TRACK_AUX = {"track"}
ROAD_CLASS_MAP = {
    "motorway": "MOTORWAY",
    "motorway_link": "MOTORWAY",
    "trunk": "TRUNK",
    "trunk_link": "TRUNK",
    "primary": "PRIMARY",
    "primary_link": "PRIMARY",
    "secondary": "SECONDARY",
    "secondary_link": "SECONDARY",
    "tertiary": "TERTIARY",
    "tertiary_link": "TERTIARY",
    "unclassified": "UNCLASSIFIED",
    "residential": "RESIDENTIAL",
    "living_street": "LIVING_STREET",
    "service": "SERVICE",
    "road": "ROAD_OTHER",
    "track": "TRACK_AUXILIARY",
}
OSM_FIELDS = [
    "osm_id",
    "osm_type",
    "highway",
    "name",
    "ref",
    "oneway",
    "lanes",
    "maxspeed",
    "bridge",
    "tunnel",
    "junction",
    "access",
    "service",
    "surface",
    "width",
    "layer",
    "lit",
    "toll",
    "motor_vehicle",
    "vehicle",
    "bicycle",
    "foot",
    "other_tags",
]
PROJECT_FIELDS = [
    "segment_id",
    "source",
    "snapshot_date",
    "study_area",
    "road_class",
    "length_m",
    "is_oneway",
    "is_bridge",
    "is_tunnel",
    "is_service",
    "motor_vehicle_candidate",
    "geometry_valid",
]
TAG_RE = re.compile(r'"([^"]+)"=>"([^"]*)"')


def fail(message: str) -> None:
    raise RuntimeError(message)


def hash_file(path: Path, algorithm: str) -> str:
    h = hashlib.new(algorithm)
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def md5_expected(path: Path) -> str | None:
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8", errors="replace").strip()
    return text.split()[0].lower() if text else None


def as_code(value) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip()
    if text.endswith(".0"):
        text = text[:-2]
    return text.zfill(2)


def validate_no_overwrite() -> None:
    existing = [str(p) for p in FINAL_PATHS.values() if p.exists()]
    if existing:
        fail("Target output exists; refusing to overwrite: " + "; ".join(existing))


def validate_boundary() -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame, gpd.GeoDataFrame, gpd.GeoDataFrame]:
    if not BOUNDARY_WGS.exists() or not BOUNDARY_RSO.exists():
        fail("D01 STUDY AREA VALIDATION: FAIL - required GPKG missing")
    layers_wgs = set(pyogrio.list_layers(BOUNDARY_WGS)[:, 0])
    layers_rso = set(pyogrio.list_layers(BOUNDARY_RSO)[:, 0])
    required = {"study_area_district", "subdistrict_units"}
    if not required.issubset(layers_wgs) or not required.issubset(layers_rso):
        fail("D01 STUDY AREA VALIDATION: FAIL - required layers missing")

    district_wgs = gpd.read_file(BOUNDARY_WGS, layer="study_area_district")
    sub_wgs = gpd.read_file(BOUNDARY_WGS, layer="subdistrict_units")
    district_rso = gpd.read_file(BOUNDARY_RSO, layer="study_area_district")
    sub_rso = gpd.read_file(BOUNDARY_RSO, layer="subdistrict_units")

    checks = [
        district_wgs.crs and district_wgs.crs.to_epsg() == 4326,
        sub_wgs.crs and sub_wgs.crs.to_epsg() == 4326,
        district_rso.crs and district_rso.crs.to_epsg() == 3375,
        len(district_wgs) == 1,
        len(sub_wgs) == 8,
        str(district_wgs.iloc[0]["NAM"]).strip().upper() == "JOHOR BAHRU",
        as_code(district_wgs.iloc[0]["KOD_NEGERI"]) == "01",
        as_code(district_wgs.iloc[0]["KOD_DAERAH"]) == "02",
    ]
    unit_counts = sub_wgs["admin_unit_type"].astype(str).str.strip().str.lower().value_counts()
    checks.extend([int(unit_counts.get("mukim", 0)) == 6, int(unit_counts.get("bandar", 0)) == 2])
    if not all(checks):
        fail("D01 STUDY AREA VALIDATION: FAIL")
    return district_wgs, sub_wgs, district_rso, sub_rso


def parse_other_tags(value) -> dict[str, str]:
    if value is None or pd.isna(value):
        return {}
    return {k: v for k, v in TAG_RE.findall(str(value))}


def tag_value(row: pd.Series, tag: str, tags: dict[str, str]):
    if tag in row.index and pd.notna(row[tag]):
        return row[tag]
    return tags.get(tag)


def bool_oneway(value):
    if value is None or pd.isna(value):
        return None
    text = str(value).strip().lower()
    if text in {"yes", "true", "1", "-1"}:
        return True
    if text in {"no", "false", "0"}:
        return False
    return None


def bool_present(value):
    if value is None or pd.isna(value):
        return None
    text = str(value).strip().lower()
    if text in {"", "no", "false", "0"}:
        return False
    return True


def iter_line_parts(geom):
    if geom is None or geom.is_empty:
        return
    if isinstance(geom, LineString):
        if len(geom.coords) >= 2:
            yield geom
    elif isinstance(geom, MultiLineString):
        for part in geom.geoms:
            if len(part.coords) >= 2:
                yield part
    elif isinstance(geom, GeometryCollection):
        for part in geom.geoms:
            yield from iter_line_parts(part)


def read_highway_lines(boundary_wgs: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    bbox = tuple(boundary_wgs.total_bounds)
    gdf = pyogrio.read_dataframe(RAW_PBF, layer="lines", bbox=bbox)
    if gdf.crs is None:
        gdf = gdf.set_crs(WORKING_CRS)
    else:
        gdf = gdf.to_crs(WORKING_CRS)
    gdf = gdf[gdf["highway"].notna()].copy()
    poly = boundary_wgs.geometry.union_all()
    gdf = gdf[gdf.geometry.notna() & ~gdf.geometry.is_empty].copy()
    gdf = gdf[gdf.geometry.intersects(poly)].copy()
    return gdf


def clip_and_standardize(
    highway_gdf: gpd.GeoDataFrame,
    boundary_wgs: gpd.GeoDataFrame,
    study_area_name: str,
) -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame, set[int]]:
    allowed = MOTOR_HIGHWAYS | TRACK_AUX
    src = highway_gdf[highway_gdf["highway"].isin(allowed)].copy()
    poly = boundary_wgs.geometry.union_all()
    rows = []
    for _, row in src.iterrows():
        inter = row.geometry.intersection(poly)
        for part in iter_line_parts(inter):
            data = row.drop(labels="geometry").to_dict()
            data["geometry"] = part
            rows.append(data)
    if not rows:
        fail("No road line geometries after clipping")
    out = gpd.GeoDataFrame(rows, geometry="geometry", crs=WORKING_CRS)

    standardized = []
    for _, row in out.iterrows():
        tags = parse_other_tags(row.get("other_tags"))
        item = {field: None for field in OSM_FIELDS}
        item["osm_id"] = str(row.get("osm_id")) if pd.notna(row.get("osm_id")) else None
        item["osm_type"] = "way"
        for field in ["highway", "name", "other_tags"]:
            item[field] = row.get(field) if field in row.index and pd.notna(row.get(field)) else None
        for field in OSM_FIELDS:
            if field in {"osm_id", "osm_type", "highway", "name", "other_tags"}:
                continue
            item[field] = tag_value(row, field, tags)
        highway = str(item["highway"]).strip()
        item["source"] = "OSM"
        item["snapshot_date"] = SNAPSHOT_DATE
        item["study_area"] = study_area_name
        item["road_class"] = ROAD_CLASS_MAP.get(highway)
        item["is_oneway"] = bool_oneway(item["oneway"])
        item["is_bridge"] = bool_present(item["bridge"])
        item["is_tunnel"] = bool_present(item["tunnel"])
        item["is_service"] = bool(highway == "service" or item["service"] not in (None, ""))
        item["motor_vehicle_candidate"] = bool(highway in MOTOR_HIGHWAYS)
        item["geometry_valid"] = bool(row.geometry.is_valid)
        item["geometry"] = row.geometry
        standardized.append(item)

    full = gpd.GeoDataFrame(standardized, geometry="geometry", crs=WORKING_CRS)
    full = full[full.geometry.notna() & ~full.geometry.is_empty].copy()
    full_rso = full.to_crs(METRIC_CRS)
    full["length_m"] = full_rso.geometry.length.astype(float).round(3)

    full["_osm_sort"] = pd.to_numeric(full["osm_id"], errors="coerce")
    full["_wkb_sort"] = full.geometry.apply(lambda g: g.wkb_hex)
    full = full.sort_values(["_osm_sort", "osm_id", "highway", "_wkb_sort"], kind="mergesort").reset_index(drop=True)
    full["segment_id"] = [f"JB_OSM_{i:08d}" for i in range(1, len(full) + 1)]
    full = full.drop(columns=["_osm_sort", "_wkb_sort"])
    full = full[PROJECT_FIELDS + OSM_FIELDS + ["geometry"]]

    motor = full[full["motor_vehicle_candidate"] == True].copy()
    aux = full[full["road_class"] == "TRACK_AUXILIARY"].copy()

    selected_ids = set()
    for osm_id in highway_gdf["osm_id"].dropna().astype(str):
        try:
            selected_ids.add(int(osm_id))
        except ValueError:
            pass
    return motor, aux, selected_ids


class RefCollector(osmium.SimpleHandler):
    def __init__(self, way_ids: set[int]):
        super().__init__()
        self.way_ids = way_ids
        self.node_ids: set[int] = set()
        self.relation_ids: set[int] = set()

    def way(self, w):
        if w.id in self.way_ids:
            for n in w.nodes:
                self.node_ids.add(n.ref)

    def relation(self, r):
        for member in r.members:
            if member.type == "w" and member.ref in self.way_ids:
                self.relation_ids.add(r.id)
                break


class PbfWriter(osmium.SimpleHandler):
    def __init__(self, out_path: Path, node_ids: set[int], way_ids: set[int], relation_ids: set[int]):
        super().__init__()
        self.writer = osmium.SimpleWriter(str(out_path))
        self.node_ids = node_ids
        self.way_ids = way_ids
        self.relation_ids = relation_ids
        self.counts = Counter()

    def node(self, n):
        if n.id in self.node_ids:
            self.writer.add_node(n)
            self.counts["nodes"] += 1

    def way(self, w):
        if w.id in self.way_ids:
            self.writer.add_way(w)
            self.counts["ways"] += 1

    def relation(self, r):
        if r.id in self.relation_ids:
            self.writer.add_relation(r)
            self.counts["relations"] += 1

    def close(self):
        self.writer.close()


def write_clipped_pbf(selected_way_ids: set[int], out_path: Path) -> dict[str, int]:
    # pyosmium on Windows can fail on non-ASCII absolute paths. The working
    # directory is the project root, so use ASCII-only relative project paths.
    raw_for_osmium = RAW_PBF.relative_to(ROOT).as_posix()
    out_for_osmium = out_path.relative_to(ROOT).as_posix()
    collector = RefCollector(selected_way_ids)
    collector.apply_file(raw_for_osmium, locations=False)
    writer = PbfWriter(Path(out_for_osmium), collector.node_ids, selected_way_ids, collector.relation_ids)
    try:
        writer.apply_file(raw_for_osmium, locations=False)
    finally:
        writer.close()
    return dict(writer.counts)


def to_rso(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    rso = gdf.to_crs(METRIC_CRS)
    rso["length_m"] = rso.geometry.length.astype(float).round(3)
    return rso


def write_gpkg(path: Path, motor_wgs, aux_wgs, boundary_wgs, buffer_wgs=None) -> None:
    motor_wgs.to_file(path, layer="motor_vehicle_roads", driver="GPKG")
    aux_wgs.to_file(path, layer="road_auxiliary", driver="GPKG")
    boundary_wgs.to_file(path, layer="boundary_reference", driver="GPKG")
    if buffer_wgs is not None:
        buffer_wgs.to_file(path, layer="routing_buffer_boundary", driver="GPKG")


def stats_for(gdf: gpd.GeoDataFrame, boundary: gpd.GeoDataFrame) -> dict:
    total_len = float(gdf["length_m"].sum() / 1000.0)
    by_highway = (
        gdf.groupby("highway", dropna=False)
        .agg(segment_count=("segment_id", "count"), length_km=("length_m", lambda s: float(s.sum() / 1000.0)))
        .reset_index()
        .sort_values("highway")
    )
    by_class = (
        gdf.groupby("road_class", dropna=False)
        .agg(segment_count=("segment_id", "count"), length_km=("length_m", lambda s: float(s.sum() / 1000.0)))
        .reset_index()
        .sort_values("road_class")
    )
    poly = boundary.geometry.union_all()
    line = gpd.GeoSeries([poly.boundary], crs=boundary.crs).iloc[0]
    outside = int(gdf.geometry.disjoint(poly).sum())
    covered = int(gdf.geometry.covered_by(poly).sum())
    crossing = int(gdf.geometry.intersects(line).sum())
    empty = int((gdf.geometry.is_empty | gdf.geometry.isna()).sum())
    invalid = int((~gdf.geometry.is_valid).sum())
    return {
        "total_segments": int(len(gdf)),
        "total_length_km": round(total_len, 3),
        "by_highway": by_highway,
        "by_road_class": by_class,
        "bridge_count": int((gdf["is_bridge"] == True).sum()),
        "tunnel_count": int((gdf["is_tunnel"] == True).sum()),
        "oneway_count": int((gdf["is_oneway"] == True).sum()),
        "service_road_count": int((gdf["road_class"] == "SERVICE").sum()),
        "unnamed_road_count": int(gdf["name"].isna().sum() + (gdf["name"].astype(str).str.strip() == "").sum()),
        "missing_highway_count": int(gdf["highway"].isna().sum()),
        "invalid_geometry_count": invalid,
        "empty_geometry_count": empty,
        "duplicate_osm_id_count": int(gdf["osm_id"].duplicated(keep=False).sum()),
        "segments_inside": covered,
        "segments_crossing_boundary": crossing,
        "segments_outside": outside,
    }


def component_diagnostic(gdf_wgs: gpd.GeoDataFrame) -> dict:
    if len(gdf_wgs) == 0:
        return {"component_count": 0, "largest_component_edges": 0, "small_component_count": 0}
    gdf = gdf_wgs.to_crs(METRIC_CRS)
    graph = nx.Graph()
    for _, row in gdf.iterrows():
        for geom in iter_line_parts(row.geometry):
            coords = list(geom.coords)
            if len(coords) < 2:
                continue
            start = (round(coords[0][0], 1), round(coords[0][1], 1))
            end = (round(coords[-1][0], 1), round(coords[-1][1], 1))
            graph.add_edge(start, end, segment_id=row["segment_id"])
    comps = list(nx.connected_components(graph))
    sizes = []
    for comp in comps:
        sizes.append(graph.subgraph(comp).number_of_edges())
    return {
        "component_count": len(comps),
        "largest_component_edges": int(max(sizes) if sizes else 0),
        "small_component_count": int(sum(1 for s in sizes if s <= 2)),
    }


def road_class_check(gdf: gpd.GeoDataFrame) -> tuple[str, list[str]]:
    classes = set(gdf["road_class"].dropna().astype(str))
    required = {"PRIMARY", "SECONDARY", "TERTIARY", "RESIDENTIAL", "SERVICE"}
    if len(classes) <= 2:
        return "FAIL", sorted(required - classes)
    missing = sorted(required - classes)
    if missing:
        return "REVIEW", missing
    return "PASS", []


def draw_core_qc(path: Path, district_wgs, roads_wgs):
    fig, ax = plt.subplots(figsize=(8, 8), facecolor="white")
    ax.set_facecolor("white")
    district_wgs.boundary.plot(ax=ax, color="black", linewidth=1.8)
    major = roads_wgs[roads_wgs["road_class"].isin(["MOTORWAY", "TRUNK", "PRIMARY", "SECONDARY", "TERTIARY"])]
    local = roads_wgs[~roads_wgs.index.isin(major.index)]
    if len(local):
        local.plot(ax=ax, color="#9a9a9a", linewidth=0.25)
    if len(major):
        major.plot(ax=ax, color="#222222", linewidth=0.65)
    ax.set_title("Johor Bahru OSM Road Network - D02 QC")
    ax.set_axis_off()
    plt.tight_layout()
    fig.savefig(path, dpi=220, facecolor="white")
    plt.close(fig)


def draw_buffer_qc(path: Path, district_wgs, buffer_wgs, roads_wgs):
    fig, ax = plt.subplots(figsize=(8, 8), facecolor="white")
    ax.set_facecolor("white")
    buffer_wgs.boundary.plot(ax=ax, color="#666666", linewidth=1.0)
    district_wgs.boundary.plot(ax=ax, color="black", linewidth=1.8)
    roads_wgs.plot(ax=ax, color="#777777", linewidth=0.22)
    ax.set_title("Johor Bahru OSM Road Network - D02 QC")
    ax.set_axis_off()
    plt.tight_layout()
    fig.savefig(path, dpi=220, facecolor="white")
    plt.close(fig)


def df_to_records(df: pd.DataFrame) -> list[dict]:
    out = []
    for rec in df.to_dict(orient="records"):
        out.append({k: (round(v, 3) if isinstance(v, float) else v) for k, v in rec.items()})
    return out


def write_dictionary(path: Path) -> None:
    rows = [
        ("segment_id", "Stable project segment identifier", "string", "derived", "derived", "", "JB_OSM_########", "Assigned after deterministic sorting within each dataset."),
        ("source", "Data source", "string", "derived", "derived", "", "OSM", ""),
        ("snapshot_date", "OSM snapshot date", "date", "derived", "derived", "", "2026-10-03", ""),
        ("study_area", "Spatial processing extent name", "string", "derived", "derived", "", "Johor Bahru District; Johor Bahru District + 10 km routing buffer", ""),
        ("road_class", "Standardized road class", "string", "derived from highway", "derived", "", "; ".join(sorted(set(ROAD_CLASS_MAP.values()))), ""),
        ("length_m", "Segment length calculated in EPSG:3375", "float", "derived", "derived", "m", ">=0", ""),
        ("is_oneway", "Standardized oneway flag", "boolean", "OSM oneway", "derived", "", "TRUE; FALSE; NULL", ""),
        ("is_bridge", "Standardized bridge flag", "boolean", "OSM bridge", "derived", "", "TRUE; FALSE; NULL", ""),
        ("is_tunnel", "Standardized tunnel flag", "boolean", "OSM tunnel", "derived", "", "TRUE; FALSE; NULL", ""),
        ("is_service", "Service-road diagnostic flag", "boolean", "OSM highway/service", "derived", "", "TRUE; FALSE", ""),
        ("motor_vehicle_candidate", "Included in formal motor-vehicle candidate network", "boolean", "OSM highway", "derived", "", "TRUE; FALSE", "Track is retained in road_auxiliary with FALSE."),
        ("geometry_valid", "Geometry validity diagnostic", "boolean", "geometry", "derived", "", "TRUE; FALSE", ""),
    ]
    for field in OSM_FIELDS:
        rows.append((field, f"Original or parsed OSM tag: {field}", "string", "OSM PBF", "original", "", "", "Null if absent; other_tags is GDAL OSM HSTORE text."))
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["field_name", "description", "type", "source", "derived_or_original", "unit", "allowed_values", "notes"])
        writer.writerows(rows)


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def main() -> None:
    start = datetime.now()
    validate_no_overwrite()
    RUN_DIR.mkdir(parents=True, exist_ok=False)
    for p in FINAL_PATHS.values():
        p.parent.mkdir(parents=True, exist_ok=True)

    raw_size = RAW_PBF.stat().st_size
    raw_mtime = datetime.fromtimestamp(RAW_PBF.stat().st_mtime).isoformat()
    expected_md5 = md5_expected(RAW_MD5)
    actual_md5 = hash_file(RAW_PBF, "md5")
    raw_sha256 = hash_file(RAW_PBF, "sha256")
    if expected_md5 and expected_md5.lower() != actual_md5.lower():
        fail("MD5_MATCH = FALSE")

    district_wgs, sub_wgs, district_rso, sub_rso = validate_boundary()
    buffer_rso = district_rso.copy()
    buffer_rso["geometry"] = buffer_rso.geometry.buffer(10000)
    buffer_wgs = buffer_rso.to_crs(WORKING_CRS)
    buffer_wgs["buffer_distance_m"] = 10000
    buffer_rso["buffer_distance_m"] = 10000

    core_highway = read_highway_lines(district_wgs)
    buffer_highway = read_highway_lines(buffer_wgs)
    core_motor, core_aux, core_way_ids = clip_and_standardize(core_highway, district_wgs, "Johor Bahru District")
    buffer_motor, buffer_aux, buffer_way_ids = clip_and_standardize(buffer_highway, buffer_wgs, "Johor Bahru District + 10 km routing buffer")

    tmp = {
        "clip_core": RUN_DIR / "JB_OSM_Core_20261003.osm.pbf",
        "clip_buffer": RUN_DIR / "JB_OSM_RoutingBuffer10km_20261003.osm.pbf",
        "core_wgs": RUN_DIR / "JB_OSM_RoadNetwork_Core_WGS84.gpkg",
        "core_rso": RUN_DIR / "JB_OSM_RoadNetwork_Core_RSO.gpkg",
        "buffer_wgs": RUN_DIR / "JB_OSM_RoadNetwork_RoutingBuffer10km_WGS84.gpkg",
        "buffer_rso": RUN_DIR / "JB_OSM_RoadNetwork_RoutingBuffer10km_RSO.gpkg",
        "qc_core": RUN_DIR / "D02_OSM_Core_RoadNetwork_QC.png",
        "qc_buffer": RUN_DIR / "D02_OSM_RoutingBuffer_QC.png",
        "metadata": RUN_DIR / "D02_OSM_Metadata.json",
        "dictionary": RUN_DIR / "D02_Road_Data_Dictionary.csv",
        "report": RUN_DIR / "D02_OSM_RoadNetwork_QC_Report.txt",
        "download_log": RUN_DIR / "D02_OSM_Download_Log.txt",
        "processing_log": RUN_DIR / "D02_OSM_Processing_Log.txt",
    }

    pbf_counts_core = write_clipped_pbf(core_way_ids, tmp["clip_core"])
    pbf_counts_buffer = write_clipped_pbf(buffer_way_ids, tmp["clip_buffer"])

    write_gpkg(tmp["core_wgs"], core_motor, core_aux, district_wgs)
    write_gpkg(tmp["core_rso"], to_rso(core_motor), to_rso(core_aux), district_rso)
    write_gpkg(tmp["buffer_wgs"], buffer_motor, buffer_aux, district_wgs, buffer_wgs)
    write_gpkg(tmp["buffer_rso"], to_rso(buffer_motor), to_rso(buffer_aux), district_rso, buffer_rso)

    draw_core_qc(tmp["qc_core"], district_wgs, core_motor)
    draw_buffer_qc(tmp["qc_buffer"], district_wgs, buffer_wgs, buffer_motor)

    core_stats = stats_for(core_motor, district_wgs)
    buffer_stats = stats_for(buffer_motor, buffer_wgs)
    core_components = component_diagnostic(core_motor)
    buffer_components = component_diagnostic(buffer_motor)
    class_status, missing_classes = road_class_check(core_motor)
    final_status = "PASS" if class_status in {"PASS", "REVIEW"} and core_stats["segments_outside"] == 0 and buffer_stats["segments_outside"] == 0 else "FAIL"

    software = {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "geopandas": gpd.__version__,
        "shapely": shapely.__version__,
        "pyogrio": pyogrio.__version__,
        "osmium_python": getattr(osmium, "__version__", "installed"),
        "matplotlib": plt.matplotlib.__version__,
        "networkx": nx.__version__,
    }
    metadata = {
        "dataset_id": DATASET_ID,
        "dataset_name": "Johor Bahru OSM Road Network Extraction and Standardisation",
        "provider": "OpenStreetMap / Geofabrik",
        "snapshot_date": SNAPSHOT_DATE,
        "raw_filename": RAW_PBF.name,
        "raw_path": str(RAW_PBF),
        "raw_md5": actual_md5,
        "raw_sha256": raw_sha256,
        "raw_file_size": raw_size,
        "raw_modified_time": raw_mtime,
        "study_area": "Johor Bahru District",
        "boundary_source": "D01 frozen official Johor Bahru District boundary",
        "boundary_file": str(BOUNDARY_WGS),
        "core_definition": "Johor Bahru District official boundary",
        "routing_buffer_distance_m": 10000,
        "original_format": "OSM PBF",
        "output_formats": ["OSM PBF", "GeoPackage", "PNG", "JSON", "CSV", "TXT"],
        "working_crs": WORKING_CRS,
        "metric_crs": METRIC_CRS,
        "software": software,
        "software_version": software,
        "processing_method": "pyogrio/GDAL OSM PBF line extraction, pyosmium selected-object PBF writing, GeoPandas/Shapely polygon clipping",
        "road_types_included": sorted(MOTOR_HIGHWAYS),
        "road_types_auxiliary": sorted(TRACK_AUX),
        "processing_datetime": start.isoformat(),
        "processing_steps": [
            "Validated D01 frozen boundary layers and CRS.",
            "Validated raw PBF MD5 and calculated SHA-256.",
            "Built Johor Bahru District core extent and 10 km routing buffer in EPSG:3375.",
            "Read OSM PBF lines with highway tags within each extent.",
            "Clipped road geometries to core and routing buffer polygons.",
            "Standardized road attributes and computed length_m in EPSG:3375.",
            "Wrote WGS84 and RSO GeoPackages, clipped OSM PBF subsets, QC maps, metadata, dictionary, and logs.",
        ],
        "notes": [
            "RAW files were copied into the required RAW directory and not modified.",
            "Track roads are retained only in road_auxiliary.",
            "Routing buffer is not the formal study area.",
            "Clipped PBF files contain selected highway ways intersecting each extent, referenced nodes, and relations referencing selected ways; geometries are not simplified or snapped.",
        ],
    }
    tmp["metadata"].write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")
    write_dictionary(tmp["dictionary"])

    end = datetime.now()
    files_generated = [str(FINAL_PATHS[k]) for k in ["clip_core", "clip_buffer", "core_wgs", "core_rso", "buffer_wgs", "buffer_rso", "qc_core", "qc_buffer", "metadata", "dictionary", "report"]]
    report = f"""D02 OSM Road Network QC Report
Processing start: {start.isoformat()}
Processing end: {end.isoformat()}

1. RAW PBF path: {RAW_PBF}
2. MD5 expected: {expected_md5}
3. MD5 actual: {actual_md5}
4. MD5 match: {str(expected_md5.lower() == actual_md5.lower()).upper() if expected_md5 else 'NO_MD5_FILE'}
5. SHA-256: {raw_sha256}
6. D01 boundary validation: PASS
7. Core boundary area: {float(district_rso.geometry.area.sum() / 1_000_000):.3f} sq km
8. Routing buffer distance: 10000 m
9. Core segment count: {core_stats['total_segments']}
10. Core road length km: {core_stats['total_length_km']}
11. Buffer segment count: {buffer_stats['total_segments']}
12. Buffer road length km: {buffer_stats['total_length_km']}
13. road_class summary:
{core_stats['by_road_class'].to_string(index=False)}
14. bridge count: core={core_stats['bridge_count']}; buffer={buffer_stats['bridge_count']}
15. tunnel count: core={core_stats['tunnel_count']}; buffer={buffer_stats['tunnel_count']}
16. oneway count: core={core_stats['oneway_count']}; buffer={buffer_stats['oneway_count']}
17. invalid geometry count: core={core_stats['invalid_geometry_count']}; buffer={buffer_stats['invalid_geometry_count']}
18. empty geometry count: core={core_stats['empty_geometry_count']}; buffer={buffer_stats['empty_geometry_count']}
19. duplicate diagnostic: core duplicated osm_id rows={core_stats['duplicate_osm_id_count']}; buffer duplicated osm_id rows={buffer_stats['duplicate_osm_id_count']}
20. spatial extent check: core inside={core_stats['segments_inside']}, crossing_boundary={core_stats['segments_crossing_boundary']}, outside={core_stats['segments_outside']}; buffer inside={buffer_stats['segments_inside']}, crossing_boundary={buffer_stats['segments_crossing_boundary']}, outside={buffer_stats['segments_outside']}
21. CRS check: WGS84 outputs EPSG:4326; RSO outputs EPSG:3375; length_m calculated in EPSG:3375
22. files generated:
{chr(10).join(files_generated)}
23. warnings:
- ROAD CLASS CHECK: {class_status}{' - missing ' + ', '.join(missing_classes) if missing_classes else ''}
- Component diagnostic core: {core_components}
- Component diagnostic buffer: {buffer_components}
- Clipped PBF counts core: {pbf_counts_core}
- Clipped PBF counts buffer: {pbf_counts_buffer}
24. final status: {final_status}
"""
    write_text(tmp["report"], report)

    download_log = f"""D02 OSM Download Log
Dataset: OSM / Geofabrik
Snapshot date: {SNAPSHOT_DATE}
Raw path: {RAW_PBF}
Raw file size: {raw_size}
MD5: {actual_md5}
SHA-256: {raw_sha256}
No new OSM data downloaded during D02-B.
QC result: {final_status}
"""
    processing_log = f"""D02 OSM Processing Log
Processing start: {start.isoformat()}
Processing end: {end.isoformat()}
Software: {json.dumps(software, ensure_ascii=False)}
Method: {metadata['processing_method']}
Outputs:
{chr(10).join(files_generated)}
QC result: {final_status}
"""
    write_text(tmp["download_log"], download_log)
    write_text(tmp["processing_log"], processing_log)

    # Move only files created in this run into their final locations after all validations complete.
    for key, final_path in FINAL_PATHS.items():
        if final_path.exists():
            fail(f"Target appeared before finalization; refusing overwrite: {final_path}")
        shutil.move(str(tmp[key]), str(final_path))

    summary = {
        "raw_pbf": str(RAW_PBF),
        "raw_size": raw_size,
        "md5_expected": expected_md5,
        "md5_actual": actual_md5,
        "sha256": raw_sha256,
        "d01_boundary_status": "PASS",
        "processing_tool": metadata["processing_method"],
        "core": core_stats,
        "buffer": buffer_stats,
        "core_components": core_components,
        "buffer_components": buffer_components,
        "road_class_check": class_status,
        "missing_road_classes": missing_classes,
        "buffer_additional_segment_count": buffer_stats["total_segments"] - core_stats["total_segments"],
        "buffer_additional_road_length_km": round(buffer_stats["total_length_km"] - core_stats["total_length_km"], 3),
        "output_files": {k: str(v) for k, v in FINAL_PATHS.items()},
        "software": software,
        "pbf_counts_core": pbf_counts_core,
        "pbf_counts_buffer": pbf_counts_buffer,
        "final_status": final_status,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
