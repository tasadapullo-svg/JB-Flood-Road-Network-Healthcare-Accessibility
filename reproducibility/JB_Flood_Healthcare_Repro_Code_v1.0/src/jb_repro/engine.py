"""Directed-graph accessibility engine with partial-closure aware point connectors.

This is a new implementation from method descriptions, NOT the original source.
"""
from __future__ import annotations
from dataclasses import dataclass
from itertools import permutations
from typing import Sequence
import numpy as np
import pandas as pd
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import dijkstra
from .io import validate_tables
from .spec import RESTORATION_ROADS, SCENARIOS

EPS=1e-7

def weighted_quantile(values: np.ndarray, weights: np.ndarray, q: float) -> float:
    if len(values)==0: return float("nan")
    ix=np.argsort(values,kind="stable");v=values[ix]; w=weights[ix]
    # First observed value with cumulative population weight >= requested quantile.
    return float(v[min(len(v)-1, int(np.searchsorted(np.cumsum(w),q*w.sum(),side="left")))])

def _key(x): return str(x)

def _intervals(closures: pd.DataFrame, active_ids: Sequence[str]) -> dict[str,list[tuple[float,float]]]:
    out={}
    if not active_ids:return out
    filtered=closures[closures.closure_id.isin(active_ids)]
    for row in filtered.itertuples(index=False):
        a=float(row.closure_a_from_u_m) if pd.notna(row.closure_a_from_u_m) else float("-inf")
        b=float(row.closure_b_from_u_m) if pd.notna(row.closure_b_from_u_m) else float("inf")
        out.setdefault(_key(row.subedge_idx),[]).append((a,b))
    missing=set(active_ids)-set(filtered.closure_id)
    if missing:raise ValueError(f"Missing exact closure edge records: {sorted(missing)}")
    return out

def _clear(intervals:list[tuple[float,float]], x:float,y:float) -> bool:
    # Check if positive-length overlap; position touching a closed point is handled separately.
    a,b=sorted((x,y))
    return all(max(a,lo) >= min(b,hi)-EPS for lo,hi in intervals)

def _inside(intervals:list[tuple[float,float]], pos:float) -> bool:
    return any(a+EPS < pos < b-EPS or (a==float("-inf") and b==float("inf")) for a,b in intervals)

