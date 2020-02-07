# -*- coding: utf-8 -*-
import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_style("white")
#sns.set_style("darkgrid", {"axes.facecolor": ".97"})


num_elections = 1

election_names = ["PRES2008"]

election_columns = [["P2008_D",  "P2008_R"]]

fips_list = [
        '01',
        #'02',
        '04',
        '05',
        '06',
        '08',
        '09',
        #'10',
        #'11',
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

plan_name = "Enacted"


num_districts = 7 #replace this with length of vote vector

max_steps = 100000
step_size = 10000

ts = [x * step_size for x in range(1, int(max_steps / step_size) + 1)]


burn = 0
sub_sample = 1



for state_fips in fips_list:
    for run in ['0']:
        print('starting', state_fips, run)

        
        datadir = f"../../../Dropbox/dislocation_intermediate_files/100_ensembles/{state_fips}_run{run}/"        
        newdir = f"../../../Dropbox/dislocation_intermediate_files/100_ensembles/{state_fips}_run{run}/"
        
        os.makedirs(os.path.dirname(newdir + "init.txt"), exist_ok=True)
        with open(newdir + "init.txt", "w") as f:
            f.write("Created Folder")
        

        
        

        for elect in range(num_elections):
            a = []
            c = 'k'
            for t in ts:
                tempvotes = np.loadtxt(
                    datadir + election_names[elect] + "_" + str(t) + ".csv", delimiter=","
                )
                for s in range(step_size):
                    a.append(tempvotes[s, :])
        
            a = np.array(a)
            
            b = a - 0.0369
            
            swung_seats = []
            
            for i in range(max_steps):
                swung_seats.append(sum([x>.5 for x in a[i,:]])
                
            with open(newdir + "swungseats.csv", "w") as tf1:
                writer = csv.writer(tf1, lineterminator="\n")
                writer.writerows([swung_seats])
                
                
            with open(newdir + "swungvotes.csv", "w") as tf1:
                writer = csv.writer(tf1, lineterminator="\n")
                writer.writerows(b)            
            
            
            
            



       
