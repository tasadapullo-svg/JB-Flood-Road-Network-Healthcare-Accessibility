"""Compare computed numbers against frozen archived targets, without data substitution."""
from __future__ import annotations
import json
from pathlib import Path
from .spec import REFERENCE_TARGETS

def compare_targets(summaries:dict[str,dict], outdir:Path, tolerance_population:float=.02, tolerance_pp:float=.0001, tolerance_time_min:float=.0001):
    entries=[]
    mapping={
      "baseline_reachable_population":("S0","reachable_population"),
      "baseline_mean_min":("S0","mean_min"),
      "baseline_30min_coverage_pct":("S0","coverage_30min_pct"),
      "MAR20_newly_unreachable_population":("MAR20_OBSERVED","newly_unreachable_population"),
      "MAR20_newly_unreachable_origins":("MAR20_OBSERVED","newly_unreachable_origins"),
      "MAR20_population_delayed_ge_1min":("MAR20_OBSERVED","population_delay_ge_1min"),
      "MAR20_delta_30min_pp":("MAR20_OBSERVED","delta_30min_pp"),
      "J105_newly_unreachable_population":("J105","newly_unreachable_population"),
      "FT01_newly_unreachable_population":("FT01","newly_unreachable_population"),
      "FT003_newly_unreachable_population":("FT003","newly_unreachable_population"),
      "J46_newly_unreachable_population":("J46","newly_unreachable_population")}
    for key,reference in REFERENCE_TARGETS.items():
        scenario,metric=mapping[key]
        if scenario not in summaries:
            entries.append({"metric":key,"status":"NOT_RUN","frozen_reference":reference})
            continue
        actual=float(summaries[scenario][metric])
        tol=tolerance_pp if "_pct" in key or "_pp" in key else tolerance_time_min if "min" in key else 0 if "origins" in key else tolerance_population
        delta=actual-reference
        entries.append({"metric":key,"scenario":scenario,"frozen_reference":reference,"computed":actual,"difference":delta,"tolerance":tol,"status":"PASS" if abs(delta)<=tol else "FAIL"})
    state="PASS" if all(e["status"]=="PASS" for e in entries) else "NOT_VERIFIED"
    result={"overall":state,"description":"Comparison of independently computed outputs with archived values; not the original execution code.","checks":entries}
    outdir=Path(outdir);outdir.mkdir(parents=True,exist_ok=True)
    (outdir/"frozen_reference_comparison.json").write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding="utf-8")
    return result
