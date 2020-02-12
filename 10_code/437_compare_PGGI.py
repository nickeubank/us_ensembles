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


#newdir = f"../20_intermediate_files/chain_ouputs/{state_fips}_run{run}/"
#os.makedirs(os.path.dirname(newdir + "init.txt"), exist_ok=True)
#with open(newdir + "init.txt", "w") as f:
#    f.write("Created Folder")


def draw_plot(data, offset, edge_color, fill_color):
    pos = [1+offset] #np.arange(data.shape[1])+1+offset
    #bp = ax.boxplot(data, positions= pos, widths=0.3, patch_artist=True, manage_xticks=False)
    bp = ax.boxplot(data, positions= pos,widths=1, whis=[25,75],showfliers=False, patch_artist=True, manage_ticks=False,zorder=4)
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
        #'06',
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

    
    for run in ['0']:#['0','1','2']:
        names.append(state_names[state_fips])
        max_steps = 100000
        step_size = 10000

            
        ts = [x * step_size for x in range(1, int(max_steps / step_size) + 1)]
        
        datadir = f"../../../Dropbox/dislocation_intermediate_files/100_ensembles/{state_fips}_run{run}/rerun4/"
        
        
        datadir2 = f"../../../Dropbox/dislocation_intermediate_files/100_ensembles/{state_fips}_run{run}/" 
        
        newdir = f"../../../Dropbox/dislocation_intermediate_files/Filtered_Swung_Plots/Comparisons/{state_fips}_"
        
        #os.makedirs(os.path.dirname(newdir + "init.txt"), exist_ok=True)
        #with open(newdir + "init.txt", "w") as f:
        #    f.write("Created Folder")
            
            
        qdlocs = np.zeros([1, max_steps])
        seats = np.zeros([1, max_steps])
        mms = np.zeros([1, max_steps]) 
        pbs = np.zeros([1, max_steps]) 
        pgs = np.zeros([1, max_steps]) 
        
        for t in ts:
            temp = np.loadtxt(datadir + "dloc_q" + str(t) + ".csv", delimiter=",")
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
        
        
        loaded_vec = np.loadtxt(datadir2+"swungvotes.csv", delimiter=",")
        


        
        medians = [np.median(loaded_vec[:,i]) for i in range(len(list(loaded_vec[0,:])))]
        #print(len(medians))
        
        dgi = np.zeros([1, max_steps])
        for j in range(max_steps):
            #dgi.append(math.sqrt(sum([(medians[i]-loaded_vec[j,i])**2 for i in range(len(medians))])))
            dgi[0,j] = math.sqrt(sum([(medians[i]-loaded_vec[j,i])**2 for i in range(len(medians))]))
            
        
        
        dgi = np.array(dgi)
        
        seats[0,:] = np.loadtxt(datadir2+"swungseats.csv", delimiter=",")        
        
        
        
        
        lbound = np.percentile(qdlocs, 1)
        ubound = np.percentile(qdlocs, 99)
        
        #for i in range(max_steps):
        #    if
        
        lwseats = seats[(qdlocs<lbound)]    
        uwseats = seats[(qdlocs>ubound)]  
        lmms = mms[(qdlocs<lbound)]   
        umms = mms[(qdlocs>ubound)] 
        lpbs = pbs[(qdlocs<lbound)]   
        upbs = pbs[(qdlocs>ubound)] 
        lpgs = pgs[(qdlocs<lbound)]   
        upgs = pgs[(qdlocs>ubound)] 
        ldgi = dgi[(qdlocs<lbound)]   
        udgi = dgi[(qdlocs>ubound)]
        lqd = qdlocs[(qdlocs<lbound)]   
        uqd = qdlocs[(qdlocs>ubound)]

        avg_dgi.append(np.mean(dgi))
        avg_pg.append(np.mean(pgs))
        fu_avg_dgi.append(np.mean(udgi))
        fu_avg_pg.append(np.mean(upgs))
        fl_avg_dgi.append(np.mean(ldgi))
        fl_avg_pg.append(np.mean(lpgs))
        
        if state_fips == '00':#state_fips:
            plt.figure()
            plt.plot(dgi,pgs,'o',color='gray',markersize=2)
            plt.plot(udgi,upgs,'o',color='yellow',markersize=2)
            plt.plot(ldgi,lpgs,'o',color='green',markersize=2)
            plt.plot([],[],'o',color='gray',markersize=2,label='All Plans')
            plt.plot([],[],'o',color='green',markersize=2,label='Low  Dislocation')
            plt.plot([],[],'o',color='yellow',markersize=2,label='High Dislocation')

            plt.xlabel('Gerrymandering Index')
            plt.ylabel('Partisan Gini')
            plt.legend()
            plt.savefig(newdir+'dgivspg.png')
            plt.close()
            
            
        draw_plot(ldgi, offset, 'green', None)    
        draw_plot(udgi, offset+2, 'gray', None)    
        draw_plot(dgi, offset+4, 'yellow', None)    
        
        offset += 10
        
newdir = f"../../../Dropbox/dislocation_intermediate_files/Filtered_Swung_Plots/Comparisons/"

plt.plot([],[],color='gray',label='All Plans')
plt.plot([],[],color='green',label='Low  Dislocation')
plt.plot([],[],color='yellow',label='High Dislocation')
plt.legend()
plt.savefig(newdir+'box_allstatesdgi.png')
plt.close()


"""

plt.figure()
plt.plot(range(len(names)),avg_dgi,'*',color='gray')
plt.plot(range(len(names)),fu_avg_dgi,'*',color='yellow')
plt.plot(range(len(names)),fl_avg_dgi,'*',color='green')
plt.ylabel('Gerrymandering Index')
plt.xticks(range(len(names)),names,rotation=90,fontsize=6)
plt.plot([],[],'*',color='gray',label='All Plans')
plt.plot([],[],'*',color='green',label='Low  Dislocation')
plt.plot([],[],'*',color='yellow',label='High Dislocation')
plt.legend()
plt.savefig(newdir+'allstatesdgi.png')
plt.close()

plt.figure()
plt.plot(range(len(names)),avg_pg,'*',color='gray')
plt.plot(range(len(names)),fu_avg_pg,'*',color='yellow')
plt.plot(range(len(names)),fl_avg_pg,'*',color='green')
plt.ylabel('Partisan Gini')
plt.xticks(range(len(names)),names,rotation=90,fontsize=6)
plt.plot([],[],'*',color='gray',label='All Plans')
plt.plot([],[],'*',color='green',label='Low  Dislocation')
plt.plot([],[],'*',color='yellow',label='High Dislocation')
plt.legend()
plt.savefig(newdir+'allstatespgs.png')
plt.close()

"""

        
