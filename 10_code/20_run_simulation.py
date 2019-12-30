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
# Set Initial Partition
##########

from gerrychain import Graph, Partition, Election
from gerrychain.updaters import Tally, cut_edges

# Ignore errors: some overlap issues, but shouldn't matter for adjacency
graph = Graph.from_json(f'20_intermediate_files/precinct_graphs/precinct_graphs_{state_fips}.json')

election = Election("PRES2008", {"Dem": "P2008_D", "Rep": "P2008_R"})

initial_partition = Partition(
    graph,
    assignment="district",
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
