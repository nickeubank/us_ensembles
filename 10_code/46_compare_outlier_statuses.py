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

e_dir = f"../../../Dropbox/dislocation_intermediate_files/Enacted_Stats_Swung/"
newdir = f"../../../Dropbox/dislocation_intermediate_files/Outlier_Comparisons_Swung/"
os.makedirs(os.path.dirname(newdir + "init.txt"), exist_ok=True)
with open(newdir + "init.txt", "w") as f:
    f.write("Created Folder")
    
plan_name = "Enacted"

election_name = election_names[0]


e_mms = []
e_egs = []
e_pbs = []
e_pgs = []

e_seats = []

e_adlocs = []
e_qdlocs = []
e_vshare = []

e_dgi = []


names = []


m_mms = []
m_egs = []
m_pbs = []
m_pgs = []

m_seats = []

m_adlocs = []
m_qdlocs = []

m_vshare = []

m_dgi = []

for state_fips in fips_list:
    print(f"Starting {state_fips}")
    names.append(state_names[state_fips])    

    with open(e_dir + "Start_Values_"+str(state_fips)+".txt", "r") as f:
        for index, line in enumerate(f):
            if index == 5:
                temp = line[29:-3].split(',')
                e_vshare.append(np.mean([float(x) for x in temp]))
            if index == 7:
                #print(line[21:])
                e_mms.append(float(line[21:]))
            if index == 9: 
                e_egs.append(float(line[24:]))
            if index == 11:
                e_pbs.append(float(line[23:]))
                #print(line[23:])
            if index == 13:
                e_pgs.append(float(line[23:]))
            if index == 15:
                e_seats.append(float(line[24:]))/len(temp))
                #print(seats)
                #print(line[24:])
            if index == 19:
                #print(line[38:])
                e_adlocs.append(float(line[38:]))    
    
            if index == 21:
                #print(line[38:])
                e_qdlocs.append(float(line[38:]))    
        


    
    for run in ['0']:#['0','1','2']:

        max_steps = 100000

        burn = 0
        sub_sample = 1
        step_size = 10000
    
        #if int(state_fips)<17:
        #    step_size = 100000
            
        ts = [x * step_size for x in range(1, int(max_steps / step_size) + 1)]
        
        datadir = f"../../../Dropbox/dislocation_intermediate_files/100_ensembles/{state_fips}_run{run}/rerun4/"
        
        
        datadir2 = f"../../../Dropbox/dislocation_intermediate_files/100_ensembles/{state_fips}_run{run}/" 
        
            
        adlocs = np.zeros([1, max_steps])
        seats = np.zeros([1, max_steps])
        mms = np.zeros([1, max_steps]) 
        pbs = np.zeros([1, max_steps]) 
        pgs = np.zeros([1, max_steps]) 
        egs = np.zeros([1, max_steps])
        
        for t in ts:
            temp = np.loadtxt(datadir + "new_adloc" + str(t) + ".csv", delimiter=",")
            #print(t,len(temp))
            adlocs[0, t - step_size  : t] = temp
            
        step_size = 10000
            
        ts = [x * step_size for x in range(1, int(max_steps / step_size) + 1)]    
         
        for t in ts:       
            #temp = np.loadtxt(datadir2 + "hmss" + str(t) + ".csv", delimiter=",")
            #seats[:, t - step_size : t] = temp.T
            temp = np.loadtxt(datadir2 + "mms" + str(t) + ".csv", delimiter=",")
            mms[:, t - step_size : t] = temp.T
            temp = np.loadtxt(datadir2 + "pbs" + str(t) + ".csv", delimiter=",")
            pbs[:, t - step_size : t] = temp.T
            temp = np.loadtxt(datadir2 + "pgs" + str(t) + ".csv", delimiter=",")
            pgs[:, t - step_size : t] = temp.T
            temp = np.loadtxt(datadir2 + "egs" + str(t) + ".csv", delimiter=",")
            egs[:, t - step_size : t] = temp.T
            


        loaded_vec = np.loadtxt(datadir2+"swungvotes.csv", delimiter=",")
        


        
        medians = [np.median(loaded_vec[:,i]) for i in range(len(list(loaded_vec[0,:])))]
        
        dgi = []
        for j in range(max_steps):
            dgi.append(math.sqrt(sum([(medians[i]-loaded_vec[j,i])**2 for i in range(len(medians))])))
        
        m_dgi.append(np.mean(dgi)) 
        
        e_dgi.append(math.sqrt(sum([(medians[i]-temp[i])**2 for i in range(len(medians))])))       

        seats = np.loadtxt(datadir2+"swungseats.csv", delimiter=",")
        
        m_mms.append(np.mean(mms))
        m_egs.append(np.mean(egs))
        m_pbs.append(np.mean(pbs))
        m_pgs.append(np.mean(pgs))

        m_seats.append(np.mean(seats)/len(temp))

        m_adlocs.append(np.mean(adlocs))
        
