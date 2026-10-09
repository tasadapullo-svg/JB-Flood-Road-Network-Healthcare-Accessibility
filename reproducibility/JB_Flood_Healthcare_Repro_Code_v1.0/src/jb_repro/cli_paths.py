"""Existing GitHub archive paths, relative to the repository root."""
from pathlib import Path
FOLDER="03_Nature_Portfolio_Project"
CANDIDATES={
 "edges":"Supporting_Information/Archive_Extractions/D06_Routing_Graph_Arcs_Time.csv/Data_Tables/D06_Routing_Graph_Arcs_Time.csv",
 "origins":"Figures/Data_Tables/D06_Origin_Access_to_RoutingGraph_Mapping.csv",
 "hospitals":"Figures/Data_Tables/D06_Hospital_Access_to_RoutingGraph_Mapping.csv",
 "closures":"Supporting_Information/Data_Tables/D08_Closure_Subedge_Intervals.csv",
 "origin_population":"Supporting_Information/Data_Tables/D05A_WorldPop_Origins.csv",
 "baseline_reference":"Supporting_Information/Data_Tables/D06R_Accessibility_Global_Summary.csv",
 "impact_reference":"Supporting_Information/Data_Tables/D08_Global_Accessibility_Impact_Summary.csv",
 "recovery_reference":"Submission_Materials/Data_Tables/D10_All_6_Recovery_Orders.csv",
}
def candidate_paths(root):return {k:Path(root)/FOLDER/path for k,path in CANDIDATES.items()}
