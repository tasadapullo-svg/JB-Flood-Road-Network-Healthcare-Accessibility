"""Write small SYNTHETIC example; these are not any Johor Bahru field records."""
from pathlib import Path
import pandas as pd
import numpy as np

p=Path(__file__).resolve().parent/"synthetic_inputs";p.mkdir(parents=True,exist_ok=True)
paths={"edges":p/"edges.csv","origins":p/"origins.csv","hospitals":p/"hospitals.csv","closures":p/"closures.csv"}
# One hub; three branch roads contain population sites; closing each branch
# disconnects that site. J46 represents an irrelevant separate road.
arc=[]
def edge(label,u,v,oneway=0):
    arc.append({"subedge_idx":label,"from_node":u,"to_node":v,"time_min":.1})
    if oneway==0:arc.append({"subedge_idx":label,"from_node":v,"to_node":u,"time_min":.1})
for lab,end in (("segJ105","A"),("segFT01","B"),("segFT003","C"),("segJ46","Z")):
    edge(lab,"H",end)
edge("hospital_edge","H","X")
pd.DataFrame(arc).to_csv(paths["edges"],index=False)
common=lambda edge, u,v,pos: {"route_subedge_idx":edge,"route_node_u":u,"route_node_v":v,"route_edge_length_m":100.,"chainage_from_u_m":pos,"oneway_code":0,"speed_kmh":60.}
origins=[]
for oid,edgeid,end,weight,area in (("oA","segJ105","A",8,"Mukim Tebrau"),("oB","segFT01","B",3,"Mukim Tebrau"),("oC","segFT003","C",2,"Mukim Plentong")):
    origins.append({"origin_id":oid,"population":weight,"subdistrict":area,**common(edgeid,"H",end,90.)})
pd.DataFrame(origins).to_csv(paths["origins"],index=False)
pd.DataFrame([{"facility_id":"HOSP_S","facility_name":"Synthetic hospital",**common("hospital_edge","H","X",20.)}]).to_csv(paths["hospitals"],index=False)
cls=[]
for cid,edgeid in (("C2025_J105_7.0_7.5","segJ105"),("C2025_FT01_19.6_20.0","segFT01"),("C2025_FT003_9.1_10.0","segFT003"),("C2025_J46_2.0_2.3","segJ46")):
    cls.append({"closure_id":cid,"subedge_idx":edgeid,"closure_a_from_u_m":np.nan,"closure_b_from_u_m":np.nan})
pd.DataFrame(cls).to_csv(paths["closures"],index=False)
print("Generated synthetic sample in",p)
print("This is NOT original research input data. A frozen reference audit MUST NOT match.")