plt.figure()   
plt.plot([abs(m_dgi[x]-e_dgi[x]) for x in range(len(fips_list))],e_adlocs, 'ob')
plt.xlabel('Distance to Ensemble Gerrymandering Index Mean')
plt.ylabel('Absolute Average Dislocation')
plt.savefig(newdir+ 'adlocVSdgi_distance.png')
plt.close()        
            
plt.figure()   
plt.plot([abs(m_seats[x]-e_seats[x]) for x in range(len(fips_list))],e_adlocs, 'ob')
plt.xlabel('Distance to Ensemble Seat Share Mean')
plt.ylabel('Absolute Average Dislocation')
plt.savefig(newdir+ 'adlocVSseat_distance.png')
plt.close()
    
plt.figure()   
plt.plot([abs(m_mms[x]-e_mms[x]) for x in range(len(fips_list))],e_adlocs, 'ob')
plt.xlabel('Distance to Ensemble Mean-Median Mean')
plt.ylabel('Absolute Average Dislocation')
plt.savefig(newdir+ 'adlocVSmm_distance.png')
plt.close()

plt.figure()   
plt.plot([abs(m_egs[x]-e_egs[x]) for x in range(len(fips_list))],e_adlocs, 'ob')
plt.xlabel('Distance to Ensemble Efficiency Gap Mean')
plt.ylabel('Absolute Average Dislocation')
plt.savefig(newdir+ 'adlocVSeg_distance.png')
plt.close()


plt.figure()   
plt.plot([abs(m_pgs[x]-e_pgs[x]) for x in range(len(fips_list))],e_adlocs, 'ob')
plt.xlabel('Distance to Ensemble Partisan Gini Mean')
plt.ylabel('Absolute Average Dislocation')
plt.savefig(newdir+ 'adlocVSpg_distance.png')
plt.close()

plt.figure()   
plt.plot([abs(m_pbs[x]-e_pbs[x]) for x in range(len(fips_list))],e_adlocs, 'ob')
plt.xlabel('Distance to Ensemble Partisan Bias Mean')
plt.ylabel('Absolute Average Dislocation')
plt.savefig(newdir+ 'adlocVSpb_distance.png')
plt.close()


            
plt.figure()   
plt.plot([abs(m_seats[x]-e_seats[x]) for x in range(len(fips_list))],[abs(m_adlocs[x]-e_adlocs[x]) for x in range(len(fips_list))], 'ob')
plt.xlabel('Distance to Ensemble Seat Share Mean')
plt.ylabel('Distance to Ensemble Absolute Average Dislocation Mean')
plt.savefig(newdir+ 'dist_adlocVSseat_distance.png')
plt.close()


            
plt.figure()   
plt.plot([abs(m_dgi[x]-e_dgi[x]) for x in range(len(fips_list))],[abs(m_adlocs[x]-e_adlocs[x]) for x in range(len(fips_list))], 'ob')
plt.xlabel('Distance to Ensemble Gerrymandering Index Mean')
plt.ylabel('Distance to Ensemble Absolute Average Dislocation Mean')
plt.savefig(newdir+ 'dist_adlocVSdgi_distance.png')
plt.close()
    
    
plt.figure()   
plt.plot([abs(m_mms[x]-e_mms[x]) for x in range(len(fips_list))],[abs(m_adlocs[x]-e_adlocs[x]) for x in range(len(fips_list))], 'ob')
plt.xlabel('Distance to Ensemble Mean-Median Mean')
plt.ylabel('Distance to Ensemble Absolute Average Dislocation Mean')
plt.savefig(newdir+ 'dist_adlocVSmm_distance.png')
plt.close()

plt.figure()   
plt.plot([abs(m_egs[x]-e_egs[x]) for x in range(len(fips_list))],[abs(m_adlocs[x]-e_adlocs[x]) for x in range(len(fips_list))], 'ob')
plt.xlabel('Distance to Ensemble Efficiency Gap Mean')
plt.ylabel('Distance to Ensemble Absolute Average Dislocation Mean')
plt.savefig(newdir+ 'dist_adlocVSeg_distance.png')
plt.close()


