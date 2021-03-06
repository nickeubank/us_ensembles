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
"44":"Rhode_Island","45":"South_Carolina","46":"South_Dakota","47":"Tennessee",
"48":"Texas","49":"Utah","51":"Virginia","50":"Vermont","53":"Washington",
"55":"Wisconsin","54":"West_Virginia","56":"Wyoming"}


num_elections = 1

election_names = ["PRES2008"]

election_columns = [["P2008_D",  "P2008_R"]]


#1 thourgh 16 only wrote a single file. 
fips_list = ['12','36']

plan_name = "Enacted"

election_name = election_names[0]



from gerrychain import Graph, Partition, Election
from gerrychain.updaters import Tally, cut_edges

    
##
# Analysis function to parallelize
##
    
    
def join_and_evaluate_dislocation(state_fips):

    dlocs = []
    adlocs = []
    Rdlocs = []
    Ddlocs = []
    Ravgdlocs = []
    Davgdlocs = []
    #seats = []
    #wseats = []


    #Point initialization happens here
    #check for crs matching!
    state_precincts = gpd.read_file(f"../20_intermediate_files/pre_processed_precinct_maps/precincts_{state_fips}.shp")
    state_points = gpd.read_file(f"../../../Dropbox/dislocation_intermediate_files/60_voter_knn_scores/shapefiles/{state_names[state_fips]}_USHouse.shp") # THIS FILEANAME isn't quite right - need to check format values. 
    print("loaded precincts/points")

    print(state_precincts.crs)
    print(state_points.crs)
    
    
    #state_points['geometry'] = state_points.to_crs(state_precincts.crs)#this one didn't work!
    
    state_points = state_points.to_crs({'init': 'epsg:3085'})

    
    
    
    #state_precincts = state_precincts.to_crs(state_points.crs)

    print(state_precincts.crs)
    print(state_points.crs)
    
    state_precincts.to_file(f"../../../Dropbox/dislocation_intermediate_files/60_voter_knn_scores/shapefiles/{state_names[state_fips]}_Matched_Precincts.shp")


    print("changed crs")
    
    state_points.to_file(f"../../../Dropbox/dislocation_intermediate_files/60_voter_knn_scores/shapefiles/{state_names[state_fips]}_Matched_Points_TEMPORARY.shp")
    
    print("saved temporary")
    
    state_points = state_points[~state_points.index.duplicated()]

    point_assign = assign(state_points, state_precincts)
    
    stateprecincts = []
 
    print("Made Assignment")
    
    state_points['precinct'] = point_assign
    state_points.to_file(f"../../../Dropbox/dislocation_intermediate_files/60_voter_knn_scores/shapefiles/{state_names[state_fips]}_Matched_Points.shp")
    #state_points['precinct'] = state_points['precinct'].map(state_precincts.index)
    #Maybe unnecessary?
    
    for run in ['0']:#['0','1','2']:
        
        datadir = f"../../../Dropbox/dislocation_intermediate_files/100_ensembles/{state_fips}_run{run}/"
        
        newdir = f"../../../Dropbox/dislocation_intermediate_files/100_ensembles/{state_fips}_run{run}/rerun2/"
        
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
        
        
        #seats.append([])
        #wseats.append([])

        for t in ts:
            print(state_fips, t,run)
            dlocs.append([])
            adlocs.append([])
            Rdlocs.append([])
            Ddlocs.append([])
            Ravgdlocs.append([])
            Davgdlocs.append([])
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
 
    
                state_points["dislocate"] = -(state_points["KnnShrDem"] - (state_points["current"].map(pdict) - 0.0369))

                #dstate_points["abs_dislocate"] = np.abs(state_points["dislocate"])

            
                #district_averages = {x: pf.groupby('current')['dislocate'].mean()[x] for x in new_partition.parts}   # for now just average over whole state
                
                #seats[-1].append(new_partition[election_name].wins("Dem"))
            
            
                dlocs[-1].append(state_points["dislocate"].mean())
                adlocs[-1].append((state_points["dislocate"].abs()).mean())
                #if adlocs[-1][-1] < .05:
                #    wseats[-1].append(new_partition[election_name].wins("Dem"))

                #Rdlocs[-1].append(len(state_points[state_points["dislocate"]>0]))
                #Ddlocs[-1].append(len(state_points[state_points["dislocate"]<0]))
                #Ravgdlocs[-1].append(abs(state_points[state_points["dislocate"]>0].mean()))
                #Davgdlocs[-1].append(abs(state_points[state_points["dislocate"]<0].mean()))

                
            #plt.figure()
            #state_precincts.plot(color = 'bisque', linewidth = 1, edgecolor = 'slategray')
            #state_points.plot(column = 'dislocate', cmap = 'seismic',markersize=5)
            #plt.savefig(newdir+"pointcolors"+str(t)+".png")
            #plt.close()

                 
            
        


            with open(newdir + "dloc" + str(t) + ".csv", "w") as tf1:
                writer = csv.writer(tf1, lineterminator="\n")
                writer.writerows(dlocs)            
                          
            with open(newdir + "adloc" + str(t) + ".csv", "w") as tf1:
                writer = csv.writer(tf1, lineterminator="\n")
                writer.writerows(adlocs)
            """
            with open(newdir + "Rdloc" + str(t) + ".csv", "w") as tf1:
                writer = csv.writer(tf1, lineterminator="\n")
                writer.writerows(Rdlocs)

            with open(newdir + "Ddloc" + str(t) + ".csv", "w") as tf1:
                writer = csv.writer(tf1, lineterminator="\n")
                writer.writerows(Ddlocs)

            with open(newdir + "Ravgdloc" + str(t) + ".csv", "w") as tf1:
                writer = csv.writer(tf1, lineterminator="\n")
                writer.writerows(Ravgdlocs)

            with open(newdir + "Davgdloc" + str(t) + ".csv", "w") as tf1:
                writer = csv.writer(tf1, lineterminator="\n")
                writer.writerows(Davgdlocs)
            

            plt.figure()
            sns.distplot(adlocs[-1], kde=False, bins=1000)
            plt.savefig(newdir+"abs_disc.png")

            plt.close()
            
            plt.figure()
            sns.distplot(Ravgdlocs[-1], kde=False, bins=1000,color='r')
            sns.distplot(Davgdlocs[-1], kde=False, bins=1000,color='b')

            plt.savefig(newdir+"party_disc.png")

            plt.close()

            plt.figure()
            sns.distplot(Rdlocs[-1], kde=False, bins=100,color='r')
            sns.distplot(Ddlocs[-1], kde=False, bins=100,color='b')

            plt.savefig(newdir+"number_party_disc.png")

            plt.close()
            
            
            seats[-1] = np.array(seats[-1])
            
            adlocs = np.array(adlocs)
            
            bound = np.percentile(adlocs, 10)
            
            wseats = seats[-1][adlocs < bound]
            
            plt.figure()
            sns.distplot(seats[-1], kde=False, bins = [x for x in range(int(min(seats[-1]))-1,int(max(seats[-1]))+2)], color='gray',label = 'All Plans')
            sns.distplot(wseats, kde=False, bins=[x for x in range(int(min(seats[-1]))-1,int(max(seats[-1]))+2)],color='green',label='Small Dislocation')
            plt.legend()
            plt.savefig(newdir+"seats_comparison.png")

            plt.close()

            """  
            dlocs = []
            adlocs = []
            Rdlocs = []
            Ddlocs = []
            Ravgdlocs = []
            Davgdlocs = []      
            seats = []
            wseats = []

        return state_fips
        

##
# And... EXECUTE!
##
        
from joblib import Parallel, delayed

n_jobs = 1

results = (Parallel(n_jobs=n_jobs, verbose=10)
           (delayed(join_and_evaluate_dislocation)(fips) for fips in fips_list)
          )


