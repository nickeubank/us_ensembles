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
import math
#from dislocation_chain_utility import * 


#state_run = os.getenv('STATE_RUN')
#state_index = int(state_run) // 3
#run = int(state_run) % 3


#f='../20_intermediate_files/sequential_to_fips.pickle'
#state_fips = pickle.load(open(f, "rb" ))[state_index]



def draw_plot(data, offset, edge_color, fill_color):
    pos = [1+offset] #np.arange(data.shape[1])+1+offset
    #bp = ax.boxplot(data, positions= pos, widths=0.3, patch_artist=True, manage_xticks=False)
    bp = ax.boxplot(data, positions= pos,widths=4, whis=[25,75],showfliers=False, patch_artist=True, manage_ticks=False,zorder=4)
    for element in ['boxes', 'whiskers', 'medians', 'caps']:
        plt.setp(bp[element], color=edge_color,zorder=4)
    for patch in bp['boxes']:
        patch.set(facecolor=fill_color,zorder=4)


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
        #'30',
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

plan_name = "Enacted"

election_name = election_names[0]

meds = []
p95 = []
p75 = []
p25 = []
p5 = []
names = []
mins = []
maxs = []

enacted = []
avg_dgi = []
avg_pg = []
fu_avg_dgi = []
fu_avg_pg = []
fl_avg_dgi = []
fl_avg_pg = []

fig, ax = plt.subplots()


offset = 0


coeffs = []


for state_fips in fips_list:
    print(f"Starting {state_fips}")
    
    
    
##
# Analysis function to parallelize
##
    
    
    dlocs = []
    qdlocs = []
    Rdlocs = []
    Ddlocs = []
    Ravgdlocs = []
    Davgdlocs = []
    #seats = []
    #wseats = []

    
    for run in ['2']:

        names.append(state_names[state_fips])
        max_steps = 100000
        step_size = 10000

            
        ts = [x * step_size for x in range(1, int(max_steps / step_size) + 1)]
        
        datadir = f"../../../../Dropbox/dislocation_intermediate_files/120_vra_ensembles/{state_fips}_run{run}/dislocations/"
        
        
        datadir2 = f"../../../../Dropbox/dislocation_intermediate_files/120_vra_ensembles/{state_fips}_run{run}/" 
        
            
            
        qdlocs = np.zeros([1, max_steps])
        seats = np.zeros([1, max_steps])
        mms = np.zeros([1, max_steps]) 
        pbs = np.zeros([1, max_steps]) 
        pgs = np.zeros([1, max_steps]) 
        
        for t in ts:
            temp = np.loadtxt(datadir + "new_adloc" + str(t) + ".csv", delimiter=",")
            #print(t,len(temp))
            qdlocs[0, t - step_size  : t] = temp
            

         
        for t in ts:       
            temp = np.loadtxt(datadir2 + "mms" + str(t) + ".csv", delimiter=",")
            mms[:, t - step_size : t] = temp.T
            temp = np.loadtxt(datadir2 + "pbs" + str(t) + ".csv", delimiter=",")
            pbs[:, t - step_size : t] = temp.T
            temp = np.loadtxt(datadir2 + "pgs" + str(t) + ".csv", delimiter=",")
            pgs[:, t - step_size : t] = temp.T
            
        #wseats = []

        coeffs.append(np.corrcoef(qdlocs,pgs)[1,0])
        
        
        
newdir = f"../../../../Dropbox/dislocation_intermediate_files/Revised_Filtered_Swung_Plots_VRA/Comparisons/Run{run}/"

os.makedirs(os.path.dirname(newdir + "init.txt"), exist_ok=True)
with open(newdir + "init.txt", "w") as f:
    f.write("Created Folder")



plt.figure()
plt.plot(coeffs,'*', color = 'slategray')
plt.ylabel('Correlation Coefficient')
plt.xticks(range(len(names)),names,rotation=90,fontsize=5)
plt.savefig(newdir+'corrcoef_PGvsDL.png')
fig = plt.gcf()
fig.set_size_inches((12,6), forward=False)
fig.savefig(newdir+'corrcoef_PGvsDL_dpi.png',dpi=500)           
plt.close()


coeffs=np.array(coeffs)
sort_indices = list(np.argsort(coeffs))
coeffs = np.sort(coeffs)

new_names = []
for i in range(len(names)):
    new_names.append(names[sort_indices[i]])


plt.figure()
plt.plot(coeffs,'*', color = 'slategray')
plt.ylabel('Correlation Coefficient')
plt.xticks(range(len(new_names)),new_names,rotation=90,fontsize=5)
plt.savefig(newdir+'sorted_corrcoef_PGvsDL.png')
fig = plt.gcf()
fig.set_size_inches((12,6), forward=False)
fig.savefig(newdir+'sorted_corrcoef_PGvsDL_dpi.png',dpi=500)           
plt.close()





        
        
        
    





        