plt.figure()   
plt.plot([abs(m_pgs[x]-e_pgs[x]) for x in range(len(fips_list))],[abs(m_adlocs[x]-e_adlocs[x]) for x in range(len(fips_list))], 'ob')
plt.xlabel('Distance to Ensemble Partisan Gini Mean')
plt.ylabel('Distance to Ensemble Absolute Average Dislocation Mean')
plt.savefig(newdir+ 'dist_adlocVSpg_distance.png')
plt.close()

plt.figure()   
plt.plot([abs(m_pbs[x]-e_pbs[x]) for x in range(len(fips_list))],[abs(m_adlocs[x]-e_adlocs[x]) for x in range(len(fips_list))], 'ob')
plt.xlabel('Distance to Ensemble Partisan Bias Mean')
plt.ylabel('Distance to Ensemble Absolute Average Dislocation Mean')
plt.savefig(newdir+ 'dist_adlocVSpb_distance.png')
plt.close()






fig, ax = plt.subplots()
plt.plot([abs(m_dgi[x]-e_dgi[x]) for x in range(len(fips_list))],e_adlocs, 'ob')
plt.xlabel('Distance to Ensemble Gerrymandering Index Mean')
plt.ylabel('Absolute Average Dislocation')
for i, txt in enumerate(names):
    ax.annotate(txt, ([abs(m_dgi[x]-e_dgi[x]) for x in range(len(fips_list))][i],e_adlocs[i]))
plt.savefig(newdir+ 'N_adlocVSdgi_distance.png')
plt.close()

fig, ax = plt.subplots()
plt.plot([abs(m_seats[x]-e_seats[x]) for x in range(len(fips_list))],e_adlocs, 'ob')
plt.xlabel('Distance to Ensemble Seat Share Mean')
plt.ylabel('Absolute Average Dislocation')
for i, txt in enumerate(names):
    ax.annotate(txt, ([abs(m_seats[x]-e_seats[x]) for x in range(len(fips_list))][i],e_adlocs[i]))
plt.savefig(newdir+ 'N_adlocVSseat_distance.png')
plt.close()
    
fig, ax = plt.subplots()   
plt.plot([abs(m_mms[x]-e_mms[x]) for x in range(len(fips_list))],e_adlocs, 'ob')
plt.xlabel('Distance to Ensemble Mean-Median Mean')
plt.ylabel('Absolute Average Dislocation')
for i, txt in enumerate(names):
    ax.annotate(txt, ([abs(m_mms[x]-e_mms[x]) for x in range(len(fips_list))][i],e_adlocs[i]))
plt.savefig(newdir+ 'N_adlocVSmm_distance.png')
plt.close()

fig, ax = plt.subplots()   
plt.plot([abs(m_egs[x]-e_egs[x]) for x in range(len(fips_list))],e_adlocs, 'ob')
plt.xlabel('Distance to Ensemble Efficiency Gap Mean')
plt.ylabel('Absolute Average Dislocation')
for i, txt in enumerate(names):
    ax.annotate(txt, ([abs(m_egs[x]-e_egs[x]) for x in range(len(fips_list))][i],e_adlocs[i]))
plt.savefig(newdir+ 'N_adlocVSeg_distance.png')
plt.close()


fig, ax = plt.subplots()   
plt.plot([abs(m_pgs[x]-e_pgs[x]) for x in range(len(fips_list))],e_adlocs, 'ob')
plt.xlabel('Distance to Ensemble Partisan Gini Mean')
plt.ylabel('Absolute Average Dislocation')
for i, txt in enumerate(names):
    ax.annotate(txt, ([abs(m_pgs[x]-e_pgs[x]) for x in range(len(fips_list))][i],e_adlocs[i]))
plt.savefig(newdir+ 'N_adlocVSpg_distance.png')
plt.close()

fig, ax = plt.subplots()   
plt.plot([abs(m_pbs[x]-e_pbs[x]) for x in range(len(fips_list))],e_adlocs, 'ob')
plt.xlabel('Distance to Ensemble Partisan Bias Mean')
plt.ylabel('Absolute Average Dislocation')
for i, txt in enumerate(names):
    ax.annotate(txt, ([abs(m_pbs[x]-e_pbs[x]) for x in range(len(fips_list))][i],e_adlocs[i]))
plt.savefig(newdir+ 'N_adlocVSpb_distance.png')
plt.close()


