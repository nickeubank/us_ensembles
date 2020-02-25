import geopandas as gpd
import os
import pickle
import csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt 
import seaborn as sns
import networkx as nx
from functools import partial
import json
import random
from maup import assign
import numpy as np
import ast
#from dislocation_chain_utility import * 
from gerrychain.constraints.contiguity import contiguous_components, contiguous

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


num_elections = 1

election_names = ["PRES2008"]

election_columns = [["P2008_D",  "P2008_R"]]


#1 thourgh 16 only wrote a single file. 
fips_list = [
        #'01',
        ##'02',
        #'04',
        #'05',
        ##'06',
        #'08',
        #'09',
        ##'10',
        ##'11',
        ##'12',
        #'13',
        #'16',
        #'17',
        '18',
        #'19',
        #'20',
        #'21',
        #'22',
        '23',
        #'24',
        #'25',
        '26',
        '27',
        #'28',
        '29',
        ##'30',
        #'31',
        #'32',
        #'33',
        '34',
        #'35',
        '36',
        '37',
        ##'38',
        #'39',
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
        #'54',
        '55',
        #'56'
             ]

#fips_list = ['12','36']
plan_name = "Enacted"

election_name = election_names[0]



from gerrychain import Graph, Partition, Election
from gerrychain.updaters import Tally, cut_edges

    
##
# Analysis function to parallelize
##
    
    
def join_and_evaluate_dislocation(state_fips,runs,restart):

    dlocs = []
    dlocs_q = []
    new_adlocs = []
    Rdlocs = []
    Ddlocs = []
    Ravgdlocs = []
    Davgdlocs = [] 
    dists = []
    dists_q = []
    percs = []
    bvaps = []
    hvaps = []


    #Point initialization happens here
    #check for crs matching!
    
    
    #state_precincts = gpd.read_file(f"../../../Dropbox/dislocation_intermediate_files/60_voter_knn_scores/shapefiles/{state_names[state_fips]}_Matched_Precincts.shp")
    
    
    #state_precincts = gpd.read_file(f"../20_intermediate_files/pre_processed_precinct_maps/precincts_{state_fips}.shp")#ONLY FOR CA!!!! use above for everywhere else. 
    
    
    #state_points = gpd.read_file(f"../../../Dropbox/dislocation_intermediate_files/60_voter_knn_scores/shapefiles/{state_names[state_fips]}_USHouse.shp") # THIS FILEANAME isn't quite right - need to check format values. 

    
    
    """
    
    state_precincts = state_precincts.to_crs(state_points.crs)
    print(state_precincts.crs)
    print(state_points.crs)

    print("changed crs")

    point_assign = assign(state_points, state_precincts)
    
    state_precincts.to_file(f"../../../Dropbox/dislocation_intermediate_files/60_voter_knn_scores/shapefiles/{state_names[state_fips]}_Matched_Precincts.shp")
    state_precincts = []
    
    print("Made Assignment")
    
    state_points['precinct'] = point_assign
    
    point_assign = []
    

    state_points.to_file(f"../../../Dropbox/dislocation_intermediate_files/60_voter_knn_scores/shapefiles/{state_names[state_fips]}_Matched_Points.shp")
    """
    
    state_points = gpd.read_file(f"../../../../Dropbox/dislocation_intermediate_files/60_voter_knn_scores/shapefiles/{state_names[state_fips]}_Matched_Points.shp")
    
    print("loaded precincts/points")
    
    for run in [runs]:#for run in ['0','1','2']:#['0','1','2']:
        
        datadir = f"../../../../Dropbox/dislocation_intermediate_files/120_vra_ensembles/{state_fips}_run{run}/"
        
        newdir = f"../../../../Dropbox/dislocation_intermediate_files/120_vra_ensembles/{state_fips}_run{run}/dislocations/"
        
        os.makedirs(os.path.dirname(newdir + "init.txt"), exist_ok=True)
        with open(newdir + "init.txt", "w") as f:
            f.write("Created Folder")

        graph = Graph.from_json(f'../../20_intermediate_files/precinct_graphs/VRAseeds_Final/precinct_graph_{state_fips}_seed{run}.json')

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
                
        new_assignment = dict(initial_partition.assignment)
        #load graph and make initial partition


        #load json one at a time
        max_steps = restart#100000
        step_size = 10000

        ts = [x * step_size for x in range(1, int(max_steps / step_size) + 1)]
        
        
        #seats.append([])
        #wseats.append([])

        for t in ts:
            print(state_fips, t,run)
            
            #dict_list = json.loads(datadir + f'flips_{t}.json')
            with open(datadir+f'flips_{t}.json') as f:
                #dict_list = ast.literal_eval(f.read())#OLD and RAM intensive
                dict_list = json.load(f)

 
            
        

            
            
            for step in range(step_size):
            
                new_assignment.update({int(item[0]):int(item[1]) for item in dict_list[step].items()})
                
                new_partition = Partition(
                    graph,
                    assignment=new_assignment,
                    updaters={
                        "cut_edges": cut_edges,
                    }
                )

    restart_dict = dict(new_partition.assignment)

    for n in graph.nodes():
        graph.nodes[n]['restart_seed'] =  resart_dict[n]

    graph.to_json(f"./restart_seed_{state_fips}_run{run}_restart{restart}.json")
    print(f"restart_seed_{state_fips}_run{run}_restart{restart} ",contiguous(new_partition))

        
        
                

    return state_fips
        

##
# And... EXECUTE!
##



        
from joblib import Parallel, delayed

fips_list = [('17',0,90000),('17',1,90000),('20',1,50000),('20',2,50000),
('22',0,90000),('22',1,70000),('22',2,50000),('39',1,90000),('39',2,90000),('54',2,90000)]

n_jobs = 5

results = (Parallel(n_jobs=n_jobs, verbose=10)
           (delayed(join_and_evaluate_dislocation)(fips[0],fips[1],fips[2]) for fips in fips_list)
          )


