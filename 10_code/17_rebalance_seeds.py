# -*- coding: utf-8 -*-
"""
Created on Wed Jan  8 20:37:05 2020

@author: daryl
"""

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
import pysal as ps
from gerrychain import Graph


from gerrychain import Graph, Partition, Election
from gerrychain.updaters import Tally, cut_edges

state_fip = '06'

seed_num = '2'

# Ignore errors: some overlap issues, but shouldn't matter for adjacency
graph = Graph.from_json(f'../20_intermediate_files/precinct_graphs/precinct_graphs_{state_fip}_seed{seed_num}.json')




initial_partition = Partition(
    graph,
    assignment='New_Seed',
    updaters={
        "cut_edges": cut_edges,
        "population": Tally("population", alias="population"),
    }
)

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
    constraints=[within_percent_of_ideal_population(initial_partition, 0.6)],
    accept=always_accept,
    initial_state=initial_partition,
    total_steps=100000
)

test_fun = within_percent_of_ideal_population(initial_partition, 0.05)

pos = {node:(float(graph.nodes[node]['C_X']), float(graph.nodes[node]['C_Y'])) for node in graph.nodes}


temp = 0
for part in chain:
    temp += 1
    if temp %100 == 0: 
        print(temp)
        print(part['population'])
        
    if test_fun(part):
        print(temp)
        break
        
        
new_dict = dict(part.assignment)

for node in graph.nodes():
    graph.nodes[node]['New_Seed'] = new_dict[node]
    
graph.to_json(f'../20_intermediate_files/precinct_graphs/precinct_graphs_{state_fip}_newseed{seed_num}.json')  
    
          
        


