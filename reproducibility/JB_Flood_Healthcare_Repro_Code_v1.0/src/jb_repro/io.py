"""Strict canonical CSV schema and explicit, checked mapping of archived columns.

Every row in edges.csv is an actually permitted directed arc. Columns:
  subedge_idx,from_node,to_node,time_min
Sites (origins.csv / hospitals.csv) are projected points on an unsplit subedge:
  origin_id,population,subdistrict,route_subedge_idx,route_node_u,route_node_v,
  route_edge_length_m,chainage_from_u_m,oneway_code,speed_kmh
  facility_id instead of origin_id/population/subdistrict for hospital sites.
Closure rows: closure_id,subedge_idx,closure_a_from_u_m,closure_b_from_u_m.
Missing interval endpoints imply a whole-subedge block; other than that do not
impute a side for ambiguous partial overlaps.
"""
from __future__ import annotations
import csv
from pathlib import Path
import pandas as pd
import numpy as np

REQUIRED = {
  "edges": ["subedge_idx", "from_node", "to_node", "time_min"],
  "origins": ["origin_id", "population", "subdistrict", "route_subedge_idx", "route_node_u", "route_node_v", "route_edge_length_m", "chainage_from_u_m", "oneway_code", "speed_kmh"],
  "hospitals": ["facility_id", "route_subedge_idx", "route_node_u", "route_node_v", "route_edge_length_m", "chainage_from_u_m", "oneway_code", "speed_kmh"],
  "closures": ["closure_id", "subedge_idx", "closure_a_from_u_m", "closure_b_from_u_m"],
}
ALIASES = {
 "edges": {
    "subedge_idx": ["subedge_idx", "route_subedge_idx", "subedge_id", "edge_idx"],
    "from_node": ["from_node", "source", "node_from", "u", "node_u", "src", "from_node_id"],
    "to_node": ["to_node", "target", "node_to", "v", "node_v", "dst", "to_node_id"],
    "time_min": ["time_min", "travel_time_min", "edge_time_min", "travel_min", "weight_min", "time_minutes", "travel_time_minutes"],
 },
 "origins": {
    "origin_id": ["origin_id", "id", "cell_id"],
    "population": ["population", "pop", "pop_weight", "population_weight"],
    "subdistrict": ["subdistrict", "mukim", "subdistrict_name", "admin_name"],
    "route_subedge_idx": ["route_subedge_idx", "subedge_idx"],
    "route_node_u": ["route_node_u", "node_u"],
    "route_node_v": ["route_node_v", "node_v"],
    "route_edge_length_m": ["route_edge_length_m", "edge_length_m"],
    "chainage_from_u_m": ["chainage_from_u_m", "distance_from_u_m"],
    "oneway_code": ["oneway_code", "oneway"],
    "speed_kmh": ["speed_kmh", "edge_speed_kmh"],
 },
 "hospitals": {
    "facility_id": ["facility_id", "hospital_id"],
    "route_subedge_idx": ["route_subedge_idx", "subedge_idx"],
    "route_node_u": ["route_node_u", "node_u"],
    "route_node_v": ["route_node_v", "node_v"],
    "route_edge_length_m": ["route_edge_length_m", "edge_length_m"],
    "chainage_from_u_m": ["chainage_from_u_m", "distance_from_u_m"],
    "oneway_code": ["oneway_code", "oneway"],
    "speed_kmh": ["speed_kmh", "edge_speed_kmh"],
 },
}

def read_csv(path: str|Path, nrows: int|None = None) -> pd.DataFrame:
    return pd.read_csv(path, encoding="utf-8-sig", nrows=nrows, low_memory=False)

def read_header(path: str|Path) -> list[str]:
    path = Path(path)
    import gzip
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, mode="rt", encoding="utf-8-sig", newline="") as f:
        return next(csv.reader(f))

def normalize_table(df: pd.DataFrame, kind: str, overrides: dict[str,str]|None=None) -> pd.DataFrame:
    if kind not in REQUIRED:
        raise ValueError(f"Unknown kind: {kind}")
    overrides=overrides or {}
    columns = {str(c).strip().lower(): str(c) for c in df.columns}
    rename={}
    if kind == "closures":
        for required in ["closure_id", "subedge_idx"]:
            if required not in df.columns:
                raise ValueError(f"Closure CSV must supply exact column {required}")
        result=df.copy()
        for col in ["closure_a_from_u_m","closure_b_from_u_m"]:
            if col not in result:
                result[col]=np.nan
        return result
    for required in REQUIRED[kind]:
        matches=[c for c in ALIASES[kind][required] if c.lower() in columns]
        if required in overrides:
            c=overrides[required]
            if c not in df.columns:
                raise ValueError(f"Mapping {required}={c} missing from source")
            matches=[c]
        if not matches:
            raise ValueError(f"{kind}: required column {required} missing. Source columns: {list(df.columns)}. Provide explicit mapping in a custom preprocessor, do NOT guess!")
        rename[columns[matches[0].lower()]]=required
    out=df.rename(columns=rename)
    if len(set(rename.values())) != len(rename):
        raise ValueError("Source column mapped to two canonical targets")
    return out

