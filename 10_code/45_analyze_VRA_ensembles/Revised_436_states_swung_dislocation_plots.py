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
e_dir = f"../../../../Dropbox/dislocation_intermediate_files/Enacted_Stats_Swung/"
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

for state_fips in fips_list:
    print(f"Starting {state_fips}")
    names.append(state_names[state_fips])    

    with open(e_dir + "Start_Values_"+str(state_fips)+".txt", "r") as f:
        for index, line in enumerate(f):

            if index == 19:
                #print(line[38:])
                enacted.append(float(line[38:]))    
    

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

    
    for run in ['0']:
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
            


        
        
        
        
                   
        meds.append(np.percentile(qdlocs,50))
        p5.append(np.percentile(qdlocs,5))
        p25.append(np.percentile(qdlocs,25))
        p75.append(np.percentile(qdlocs,75))
        p95.append(np.percentile(qdlocs,95))
        mins.append(np.min(qdlocs))
        maxs.append(np.max(qdlocs))
        

newdir = f"../../../../Dropbox/dislocation_intermediate_files/Revised_Enacted_Stats_Swung/Run{run}/"
os.makedirs(os.path.dirname(newdir + "init.txt"), exist_ok=True)
with open(newdir + "init.txt", "w") as f:
    f.write("Created Folder")

c0 = 'crimson'
c1 = 'darkblue'
c2 = 'deepskyblue'
c3 = 'aqua'
c4 = 'paleturquoise'


    
plt.figure()

for i in range(len(meds)):
    plt.plot([i,i],[p5[i],p25[i]],c3,linewidth=3)
    plt.plot([i,i],[p75[i],p95[i]],c3,linewidth=3)
    plt.plot([i,i],[p25[i],p75[i]],c2,linewidth=6)
    plt.plot([i-.25,i+.25],[meds[i],meds[i]],c1,linewidth=3)
plt.legend()
plt.xticks(range(len(meds)),names,rotation=90,fontsize=5)
plt.savefig(newdir+"compare_dislocations.png")
fig = plt.gcf()
fig.set_size_inches((12,6), forward=False)
plt.savefig(newdir+"compare_dislocations_dpi.png")

plt.close()

plt.figure()
for i in range(len(meds)):
    plt.plot([i,i],[p5[i],mins[i]],c4,linewidth=1)
    plt.plot([i,i],[p95[i],maxs[i]],c4,linewidth=1)
    plt.plot([i,i],[p5[i],p25[i]],c3,linewidth=3)
    plt.plot([i,i],[p75[i],p95[i]],c3,linewidth=3)
    plt.plot([i,i],[p25[i],p75[i]],c2,linewidth=6)
    plt.plot([i-.25,i+.25],[meds[i],meds[i]],c1,linewidth=3)
plt.legend()
plt.xticks(range(len(meds)),names,rotation=90,fontsize=5)
plt.savefig(newdir+"compare_dislocations_mm.png")
fig = plt.gcf()
fig.set_size_inches((12,6), forward=False)
plt.savefig(newdir+"compare_dislocations_mm_dpi.png")

plt.close()

plt.figure()

for i in range(len(meds)):
    plt.plot([i,i],[p5[i],p25[i]],c3,linewidth=3)
    plt.plot([i,i],[p75[i],p95[i]],c3,linewidth=3)
    plt.plot([i,i],[p25[i],p75[i]],c2,linewidth=6)
    plt.plot([i-.25,i+.25],[meds[i],meds[i]],c1,linewidth=3)
    plt.plot([i],[enacted[i]],'o',color=c0, markersize=4)
plt.plot([],[],c1,label='Median')
plt.plot([],[],'o',color=c0,label='Enacted')
plt.legend()
plt.xticks(range(len(meds)),names,rotation=90,fontsize=5)
plt.savefig(newdir+"compare_dislocations_e.png")
fig = plt.gcf()
fig.set_size_inches((12,6), forward=False)
plt.savefig(newdir+"compare_dislocations_e_dpi.png")
plt.close()

plt.figure()
for i in range(len(meds)):
    plt.plot([i,i],[p5[i],mins[i]],c4,linewidth=1)
    plt.plot([i,i],[p95[i],maxs[i]],c4,linewidth=1)
    plt.plot([i,i],[p5[i],p25[i]],c3,linewidth=3)
    plt.plot([i,i],[p75[i],p95[i]],c3,linewidth=3)
    plt.plot([i,i],[p25[i],p75[i]],c2,linewidth=6)
    plt.plot([i-.25,i+.25],[meds[i],meds[i]],c1,linewidth=3)
    plt.plot([i],[enacted[i]],'o',color=c0, markersize=4)
