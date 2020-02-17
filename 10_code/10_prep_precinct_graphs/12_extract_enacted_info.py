import geopandas as gpd
import os
import pickle
import numpy as np
import gerrychain as gc
from gerrychain import Graph, Partition, Election
from gerrychain.updaters import Tally, cut_edges
from maup import assign
from gerrychain.metrics import efficiency_gap, mean_median, partisan_bias, partisan_gini

indices=['01',
        '04',
        '05',
        '06',
        '08',
        '09',
        #'10',
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
"44":"Rhode_Island","45":"South_Carolina","46":"South_Dakota","47":"Tennessee",
"48":"Texas","49":"Utah","51":"Virginia","50":"Vermont","53":"Washington",
"55":"Wisconsin","54":"West_Virginia","56":"Wyoming"}

newdir = f"../../../../Dropbox/dislocation_intermediate_files/Enacted_Take2/"
os.makedirs(os.path.dirname(newdir + "init.txt"), exist_ok=True)
with open(newdir + "init.txt", "w") as f:
    f.write("Created Folder")

        
for state_fips in indices:

    graph = Graph.from_json(f"../../20_intermediate_files/precinct_graphs/precinct_graphs_{state_fips}_seed0.json")
    
    election = Election("PRES2008", {"Dem": "P2008_D", "Rep": "P2008_R"})

    for n in graph.nodes():
        graph.nodes[n]["nBVAP"] = graph.nodes[n]["pop_VAP"] - graph.nodes[n]["pop_BVAP"] 
        graph.nodes[n]["nHVAP"] = graph.nodes[n]["pop_VAP"] - graph.nodes[n]["pop_HVAP"] 

    electionbvap = Election("BVAP", {"BVAP": "pop_BVAP", "nBVAP": "nBVAP"})

    electionhavp = Election("HVAP", {"HVAP": "pop_HVAP", "nHVAP": "nHVAP"})

    initial_partition = Partition(
        graph,
        assignment='district',
        updaters={
            "cut_edges": cut_edges,
            "population": Tally("population", alias="population"),
            "PRES2008": election, 
            "BVAP" : electionbvap,
            "HVAP" : electionhvap
        }
    )
    
    state_points = gpd.read_file(f"../../../Dropbox/dislocation_intermediate_files/60_voter_knn_scores/shapefiles/{state_names[state_fips]}_Matched_Points.shp") 
    print("loaded precincts/points")

    


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

        f.write('BVAP vector:', str(sorted(initial_partition["BVAP"].percents("BVAP")))
        f.write("\n")
        f.write("\n")

        f.write('BVAP over 40:',  str(sum([x>.4 for x in sorted(initial_partition["BVAP"].percents("BVAP"))])
        f.write("\n")
        f.write("\n")
        f.write('BVAP over 45:',  str(sum([x>.45 for x in sorted(initial_partition["BVAP"].percents("BVAP"))])
        f.write("\n")
        f.write("\n")
        f.write('BVAP over 40:',  str(sum([x>.4 for x in sorted(initial_partition["BVAP"].percents("BVAP"))])
        f.write("\n")
        f.write("\n")

        f.write('HVAP vector:', str(sorted(initial_partition["HVAP"].percents("HVAP")))
        f.write("\n")
        f.write("\n")
        f.write('HVAP over 40:',  str(sum([x>.4 for x in sorted(initial_partition["HVAP"].percents("HVAP"))])
        f.write("\n")
        f.write("\n")
        f.write('HVAP over 45:',  str(sum([x>.45 for x in sorted(initial_partition["HVAP"].percents("HVAP"))])
        f.write("\n")
        f.write("\n")
        f.write('HVAP over 40:',  str(sum([x>.4 for x in sorted(initial_partition["HVAP"].percents("HVAP"))])

        f.write("\n")
        f.write("\n")
        for elect in range(num_elections):
            tempvec = [x - 0.0369 for x in sorted(initial_partition[election_names[elect]].percents("Dem"))]
            f.write(election_names[elect] + "District Percentages" + str(tempvec))
            f.write("\n")
            f.write("\n")

            f.write(election_names[elect] + "Mean-Median :"+ str(np.median(tempvec)-np.mean(tempvec)))
        
            f.write("\n")
            f.write("\n")
        
            #f.write(election_names[elect] + "Efficiency Gap :" + str(2*(initial_partition[election_names[elect]].percent("Dem") - 0.0369) - sum([x>.5 for x in tempvec])/len(tempvec) -.5 ))
            
            #2v-s-.5
            f.write(election_names[elect] + "Efficiency Gap :" + str(efficiency_gap(initial_partition[election_names[elect]])))
            
            f.write("\n")
            f.write("\n")

            f.write(election_names[elect] + "Partisan Bias :" + str(partisan_bias(initial_partition[election_names[elect]])))
        
            f.write("\n")
            f.write("\n")   
            
            overall_result = initial_partition[election_names[elect]].percent("Dem") - 0.0369
            race_results = sorted(tempvec, reverse=True)
            seats_votes = [overall_result - r + 0.5 for r in race_results]

            # Apply reflection of seats-votes curve about (.5, .5)
            reflected_sv = reversed([1 - s for s in seats_votes])
            # Calculate the unscaled, unsigned area between the seats-votes curve
            # and its reflection. For each possible number of seats attained, we find
            # the area of a rectangle of unit height, with a width determined by the
            # horizontal distance between the curves at that number of seats.
            unscaled_area = sum(abs(s - r) for s, r in zip(seats_votes, reflected_sv))
            # We divide by area by the number of seats to obtain a partisan Gini score
            # between 0 and 1.
            f.write(election_names[elect] + "Partisan Gini :" + str(unscaled_area / len(race_results)))
        
            f.write("\n")
            f.write("\n")             
            f.write(election_names[elect] + "How Many Seats :" + str(sum([x>.5 for x in tempvec])))
         
            f.write("\n")
            f.write("\n")    
    
            f.write(election_names[elect] + "Average Signed Dislocation :" + str(state_points["dislocate"].mean()))
         
            f.write("\n")
            f.write("\n")    
   
            f.write(election_names[elect] + "Average Absolute Dislocation :" + str((state_points["dislocate"].abs()).mean()))
         
            f.write("\n")
            f.write("\n")    


            f.write(election_names[elect] + "Average Squaredd Dislocation :" + str((state_points["dislocate"].pow(2)).mean()))
         
            f.write("\n")
            f.write("\n")
