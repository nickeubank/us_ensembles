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
import math
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


#1 through 16 only wrote a single file. 

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

e_dir = f"../../../Dropbox/dislocation_intermediate_files/Enacted_Stats_Swung/"

    
plan_name = "Enacted"

election_name = election_names[0]


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


#fips_list = ['48']

for state_fips in fips_list:
    print(f"Starting {state_fips}")
    newdir = f"../../../Dropbox/dislocation_intermediate_files/106_Quad_Optimized_Outputs/Comparison_Plots_Swung/{state_fips}_"
    #os.makedirs(os.path.dirname(newdir + "init.txt"), exist_ok=True)
    #with open(newdir + "init.txt", "w") as f:
    #    f.write("Created Folder")
    names.append(state_names[state_fips])    

    with open(e_dir + "Start_Values_"+str(state_fips)+".txt", "r") as f:
        for index, line in enumerate(f):
            if index == 5:
                temp = line[29:-3].split(',')
                tempvec = [float(x) for x in temp]
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
    
    
    #e_seats = [11] #for TX swung

    
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
        for t in ts:
            temp = np.loadtxt(datadir + "dloc_q" + str(t) + ".csv", delimiter=",")
            #print(t,len(temp))
            adlocs[0, t - step_size  : t] = temp

        #"""    
        
        seats = np.zeros([1, max_steps])
        mms = np.zeros([1, max_steps]) 
        pbs = np.zeros([1, max_steps]) 
        pgs = np.zeros([1, max_steps]) 
        egs = np.zeros([1, max_steps])
        
            
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
            
        
        #"""
        
        

        loaded_vec = np.loadtxt(datadir2+"swungvotes.csv", delimiter=",")
        

        print(loaded_vec[:,0].shape)
        #advjsn
        
        medians = [np.median(loaded_vec[:,i]) for i in range(len(list(loaded_vec[0,:])))]
        
        print(medians)
        #fdvd
        
        dgi = []
        
        for j in range(max_steps):
            dgi.append(math.sqrt(sum([(medians[i]-loaded_vec[j,i])**2 for i in range(len(medians))])))
            
        
        
        seats = np.loadtxt(datadir2+"swungseats.csv", delimiter=",")
        
        
        
        #print(seats.shape)
        
        o_datadir = f"../../../Dropbox/dislocation_intermediate_files/106_Quad_Optimized_Outputs/{state_fips}_run0/"       
        
        for elect in range(num_elections):
            a = []
            c = 'k'
            for tempindex in range(10):
                tempvotes = np.loadtxt(
                    o_datadir + election_names[elect] + f"_{(1+tempindex)*10}.csv", delimiter=","
                )
                for s in range(10):
                    a.append(tempvotes[s, :])
        
            a = np.array(a)
            
            b = a 
            
            o_dgi = []
            
            for j in range(100):
                o_dgi.append(math.sqrt(sum([(medians[i]-b[j,i])**2 for i in range(len(medians))])))
            
            
            o_seats = []
            
            for i in range(100):
                o_seats.append(sum([x>.5 for x in b[i,:]])) 
                  
                #if i == 42 or i == 30:
                #    print(o_seats[-1], b[i,:])
                
            #print(o_seats)

   
            
        plt.figure()
        sns.distplot(dgi,kde=False, bins=1000, color='gray', norm_hist = True, label = 'All Plans')     
        sns.distplot(o_dgi,kde=False, bins=100, color='green', norm_hist = True, label = 'Optimized Plans') 
        plt.axvline(x=math.sqrt(sum([(medians[i]-e_swung_votes[i])**2 for i in range(len(medians))])),color='red',label='Enacted') 
        plt.ylabel("Frequency")
        plt.xlabel("Gerrymandering Index")    
        plt.legend()
        plt.savefig(newdir+"Opt_DGI_quad.png")
        plt.close()
        
        
        max_steps = 100
        step_size = 10
            
        ts = [x * step_size for x in range(1, int(max_steps / step_size) + 1)]    
        o_seats = np.zeros([1, 100])
        o_mms = np.zeros([1, 100]) 
        o_pbs = np.zeros([1, 100]) 
        o_pgs = np.zeros([1, 100]) 
        o_egs = np.zeros([1, 100])
        o_adlocs = np.zeros([1, 100])
                         
        for t in ts:       
            temp = np.loadtxt(datadir2 + "hmss" + str(t) + ".csv", delimiter=",")
            seats[:, t - step_size : t] = temp.T
            temp = np.loadtxt(o_datadir + "mms" + str(t) + ".csv", delimiter=",")
            mms[:, t - step_size : t] = temp.T
            temp = np.loadtxt(o_datadir + "pbs" + str(t) + ".csv", delimiter=",")
            pbs[:, t - step_size : t] = temp.T
            temp = np.loadtxt(o_datadir + "pgs" + str(t) + ".csv", delimiter=",")
            pgs[:, t - step_size : t] = temp.T
            temp = np.loadtxt(o_datadir + "egs" + str(t) + ".csv", delimiter=",")
            egs[:, t - step_size : t] = temp.T
            temp = np.loadtxt(o_datadir + "adloc" + str(t) + ".csv", delimiter=",")
            o_adlocs[:, t - step_size : t] = temp.T  


        #o_adlocs[0,:] = np.loadtxt(o_datadir + "adloc100.csv", delimiter=",")

        
        """

        
         
        
               
        o_seats[0,:] = np.loadtxt(o_datadir + "hmss100.csv", delimiter=",")
        o_mms[0,:] = np.loadtxt(o_datadir + "mms100.csv", delimiter=",") 
        o_pbs[0,:] = np.loadtxt(o_datadir + "pbs100.csv", delimiter=",")
        o_pgs[0,:] = np.loadtxt(o_datadir + "pgs100.csv", delimiter=",")
        o_egs[0,:] = np.loadtxt(o_datadir + "egs100.csv", delimiter=",")    
        """
        
        plt.figure()
        sns.distplot(mms,kde=False, bins=1000, color='gray', norm_hist = True, label = 'All Plans')     
        sns.distplot(o_mms,kde=False, color='green', norm_hist = True, label = 'Optimized Plans')
        plt.axvline(x=e_mms[-1],color='red',label='Enacted') 
        plt.ylabel("Frequency")
        plt.xlabel("Mean Median")    
        plt.legend()
        plt.savefig(newdir+"Opt_MM_quad.png")
        plt.close()
        
   
        
        
        plt.figure()
        sns.distplot(egs,kde=False, bins=1000, color='gray', norm_hist = True, label = 'All Plans')     
        sns.distplot(o_egs,kde=False, color='green', norm_hist = True, label = 'Optimized Plans') 
        plt.axvline(x=e_egs[-1],color='red',label='Enacted') 
        plt.ylabel("Frequency")
        plt.xlabel("Efficiency Gap")    
        plt.legend()
        plt.savefig(newdir+"Opt_EG_quad.png")
        plt.close()            
        
        plt.figure()
        sns.distplot(pbs,kde=False, bins=1000, color='gray', norm_hist = True, label = 'All Plans')     
        sns.distplot(o_pbs,kde=False, color='green', norm_hist = True, label = 'Optimized Plans') 
        plt.axvline(x=e_pbs[-1],color='red',label='Enacted') 
        plt.ylabel("Frequency")
        plt.xlabel("Partisan Bias")    
        plt.legend()
        plt.savefig(newdir+"Opt_PB_quad.png")
        plt.close()        
            
        plt.figure()
        sns.distplot(pgs,kde=False, bins=1000, color='gray', norm_hist = True, label = 'All Plans')     
        sns.distplot(o_pgs,kde=False, color='green', norm_hist = True, label = 'Optimized Plans') 
        plt.axvline(x=e_pgs[-1],color='red',label='Enacted') 
        plt.ylabel("Frequency")
        plt.xlabel("Partisan Gini")    
        plt.legend()
        plt.savefig(newdir+"Opt_pg_quad.png")
        plt.close()
        #"""
        #"""
        plt.figure()        
        sns.distplot(seats, kde=False, bins = [x-.15 for x in range(int(min(seats))-1,int(max(seats))+2)], color='gray', norm_hist = True, label = 'All Plans',hist_kws={"rwidth":.3,"align":"left"})
        sns.distplot([x+1 for x in o_seats], kde=False, bins=[x+.15 for x in range(int(min(seats))-1,int(max(seats))+2)],color='green', norm_hist = True, label='Optimized Plans',hist_kws={"rwidth":.3,"align":"left"}) 
        plt.axvline(x=e_seats[-1],color='red',label='Enacted') 
        plt.ylabel("Frequency")
        plt.xlabel("Dem Seats")    
        plt.legend()
        plt.savefig(newdir+"Opt_seats_quad.png")
        plt.close()  

        plt.figure()
        sns.distplot(adlocs,kde=False, bins=1000, color='gray', norm_hist = True, label = 'All Plans')     
        sns.distplot(o_adlocs,kde=False, color='green', norm_hist = True, label = 'Optimized Plans') 
        plt.axvline(x=e_adlocs[-1],color='red',label='Enacted') 
        plt.ylabel("Frequency")
        plt.xlabel("Squared Absolute Dislocation")    
        plt.legend()
        plt.savefig(newdir+"Opt_adloc_quad.png")
        plt.close()      
        #"""