def validate_tables(edges: pd.DataFrame, origins: pd.DataFrame, hospitals: pd.DataFrame, closures: pd.DataFrame):
    for kind,df in (("edges",edges),("origins",origins),("hospitals",hospitals),("closures",closures)):
        missing=[x for x in REQUIRED[kind] if x not in df]
        if missing: raise ValueError(f"{kind} missing {missing}")
    if not len(edges) or not len(origins) or not len(hospitals): raise ValueError("Empty essential table")
    if edges[["subedge_idx","from_node","to_node","time_min"]].isna().any().any(): raise ValueError("Null arc ID/endpoints/travel time")
    if (pd.to_numeric(edges.time_min,errors="coerce")<0).any() or not np.isfinite(pd.to_numeric(edges.time_min,errors="coerce")).all(): raise ValueError("Invalid directed arc time")
    if origins.origin_id.duplicated().any() or hospitals.facility_id.duplicated().any(): raise ValueError("Duplicate origin or hospital ID")
    if origins["population"].isna().any() or (pd.to_numeric(origins.population,errors="coerce")<=0).any():raise ValueError("Each origin must have a positive numeric population weight")
    for kind,df in (("origins",origins),("hospitals",hospitals)):
        for col in ["route_edge_length_m","chainage_from_u_m","oneway_code","speed_kmh"]:
            if df[col].isna().any(): raise ValueError(f"{kind}.{col} has missing values")
        if not set(df.oneway_code.astype(int).unique()).issubset({-1,0,1}): raise ValueError(f"{kind} oneway_code must be -1,0,1")
        if (df.speed_kmh.astype(float)<=0).any(): raise ValueError("Nonpositive speed")
        if ((df.chainage_from_u_m.astype(float)<-1e-4) | (df.chainage_from_u_m.astype(float)>df.route_edge_length_m.astype(float)+1e-4)).any(): raise ValueError("Projected site chainage exceeds edge bounds")
    if closures[["closure_id","subedge_idx"]].isna().any().any():raise ValueError("Closure identifier/edge missing")
    a=closures.closure_a_from_u_m.notna(); b=closures.closure_b_from_u_m.notna()
    if (a!=b).any():raise ValueError("Closure start and end intervals must BOTH be present or BOTH be absent")
    if ((closures.loc[a,"closure_a_from_u_m"].astype(float)<0) | (closures.loc[a,"closure_b_from_u_m"].astype(float)<closures.loc[a,"closure_a_from_u_m"].astype(float))).any(): raise ValueError("Invalid closure interval")
    edgeids=set(edges.subedge_idx.astype(str).tolist()); siteids=set(pd.concat([origins.route_subedge_idx,hospitals.route_subedge_idx]).astype(str))
    badsite=siteids-edgeids
    if badsite: raise ValueError(f"{len(badsite)} mapped origin/hospital subedge IDs have no directed arcs; examples: {list(sorted(badsite))[:4]}")
    badclosure=set(closures.subedge_idx.astype(str))-edgeids
    if badclosure:raise ValueError(f"{len(badclosure)} closure subedges not in graph; examples: {list(sorted(badclosure))[:4]}")

def normalize_files(edge_in, origin_in, hospital_in, closure_in, outdir):
    outdir=Path(outdir);outdir.mkdir(parents=True,exist_ok=True)
    for kind,path in (("edges",edge_in),("origins",origin_in),("hospitals",hospital_in),("closures",closure_in)):
        df=normalize_table(read_csv(path),kind)
        target=outdir/(kind+".csv")
        df[REQUIRED[kind]].to_csv(target,index=False)
        print(f"{kind}: {len(df):,} rows -> {target}")
    es,os,hs,cs=[read_csv(outdir/(k+".csv")) for k in REQUIRED]
    validate_tables(es,os,hs,cs)
    print("Normalized data validated. This is a schema check, NOT a reproduction result.")
