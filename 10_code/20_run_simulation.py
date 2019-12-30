import geopandas as gpd
import os
import pickle

os.chdir('/users/nick/github/us_ensembles')

###########
# Get environment var from SLURM
# and convert
###########

# state = os.getenv('STATE')
state = 0  
f='20_intermediate_files/sequential_to_fips.pickle'
state_fips = pickle.load(open(f, "rb" ))[state]


##########
# Setup for analysis
##########

from gerrychain import Graph, Partition, Election
from gerrychain.updaters import Tally, cut_edges

file = f'20_intermediate_files/pre_processed_precinct_maps/precincts_{state_fips}.shp'

# Ignore errors: some overlap issues, but shouldn't matter for adjacency
graph = Graph.from_file(file, cols_to_add=['DISTRICT', 'population'],
                        ignore_errors=True)

election = Election("PRES2008", {"Dem": "P20008_D", "Rep": "P2008_R"})

initial_partition = Partition(
    graph,
    assignment="DISTRICT",
    updaters={
        "cut_edges": cut_edges,
        "population": Tally("population", alias="population"),
        "PRES2008": election
    }
)


############
# Run a simulation!
############

from gerrychain import MarkovChain
from gerrychain.constraints import single_flip_contiguous
from gerrychain.proposals import propose_random_flip
from gerrychain.accept import always_accept

chain = MarkovChain(
    proposal=propose_random_flip,
    constraints=[single_flip_contiguous],
    accept=always_accept,
    initial_state=initial_partition,
    total_steps=1000
)
