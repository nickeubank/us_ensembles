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



num_elections = 1

election_names = ["PRES2008"]

election_columns = [["P2008_D",  "P2008_R"]]


#1 thourgh 16 only wrote a single file. 
fips_list = [
        '01',
        '02',
        '04',
        '05',
        '06',
        '08',
        '09',
        '10',
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

plan_name = "Enacted"

election_name = election_names[0]


for state_fips in fips_llist:

    
##
# Analysis function to parallelize
##
    
    
    dlocs = []
    adlocs = []
    Rdlocs = []
    Ddlocs = []
    Ravgdlocs = []
    Davgdlocs = []
    #seats = []
    #wseats = []

    
    for run in ['0']:#['0','1','2']:
        
        datadir = f"../../../Dropbox/dislocation_intermediate_files/100_ensembles/{state_fips}_run{run}/"
        
        newdir = f"../../../Dropbox/dislocation_intermediate_files/100_ensembles/{state_fips}_run{run}/rerun2/"
        
        os.makedirs(os.path.dirname(newdir + "init.txt"), exist_ok=True)
        with open(newdir + "init.txt", "w") as f:
            f.write("Created Folder")


