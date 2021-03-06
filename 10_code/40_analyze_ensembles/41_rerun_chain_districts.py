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
        '01',
        #'02',
        '04',
        '05',
        #'06',
        '08',
        '09',
        #'10',
        #'11',
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
        #'36',
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
    dlocs_q = []
    new_adlocs = []
    Rdlocs = []
    Ddlocs = []
    Ravgdlocs = []
    Davgdlocs = [] 
    dists = []
    dists_q = []
    percs = []


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
    
    state_points = gpd.read_file(f"../../../Dropbox/dislocation_intermediate_files/60_voter_knn_scores/shapefiles/{state_names[state_fips]}_Matched_Points.shp")
    
    print("loaded precincts/points")
    
    for run in ['0']:#['0','1','2']:
        
        datadir = f"../../../Dropbox/dislocation_intermediate_files/100_ensembles/{state_fips}_run{run}/"
        
        newdir = f"../../../Dropbox/dislocation_intermediate_files/100_ensembles/{state_fips}_run{run}/rerun4/"
        
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
            new_adlocs.append([])
            Rdlocs.append([])
            Ddlocs.append([])
            Ravgdlocs.append([])
            Davgdlocs.append([])
            dists.append([])
            dists_q.append([])
            dlocs_q.append([])
            percs.append([])

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
 
    
                state_points["dislocate"] = (state_points["KnnShrDem"] - (state_points["current"].map(pdict) - 0.0369)).abs()

                #state_points["abs_dislocate"] = state_points["dislocate"].abs()
                #state_points["dislocate"] = state_points["dislocate"].abs()
                

                state_points["quadratic"] = state_points["dislocate"].pow(2)

                
                #percs.append(state_points['abs_dislocate'].quantile([.05* x for x in range(21)]))
                dists.append([state_points.groupby('current')['dislocate'].mean()[x] for x in new_partition.parts])
                
                dlocs_q[-1].append(state_points['quadratic'].mean())
                
                dists_q.append([state_points.groupby('current')['quadratic'].mean()[x] for x in new_partition.parts])
                
                #district_averages = [state_points.groupby('current')['dislocate'].mean()[x] for x in new_partition.parts] 
                #district_averages_q = [state_points.groupby('current')['quadratic'].mean()[x] for x in new_partition.parts] 

                #{x: pf.groupby('current')['dislocate'].mean()[x] for x in new_partition.parts}   # for now just average over whole state
                
            
            
                #dlocs[-1].append(state_points["dislocate"].mean())
                new_adlocs[-1].append(state_points["dislocate"].mean())

                #Rdlocs[-1].append(len(state_points[state_points["dislocate"]>0]))
                #Ddlocs[-1].append(len(state_points[state_points["dislocate"]<0]))
                #Ravgdlocs[-1].append(abs(state_points[state_points["dislocate"]>0].mean()))
                #Davgdlocs[-1].append(abs(state_points[state_points["dislocate"]<0].mean()))

                
            #plt.figure()
            #state_precincts.plot(color = 'bisque', linewidth = 1, edgecolor = 'slategray')
            #state_points.plot(column = 'dislocate', cmap = 'seismic',markersize=5)
            #plt.savefig(newdir+"pointcolors"+str(t)+".png")
            #plt.close()

                 
            
        

            """
            with open(newdir + "dloc" + str(t) + ".csv", "w") as tf1:
                writer = csv.writer(tf1, lineterminator="\n")
                writer.writerows(dlocs)            
                          
            with open(newdir + "adloc" + str(t) + ".csv", "w") as tf1:
                writer = csv.writer(tf1, lineterminator="\n")
                writer.writerows(adlocs)
            
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
            """
            with open(newdir + "new_adloc" + str(t) + ".csv", "w") as tf1:
                writer = csv.writer(tf1, lineterminator="\n")
                writer.writerows(new_adlocs)
            with open(newdir + "dists" + str(t) + ".csv", "w") as tf1:
                writer = csv.writer(tf1, lineterminator="\n")
                writer.writerows(dists)
            
            with open(newdir + "dists_q" + str(t) + ".csv", "w") as tf1:
                writer = csv.writer(tf1, lineterminator="\n")
                writer.writerows(dists_q)

            #with open(newdir + "percs" + str(t) + ".csv", "w") as tf1:
            #    writer = csv.writer(tf1, lineterminator="\n")
            #    writer.writerows(percs)
                
            with open(newdir + "dloc_q" + str(t) + ".csv", "w") as tf1:
                writer = csv.writer(tf1, lineterminator="\n")
                writer.writerows(dlocs_q)
            """
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
            """          
            
            dlocs = []
            new_adlocs = []
            Rdlocs = []
            Ddlocs = []
            Ravgdlocs = []
            Davgdlocs = []      
            dists = []
            dists_q = []
            dlocs_q = []
            percs = []

        return state_fips
        

##
# And... EXECUTE!
##
        
from joblib import Parallel, delayed

n_jobs = 1

results = (Parallel(n_jobs=n_jobs, verbose=10)
           (delayed(join_and_evaluate_dislocation)(fips) for fips in fips_list)
          )


