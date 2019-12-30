import geopandas as gpd
import os
import pickle

os.chdir('/users/nick/github/us_ensembles')

###########
# Get environment var from SLURM
# and convert
###########

# state = os.getenv('STATE')
state = 22
f='20_intermediate_files/sequential_to_fips.pickle'
state_fips = pickle.load(open(f, "rb" ))[state]


##########
# Find nearest gaps and connect
##########
from gerrychain import Graph
from gerrychain.constraints.contiguity import contiguous_components, contiguous
file = f'20_intermediate_files/pre_processed_precinct_maps/precincts_{state_fips}.shp'

# Build adjacency graph and import dataframce (for distance calculations)
graph = gc.Graph.from_file(file, cols_to_add=['district', 'population'], 
                           ignore_errors=True)
gdf = gpd.read_file(file)


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
while len(list(connected_components(graph))) > 1:

    sub = list(connected_components(graph))[0]

    # Split geodataframe
    trying_to_connect = gdf.iloc[list(sub)].copy()
    remainder = set(gdf.index).difference(sub)
    others = gdf.iloc[list(remainder)].copy()

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
            graph[close, match]['shared_perim']=0
    print('finished one pass')
