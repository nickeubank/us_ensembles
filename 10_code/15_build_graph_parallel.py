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

#for idx, state_fips in enumerate(state_fips_codes):

def build_graphs(state_fips):
    print(f'starting fips {state_fips}', flush=True)
    file = f'../20_intermediate_files/pre_processed_precinct_maps/precincts_{state_fips}.shp'

    gdf = gpd.read_file(file)

    # Add centroids
    centroids = gdf.centroid

    gdf["C_X"] = centroids.x
    gdf["C_Y"] = centroids.y

    # Convert to graph
    graph = gc.Graph.from_geodataframe(gdf,ignore_errors =True)

    graph.add_data(gdf)
    totpop = sum(gdf['population'])
    num_districts = gdf.district.nunique()

    ##########
    # First, deal with unconnected nodes
    ##########

    for i in graph.islands:

        # Get distance
        island = gdf.iloc[i].geometry
        distances = gdf.geometry.distance(island).sort_values(ascending=True)
        assert distances.iloc[0] == 0
        distances = distances.iloc[1:] # Drop self

        # Find all within 5% of closest. 
        acceptance_distance = distances.iloc[0] * 1.05
        to_connect = distances[distances <= acceptance_distance].index.tolist()

        for close in to_connect: 
            graph.add_edge(i,close)
            graph[i][close]['shared_perim']=0

    # Check work
    degrees = np.array(graph.degree)
    assert (degrees != 0).any()

    ##########
    # Second, deal with unconnected components
    ##########

    from networkx import is_connected, connected_components

    # Make sure index is rows. 
    # Should happen naturally, but one can never be too sure!
    gdf = gdf.reset_index(drop=False)
    assert (gdf.index == gdf['index']).all()
    gdf = gdf.drop('index', axis='columns')


    # Let's do some connecting! :)
    print(f'starting with {len(list(connected_components(graph)))} components for {state_fips}', flush=True)

    while len(list(connected_components(graph))) > 1:
        
        sub = list(connected_components(graph))[0]

        # Split geodataframe
        trying_to_connect = gdf.loc[list(sub)].copy()
        remainder = set(gdf.index).difference(sub)
        others = gdf.loc[list(remainder)].copy()

        # Find precincts closest to the component I want to connect
        trying_union = trying_to_connect.geometry.unary_union
        distances = others.distance(trying_union).sort_values(ascending=True)

        acceptance_distance = distances.iloc[0] * 1.05
        to_match = distances[distances <= acceptance_distance].index.tolist()

        # Now find precincts in original component close to those precincts
        # and connect
        for match in to_match: 
            distances = trying_to_connect.distance(others.loc[match, 'geometry'])
            distances = distances.sort_values(ascending=True)

            acceptance_distance = distances.iloc[0] * 1.05
            to_connect = distances[distances <= acceptance_distance].index.tolist()

            for close in to_connect: 
                graph.add_edge(close, match)
                graph[close][match]['shared_perim'] = 0

        print('finished one pass')
        print(f'Now have {len(list(connected_components(graph)))} components')

    print(f'done with connections for {state_fips}', flush=True)


    for new_seed in range(3):

        cddict =  recursive_tree_part(graph, range(num_districts), 
                                      totpop / num_districts,"population", .02, 1)
        pos = {node:(float(graph.nodes[node]['C_X']), 
                     float(graph.nodes[node]['C_Y'])) for node in graph.nodes}

        for node in graph.nodes():
            graph.nodes[node]['New_Seed'] = cddict[node]
            graph.nodes[node]['pos'] = pos[node]

        graph.to_json(f'../20_intermediate_files/precinct_graphs/'
                      f'precinct_graphs_{state_fips}_seed{new_seed}.json')

    print(f'all done with {state_fips}', flush=True)
        
#######
# Now run in parallel!
#######

results = (Parallel(n_jobs=8, verbose=10, backend='multiprocessing')
           (delayed(build_graphs)
           (fips) for fips in state_fips_codes)
          )
