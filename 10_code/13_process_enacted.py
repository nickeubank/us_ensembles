import geopandas as gpd
import os
import pickle
import numpy as np
import gerrychain as gc
from gerrychain import Graph, Partition, Election
from gerrychain.updaters import Tally, cut_edges
from maup import assign
from gerrychain.metrics import efficiency_gap, mean_median, partisan_bias, partisan_gini
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_style("white")


indices=['01',
        '04',
        '05',
        '06',
        '08',
        '09',
        '10',
        #'11',
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
        '31',
        '32',
        '33',
        '34',
        '35',
        #'36',
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
"44":"Rhode_Island","45":"South_Carolina","46":"South_Dakota","47":"Tennessee",
"48":"Texas","49":"Utah","51":"Virginia","50":"Vermont","53":"Washington",
"55":"Wisconsin","54":"West_Virginia","56":"Wyoming"}

newdir = f"../../../Dropbox/dislocation_intermediate_files/Enacted_Stats/"
os.makedirs(os.path.dirname(newdir + "init.txt"), exist_ok=True)
with open(newdir + "init.txt", "w") as f:
    f.write("Created Folder")


mms = []
egs = []
pbs = []
pgs = []

seats = []

adlocs = []

vshare = []

names = []

#indices = ['44']

for state_fips in indices:
    names.append(state_names[state_fips])
    with open(newdir + "Start_Values_"+str(state_fips)+".txt", "r") as f:
        for index, line in enumerate(f):
            if index == 5:
                temp = line[29:-3].split(',')
                vshare.append(np.mean([float(x) for x in temp]))
            if index == 7:
                #print(line[21:])
                mms.append(float(line[21:]))
            if index == 9: 
                egs.append(float(line[24:]))
            if index == 11:
                pbs.append(float(line[23:]))
                #print(line[23:])
            if index == 13:
                pgs.append(float(line[23:]))
            if index == 15:
                seats.append(float(line[24:])/len(temp))
                #print(seats)
                #print(line[24:])
            if index == 19:
                #print(line[38:])
                adlocs.append(float(line[38:]))
                
                
plt.figure()                
                

