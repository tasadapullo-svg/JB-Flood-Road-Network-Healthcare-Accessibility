"""Small *synthetic* topology tests. Passing these is not field-data reproduction."""
import numpy as np
import pandas as pd
import pytest
from jb_repro.engine import Simulation, summarize, all_restoration_orders
from jb_repro.spec import SCENARIOS

def edge(idx,u,v,tm):return {"subedge_idx":idx,"from_node":u,"to_node":v,"time_min":tm}

def site(idx,side,position,oneway=0,speed=60,subdistrict="A",pop=1,siteid="X",hospital=False):
    d={"route_subedge_idx":idx,"route_node_u":side[0],"route_node_v":side[1],"route_edge_length_m":100,"chainage_from_u_m":position,"oneway_code":oneway,"speed_kmh":speed}
    if hospital:d["facility_id"]=siteid
    else:d.update({"origin_id":siteid,"population":pop,"subdistrict":subdistrict})
    return d

def make(closure=True,oneway=1):
    # Origin travels A->B->C (edges e1 and e2); hospital is at C on e3.
    edges=pd.DataFrame([edge("e1","A","B",.1),edge("e2","B","C",.1),edge("e3","C","D",.1)])
    origins=pd.DataFrame([site("e1",("A","B"),40,oneway=oneway,pop=8,siteid="p1")])
    hosp=pd.DataFrame([site("e3",("C","D"),1,oneway=1,hospital=True,siteid="h")])
    cls=pd.DataFrame([{"closure_id":"cut","subedge_idx":"e2","closure_a_from_u_m":np.nan,"closure_b_from_u_m":np.nan}]) if closure else pd.DataFrame(columns=["closure_id","subedge_idx","closure_a_from_u_m","closure_b_from_u_m"])
    return Simulation(origins,hosp,edges,cls)

def test_forward_oneway_and_full_block():
    sim=make()
    base=sim.solve()
    assert base.reachable.iloc[0]
    assert base.travel_time_min.iloc[0]==pytest.approx(.06+.1+.001,rel=1e-8)
    closed=sim.solve(["cut"])
    assert not closed.reachable.iloc[0]
    assert summarize(base,closed,"cut")["newly_unreachable_population"]==8

def test_origin_reverse_exit_respects_d06r():
    # One-way A->B means departing to u=A is illegal (D06R fix).
    e=pd.DataFrame([edge("e1","A","B",.1),edge("e2","A","C",.1),edge("e3","C","D",.1)])
    o=pd.DataFrame([site("e1",("A","B"),40,oneway=1,siteid="p")])
    h=pd.DataFrame([site("e3",("C","D"),0,oneway=1,hospital=True,siteid="h")])
    cls=pd.DataFrame(columns=["closure_id","subedge_idx","closure_a_from_u_m","closure_b_from_u_m"])
    assert not Simulation(o,h,e,cls).solve().reachable.iloc[0]
    # A two-way origin can instead depart to A and reach hospital C.
    o.loc[0,"oneway_code"]=0
    assert Simulation(o,h,e,cls).solve().reachable.iloc[0]

def test_direct_same_edge_and_partial_barrier():
    # No graph round-trip: origin at 20 m, hospital at 80 m, direct 0.06 min.
    e=pd.DataFrame([edge("e1","A","B",.1)])
    o=pd.DataFrame([site("e1",("A","B"),20,oneway=1,siteid="p")])
    h=pd.DataFrame([site("e1",("A","B"),80,oneway=1,hospital=True,siteid="h")])
    c=pd.DataFrame([{"closure_id":"part","subedge_idx":"e1","closure_a_from_u_m":45.,"closure_b_from_u_m":55.}])
    sim=Simulation(o,h,e,c)
    assert sim.solve().travel_time_min.iloc[0]==pytest.approx(.06)
    assert not sim.solve(["part"]).reachable.iloc[0]

def test_partial_close_preserves_same_side_access():
    e=pd.DataFrame([edge("e1","A","B",.1),edge("e2","A","C",.1)])
    o=pd.DataFrame([site("e1",("A","B"),20,oneway=0,siteid="p")])
    h=pd.DataFrame([site("e2",("A","C"),0,oneway=0,hospital=True,siteid="h")])
    c=pd.DataFrame([{"closure_id":"part","subedge_idx":"e1","closure_a_from_u_m":45.,"closure_b_from_u_m":55.}])
    sim=Simulation(o,h,e,c)
    assert sim.solve(["part"]).reachable.iloc[0]
    assert sim.solve(["part"]).travel_time_min.iloc[0]==pytest.approx(.02)

def test_duplicate_arcs_choose_min_not_sum():
    sim=make()
    sim.edges=pd.concat([sim.edges,sim.edges.iloc[[1]].assign(time_min=.15)],ignore_index=True)
    sim.__post_init__()
    assert sim.solve().travel_time_min.iloc[0]==pytest.approx(.161)

def test_unmatched_closure_fail_closed():
    sim=make()
    with pytest.raises(ValueError,match="Missing exact closure"):
        sim.solve(["not_anchored"])

def test_bad_arc_label_rejected():
    sim=make()
    sim.edges.loc[0,"subedge_idx"]="wrong"
    with pytest.raises(ValueError,match="mapped origin/hospital"):
        Simulation(sim.origins,sim.hospitals,sim.edges,sim.closures)
