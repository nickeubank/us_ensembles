import geopandas as gpd
import os
import pickle
import csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt 
import networkx as nx
from functools import partial
import json
import random
###########
# Get environment var from SLURM
# and convert
###########

from gerrychain import Graph, Partition, Election
from gerrychain.updaters import Tally, cut_edges
from gerrychain import MarkovChain
from gerrychain.constraints import single_flip_contiguous
from gerrychain.proposals import propose_random_flip
from gerrychain.accept import always_accept
from gerrychain import (GeographicPartition, Partition, Graph, MarkovChain,
                        proposals, updaters, constraints, accept, Election)
from gerrychain.constraints.validity import within_percent_of_ideal_population
from gerrychain.metrics import mean_median,efficiency_gap,partisan_gini,partisan_bias

#########################################################

state_names={"02":"Alaska","01":"Alabama","05":"Arkansas","04":"Arizona",
"06":"California","08":"Colorado","09":"Connecticut","10":"Delaware",
"12":"Florida","13":"Georgia","66":"Guam","15":"Hawaii","19":"Iowa",
"16":"Idaho","17":"Illinois","18":"Indiana","20":"Kansas","21":"Kentucky",
"22":"Louisiana","25":"Massachusetts","24":"Maryland","23":"Maine","26":"Michigan",
"27":"Minnesota","29":"Missouri","28":"Mississippi","30":"Montana",
"37":"North_Carolina","38":"North_Dakota","31":"Nebraska","33":"New_Hampshire",
"34":"New_Jersey","35":"New_Mexico","32":"Nevada","36":"New_York","39":"Ohio",
"40":"Oklahoma","41":"Oregon","42":"Pennsylvania","72":"Puerto_Rico",
"44":"Rhode_Island","45":"South_Carolina","46":"South_Dakota","47":"Tennessee",
"48":"Texas","49":"Utah","51":"Virginia","50":"Vermont","53":"Washington",
"55":"Wisconsin","54":"West_Virginia","56":"Wyoming"}


#state_run = os.getenv('STATE_RUN')
#state_index = int(state_run) // 3
#run = int(state_run) % 3

#f='../20_intermediate_files/sequential_to_fips.pickle'
#state_fips = pickle.load(open(f, "rb" ))[state_index]

state_fips='37'
run='0'

newdir = f"../../../Dropbox/dislocation_intermediate_files/105_Optimized_Outputs/PP/{state_fips}_run{run}/"
os.makedirs(os.path.dirname(newdir + "init.txt"), exist_ok=True)
with open(newdir + "init.txt", "w") as f:
    f.write("Created Folder")

##########
# Set Initial Partition
##########

from gerrychain import Graph, Partition, Election
from gerrychain.updaters import Tally, cut_edges
from gerrychain.proposals import propose_random_flip

# Ignore errors: some overlap issues, but shouldn't matter for adjacency
graph = Graph.from_json(f'../20_intermediate_files/precinct_graphs/precinct_graphs_{state_fips}_seed{run}.json')

election = Election("PRES2008", {"Dem": "P2008_D", "Rep": "P2008_R"})



############
# Uniform Tree Utilities
############
from gerrychain.tree import recursive_tree_part, bipartition_tree_random, PopulatedGraph,contract_leaves_until_balanced_or_none,find_balanced_edge_cuts


def get_spanning_tree_u_w(G):
    node_set=set(G.nodes())
    x0=random.choice(tuple(node_set))
    x1=x0
    while x1==x0:
        x1=random.choice(tuple(node_set))
    node_set.remove(x1)
    tnodes ={x1}
    tedges=[]
    current=x0
    current_path=[x0]
    current_edges=[]
    while node_set != set():
        next=random.choice(list(G.neighbors(current)))
        current_edges.append((current,next))
        current = next
        current_path.append(next)

        if next in tnodes:
            for x in current_path[:-1]:
                node_set.remove(x)
                tnodes.add(x)
            for ed in current_edges:
                tedges.append(ed)
            current_edges = []
            if node_set != set():
                current=random.choice(tuple(node_set))
            current_path=[current]


        if next in current_path[:-1]:
            current_path.pop()
            current_edges.pop()
            for i in range(len(current_path)):
                if current_edges !=[]:
                    current_edges.pop()
                if current_path.pop() == next:
                    break
            if len(current_path)>0:
                current=current_path[-1]
            else:
                current=random.choice(tuple(node_set))
                current_path=[current]

    #tgraph = Graph()
    #tgraph.add_edges_from(tedges)
    return G.edge_subgraph(tedges)

