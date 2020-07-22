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
        #'05',
        '06',
        '08',
        '09',
        #'10',
        '12',
        '13',
        #'16',
        '17',
        '18',
        #'19',
        #'20',
        '21',
        '22',
        #'23',
        '24',
        '25',
        '26',
        '27',
        #'28',
        '29',
        #'30',
        #'31',
        #'32',
        #'33',
        '34',
        #'35',
        '36',
        '37',
        #'38',
        '39',
        '40',
        '42',
        #'44',
        '45',
        #'46',
        '47',
        '48',
        #'49',
        #'50',
        '51',
        '53',
        #'54',
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

e_dir = f"../../../../Dropbox/dislocation_intermediate_files/Enacted_Stats_Swung/"
newdir = f"../../../../Dropbox/dislocation_intermediate_files/Revised_Enacted_Stats_Swung/"


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


mms_std = []
egs_std = []
pbs_std = []
pgs_std = []

seats_std = []

adlocs_std = []
qdlocs_std = []

vshare_std = []

dgi_std = []

for state_fips in fips_list:
    print(f"Starting {state_fips}")
    names.append(state_names[state_fips])    

    with open(e_dir + "Start_Values_"+str(state_fips)+".txt", "r") as f:
        for index, line in enumerate(f):
            if index == 5:
                temp = line[29:-3].split(',')
                tempvec = list([float(x) for x in temp])
                print(len(tempvec))
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
                e_seats.append(float(line[24:])/len(temp))
                #print(seats)
                #print(line[24:])
            if index == 19:
                #print(line[38:])
                e_adlocs.append(float(line[38:]))    
    
            if index == 21:
                #print(line[38:])
                e_qdlocs.append(float(line[38:]))    
        
fig, ax = plt.subplots()   
sns.regplot(e_pgs, e_adlocs)
plt.xlabel('Partisan Gini')
plt.ylabel('Absolute Average Partisan Dislocation')
for i, txt in enumerate(names):
    ax.annotate(txt, (e_pgs[i], e_adlocs[i]))
    
plt.savefig(newdir+ 'DvsPG_L.png',dpi =200)
fig = plt.gcf()
fig.set_size_inches((12,6), forward=False)
plt.savefig(newdir+ 'DvsPG_L_dpi.png',dpi = 500)


plt.close()
