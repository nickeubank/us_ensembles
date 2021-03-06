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
import csv
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

e_dir = f"../../../Dropbox/dislocation_intermediate_files/Enacted_Stats/"
newdir = f"../../../Dropbox/dislocation_intermediate_files/Outlier_Comparisons/"
os.makedirs(os.path.dirname(newdir + "init.txt"), exist_ok=True)
with open(newdir + "init.txt", "w") as f:
    f.write("Created Folder")


e_mms = []
e_egs = []
e_pbs = []
e_pgs = []

e_seats = []

e_adlocs = []

e_vshare = []

names = []


m_mms = []
m_egs = []
m_pbs = []
m_pgs = []

m_seats = []

m_adlocs = []

m_vshare = []



#indices = ['44']

for state_fips in indices:
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
                e_seats.append(float(line[24:])/len(temp))
                #print(seats)
                #print(line[24:])
            if index == 19:
                #print(line[38:])
                e_adlocs.append(float(line[38:]))
                
                
                
                


with open(newdir + "enacted_indices.csv", "w") as tf1:
    writer = csv.writer(tf1, lineterminator="\n")
    writer.writerows([indices])

with open(newdir + "enacted_names.csv", "w") as tf1:
    writer = csv.writer(tf1, lineterminator="\n")
    writer.writerows([names])

with open(newdir + "enacted_mms.csv", "w") as tf1:
    writer = csv.writer(tf1, lineterminator="\n")
    writer.writerows([mms])

with open(newdir + "enacted_egs.csv", "w") as tf1:
    writer = csv.writer(tf1, lineterminator="\n")
    writer.writerows([egs])

with open(newdir + "enacted_pbs.csv", "w") as tf1:
    writer = csv.writer(tf1, lineterminator="\n")
    writer.writerows([pbs])

with open(newdir + "enacted_pgs.csv", "w") as tf1:
    writer = csv.writer(tf1, lineterminator="\n")
    writer.writerows([pgs])

with open(newdir + "enacted_seats.csv", "w") as tf1:
    writer = csv.writer(tf1, lineterminator="\n")
    writer.writerows([seats])

with open(newdir + "enacted_vshare.csv", "w") as tf1:
    writer = csv.writer(tf1, lineterminator="\n")
    writer.writerows([vshare])

with open(newdir + "enacted_adlocs.csv", "w") as tf1:
    writer = csv.writer(tf1, lineterminator="\n")
    writer.writerows([adlocs])
               
plt.figure()   
plt.plot(vshare,adlocs, 'ob')
plt.xlabel('Vote Share')
plt.ylabel('Absolute Average Dislocation')
plt.savefig(newdir+ 'DvsVS.png')
plt.close()

plt.figure()   
plt.plot(np.abs(mms),adlocs, 'ob')
plt.xlabel('Mean-Median')
plt.ylabel('Absolute Average Dislocation')
plt.savefig(newdir+ 'DvsMM.png')
plt.close()


plt.figure()   
plt.plot(np.abs(egs),adlocs, 'ob')
plt.xlabel('Efficiency Gap')
plt.ylabel('Absolute Average Dislocation')
plt.savefig(newdir+ 'DvsEG.png')
plt.close()


plt.figure()   
plt.plot(np.abs(pbs),adlocs, 'ob')
plt.xlabel('Partisan Bias')
plt.ylabel('Absolute Average Dislocation')
plt.savefig(newdir+ 'DvsPB.png')
plt.close()


plt.figure()   
plt.plot(np.abs(pgs),adlocs, 'ob')
plt.xlabel('Partisan Gini')
plt.ylabel('Absolute Average Dislocation')
plt.savefig(newdir+ 'DvsPG.png')
plt.close()


plt.figure()   
plt.plot(seats,adlocs, 'ob')
plt.xlabel('Seat Share')
plt.ylabel('Absolute Average Dislocation')
plt.savefig(newdir+ 'DvsSS.png')
plt.close()


                
fig, ax = plt.subplots()
plt.plot(vshare,adlocs, 'ob')
plt.xlabel('Vote Share')
plt.ylabel('Absolute Average Dislocation')
for i, txt in enumerate(names):
    ax.annotate(txt, (vshare[i], adlocs[i]))
plt.savefig(newdir+ 'DvsVS_L.png')
plt.close()

fig, ax = plt.subplots()
plt.plot(np.abs(mms),adlocs, 'ob')
for i, txt in enumerate(names):
    ax.annotate(txt, (np.abs(mms)[i], adlocs[i]))
plt.xlabel('Mean-Median')
plt.ylabel('Absolute Average Dislocation')
plt.savefig(newdir+ 'DvsMM_L.png')
plt.close()


fig, ax = plt.subplots()
plt.plot(np.abs(egs),adlocs, 'ob')
for i, txt in enumerate(names):
    ax.annotate(txt, (np.abs(egs)[i], adlocs[i]))
plt.xlabel('Efficiency Gap')
plt.ylabel('Absolute Average Dislocation')
plt.savefig(newdir+ 'DvsEG_L.png')
plt.close()


fig, ax = plt.subplots()
plt.plot(np.abs(pbs),adlocs, 'ob')
for i, txt in enumerate(names):
    ax.annotate(txt, (np.abs(pbs)[i], adlocs[i]))
plt.xlabel('Partisan Bias')
plt.ylabel('Absolute Average Dislocation')
plt.savefig(newdir+ 'DvsPB_L.png')
plt.close()


fig, ax = plt.subplots()
plt.plot(np.abs(pgs),adlocs, 'ob')
for i, txt in enumerate(names):
    ax.annotate(txt, (np.abs(pgs)[i], adlocs[i]))
plt.xlabel('Partisan Gini')
plt.ylabel('Absolute Average Dislocation')
plt.savefig(newdir+ 'DvsPG_L.png')
plt.close()


plt.figure()   
plt.plot(np.abs(seats),adlocs, 'ob')
for i, txt in enumerate(names):
    ax.annotate(txt, (np.abs(seats)[i], adlocs[i]))
plt.xlabel('Seat Share')
plt.ylabel('Absolute Average Dislocation')
plt.savefig(newdir+ 'DvsSS_L.png')
plt.close()
                

