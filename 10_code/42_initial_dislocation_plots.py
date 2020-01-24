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
        #'02',
        '04',
        '05',
        '06',
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
        '25']
""",
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
        #'56']
"""

plan_name = "Enacted"

election_name = election_names[0]


for state_fips in fips_list:

    
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
        max_steps = 100000

        burn = 0
        sub_sample = 1
        step_size = 10000
    
        if int(state_fips)<17:
            step_size = 100000
            
        ts = [x * step_size for x in range(1, int(max_steps / step_size) + 1)]
        
        datadir = f"../../../Dropbox/dislocation_intermediate_files/100_ensembles/{state_fips}_run{run}/rerun2/"
        
        if state_fips == '06':
            datadir = f"../../../Dropbox/dislocation_intermediate_files/100_ensembles/{state_fips}_run{run}/rerun/"
        
        datadir2 = f"../../../Dropbox/dislocation_intermediate_files/100_ensembles/{state_fips}_run{run}/" 
        
        newdir = f"../../../Dropbox/dislocation_intermediate_files/100_ensembles/{state_fips}_run{run}/rerun2/"
        
        os.makedirs(os.path.dirname(newdir + "init.txt"), exist_ok=True)
        with open(newdir + "init.txt", "w") as f:
            f.write("Created Folder")
            
            
        adlocs = np.zeros([1, max_steps])
        seats = np.zeros([1, max_steps])
        
        for t in ts:
            temp = np.loadtxt(datadir + "adloc" + str(t) + ".csv", delimiter=",")
            #print(t,len(temp))
            adlocs[0, t - step_size  : t] = temp
            
        step_size = 10000
            
        ts = [x * step_size for x in range(1, int(max_steps / step_size) + 1)]    
         
        for t in ts:       
            temp = np.loadtxt(datadir2 + "hmss" + str(t) + ".csv", delimiter=",")
            seats[:, t - step_size : t] = temp.T
            
        #wseats = []
        
        bound = np.percentile(adlocs,10)
        
        #for i in range(max_steps):
        #    if
        
        wseats = seats[(adlocs<bound)]    
        
        plt.figure()
        sns.distplot(seats, kde=False, bins = [x for x in range(int(min(seats[0,:]))-1,int(max(seats[0,:]))+2)], color='gray',label = 'All Plans')
        sns.distplot(wseats, kde=False, bins=[x for x in range(int(min(seats[0,:]))-1,int(max(seats[0,:]))+2)],color='green',label='Small Dislocation')
        plt.legend()
        plt.savefig(newdir+"seats_comparison2.png")

        plt.close()
            
            
            
            
            
            
        
            
            
            
            
            