@dataclass
class Simulation:
    origins:pd.DataFrame
    hospitals:pd.DataFrame
    edges:pd.DataFrame
    closures:pd.DataFrame

    def __post_init__(self):
        validate_tables(self.edges,self.origins,self.hospitals,self.closures)
        nodes=np.unique(pd.concat([self.edges.from_node,self.edges.to_node,self.origins.route_node_u,self.origins.route_node_v,self.hospitals.route_node_u,self.hospitals.route_node_v],ignore_index=True).astype(str).to_numpy())
        self.nodes=nodes
        self.nodeindex={x:i for i,x in enumerate(nodes)}
        self.hospitals=self.hospitals.sort_values("facility_id").reset_index(drop=True).copy()
        self.origins=self.origins.reset_index(drop=True).copy()
        self.hospital_ids=self.hospitals.facility_id.astype(str).to_numpy()
        self.edge_id=self.edges.subedge_idx.astype(str).to_numpy()
        self.arc_from=self.edges.from_node.astype(str).map(self.nodeindex).to_numpy(dtype=np.int64)
        self.arc_to=self.edges.to_node.astype(str).map(self.nodeindex).to_numpy(dtype=np.int64)
        self.arc_time=self.edges.time_min.to_numpy(dtype=float)
        self.origin_u=self.origins.route_node_u.astype(str).map(self.nodeindex).to_numpy(dtype=np.int64)
        self.origin_v=self.origins.route_node_v.astype(str).map(self.nodeindex).to_numpy(dtype=np.int64)
        self.hosp_u=self.hospitals.route_node_u.astype(str).map(self.nodeindex).to_numpy(dtype=np.int64)
        self.hosp_v=self.hospitals.route_node_v.astype(str).map(self.nodeindex).to_numpy(dtype=np.int64)
        self.origin_pos=self.origins.chainage_from_u_m.to_numpy(dtype=float)
        self.hosp_pos=self.hospitals.chainage_from_u_m.to_numpy(dtype=float)
        self.origin_len=self.origins.route_edge_length_m.to_numpy(dtype=float)
        self.hosp_len=self.hospitals.route_edge_length_m.to_numpy(dtype=float)
        self.origin_speed=self.origins.speed_kmh.to_numpy(dtype=float)
        self.hosp_speed=self.hospitals.speed_kmh.to_numpy(dtype=float)
        self.origin_dir=self.origins.oneway_code.to_numpy(dtype=int)
        self.hosp_dir=self.hospitals.oneway_code.to_numpy(dtype=int)
        self.origin_edge=self.origins.route_subedge_idx.astype(str).to_numpy()
        self.hosp_edge=self.hospitals.route_subedge_idx.astype(str).to_numpy()
        self.origin_pop=self.origins.population.to_numpy(dtype=float)
        self.nnode=len(self.nodes)
        self.nhosp=len(self.hospitals)

    def solve(self, active_closure_ids: Sequence[str]=()) -> pd.DataFrame:
        ivs=_intervals(self.closures,active_closure_ids)
        n=self.nnode; h=self.nhosp
        keep=~np.isin(self.edge_id,list(ivs))
        src=list(self.arc_from[keep]);dst=list(self.arc_to[keep]);weights=list(self.arc_time[keep]);
        # One virtual sink for each eligible hospital. Each sink can only be
        # approached along a legally directed section of its snapped subedge.
        for j in range(h):
            seg=ivs.get(self.hosp_edge[j],[])
            p=self.hosp_pos[j];L=self.hosp_len[j]
            if _inside(seg,p):continue
            if self.hosp_dir[j]!=-1 and _clear(seg,0.,p):
                src.append(self.hosp_u[j]);dst.append(n+j);weights.append(p*0.06/self.hosp_speed[j])
            if self.hosp_dir[j]!=1 and _clear(seg,p,L):
                src.append(self.hosp_v[j]);dst.append(n+j);weights.append((L-p)*0.06/self.hosp_speed[j])
        # Arc-level duplicate pairs are resolved with MIN, never SUM: COO
        # -> CSR by itself would incorrectly sum duplicate directed arcs.
        arcs=pd.DataFrame({"u":src,"v":dst,"t":weights}).groupby(["u","v"],sort=False,as_index=False).t.min()
        graph=coo_matrix((arcs.t.to_numpy(dtype=float),(arcs.u.to_numpy(dtype=int),arcs.v.to_numpy(dtype=int))),shape=(n+h,n+h)).tocsr()
        dist=dijkstra(graph.transpose().tocsr(),directed=True,indices=np.arange(n,n+h))
        del graph,arcs
        ns=len(self.origins)
        # Evaluate at the actual projected position on each road subedge,
        # not at a rounded road node. Origin departure direction is D06R.
        result=np.full((ns,h),np.inf,dtype=np.float64)
        o_u=np.full(ns,np.inf);o_v=np.full(ns,np.inf)
        for i in range(ns):
            seg=ivs.get(self.origin_edge[i],[]);p=self.origin_pos[i];L=self.origin_len[i]
            if _inside(seg,p):continue
            if self.origin_dir[i]!=1 and _clear(seg,0.,p):
                o_u[i]=p*0.06/self.origin_speed[i]
            if self.origin_dir[i]!=-1 and _clear(seg,p,L):
                o_v[i]=(L-p)*0.06/self.origin_speed[i]
        for j in range(h):
            result[:,j]=np.minimum(o_u+dist[j,self.origin_u],o_v+dist[j,self.origin_v])
            # Direct same-edge routes are necessary even if node-based travel
            # would otherwise require a detour to the far endpoint.
            same=np.where(self.origin_edge==self.hosp_edge[j])[0]
            for i in same:
                if not np.isfinite(o_u[i]) and not np.isfinite(o_v[i]):continue
                p0=self.origin_pos[i];p1=self.hosp_pos[j]
                orient=self.origin_dir[i]
                if orient==1 and p1<p0-EPS:continue
                if orient==-1 and p1>p0+EPS:continue
                seg=ivs.get(self.origin_edge[i],[])
                if not _clear(seg,p0,p1) or _inside(seg,p1):continue
                # Destination speed and origin speed should agree for one
                # shared subedge; fail rather than silently reconcile.
                if abs(self.origin_speed[i]-self.hosp_speed[j])>1e-6:
                    raise ValueError("Same-edge origin/hospital speed mismatch; check input subedge mapping")
                direct=abs(p1-p0)*0.06/self.origin_speed[i]
                result[i,j]=min(result[i,j],direct)
        best_idx=np.argmin(result,axis=1)
        best_t=result[np.arange(ns),best_idx]
        reachable=np.isfinite(best_t)
        hospital=np.where(reachable,self.hospital_ids[best_idx],"")
        frame=pd.DataFrame({"origin_id":self.origins.origin_id.astype(str),"population":self.origin_pop,"subdistrict":self.origins.subdistrict.astype(str),"reachable":reachable,"nearest_hospital_id":hospital,"travel_time_min":best_t})
        for m in [30,45,60]:frame[f"within_{m}min"]=best_t<=m
        return frame


