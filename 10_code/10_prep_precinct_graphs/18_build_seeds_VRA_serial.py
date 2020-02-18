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

#f='../../20_intermediate_files/sequential_to_fips.pickle'
#state_fips_codes = list(pickle.load(open(f, "rb" )).values())

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

##########
# Find nearest gaps and connect
##########
from gerrychain import Graph
from gerrychain.constraints.contiguity import contiguous_components, contiguous





def grow_seeds(state_fips):

    graph = Graph.from_json(f'../../20_intermediate_files/precinct_graphs/preseed/'
                            f'precinct_graphs_{state_fips}.json')
                            
    totpop = 0
    dists = set()
    for n in graph.nodes():
        totpop += graph.nodes[n]["population"]
        dists.add(graph.nodes[n]["district"])

    num_districts = len(dists)
    
    print(state_names[state_fips], num_districts)
    
    
    for new_seed in range(3):

        if state_fips not in ['12', '06']:
            cddict =  recursive_tree_part(graph, range(num_districts), 
                                              totpop / num_districts, "population", .01, 1)
        #else: 
        #    cddict =  recursive_tree_part(graph, range(num_districts), 
        #                                      totpop / num_districts, "population", .05, 1)

                

        for node in graph.nodes():
            graph.nodes[node]['New_Seed'] = cddict[node]


        graph.to_json(f'../../20_intermediate_files/precinct_graphs/seeded/'
                      f'precinct_graph_{state_fips}_seed{new_seed}.json')



n_jobs = 10

results = (Parallel(n_jobs=n_jobs, verbose=10)
           (delayed(grow_seeds)(fips) for fips in fips_list)
          )
