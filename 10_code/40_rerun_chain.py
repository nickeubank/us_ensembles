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



num_elections = 1

election_names = ["PRES2008"]

election_columns = [["P2008_D",  "P2008_R"]]

fips_list = ['01']

plan_name = "Enacted"

election = election_names[0]

num_districts = 7 #replace this with length of vote vector



from gerrychain import Graph, Partition, Election
from gerrychain.updaters import Tally, cut_edges

    

for state_fips in fips_list:

    dlocs = []


    #Point initialization happens here
    #check for crs matching!
    state_precincts = gpd.read_file(f"../20_intermediate_files/pre_processed_precinct_maps/precincts_{state_fips}.shp")
    state_points = gpd.read_file("../../../Dropbox/dislocation_intermediate_files/60_voter_knn_scores/shapefiles/Alabama_USHouse.shp") # THIS FILEANAME isn't quite right - need to check format values. 
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
        
        datadir = f"../../../Dropbox/dislocation_intermediate_files/100_ensembles/{state_fips}_{run}/"
        
        newdir = f"../../../Dropbox/dislocation_intermediate_files/100_ensembles/{state_fips}_{run}/rerun/"
        
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

        for t in ts:
            #dict_list = json.loads(datadir + f'flips_{t}.json')
            with open(datadir+f'flips_{t}.json') as f:
                data = ast.literal_eval(f.read())

            #if t = ts[0]:
            #    data.remove(0)
 
            
        

            #Make new partition by updating dictionary
            
            
            for step in range(step_size):
            
                new_assignment = new_assignment.update(dict_list[step])
                
                new_partition = Partition(
                    graph,
                    assignment=new_assignment,
                    updaters={
                        "cut_edges": cut_edges,
                        "population": Tally("population", alias="population"),
                        "PRES2008": election
                    }
                )
                
                
            
                pvec = new_partition[election].percents("Dem")
        
        
                state_points['current'] = state_points['precinct'].map(dict(new_assignment))
            
                id_dict = {tuple(new_partition[election].races)[x]:x for x in range(len(partition.parts.keys()))}

    
                pdict = {x:pvec[id_dict[x]] for x in new_partition.parts.keys()}
 
    
                pf["dislocate"]=pf["KnnShrDem"]-(pf["current"].map(pdict) - 0.0369)
            
                #district_averages = {x: pf.groupby('current')['dislocate'].mean()[x] for x in partition.parts}   # for now just average over whole state
            
            
                dlocs[-1].append(np.mean(pf["dislocate"]))
                #measure dislocation and write to file 
                #dlocs.append()
            
            
    with open(newdir + "dloc" + str(step_index) + ".csv", "w") as tf1:
        writer = csv.writer(tf1, lineterminator="\n")
        writer.writerows(dlocs)            
            
    dlocs = []
