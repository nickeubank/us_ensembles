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
state_index = int(state_run) // 3
run = int(state_run) % 3

f='../../20_intermediate_files/sequential_to_fips.pickle'
state_fips = pickle.load(open(f, "rb" ))[state_index]

newdir = f"../../20_intermediate_files/chain_ouputs/{state_fips}_run{run}/"
os.makedirs(os.path.dirname(newdir + "init.txt"), exist_ok=True)
with open(newdir + "init.txt", "w") as f:
    f.write("Created Folder")


bvap_dict = {'01': (1, 1, 1), '04': (0, 0, 0), '05': (0, 0, 0), '06': (0, 0, 0), '08': (0, 0, 0), '09': (0, 0, 0), '12': (3, 3, 1), '13': (4, 4, 3), '16': (0, 0, 0), '17': (3, 3, 2), '18': (0, 0, 0), '19': (0, 0, 0), '20': (0, 0, 0), '21': (0, 0, 0), '22': (1, 1, 1), '23': (0, 0, 0), '24': (2, 2, 2), '25': (0, 0, 0), '26': (2, 2, 2), '27': (0, 0, 0), '28': (1, 1, 1), '29': (1, 1, 0), '31': (0, 0, 0), '32': (0, 0, 0), '33': (0, 0, 0), '34': (1, 1, 1), '35': (0, 0, 0), '36': (3, 3, 3), '37': (2, 2, 1), '39': (1, 1, 1), '40': (0, 0, 0), '42': (1, 1, 1), '44': (0, 0, 0), '45': (1, 1, 1), '47': (1, 1, 1), '48': (2, 0, 0), '49': (0, 0, 0), '51': (1, 1, 1), '53': (0, 0, 0), '54': (0, 0, 0), '55': (0, 0, 0)}
hvap_dict = {'01': (0, 0, 0), '04': (2, 2, 2), '05': (0, 0, 0), '06': (15, 12, 12), '08': (0, 0, 0), '09': (0, 0, 0), '12': (4, 3, 3), '13': (0, 0, 0), '16': (0, 0, 0), '17': (1, 1, 1), '18': (0, 0, 0), '19': (0, 0, 0), '20': (0, 0, 0), '21': (0, 0, 0), '22': (0, 0, 0), '23': (0, 0, 0), '24': (0, 0, 0), '25': (0, 0, 0), '26': (0, 0, 0), '27': (0, 0, 0), '28': (0, 0, 0), '29': (0, 0, 0), '31': (0, 0, 0), '32': (0, 0, 0), '33': (0, 0, 0), '34': (1, 1, 1), '35': (2, 1, 0), '36': (4, 2, 2), '37': (0, 0, 0), '39': (0, 0, 0), '40': (0, 0, 0), '42': (0, 0, 0), '44': (0, 0, 0), '45': (0, 0, 0), '47': (0, 0, 0), '48': (10, 10, 9), '49': (0, 0, 0), '51': (0, 0, 0), '53': (0, 0, 0), '54': (0, 0, 0), '55': (0, 0, 0)}
seed2bound = {0: .4, 1: .45, 2: .5}

bbound = bvap_dict[state_fips][run]
hbound = hvap_dict[state_fips][run]
percbound = seed2bound[run]

if state_fips == '37':
    if run == 0:
        bbound = 2
        percbound =.4
        b35 = 1

    if run == 1:
        bbound = 1
        percbound =.4
        b35 = 2
    if run == 2:
        bbound = 1
        percbound =.4
        b35 = 1

if state_fips == '12':
    if run == 0:
        bbound = 2
        percbound =.4
        b35 = 3
    if run == 1:
        bbound = 1
        percbound =.45
        b35 = 1
    if run == 2:
        bbound = 1
        percbound =.5
        b35 = 1

##########
# Set Initial Partition
##########

from gerrychain import Graph, Partition, Election
from gerrychain.updaters import Tally, cut_edges

# Ignore errors: some overlap issues, but shouldn't matter for adjacency
graph = Graph.from_json(f'../../20_intermediate_files/precinct_graphs/'
                        'VRAseeds_Final/precinct_graphs_{state_fips}_seed{run}.json')

election = Election("PRES2008", {"Dem": "P2008_D", "Rep": "P2008_R"})
for n in graph.nodes():
    graph.nodes[n]["nBVAP"] = graph.nodes[n]["pop_VAP"] - graph.nodes[n]["pop_BVAP"]
    graph.nodes[n]["nHVAP"] = graph.nodes[n]["pop_VAP"] - graph.nodes[n]["pop_HVAP"]

electionbvap = Election("BVAP", {"BVAP": "pop_BVAP", "nBVAP": "nBVAP"})

electionhvap = Election("HVAP", {"HVAP": "pop_HVAP", "nHVAP": "nHVAP"})

initial_partition = Partition(
    graph,
    assignment='New_Seed',
    updaters={
        "cut_edges": cut_edges,
        "population": Tally("population", alias="population"),
        "PRES2008": election,
        "BVAP" : electionbvap,
        "HVAP" : electionhvap
    }
)

if len(initial_partition.parts) == 1:
    print('quitting because 1 district!')
    import sys
    sys.exit()

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

def VRA_bound(partition):
    bvec = sorted(partition["BVAP"].percents("BVAP"))
    hvec = sorted(partition["HVAP"].percents("HVAP"))

    if state_fips in ['12', '37']:
        if bvec[-b35] < .345:
            return False

    if sum([x>percbound for x in bvec]) >= bbound:
        if sum([x>percbound for x in hvec]) >= hbound:
            return True
    else:
        return False


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

threshold = 0.01

chain = MarkovChain(
    proposal=proposal,
    constraints=[VRA_bound, within_percent_of_ideal_population(initial_partition, threshold)],
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

chain_flips = []

step_index = 0
for part in chain:
    step_index += 1

    if part.flips is not None:
        chain_flips.append(dict(part.flips))
    else:
        chain_flips.append(dict())
    #Too much writing!
    #if part.flips is not None:
    #    with open(newdir+f'flips_{step_index}.json', 'w') as fp:
    #        json.dump(dict(part.flips), fp)
    #else:
    #    with open(newdir+f'flips_{step_index}.json', 'w') as fp:
    #        json.dump(dict(), fp)


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

    if step_index % 10000 == 0:
        print(step_index)

        with open(newdir+f'flips_{step_index}.json', 'w') as fp1:
            json.dump(chain_flips, fp1)

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

        plt.figure(figsize=(8, 6), dpi=500)
        nx.draw(graph, pos=pos, node_color=[dict(part.assignment)[node] for node in graph.nodes()], node_size = 20, cmap='tab20')
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
        chain_flips = []