plt.plot([],[],c1,label='Median')
plt.plot([],[],'o',color=c0,label='Enacted')
plt.legend()
plt.xticks(range(len(meds)),names,rotation=90,fontsize=5)
plt.savefig(newdir+"compare_dislocations_mm_e.png")
fig = plt.gcf()
fig.set_size_inches((12,6), forward=False)
plt.savefig(newdir+"compare_dislocations_mm_e_dpi.png")

plt.close()



meds=np.array(meds)
sort_indices = list(np.argsort(meds))
meds = np.sort(meds)

new_names = []
for i in range(len(meds)):
    new_names.append(names[sort_indices[i]])

sort_dict = {x: sort_indices[x] for x in range(len(new_names))}

mins = [mins[sort_dict[x]] for x in range(len(new_names))]
maxs = [maxs[sort_dict[x]] for x in range(len(new_names))]
p5 = [p5[sort_dict[x]] for x in range(len(new_names))]
p25 = [p25[sort_dict[x]] for x in range(len(new_names))]
p75 = [p75[sort_dict[x]] for x in range(len(new_names))]
p95 = [p95[sort_dict[x]] for x in range(len(new_names))]

names = new_names

plt.figure()

for i in range(len(meds)):
    plt.plot([i,i],[p5[i],p25[i]],c3,linewidth=3)
    plt.plot([i,i],[p75[i],p95[i]],c3,linewidth=3)
    plt.plot([i,i],[p25[i],p75[i]],c2,linewidth=6)
    plt.plot([i-.25,i+.25],[meds[i],meds[i]],c1,linewidth=3)
plt.legend()
plt.xticks(range(len(meds)),names,rotation=90,fontsize=5)
plt.savefig(newdir+"sorted_compare_dislocations.png")
fig = plt.gcf()
fig.set_size_inches((12,6), forward=False)
plt.savefig(newdir+"sorted_compare_dislocations_dpi.png",dpi = 500)

plt.close()

plt.figure()
for i in range(len(meds)):
    plt.plot([i,i],[p5[i],mins[i]],c4,linewidth=1)
    plt.plot([i,i],[p95[i],maxs[i]],c4,linewidth=1)
    plt.plot([i,i],[p5[i],p25[i]],c3,linewidth=3)
    plt.plot([i,i],[p75[i],p95[i]],c3,linewidth=3)
    plt.plot([i,i],[p25[i],p75[i]],c2,linewidth=6)
    plt.plot([i-.25,i+.25],[meds[i],meds[i]],c1,linewidth=3)
plt.legend()
plt.xticks(range(len(meds)),names,rotation=90,fontsize=5)
plt.savefig(newdir+"sorted_compare_dislocations_mm.png")
fig = plt.gcf()
fig.set_size_inches((12,6), forward=False)
plt.savefig(newdir+"sorted_compare_dislocations_mm_dpi.png",dpi = 500)

plt.close()

plt.figure()

for i in range(len(meds)):
    plt.plot([i,i],[p5[i],p25[i]],c3,linewidth=3)
    plt.plot([i,i],[p75[i],p95[i]],c3,linewidth=3)
    plt.plot([i,i],[p25[i],p75[i]],c2,linewidth=6)
    plt.plot([i-.25,i+.25],[meds[i],meds[i]],c1,linewidth=3)
    plt.plot([i],[enacted[i]],'o',color=c0, markersize=4)
plt.plot([],[],c1,label='Median')
plt.plot([],[],'o',color=c0,label='Enacted')
plt.legend()
plt.xticks(range(len(meds)),names,rotation=90,fontsize=5)
plt.savefig(newdir+"sorted_compare_dislocations_e.png")
fig = plt.gcf()
fig.set_size_inches((12,6), forward=False)
plt.savefig(newdir+"sorted_compare_dislocations_e_dpi.png",dpi = 500)
plt.close()

plt.figure()
for i in range(len(meds)):
    plt.plot([i,i],[p5[i],mins[i]],c4,linewidth=1)
    plt.plot([i,i],[p95[i],maxs[i]],c4,linewidth=1)
    plt.plot([i,i],[p5[i],p25[i]],c3,linewidth=3)
    plt.plot([i,i],[p75[i],p95[i]],c3,linewidth=3)
    plt.plot([i,i],[p25[i],p75[i]],c2,linewidth=6)
    plt.plot([i-.25,i+.25],[meds[i],meds[i]],c1,linewidth=3)
    plt.plot([i],[enacted[i]],'o',color=c0, markersize=4)
plt.plot([],[],c1,label='Median')
plt.plot([],[],'o',color=c0,label='Enacted')
plt.legend()
plt.xticks(range(len(meds)),names,rotation=90,fontsize=5)
plt.savefig(newdir+"sorted_compare_dislocations_mm_e.png")
fig = plt.gcf()
fig.set_size_inches((12,6), forward=False)
plt.savefig(newdir+"sorted_compare_dislocations_mm_e_dpi.png",dpi = 500)

plt.close()





