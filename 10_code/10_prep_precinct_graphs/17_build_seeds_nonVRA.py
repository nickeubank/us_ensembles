import geopandas as gpd
import os
import pickle
import numpy as np
import gerrychain as gc
from gerrychain.tree import recursive_tree_part
from joblib import Parallel, delayed


###########
# Get environment var from SLURM
# and convert
###########

f='../20_intermediate_files/sequential_to_fips.pickle'
state_fips_codes = list(pickle.load(open(f, "rb" )).values())

##########
# Find nearest gaps and connect
##########
from gerrychain import Graph
from gerrychain.constraints.contiguity import contiguous_components, contiguous

graph = Graph.from_json(f'../20_intermediate_files/precinct_graphs/preseed'
                        f'precinct_graphs_{state_fips}.json')

for new_seed in range(3):

    if state_fips not in ['12', '06']:
        cddict =  recursive_tree_part(graph, range(num_districts), 
                                          totpop / num_districts, "population", .02, 1)
    else: 
        cddict =  recursive_tree_part(graph, range(num_districts), 
                                          totpop / num_districts, "population", .05, 1)

            
    pos = {node:(float(graph.nodes[node]['C_X']), 
                 float(graph.nodes[node]['C_Y'])) for node in graph.nodes}

    for node in graph.nodes():
        graph.nodes[node]['New_Seed'] = cddict[node]
        graph.nodes[node]['pos'] = pos[node]

    graph.to_json(f'../20_intermediate_files/precinct_graphs/'
                  f'precinct_graph_{state_fips}_seed{new_seed}.json')