fig, ax = plt.subplots()   
plt.plot([abs(m_dgi[x]-e_dgi[x]) for x in range(len(fips_list))],[abs(m_adlocs[x]-e_adlocs[x]) for x in range(len(fips_list))], 'ob')
plt.xlabel('Distance to Ensemble Gerrymandering Index Mean')
plt.ylabel('Distance to Ensemble Absolute Average Dislocation Mean')
for i, txt in enumerate(names):
    ax.annotate(txt, ([abs(m_dgi[x]-e_dgi[x]) for x in range(len(fips_list))][i],[abs(m_adlocs[x]-e_adlocs[x]) for x in range(len(fips_list))][i]))
plt.savefig(newdir+ 'N_dist_adlocVSdgi_distance.png')
plt.close()
            
fig, ax = plt.subplots()   
plt.plot([abs(m_seats[x]-e_seats[x]) for x in range(len(fips_list))],[abs(m_adlocs[x]-e_adlocs[x]) for x in range(len(fips_list))], 'ob')
plt.xlabel('Distance to Ensemble Seat Share Mean')
plt.ylabel('Distance to Ensemble Absolute Average Dislocation Mean')
for i, txt in enumerate(names):
    ax.annotate(txt, ([abs(m_seats[x]-e_seats[x]) for x in range(len(fips_list))][i],[abs(m_adlocs[x]-e_adlocs[x]) for x in range(len(fips_list))][i]))
plt.savefig(newdir+ 'N_dist_adlocVSseat_distance.png')
plt.close()
    
fig, ax = plt.subplots()   
plt.plot([abs(m_mms[x]-e_mms[x]) for x in range(len(fips_list))],[abs(m_adlocs[x]-e_adlocs[x]) for x in range(len(fips_list))], 'ob')
plt.xlabel('Distance to Ensemble Mean-Median Mean')
plt.ylabel('Distance to Ensemble Absolute Average Dislocation Mean')
for i, txt in enumerate(names):
    ax.annotate(txt, ([abs(m_mms[x]-e_mms[x]) for x in range(len(fips_list))][i],[abs(m_adlocs[x]-e_adlocs[x]) for x in range(len(fips_list))][i]))
plt.savefig(newdir+ 'N_dist_adlocVSmm_distance.png')
plt.close()

fig, ax = plt.subplots()   
plt.plot([abs(m_egs[x]-e_egs[x]) for x in range(len(fips_list))],[abs(m_adlocs[x]-e_adlocs[x]) for x in range(len(fips_list))], 'ob')
plt.xlabel('Distance to Ensemble Efficiency Gap Mean')
plt.ylabel('Distance to Ensemble Absolute Average Dislocation Mean')
for i, txt in enumerate(names):
    ax.annotate(txt, ([abs(m_egs[x]-e_egs[x]) for x in range(len(fips_list))][i],[abs(m_adlocs[x]-e_adlocs[x]) for x in range(len(fips_list))][i]))
plt.savefig(newdir+ 'N_dist_adlocVSeg_distance.png')
plt.close()


fig, ax = plt.subplots()   
plt.plot([abs(m_pgs[x]-e_pgs[x]) for x in range(len(fips_list))],[abs(m_adlocs[x]-e_adlocs[x]) for x in range(len(fips_list))], 'ob')
plt.xlabel('Distance to Ensemble Partisan Gini Mean')
plt.ylabel('Distance to Ensemble Absolute Average Dislocation Mean')
for i, txt in enumerate(names):
    ax.annotate(txt, ([abs(m_pgs[x]-e_pgs[x]) for x in range(len(fips_list))][i],[abs(m_adlocs[x]-e_adlocs[x]) for x in range(len(fips_list))][i]))
plt.savefig(newdir+ 'N_dist_adlocVSpg_distance.png')
plt.close()

fig, ax = plt.subplots()   
plt.plot([abs(m_pbs[x]-e_pbs[x]) for x in range(len(fips_list))],[abs(m_adlocs[x]-e_adlocs[x]) for x in range(len(fips_list))], 'ob')
plt.xlabel('Distance to Ensemble Partisan Bias Mean')
plt.ylabel('Distance to Ensemble Absolute Average Dislocation Mean')
for i, txt in enumerate(names):
    ax.annotate(txt, ([abs(m_pbs[x]-e_pbs[x]) for x in range(len(fips_list))][i],[abs(m_adlocs[x]-e_adlocs[x]) for x in range(len(fips_list))][i]))
    
plt.savefig(newdir+ 'N_dist_adlocVSpb_distance.png')
plt.close()
