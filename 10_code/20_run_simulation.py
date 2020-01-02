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

state_run = os.getenv('STATE_RUN')
state_index = state_run // 3
run = state_run % 3


f='../20_intermediate_files/sequential_to_fips.pickle'
state_fips = pickle.load(open(f, "rb" ))[state]

newdir = f"../20_intermediate_files/chain_ouputs/{state_fips}_run{run}/"
os.makedirs(os.path.dirname(newdir + "init.txt"), exist_ok=True)
with open(newdir + "init.txt", "w") as f:
    f.write("Created Folder")

##########
# Set Initial Partition
##########

from gerrychain import Graph, Partition, Election
from gerrychain.updaters import Tally, cut_edges

# Ignore errors: some overlap issues, but shouldn't matter for adjacency
graph = Graph.from_json(f'../20_intermediate_files/precinct_graphs/precinct_graphs_{state_fips}.json')

election = Election("PRES2008", {"Dem": "P2008_D", "Rep": "P2008_R"})


initial_partition = Partition(
    graph,
    assignment='New_Seed',
    updaters={
        "cut_edges": cut_edges,
        "population": Tally("population", alias="population"),
        "PRES2008": election
    }
)


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
    if spanning_tree is None:
        spanning_tree = get_spanning_tree_u_w(graph)

    while len(possible_cuts) == 0:
        spanning_tree = get_spanning_tree_u_w(graph)
        h = PopulatedGraph(spanning_tree, populations, pop_target, epsilon)
        possible_cuts = find_balanced_edge_cuts(h, choice=choice)

    return choice(possible_cuts).subset



############
# Run a simulation!
############

from gerrychain import MarkovChain
from gerrychain.constraints import single_flip_contiguous, contiguous_bfs, within_percent_of_ideal_population
from gerrychain.proposals import propose_random_flip
from gerrychain.accept import always_accept
from gerrychain.metrics import efficiency_gap, mean_median, partisan_bias, partisan_gini
from gerrychain.proposals import recom

election_names = ["PRES2008"]
num_elections = 1 

ideal_population = sum(initial_partition["population"].values()) / len(
    initial_partition
)

proposal = partial(
    recom, pop_col="population", pop_target=ideal_population, epsilon=0.01, node_repeats=1, method =my_uu_bipartition_tree_random)
    

chain = MarkovChain(
    proposal=proposal,
    constraints=[within_percent_of_ideal_population(initial_partition, 0.05)],
    accept=always_accept,
    initial_state=initial_partition,
    total_steps=100
)

pos = {node:(float(graph.nodes[node]['C_X']), float(graph.nodes[node]['C_Y'])) for node in graph.nodes}


pop_vec = []
cut_vec = []
votes = [[]]
mms = []
egs = []
pbs = []
pgs = []
hmss = []

#chain_flips = []

step_index = 0
for part in chain: 
    step_index += 1
    
    #chain_flips.append(dict(part.flips))
    #Currently useless!
    if part.flips is not None:
        with open(newdir+f'flips_{step_index}.json', 'w') as fp:
            json.dump(dict(part.flips), fp)
    else:
        with open(newdir+f'flips_{step_index}.json', 'w') as fp:
            json.dump(dict(), fp)


    pop_vec.append(sorted(list(part["population"].values())))
    cut_vec.append(len(part["cut_edges"]))
    mms.append([])
    egs.append([])
    pbs.append([])
    pgs.append([])
    hmss.append([])
    for elect in range(num_elections):
    
        votes[elect].append(sorted(part[election_names[elect]].percents("Dem")))
        mms[-1].append(mean_median(part[election_names[elect]]))
        egs[-1].append(efficiency_gap(part[election_names[elect]]))
        hmss[-1].append(part[election_names[elect]].wins("Dem"))
        pbs[-1].append(partisan_bias(part[election_names[elect]]))
        pgs[-1].append(partisan_gini(part[election_names[elect]]))
        
    if step_index % 100 == 0:
        print(step_index)
        
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

        plt.figure()
        nx.draw(graph, pos=pos, node_color=[dict(part.assignment)[node] for node in graph.nodes()], node_size = 50, cmap='tab20')                   
        plt.savefig(newdir + "plot" + str(step_index) + ".png")
        plt.close()
        
        pop_vec = []
        cut_vec = []
        votes = [[]]
        mms = []
        egs = []
        pbs = []
        pgs = []
        hmss = []

        
    