def summarize(base:pd.DataFrame,now:pd.DataFrame,scenario:str) -> dict:
    if not base.origin_id.equals(now.origin_id) or not np.array_equal(base.population,now.population):
        raise ValueError("Baseline and scenario origins/population weights mismatch")
    w=now.population.to_numpy(float); t=now.travel_time_min.to_numpy(float); b=base.travel_time_min.to_numpy(float)
    finite=np.isfinite(t);common=finite&np.isfinite(b)
    newly=(~finite)&np.isfinite(b)
    delayed=common&(t-b >= 1-1e-8)
    total=w.sum()
    out={"scenario":scenario,"origin_count":len(now),"population_total":float(total),"reachable_population":float(w[finite].sum()),"reachable_population_pct":float(100*w[finite].sum()/total),"newly_unreachable_origins":int(newly.sum()),"newly_unreachable_population":float(w[newly].sum()),"population_delay_ge_1min":float(w[delayed].sum()),"population_delay_ge_5min":float(w[common & (t-b>=5-1e-8)].sum()),"population_delay_ge_10min":float(w[common & (t-b>=10-1e-8)].sum()),"mean_min":float(np.average(t[finite],weights=w[finite])) if finite.any() else float("nan"),"weighted_p90_min":weighted_quantile(t[finite],w[finite],.9),"weighted_mean_increase_common_reachable_min":float(np.average(t[common]-b[common],weights=w[common])) if common.any() else float("nan")}
    for threshold in (30,45,60):
        cover=100*w[t<=threshold].sum()/total
        basecover=100*w[b<=threshold].sum()/total
        out[f"coverage_{threshold}min_pct"]=float(cover)
        out[f"delta_{threshold}min_pp"]=float(cover-basecover)
    return out

def subdistrict_summary(base:pd.DataFrame,now:pd.DataFrame,scenario:str)->pd.DataFrame:
    lost=(base.reachable & ~now.reachable).to_numpy()
    b=base[["origin_id","population","subdistrict"]].copy()
    b["newly_unreachable_weight"]=np.where(lost,now.population.to_numpy(float),0.)
    bt=base.travel_time_min.to_numpy(float); nt=now.travel_time_min.to_numpy(float)
    b["baseline_30min_weight"]=np.where(bt<=30,b.population.to_numpy(),0.)
    b["scenario_30min_weight"]=np.where(nt<=30,b.population.to_numpy(),0.)
    common=np.isfinite(bt)&np.isfinite(nt)
    b["delayed_ge_1min_weight"]=np.where(common & (nt-bt>=1-1e-8),b.population.to_numpy(),0.)
    gr=b.groupby("subdistrict",sort=True,dropna=False).agg(
        population=("population","sum"),
        newly_unreachable_population=("newly_unreachable_weight","sum"),
        baseline_30min_population=("baseline_30min_weight","sum"),
        scenario_30min_population=("scenario_30min_weight","sum"),
        delayed_ge_1min_population=("delayed_ge_1min_weight","sum"))
    gr["newly_unreachable_pct_subdistrict"]=100*gr.newly_unreachable_population/gr.population
    gr["delta_30min_pp"]=100*(gr.scenario_30min_population-gr.baseline_30min_population)/gr.population
    gr=gr.reset_index();gr.insert(0,"scenario",scenario)
    return gr

def weighted_gini(values:np.ndarray,weights:np.ndarray)->float:
    """Weighted Gini of nonnegative location-specific rates; no inferred sampling significance."""
    x=np.asarray(values,dtype=float);w=np.asarray(weights,dtype=float)
    if (w<=0).any() or (x<0).any():raise ValueError("Invalid Gini weights/rates")
    sw=float(w.sum());mu=float(np.sum(w*x)/sw)
    if mu<=0:return 0.
    return float(np.sum(np.abs(x[:,None]-x[None,:])*w[:,None]*w[None,:])/(2*mu*sw*sw))

def all_restoration_orders(sim:Simulation,baseline:pd.DataFrame,cache:dict[tuple[str,...],pd.DataFrame]):
    closers={k:tuple(SCENARIOS[k]) for k in RESTORATION_ROADS}
    def lookup(blocked_roads):
        ids=tuple(sorted(x for road in blocked_roads for x in closers[road]))
        if ids not in cache:cache[ids]=sim.solve(ids)
        return cache[ids]
    rows=[]
    allroads=tuple(RESTORATION_ROADS)
    initial=lookup(allroads)
    initial_loss=summarize(baseline,initial,"INITIAL")["newly_unreachable_population"]
    for order_id,order in enumerate(permutations(allroads),1):
        blocked=set(allroads)
        prev=initial_loss
        for stage,restored in enumerate(order,1):
            blocked.remove(restored)
            item=summarize(baseline,lookup(blocked),"RECOVERY")
            left=item["newly_unreachable_population"]
            recovered=initial_loss-left
            sub=subdistrict_summary(baseline,lookup(blocked),"RECOVERY")
            byname=sub.set_index("subdistrict")["newly_unreachable_population"]
            gini=weighted_gini(sub["newly_unreachable_pct_subdistrict"].to_numpy(),sub.population.to_numpy())
            rows.append({"order_id":order_id,"order":" > ".join(order),"stage":stage,"restored_road":restored,"remaining_closed_roads":";".join(sorted(blocked)),"incremental_population_restored":prev-left,"cumulative_population_restored":recovered,"cumulative_recovery_pct_of_initial_loss":100*recovered/initial_loss if initial_loss else 0,"remaining_newly_unreachable_population":left,"coverage_30min_pct":item["coverage_30min_pct"],"Tebrau_remaining_newly_unreachable_population":float(byname.get("Mukim Tebrau",0)),"Plentong_remaining_newly_unreachable_population":float(byname.get("Mukim Plentong",0)),"weighted_subdistrict_gini_unreachable_rate":gini})
            prev=left
    return pd.DataFrame(rows)