def my_uu_bipartition_tree_random(
    graph,
    pop_col,
    pop_target,
    epsilon,
    node_repeats=1,
    spanning_tree=None,
    choice=random.choice):
    populations = {node: graph.nodes[node][pop_col] for node in graph}

    possible_cuts = []
    #if spanning_tree is None:
    #    spanning_tree = get_spanning_tree_u_w(graph)

    tree_attempts = 0
    while len(possible_cuts) == 0:
        tree_attempts += 1
        if tree_attempts == 25:
            #print('25 trees')
            return set()
        spanning_tree = get_spanning_tree_u_w(graph)
        h = PopulatedGraph(spanning_tree, populations, pop_target, epsilon)
        possible_cuts = find_balanced_edge_cuts(h, choice=choice)

    return choice(possible_cuts).subset



########################Dislocation Calculations##############################

state_points = gpd.read_file(f"../../../Dropbox/dislocation_intermediate_files/60_voter_knn_scores/shapefiles/{state_names[state_fips]}_Matched_Points.shp")

def abs_dislocation(partition):

    pvec = partition["PRES2008"].percents("Dem")
            
            
    state_points['current'] = state_points['precinct'].map(dict(partition.assignment))

    id_dict = {tuple(partition["PRES2008"].races)[x]:x for x in range(len(partition.parts.keys()))}


    pdict = {x:pvec[id_dict[x]] for x in partition.parts.keys()}


    state_points["dislocate"] = (state_points["KnnShrDem"] - (state_points["current"].map(pdict) - 0.0369)).abs()
    
    return state_points["dislocate"].mean()


def dloc_accept(partition):
    bound = 1

    if partition.parent is not None:
        if partition.parent["abs_dislocation"] < partition["abs_dislocation"]:
            bound = 0 
    
    return bound

def pp_accept(partition):
    bound = 1

    if partition.parent is not None:
        if partition.parent["pp"] < partition["pp"]:
            bound = 0 
    
    return bound
    
############
# Run a simulation!
############

from gerrychain.updaters import (
    Tally,
    boundary_nodes,
    cut_edges,
    cut_edges_by_part,
    exterior_boundaries,
    interior_boundaries,
    perimeter,
)


initial_partition = GeographicPartition(
    graph,
    assignment='New_Seed',
    updaters={
        "cut_edges": cut_edges,
        "population": Tally("population", alias="population"),
        "PRES2008": election,
        #"abs_dislocation": abs_dislocation
    }
)

if len(initial_partition.parts) == 1:
    import sys
    sys.exit()

from gerrychain import MarkovChain
from gerrychain.constraints import single_flip_contiguous, contiguous_bfs, within_percent_of_ideal_population
from gerrychain.proposals import propose_random_flip
from gerrychain.accept import always_accept
from gerrychain.metrics import efficiency_gap, mean_median, partisan_bias, partisan_gini, polsby_popper
from gerrychain.proposals import recom

election_names = ["PRES2008"]
num_elections = 1 

ideal_population = sum(initial_partition["population"].values()) / len(
    initial_partition
)

tree_proposal = partial(
    recom, pop_col="population", pop_target=ideal_population, epsilon=0.01, node_repeats=1, method =my_uu_bipartition_tree_random)
    
threshold = 0.02
if state_fips in ['06', '12']:
    threshold = 0.05
    


pos = {node:(float(graph.nodes[node]['C_X']), float(graph.nodes[node]['C_Y'])) for node in graph.nodes}




samples = 10
reset_steps = 200
opt_steps = 10000

intermediate_pp = []

pop_vec = []
cut_vec = []
votes = [[]]
mms = []
egs = []
pbs = []
pgs = []
hmss = []
adlocs = []
pps = []

mms.append([])
egs.append([])
pbs.append([])
pgs.append([])
hmss.append([])
adlocs.append([])
pps.append([])
assignments = []


step_index = samples

part = initial_partition

