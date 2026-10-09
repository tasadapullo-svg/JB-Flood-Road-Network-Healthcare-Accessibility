"""Command-line workflows. Usage: jb-repro --help."""
from __future__ import annotations
import argparse
import itertools
import json
from pathlib import Path
import pandas as pd
from . import __version__
from .engine import Simulation, summarize, subdistrict_summary, all_restoration_orders
from .io import read_csv, read_header, normalize_files, validate_tables
from .spec import SCENARIOS, RESTORATION_ROADS
from .audit import compare_targets

from .cli_paths import candidate_paths, CANDIDATES

def inspect(repo_root):
    root=Path(repo_root)
    result={"repo_root":str(root.resolve()),"files":{}}
    for kind,rel in CANDIDATES.items():
        path=candidate_paths(root)[kind]
        status={"path":str(path),"exists":path.is_file()}
        if path.is_file():
            try:status["columns"]=read_header(path)
            except Exception as e:status["header_error"]=str(e)
        elif path.with_suffix(path.suffix+".restore.json").exists():
            status["note"]="Split file: run python tools/restore_large_files.py from repository root first."
        result["files"][kind]=status
    print(json.dumps(result,indent=2,ensure_ascii=False))

def _load(path):
    if not Path(path).is_file():raise FileNotFoundError(f"Required input missing: {path}")
    return read_csv(path)

def run(args):
    out=Path(args.outdir);out.mkdir(parents=True,exist_ok=True)
    e=_load(args.edges);o=_load(args.origins);h=_load(args.hospitals);c=_load(args.closures)
    validate_tables(e,o,h,c)
    s=Simulation(o,h,e,c)
    summaries={}; cache={}
    scenarios=SCENARIOS if not args.baseline_only else {"S0":()}
    baseline=s.solve(())
    baseline.to_csv(out/"S0_origin_accessibility.csv",index=False)
    cache[()]=baseline
    rows=[];sub=[]
    for name,ids in scenarios.items():
        key=tuple(sorted(ids))
        if key not in cache:cache[key]=s.solve(ids)
        now=cache[key]
        # Emit full origins only if requested to avoid large outputs by default.
        if args.full_origin_results and name!="S0":now.to_csv(out/f"{name}_origin_accessibility.csv",index=False)
        stats=summarize(baseline,now,name);summaries[name]=stats;rows.append(stats)
        sub.append(subdistrict_summary(baseline,now,name))
        print(f"{name}: reachable population {stats['reachable_population']:.3f}; newly unreachable {stats['newly_unreachable_population']:.3f}",flush=True)
    pd.DataFrame(rows).to_csv(out/"scenario_summary.csv",index=False)
    pd.concat(sub,ignore_index=True).to_csv(out/"subdistrict_summary.csv",index=False)
    if not args.baseline_only:
        orders=all_restoration_orders(s,baseline,cache)
        orders.to_csv(out/"six_restoration_orders.csv",index=False)
        # The sensitivity analysis needs actual per-position subedge sets.
        # A table with only shifted counts cannot reproduce 27 scenarios.
        if args.shifted_closures:
            shift=read_csv(args.shifted_closures)
            required={"road","shift_label","subedge_idx","closure_a_from_u_m","closure_b_from_u_m"}
            if not required.issubset(shift.columns):
                raise ValueError(f"shifted_closures CSV requires {sorted(required)}; not just counts")
            labels={"SIDE_A","NOMINAL","SIDE_B"}
            if not set(shift.shift_label).issuperset(labels):raise ValueError("Missing at least one shift label")
            results=[]
            for option in itertools.product(("SIDE_A","NOMINAL","SIDE_B"),repeat=3):
                chunks=[];act=[]
                for road,label in zip(RESTORATION_ROADS,option):
                    rows=shift[(shift.road==road)&(shift.shift_label==label)].copy()
                    if rows.empty:raise ValueError(f"No edges for road {road} shift {label}")
                    ident=f"{road}_{label}";rows["closure_id"]=ident
                    chunks.append(rows[["closure_id","subedge_idx","closure_a_from_u_m","closure_b_from_u_m"]]);act.append(ident)
                z=pd.concat(chunks,ignore_index=True)
                sim=Simulation(o,h,e,z)
                stat=summarize(baseline,sim.solve(act),";".join(option))
                results.append({"J105_shift":option[0],"FT01_shift":option[1],"FT003_shift":option[2],**stat})
            pd.DataFrame(results).to_csv(out/"shifted_27_combinations.csv",index=False)
    report=compare_targets(summaries,out)
    meta={"implementation":"independent reference reimplementation","version":__version__,"status":report["overall"],"normalized_input_required":True,"input_paths":{k:str(getattr(args,k)) for k in ("edges","origins","hospitals","closures")},"reported_results_not_presumed_replicated":True}
    (out/"run_metadata.json").write_text(json.dumps(meta,indent=2),encoding="utf-8")
    print(f"FROZEN REFERENCE AUDIT: {report['overall']}; read {out/'frozen_reference_comparison.json'}")
    if args.require_match and report["overall"]!="PASS":raise SystemExit("Frozen values not reproduced. See failed checks; DO NOT claim verified reproduction.")


def main():
    p=argparse.ArgumentParser(prog="jb-repro",description="Independent reference model, not original experimental scripts")
    p.add_argument("--version",action="version",version=__version__)
    sub=p.add_subparsers(dest="cmd",required=True)
    a=sub.add_parser("inspect",help="Inspect archived dataset paths and CSV headers")
    a.add_argument("--repo-root",required=True)
    b=sub.add_parser("normalize",help="Normalize four already joined input CSVs; strict schema validation")
    for name in ("edges","origins","hospitals","closures"):b.add_argument("--"+name,required=True)
    b.add_argument("--outdir",required=True)
    a2=sub.add_parser("prepare",help="Prepare inputs from known local archive paths (fails if keys/joins are missing)")
    a2.add_argument("--repo-root",required=True)
    a2.add_argument("--outdir",required=True)
    d=sub.add_parser("run",help="Compute D06R/D08/D10 from four canonical input CSVs")
    for name in ("edges","origins","hospitals","closures"):d.add_argument("--"+name,required=True)
    d.add_argument("--outdir",required=True)
    d.add_argument("--baseline-only",action="store_true")
    d.add_argument("--full-origin-results",action="store_true")
    d.add_argument("--shifted-closures",help="Optional full 27-case geometry-edge interval data, NOT counts-only table")
    d.add_argument("--require-match",action="store_true",help="Nonzero exit if any frozen targets mismatch")
    args=p.parse_args()
    if args.cmd=="inspect":inspect(args.repo_root)
    elif args.cmd=="prepare":
        from .archive_adapter import prepare
        prepare(args.repo_root,args.outdir)
    elif args.cmd=="normalize":normalize_files(args.edges,args.origins,args.hospitals,args.closures,args.outdir)
    else:run(args)

if __name__=="__main__":main()
