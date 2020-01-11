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

state_run = os.getenv('STATE_RUN')
state_index = int(state_run) // 3
run = int(state_run) % 3


f='../20_intermediate_files/sequential_to_fips.pickle'
state_fips = pickle.load(open(f, "rb" ))[state_index]

newdir = f"../20_intermediate_files/chain_ouputs/{state_fips}_run{run}/"
os.makedirs(os.path.dirname(newdir + "init.txt"), exist_ok=True)
with open(newdir + "init.txt", "w") as f:
    f.write("Created Folder")



num_elections = 1

election_names = ["PRES2008"]

election_columns = [["P2008_D",  "P2008_R"]]

fips_list = ['01']

plan_name = "Enacted"


num_districts = 7 #replace this with length of vote vector



from gerrychain import Graph, Partition, Election
from gerrychain.updaters import Tally, cut_edges

for state_fips in fips_list:
    for run in ['0','1','2']:
        
        datadir = f"../../../Dropbox/US_Ensembles/{state_fips}_{run}/"
        
        newdir = f"../../../Dropbox/US_Ensembles/{state_fips}_{run}/rerun/"
        
        os.makedirs(os.path.dirname(newdir + "init.txt"), exist_ok=True)
        with open(newdir + "init.txt", "w") as f:
            f.write("Created Folder")

		# Ignore errors: some overlap issues, but shouldn't matter for adjacency
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
		
		dlocs = []

		for t in ts:
			dict_list = json.loads(datadir + f'flips_{t}.json')
			
		

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
		

			#measure dislocation and write to file 
			#dlocs.append()