"""Best-effort, fail-closed bridge from known archived paths to canonical inputs.

This is NOT a proven recreation of the original data producer pipeline.
"""
from __future__ import annotations
from pathlib import Path
import json
import hashlib
import pandas as pd
from .cli_paths import candidate_paths
from .io import read_csv, normalize_table, validate_tables


def _hash_file(path:Path)->str:
    digest=hashlib.sha256()
    with open(path,'rb') as f:
        while (b:=f.read(2**20)):digest.update(b)
    return digest.hexdigest()


def _harmonize_cols(data:pd.DataFrame,names:dict[str,list[str]])->pd.DataFrame:
    look={str(k).lower():k for k in data.columns}
    rename={}
    for dst,options in names.items():
        if dst in data.columns:continue
        for k in options:
            if k.lower() in look:
                rename[look[k.lower()]]=dst;break
    return data.rename(columns=rename)


def _merge_origin_attributes(origin:pd.DataFrame,root:Path):
    origin=_harmonize_cols(origin,{"origin_id":["origin_id","cell_id"]})
    if "origin_id" not in origin:raise ValueError("Origin mapping lacks stable origin_id; cannot safely join by row order")
    if origin.origin_id.duplicated().any():raise ValueError("Origin snapping map contains duplicate origin IDs")
    wanted=[col for col in ("population","subdistrict") if col not in origin]
    if not wanted:return origin,[]
    appended=[]
    candidates=[root/"03_Nature_Portfolio_Project/Supporting_Information/Data_Tables/D05C_WorldPop_Origins_RoadSnap.csv",root/"03_Nature_Portfolio_Project/Supporting_Information/Data_Tables/D05A_WorldPop_Origins.csv"]
    for path in candidates:
        if not wanted:break
        if not path.is_file():continue
        attrs=read_csv(path)
        attrs=_harmonize_cols(attrs,{"origin_id":["origin_id","cell_id"],"population":["population","pop","population_weight","worldpop_population"],"subdistrict":["subdistrict","mukim","mukim_name","subdistrict_name"]})
        cols=["origin_id"]+[k for k in wanted if k in attrs]
        if len(cols)==1:continue
        if "origin_id" not in attrs:continue
        if attrs.origin_id.duplicated().any():raise ValueError(f"Nonunique origin_id in joining table {path}")
        orig_ids=origin.origin_id.astype(str).tolist()
        attrs["origin_id"]=attrs.origin_id.astype(str)
        origin["origin_id"]=origin.origin_id.astype(str)
        origin=origin.merge(attrs[cols],on="origin_id",how="left",validate="one_to_one",sort=False)
        if origin.origin_id.astype(str).tolist()!=orig_ids:raise ValueError("Origin IDs changed order on join")
        appended.append(str(path))
        wanted=[col for col in wanted if col not in origin]
    if wanted:raise ValueError(f"Cannot identify {wanted} from archived origin attributes; check local columns and make an explicit keyed join")
    if origin[["population","subdistrict"]].isna().any().any():raise ValueError("Null population or subdistrict after origin-ID join")
    return origin,appended


def prepare(repo_root:str|Path,outdir:str|Path):
    root=Path(repo_root)
    paths=candidate_paths(root)
    inputs={}
    for key in ("edges","origins","hospitals","closures"):
        p=paths[key]
        if not p.is_file():
            raise FileNotFoundError(f"{key} file missing: {p}. Restore split files first using `python tools/restore_large_files.py`.")
        inputs[key]=p
    edge=normalize_table(read_csv(inputs["edges"]),"edges")
    originraw=read_csv(inputs["origins"])
    originraw,joined=_merge_origin_attributes(originraw,root)
    origins=normalize_table(originraw,"origins")
    hospital=normalize_table(read_csv(inputs["hospitals"]),"hospitals")
    closures=normalize_table(read_csv(inputs["closures"]),"closures")
    validate_tables(edge,origins,hospital,closures)
    if len(origins)!=75149 or len(hospital)!=14:
        raise ValueError(f"Study data dimensions mismatch: origins={len(origins)}, hospitals={len(hospital)}; do not relabel a different study dataset")
    total=float(origins.population.astype(float).sum())
    if abs(total-1905758.5713106135)>0.01:
        raise ValueError(f"Total population weight {total} differs from frozen 1905758.57131")
    out=Path(outdir);out.mkdir(parents=True,exist_ok=True)
    for key,df in (("edges",edge),("origins",origins),("hospitals",hospital),("closures",closures)):
        df.to_csv(out/f"{key}.csv",index=False)
    provenance={"generated_by":"independent archive adapter","source_files":{k:{"path":str(p),"sha256":_hash_file(p)} for k,p in inputs.items()},"attribute_join_files":joined,"source_origin_count":len(origins),"source_hospital_count":len(hospital),"source_population_total":total,"note":"Preprocessed input schema PASS only; reproducibility still requires a full numerical and geometry audit."}
    (out/"PREPARE_PROVENANCE.json").write_text(json.dumps(provenance,indent=2,ensure_ascii=False),encoding="utf-8")
    print(f"Prepared {len(edge):,} directed arcs, {len(origins):,} origins, {len(hospital)} hospitals in {out}")
    print("DATA SCHEMA PASS. No D06R/D08/D10 numerical reproduction has been claimed.")
