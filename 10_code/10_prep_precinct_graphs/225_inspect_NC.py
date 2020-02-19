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
#matplotlib.use('Agg')
import matplotlib.pyplot as plt 
import networkx as nx
from functools import partial
import json
import random
import pysal as ps
from gerrychain import Graph


from gerrychain import Graph, Partition, Election
from gerrychain.updaters import Tally, cut_edges

#state_fip = '06'

#seed_num = '2'


fips_list = [
        '01',
        #'02',
        '04',
        '05',
        #'06',
        '08',
        '09',
        #'10',
        #'12',
        '13',
        '16',
        '17',
        '18',
        '19',
        '20',
        '21',
        '22',
        '23',
        '24',
        '25',
        '26',
        '27',
        '28',
        '29',
        #'30',
        '31',
        '32',
        '33',
        '34',
        '35',
        '36',
        '37',
        #'38',
        '39',
        '40',
        '42',
        '44',
        '45',
        #'46',
        '47',
        '48',
        '49',
        #'50',
        '51',
        '53',
        '54',
        '55',
        #'56'
             ]

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


bvap_dict = {'01': (1, 1, 1), '04': (0, 0, 0), '05': (0, 0, 0), '06': (0, 0, 0), '08': (0, 0, 0), '09': (0, 0, 0), '12': (3, 3, 1), '13': (4, 4, 3), '16': (0, 0, 0), '17': (3, 3, 2), '18': (0, 0, 0), '19': (0, 0, 0), '20': (0, 0, 0), '21': (0, 0, 0), '22': (1, 1, 1), '23': (0, 0, 0), '24': (2, 2, 2), '25': (0, 0, 0), '26': (2, 2, 2), '27': (0, 0, 0), '28': (1, 1, 1), '29': (1, 1, 0), '31': (0, 0, 0), '32': (0, 0, 0), '33': (0, 0, 0), '34': (1, 1, 1), '35': (0, 0, 0), '36': (3, 3, 3), '37': (2, 2, 1), '39': (1, 1, 1), '40': (0, 0, 0), '42': (1, 1, 1), '44': (0, 0, 0), '45': (1, 1, 1), '47': (1, 1, 1), '48': (2, 0, 0), '49': (0, 0, 0), '51': (1, 1, 1), '53': (0, 0, 0), '54': (0, 0, 0), '55': (0, 0, 0)}
hvap_dict = {'01': (0, 0, 0), '04': (2, 2, 2), '05': (0, 0, 0), '06': (15, 12, 12), '08': (0, 0, 0), '09': (0, 0, 0), '12': (4, 3, 3), '13': (0, 0, 0), '16': (0, 0, 0), '17': (1, 1, 1), '18': (0, 0, 0), '19': (0, 0, 0), '20': (0, 0, 0), '21': (0, 0, 0), '22': (0, 0, 0), '23': (0, 0, 0), '24': (0, 0, 0), '25': (0, 0, 0), '26': (0, 0, 0), '27': (0, 0, 0), '28': (0, 0, 0), '29': (0, 0, 0), '31': (0, 0, 0), '32': (0, 0, 0), '33': (0, 0, 0), '34': (1, 1, 1), '35': (2, 1, 0), '36': (4, 2, 2), '37': (0, 0, 0), '39': (0, 0, 0), '40': (0, 0, 0), '42': (0, 0, 0), '44': (0, 0, 0), '45': (0, 0, 0), '47': (0, 0, 0), '48': (10, 10, 9), '49': (0, 0, 0), '51': (0, 0, 0), '53': (0, 0, 0), '54': (0, 0, 0), '55': (0, 0, 0)}



seed2bound = {0: .4, 1: .45, 2: .5}




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

def VRAify_seeds(state_fips,seed_num):




    #bbound = bvap_dict[state_fips][seed_num]
    #hbound = hvap_dict[state_fips][seed_num]
    #percbound = seed2bound[seed_num]
    

    graph = Graph.from_json(f'../../20_intermediate_files/precinct_graphs/preseed/precinct_graphs_{state_fips}.json')#_seed{seed_num}.json')
    
    #nx.draw(graph, pos = {n:(graph.nodes[n]['C_X'],graph.nodes[n]['C_Y']) for n in graph.nodes()}, node_size = 5)
    #plt.show()
    #print(len(list(graph.neighbors(22065))))
    #print( graph.nodes[22065] )
    for n in graph.nodes():
        if int(graph.nodes[n]['OBJECTID'] in [138165, 136321, 136319,136312]:
            graph.nodes[n]['district'] = 293
        if int(graph.nodes[n]['OBJECTID'] in [138121, 136672,136673,136669]:
            graph.nodes[n]['district'] = 289
            
        #if state_fips in ['06','12'] and n==0:
        #    print(state_fips,nx.is_connected(graph),graph.nodes[n])
        #    print(len(list(graph.neighbors(22065))))#(nx.degree(graph)[343])
        graph.nodes[n]["nBVAP"] = graph.nodes[n]["pop_VAP"] - graph.nodes[n]["pop_BVAP"] 
        graph.nodes[n]["nHVAP"] = graph.nodes[n]["pop_VAP"] - graph.nodes[n]["pop_HVAP"] 

    electionbvap = Election("BVAP", {"BVAP": "pop_BVAP", "nBVAP": "nBVAP"})

    electionhvap = Election("HVAP", {"HVAP": "pop_HVAP", "nHVAP": "nHVAP"})

    initial_partition = Partition(
        graph,
        assignment='district',
        updaters={
            "cut_edges": cut_edges,
            "population": Tally("population", alias="population"),
            "BVAP" : electionbvap,
            "HVAP" : electionhvap
        }
    ) 
    
        
                                        
        
    part = initial_partition
    
        
          
    print(state_fips, seed_num,  "B", sum([x>percbound for x in sorted(part["BVAP"].percents("BVAP"))]),bbound,'\n',sorted(part["BVAP"].percents("BVAP")),'\n')
    print(state_fips, seed_num,  "H", sum([x>percbound for x in sorted(part["HVAP"].percents("HVAP"))]),hbound,'\n',sorted(part["HVAP"].percents("HVAP")),'\n')
    
    from gerrychain.constraints.contiguity import contiguous_components, contiguous
    
    print(contiguous(part))
    print([f"{x}\n" for x in contiguous_components(part).values()])
    
    pop_test = within_percent_of_ideal_population(initial_partition, 0.01)
    print(pop_test(part))
    
    print(part['population'].values())
    
    #print(part['population'])
            
#,(718940.0335368967, 733464.0746184502))
                
VRAify_seeds('37',0)             

        