for sample in range(samples):
    #print(f"Constructing sample: {sample}")

    reset_chain = MarkovChain(
    proposal=tree_proposal, 
    constraints=[
        constraints.within_percent_of_ideal_population(initial_partition, .02),
        #compactness_bound, #single_flip_contiguous#no_more_discontiguous
    ],
    accept=accept.always_accept,
    initial_state=part,
    total_steps=reset_steps
        )
        
    for reset_part in reset_chain:
        1+1
        

    reset_partition = GeographicPartition(graph, dict(reset_part.assignment),updaters={
        "cut_edges": cut_edges,
        "population": Tally("population", alias="population"),
        "PRES2008": election,
        "pp": polsby_popper
    })
    
    compactness_bound = constraints.UpperBound(
        lambda p: len(p["cut_edges"]),
        2*len(reset_part["cut_edges"])
    )

    opt_chain = MarkovChain(
        proposal=propose_random_flip, #tree_proposal, #
        constraints=[
            constraints.within_percent_of_ideal_population(initial_partition, .02),
             single_flip_contiguous#, compactness_bound#no_more_discontiguous
        ],
        accept=pp_accept, 
        initial_state=reset_partition,
        total_steps=opt_steps
        )
                
        
    for part in opt_chain:
        intermediate_pp.append(part['pp'])


    assignments.append(dict(part.assignment))
    pop_vec.append(sorted(list(part["population"].values())))
    cut_vec.append(len(part["cut_edges"]))
    adlocs[-1].append(abs_dislocation(part))
    pps[-1].append(part['pp'])
    for elect in range(num_elections):
    
        votes[elect].append(sorted(part[election_names[elect]].percents("Dem")))
        mms[-1].append(mean_median(part[election_names[elect]]))
        egs[-1].append(efficiency_gap(part[election_names[elect]]))
        hmss[-1].append(part[election_names[elect]].wins("Dem"))
        pbs[-1].append(partisan_bias(part[election_names[elect]]))
        pgs[-1].append(partisan_gini(part[election_names[elect]]))
        
        
    plt.figure(figsize=(8, 6), dpi=500)
    nx.draw(graph, pos=pos, node_color=[dict(part.assignment)[node] for node in graph.nodes()], node_size = 20, cmap='tab20')                   
    plt.savefig(newdir + "plot" + str(sample) + ".png")
    plt.close()
        
        
    print(f"Sample {sample}: Dem Seats  {hmss[-1][-1]} Dislocation  {adlocs[-1][-1]}\n PP: {pps[-1][-1]}")     
    
    plt.figure()
    plt.plot(intermediate_pp)
    plt.xlabel("Step")
    plt.ylabel("Polsby Popper")
    plt.savefig(newdir + "intermediate_pp" + str(sample) + ".png")
    plt.close()
    
    intermediate_pp = []
    
    

        
with open(newdir+f'optimized_assignments.json', 'w') as fp1:
    json.dump(assignments, fp1)

with open(newdir + "mms" + str(step_index) + ".csv", "w") as tf1:
    writer = csv.writer(tf1, lineterminator="\n")
    writer.writerows(mms)

with open(newdir + "egs" + str(step_index) + ".csv", "w") as tf1:
    writer = csv.writer(tf1, lineterminator="\n")
    writer.writerows(egs)
    
with open(newdir + "pbs" + str(step_index) + ".csv", "w") as tf1:
    writer = csv.writer(tf1, lineterminator="\n")
    writer.writerows(pbs)
    
with open(newdir + "pgs" + str(step_index) + ".csv", "w") as tf1:
    writer = csv.writer(tf1, lineterminator="\n")
    writer.writerows(pgs)

with open(newdir + "hmss" + str(step_index) + ".csv", "w") as tf1:
    writer = csv.writer(tf1, lineterminator="\n")
    writer.writerows(hmss)
    
with open(newdir + "adloc" + str(step_index) + ".csv", "w") as tf1:
    writer = csv.writer(tf1, lineterminator="\n")
    writer.writerows(adlocs)

with open(newdir + "pop" + str(step_index) + ".csv", "w") as tf1:
    writer = csv.writer(tf1, lineterminator="\n")
    writer.writerows(pop_vec)

with open(newdir + "cuts" + str(step_index) + ".csv", "w") as tf1:
    writer = csv.writer(tf1, lineterminator="\n")
    writer.writerows([cut_vec])     
            
            
for elect in range(num_elections):
    with open(
    newdir + election_names[elect] + "_" + str(step_index) + ".csv", "w"
    ) as tf1:
        writer = csv.writer(tf1, lineterminator="\n")
        writer.writerows(votes[elect])  
     

        
    
