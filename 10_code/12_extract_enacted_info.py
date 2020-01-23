import geopandas as gpd
import os
import pickle
import numpy as np
import gerrychain as gc
from gerrychain import Graph, Partition, Election
from gerrychain.updaters import Tally, cut_edges
from maup import assign

indices=['01',
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


num_elections = 1

election_names = ["PRES2008"]

election_columns = [["P2008_D",  "P2008_R"]]

election_name = election_names[0]

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

newdir = f"../../../Dropbox/dislocation_intermediate_files/Enacted_Stats/"
os.makedirs(os.path.dirname(newdir + "init.txt"), exist_ok=True)
with open(newdir + "init.txt", "w") as f:
    f.write("Created Folder")

        
for state_fips in indices:

    graph = Graph.from_json(f"../20_intermediate_files/precinct_graphs/precinct_graphs_{state_fips}_seed0.json")
    
    election = Election("PRES2008", {"Dem": "P2008_D", "Rep": "P2008_R"})

    initial_partition = Partition(
        graph,
        assignment='district',
        updaters={
            "cut_edges": cut_edges,
            "population": Tally("population", alias="population"),
            "PRES2008": election
        }
    )
    
    state_precincts = gpd.read_file(f"../20_intermediate_files/pre_processed_precinct_maps/precincts_{state_fips}.shp")
    state_points = gpd.read_file(f"../../../Dropbox/dislocation_intermediate_files/60_voter_knn_scores/shapefiles/{state_names[state_fips]}_USHouse.shp") # THIS FILEANAME isn't quite right - need to check format values. 
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


    pvec = initial_partition[election_name].percents("Dem")
        
        
    state_points['current'] = state_points['precinct'].map(dict(initial_partition.assignment))
            
    id_dict = {tuple(initial_partition[election_name].races)[x]:x for x in range(len(initial_partition.parts.keys()))}

    
    pdict = {x:pvec[id_dict[x]] for x in initial_partition.parts.keys()}
 
    
    state_points["dislocate"] = -(state_points["KnnShrDem"] - (state_points["current"].map(pdict) - 0.0369))

    #dstate_points["abs_dislocate"] = np.abs(state_points["dislocate"])

            
    #district_averages = {x: pf.groupby('current')['dislocate'].mean()[x] for x in new_partition.parts}   # for now just average over whole state
                
            
            
    #dlocs[-1].append(state_points["dislocate"].mean())
    #adlocs[-1].append((state_points["dislocate"].abs()).mean())
   
#### WANT Separate files instead!   Think about this 



    with open(newdir + "Start_Values_"+str(state_fips)+".txt", "w") as f:
        f.write("Values for Starting Plan: Enacted Plan:\n \n ")
        f.write("Initial Cut: "+ str(len(initial_partition["cut_edges"])))
        f.write("\n")
        f.write("\n")
        #f.write("Initial County Splits: "+ str(num_splits(initial_partition)))
        #f.write("\n")
        f.write("\n")

        for elect in range(num_elections):
            f.write(election_names[elect] + "District Percentages" + str(sorted(initial_partition[election_names[elect]].percents("Dem"))))
            f.write("\n")
            f.write("\n")

            f.write(election_names[elect] + "Mean-Median :"+ str(mean_median(initial_partition[election_names[elect]])))
        
            f.write("\n")
            f.write("\n")
        
            f.write(election_names[elect] + "Efficiency Gap :" + str(efficiency_gap(initial_partition[election_names[elect]])))
        
            f.write("\n")
            f.write("\n")

            f.write(election_names[elect] + "Partisan Bias :" + str(partisan_bias(initial_partition[election_names[elect]])))
        
            f.write("\n")
            f.write("\n")   
            f.write(election_names[elect] + "Partisan Gini :" + str(partisan_gini(initial_partition[election_names[elect]])))
        
            f.write("\n")
            f.write("\n")             
            f.write(election_names[elect] + "How Many Seats :" + str(initial_partition[election_names[elect]].wins("Dem")))
         
            f.write("\n")
            f.write("\n")    
    
            f.write(election_names[elect] + "Average Signed Dislocation :" + str(state_points["dislocate"].mean()))
         
            f.write("\n")
            f.write("\n")    
   
            f.write(election_names[elect] + "Average Absolute Dislocation :" + str((state_points["dislocate"].abs()).mean()))
         
            f.write("\n")
            f.write("\n")    



