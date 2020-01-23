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
from maup import assign
import numpy as np
import ast
#from dislocation_chain_utility import * 


#state_run = os.getenv('STATE_RUN')
#state_index = int(state_run) // 3
#run = int(state_run) % 3


#f='../20_intermediate_files/sequential_to_fips.pickle'
#state_fips = pickle.load(open(f, "rb" ))[state_index]


#newdir = f"../20_intermediate_files/chain_ouputs/{state_fips}_run{run}/"
#os.makedirs(os.path.dirname(newdir + "init.txt"), exist_ok=True)
#with open(newdir + "init.txt", "w") as f:
#    f.write("Created Folder")

state_names={"02":"Alaska","01":"Alabama","05":"Arkansas","04":"Arizona",
"06":"California","08":"Colorado","09":"Connecticut","10":"Delaware",
"12":"Florida","13":"Georgia","66":"Guam","15":"Hawaii","19":"Iowa",
"16":"Idaho","17":"Illinois","18":"Indiana","20":"Kansas","21":"Kentucky",
"22":"Louisiana","25":"Massachusetts","24":"Maryland","23":"Maine","26":"Michigan",
"27":"Minnesota","29":"Missouri","28":"Mississippi","30":"Montana",
"37":"North_Carolina","38":"North_Dakota","31":"Nebraska","33":"New_Hampshire",
"34":"New_Jersey","35":"New_Mexico","32":"Nevada","36":"New_York","39":"Ohio",
"40":"Oklahoma","41":"Oregon","42":"Pennsylvania","72":"Puerto_Rico",
"44":"Rhode_Island","45":"South_Carolina","46":"South_Dakota","47":"Tenessee",
"48":"Texas","49":"Utah","51":"Virginia","50":"Vermont","53":"Washington",
"55":"Wisconsin","54":"West_Virginia","56":"Wyoming"}


num_elections = 1

election_names = ["PRES2008"]

election_columns = [["P2008_D",  "P2008_R"]]

fips_list = [
        '01',
        '04',
        '05',
        '06',
        '08',
        '09',
        '10',
        '11',
        '12',
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
        '31',
        '32',
        '33',
        '34',
        '35',
        '36',
        '37',
        '38',
        '39',
        '40',
        '42',
        '44',
        '45',
        '46',
        '47',
        '48',
        '49',
        '50',
        '51',
        '53',
        '54',
        '55',
        '56']

plan_name = "Enacted"

election_name = election_names[0]

num_districts = 7 #replace this with length of vote vector



from gerrychain import Graph, Partition, Election
from gerrychain.updaters import Tally, cut_edges

    

for state_fips in fips_list:

    dlocs = []
    adlocs = []


    #Point initialization happens here
    #check for crs matching!
    state_precincts = gpd.read_file(f"../20_intermediate_files/pre_processed_precinct_maps/precincts_{state_fips}.shp")
    state_points = gpd.read_file("../../../Dropbox/dislocation_intermediate_files/60_voter_knn_scores/shapefiles/{state_names[state_fips]}_USHouse.shp") # THIS FILEANAME isn't quite right - need to check format values. 
    print("loaded precincts/points")

    print(state_precincts.crs)
    print(state_points.crs)
    #state_points['geometry'] = state_points['geometry'].to_crs(state_precincts.crs)
    state_precincts = state_precincts.to_crs(state_points.crs)

    print(state_precincts.crs)
    print(state_points.crs)


    print("changed crs")

    point_assign = assign(state_points,state_precincts)
 
    print("Made Assignment")
    
    state_points['precinct'] = point_assign

    #state_points['precinct'] = state_points['precinct'].map(state_precincts.index)
    #Maybe unnecessary?
    
    for run in ['0','1','2']:
        
        datadir = f"../../../Dropbox/dislocation_intermediate_files/100_ensembles/{state_fips}_run{run}/"
        
        newdir = f"../../../Dropbox/dislocation_intermediate_files/100_ensembles/{state_fips}_run{run}/rerun/"
        
        os.makedirs(os.path.dirname(newdir + "init.txt"), exist_ok=True)
        with open(newdir + "init.txt", "w") as f:
            f.write("Created Folder")

        graph = Graph.from_json(f'../20_intermediate_files/precinct_graphs/precinct_graphs_{state_fips}_seed{run}.json')

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
        
        new_assignment = dict(initial_partition.assignment)
        #load graph and make initial partition


        #load json one at a time
        max_steps = 100000
        step_size = 10000

        ts = [x * step_size for x in range(1, int(max_steps / step_size) + 1)]
        
        dlocs.append([])
        adlocs.append([])

        for t in ts:
            print(t,run)
            #dict_list = json.loads(datadir + f'flips_{t}.json')
            with open(datadir+f'flips_{t}.json') as f:
                dict_list = ast.literal_eval(f.read())

            #if t = ts[0]:
            #    data.remove(0)
 
            
        

            #Make new partition by updating dictionary
            
            
            for step in range(step_size):
            
                new_assignment.update({int(item[0]):int(item[1]) for item in dict_list[step].items()})
                
                new_partition = Partition(
                    graph,
                    assignment=new_assignment,
                    updaters={
                        "cut_edges": cut_edges,
                        "population": Tally("population", alias="population"),
                        "PRES2008": election
                    }
                )
                
                
            
                pvec = new_partition[election_name].percents("Dem")
        
        
                state_points['current'] = state_points['precinct'].map(dict(new_assignment))
            
                id_dict = {tuple(new_partition[election_name].races)[x]:x for x in range(len(new_partition.parts.keys()))}

    
                pdict = {x:pvec[id_dict[x]] for x in new_partition.parts.keys()}
 
    
                state_points["dislocate"]=state_points["KnnShrDem"]-(state_points["current"].map(pdict) - 0.0369)
            
                #district_averages = {x: pf.groupby('current')['dislocate'].mean()[x] for x in new_partition.parts}   # for now just average over whole state
            
            
                dlocs[-1].append(np.mean(state_points["dislocate"]))
                adlocs[-1].append(np.mean(np.abs(state_points["dislocate"])))


                #measure dislocation and write to file 
                #dlocs.append()
            
            
        with open(newdir + "dloc" + str(t) + ".csv", "w") as tf1:
            writer = csv.writer(tf1, lineterminator="\n")
            writer.writerows(dlocs)            

        with open(newdir + "adloc" + str(t) + ".csv", "w") as tf1:
            writer = csv.writer(tf1, lineterminator="\n")
            writer.writerows(adlocs)
            
        dlocs = []
        adlocs = []
