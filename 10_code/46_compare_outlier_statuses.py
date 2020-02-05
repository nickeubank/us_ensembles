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
        #'06',
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

e_dir = f"../../../Dropbox/dislocation_intermediate_files/Enacted_Stats/"
newdir = f"../../../Dropbox/dislocation_intermediate_files/Outlier_Comparisons/"
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

e_vshare = []

names = []


m_mms = []
m_egs = []
m_pbs = []
m_pgs = []

m_seats = []

m_adlocs = []

m_vshare = []


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

        burn = 0
        sub_sample = 1
        step_size = 10000
    
        #if int(state_fips)<17:
        #    step_size = 100000
            
        ts = [x * step_size for x in range(1, int(max_steps / step_size) + 1)]
        
        datadir = f"../../../Dropbox/dislocation_intermediate_files/100_ensembles/{state_fips}_run{run}/rerun4/"
        
        
        datadir2 = f"../../../Dropbox/dislocation_intermediate_files/100_ensembles/{state_fips}_run{run}/" 
        
        newdir = f"../../../Dropbox/dislocation_intermediate_files/100_ensembles/{state_fips}_run{run}/rerun4/"
        
        os.makedirs(os.path.dirname(newdir + "init.txt"), exist_ok=True)
        with open(newdir + "init.txt", "w") as f:
            f.write("Created Folder")
            
            
        qdlocs = np.zeros([1, max_steps])
        seats = np.zeros([1, max_steps])
        mms = np.zeros([1, max_steps]) 
        pbs = np.zeros([1, max_steps]) 
        pgs = np.zeros([1, max_steps]) 
        
        for t in ts:
            temp = np.loadtxt(datadir + "dloc_q" + str(t) + ".csv", delimiter=",")
            #print(t,len(temp))
            qdlocs[0, t - step_size  : t] = temp
            
        step_size = 10000
            
        ts = [x * step_size for x in range(1, int(max_steps / step_size) + 1)]    
         
        for t in ts:       
            temp = np.loadtxt(datadir2 + "hmss" + str(t) + ".csv", delimiter=",")
            seats[:, t - step_size : t] = temp.T
            temp = np.loadtxt(datadir2 + "mms" + str(t) + ".csv", delimiter=",")
            mms[:, t - step_size : t] = temp.T
            temp = np.loadtxt(datadir2 + "pbs" + str(t) + ".csv", delimiter=",")
            pbs[:, t - step_size : t] = temp.T
            temp = np.loadtxt(datadir2 + "pgs" + str(t) + ".csv", delimiter=",")
            pgs[:, t - step_size : t] = temp.T
            
        #wseats = []
        
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

        
        plt.figure()
        sns.distplot(mms,kde=False, bins=1000, color='gray',label = 'All Plans')     
        sns.distplot(lmms,kde=False, bins=100, color='green',label = 'Small Dislocation')   
        plt.legend()
        plt.savefig(newdir+"mms_comparison2l1_quad.png")

        plt.close()
  
        plt.figure()
        sns.distplot(mms,kde=False, bins=1000, color='gray',label = 'All Plans')     
        sns.distplot(umms,kde=False, bins=100, color='orange',label = 'Large Dislocation')   
        plt.legend()
        plt.savefig(newdir+"mms_comparisonul1_quad.png")

        plt.close()

        plt.figure()
        sns.distplot(pbs,kde=False, bins=1000, color='gray',label = 'All Plans')     
        sns.distplot(lpbs,kde=False, bins=100, color='green',label = 'Small Dislocation')   
        plt.legend()
        plt.savefig(newdir+"pbs_comparison2l1_quad.png")

        plt.close()
  
        plt.figure()
        sns.distplot(pbs,kde=False, bins=1000, color='gray',label = 'All Plans')     
        sns.distplot(upbs,kde=False, bins=100, color='orange',label = 'Large Dislocation')   
        plt.legend()
        plt.savefig(newdir+"pbs_comparisonul1_quad.png")

        plt.close()


        plt.figure()
        sns.distplot(pgs,kde=False, bins=1000, color='gray',label = 'All Plans')     
        sns.distplot(lpgs, kde=False,bins=100, color='green',label = 'Small Dislocation')   
        plt.legend()
        plt.savefig(newdir+"pgs_comparison2l1_quad.png")

        plt.close()
  
        plt.figure()
        sns.distplot(pgs,kde=False, bins=1000, color='gray',label = 'All Plans')     
        sns.distplot(upgs,kde=False, bins=100, color='orange',label = 'Large Dislocation')   
        plt.legend()
        plt.savefig(newdir+"pgs_comparisonul1_quad.png")

        plt.close()


        lbound = np.percentile(qdlocs, 5)
        ubound = np.percentile(qdlocs, 95)
        
        #for i in range(max_steps):
        #    if
        
        lmms = mms[(qdlocs<lbound)]   
        umms = mms[(qdlocs>ubound)] 
        lpbs = pbs[(qdlocs<lbound)]   
        upbs = pbs[(qdlocs>ubound)] 
        lpgs = pgs[(qdlocs<lbound)]   
        upgs = pgs[(qdlocs>ubound)] 

        
        plt.figure()
        sns.distplot(mms, kde=False,bins=1000, color='gray',label = 'All Plans')     
        sns.distplot(lmms,kde=False, bins=100, color='green',label = 'Small Dislocation')   
        plt.legend()
        plt.savefig(newdir+"mms_comparison2l5_quad.png")

        plt.close()
  
        plt.figure()
        sns.distplot(mms,kde=False, bins=1000, color='gray',label = 'All Plans')     
        sns.distplot(umms, kde=False,bins=100, color='orange',label = 'Large Dislocation')   
        plt.legend()
        plt.savefig(newdir+"mms_comparisonul5_quad.png")

        plt.close()

        plt.figure()
        sns.distplot(pbs,kde=False, bins=1000, color='gray',label = 'All Plans')     
        sns.distplot(lpbs,kde=False, bins=100, color='green',label = 'Small Dislocation')   
        plt.legend()
        plt.savefig(newdir+"pbs_comparison2l5_quad.png")

        plt.close()
  
        plt.figure()
        sns.distplot(pbs, kde=False,bins=1000, color='gray',label = 'All Plans')     
        sns.distplot(upbs,kde=False, bins=100, color='orange',label = 'Large Dislocation')   
        plt.legend()
        plt.savefig(newdir+"pbs_comparisonul5_quad.png")

        plt.close()


        plt.figure()
        sns.distplot(pgs, kde=False,bins=1000, color='gray',label = 'All Plans')     
        sns.distplot(lpgs,kde=False, bins=100, color='green',label = 'Small Dislocation')   
        plt.legend()
        plt.savefig(newdir+"pgs_comparison2l5_quad.png")

        plt.close()
  
        plt.figure()
        sns.distplot(pgs,kde=False, bins=1000, color='gray',label = 'All Plans')     
        sns.distplot(upgs,kde=False, bins=100, color='orange',label = 'Large Dislocation')   
        plt.legend()
        plt.savefig(newdir+"pgs_comparisonul5_quad.png")

        plt.close()


   
        plt.figure()
        sns.distplot(seats, kde=False, bins = [x for x in range(int(min(seats[0,:]))-1,int(max(seats[0,:]))+2)], color='gray',label = 'All Plans')
        sns.distplot(lwseats, kde=False, bins=[x for x in range(int(min(seats[0,:]))-1,int(max(seats[0,:]))+2)],color='green',label='Small Dislocation')
        plt.legend()
        plt.savefig(newdir+"seats_comparison2l1_quad.png")

        plt.close()
            
        
        plt.figure()
        sns.distplot(seats, kde=False, bins = [x for x in range(int(min(seats[0,:]))-1,int(max(seats[0,:]))+2)], color='gray',label = 'All Plans')
        sns.distplot(uwseats, kde=False, bins=[x for x in range(int(min(seats[0,:]))-1,int(max(seats[0,:]))+2)],color='orange',label='Large Dislocation')
        plt.legend()
        plt.savefig(newdir+"seats_comparison2u1_quad.png")

        plt.close()
            
        plt.figure()
        sns.distplot(seats, kde=False, bins = [x for x in range(int(min(seats[0,:]))-1,int(max(seats[0,:]))+2)], color='gray', norm_hist = True, label = 'All Plans')
        sns.distplot(lwseats, kde=False, bins=[x for x in range(int(min(seats[0,:]))-1,int(max(seats[0,:]))+2)],color='green', norm_hist = True, label='Small Dislocation')
        plt.legend()
        plt.savefig(newdir+"seats_comparison3l1_quad.png")

        plt.close()
            
        
        plt.figure()
        sns.distplot(seats, kde=False, bins = [x for x in range(int(min(seats[0,:]))-1,int(max(seats[0,:]))+2)], color='gray', norm_hist = True, label = 'All Plans')
        sns.distplot(uwseats, kde=False, bins=[x for x in range(int(min(seats[0,:]))-1,int(max(seats[0,:]))+2)],color='orange', norm_hist = True, label='Large Dislocation')
        plt.legend()
        plt.savefig(newdir+"seats_comparison3u1_quad.png")

        plt.close()
            
            
        plt.figure()
        sns.distplot(seats, kde=False, bins = [x-.15 for x in range(int(min(seats[0,:]))-1,int(max(seats[0,:]))+2)], color='gray',label = 'All Plans',hist_kws={"rwidth":.3,"align":"left"})
        sns.distplot([x+1 for x in lwseats], kde=False, bins=[x+.15 for x in range(int(min(seats[0,:]))-1,int(max(seats[0,:]))+2)],color='green',label='Small Dislocation',hist_kws={"rwidth":.3,"align":"left"})
        plt.legend()
        plt.savefig(newdir+"seats_comparison2l1ss_quad.png")

        plt.close()
            
        
        plt.figure()
        sns.distplot(seats, kde=False, bins = [x-.15 for x in range(int(min(seats[0,:]))-1,int(max(seats[0,:]))+2)], color='gray',label = 'All Plans',hist_kws={"rwidth":.3,"align":"left"})
        sns.distplot([x+1 for x in uwseats], kde=False, bins=[x+.15 for x in range(int(min(seats[0,:]))-1,int(max(seats[0,:]))+2)],color='orange',label='Large Dislocation',hist_kws={"rwidth":.3,"align":"left"})
        plt.legend()
        plt.savefig(newdir+"seats_comparison2u1ss_quad.png")

        plt.close()
            
        plt.figure()
        sns.distplot(seats, kde=False, bins = [x-.15 for x in range(int(min(seats[0,:]))-1,int(max(seats[0,:]))+2)], color='gray', norm_hist = True, label = 'All Plans',hist_kws={"rwidth":.3,"align":"left"})
        sns.distplot([x+1 for x in lwseats], kde=False, bins=[x+.15 for x in range(int(min(seats[0,:]))-1,int(max(seats[0,:]))+2)],color='green', norm_hist = True, label='Small Dislocation',hist_kws={"rwidth":.3,"align":"left"})
        plt.legend()
        plt.savefig(newdir+"seats_comparison3l1ss_quad.png")

        plt.close()
            
        
        plt.figure()
        sns.distplot(seats, kde=False, bins = [x-.15 for x in range(int(min(seats[0,:]))-1,int(max(seats[0,:]))+2)], color='gray', norm_hist = True, label = 'All Plans',hist_kws={"rwidth":.3,"align":"left"})
        sns.distplot([x+1 for x in uwseats], kde=False, bins=[x+.15 for x in range(int(min(seats[0,:]))-1,int(max(seats[0,:]))+2)],color='orange', norm_hist = True, label='Large Dislocation',hist_kws={"rwidth":.3,"align":"left"})
        plt.legend()
        plt.savefig(newdir+"seats_comparison3u1ss_quad.png")

        plt.close()
            
            
        plt.figure()
        sns.distplot(seats, kde=False, bins = [x for x in range(int(min(seats[0,:]))-1,int(max(seats[0,:]))+2)], color='gray',label = 'All Plans')
        sns.distplot(lwseats, kde=False, bins=[x for x in range(int(min(seats[0,:]))-1,int(max(seats[0,:]))+2)],color='green',label='Small Dislocation')
        sns.distplot(uwseats, kde=False, bins=[x for x in range(int(min(seats[0,:]))-1,int(max(seats[0,:]))+2)],color='orange',label='Large Dislocation')
        plt.legend()
        plt.savefig(newdir+"seats_comparison2all1_quad.png")

        plt.close()
        
            
        plt.figure()
        sns.distplot(seats, kde=False, bins = [x for x in range(int(min(seats[0,:]))-1,int(max(seats[0,:]))+2)], color='gray',label = 'All Plans', norm_hist = True)
        sns.distplot(lwseats, kde=False, bins=[x for x in range(int(min(seats[0,:]))-1,int(max(seats[0,:]))+2)],color='green',label='Small Dislocation', norm_hist = True)
        sns.distplot(uwseats, kde=False, bins=[x for x in range(int(min(seats[0,:]))-1,int(max(seats[0,:]))+2)],color='orange',label='Large Dislocation', norm_hist = True)
        plt.legend()
        plt.savefig(newdir+"seats_comparison3all1_quad.png")

        plt.close()
            
        plt.figure()
        sns.distplot([x for x in lwseats], kde=False, bins=[x-.25 for x in range(int(min(seats[0,:]))-1,int(max(seats[0,:]))+2)],color='green',label='Small Dislocation',hist_kws={"rwidth":.25,"align":"left"})
        sns.distplot(seats, kde=False, bins = [x for x in range(int(min(seats[0,:]))-1,int(max(seats[0,:]))+2)], color='gray',label = 'All Plans',hist_kws={"rwidth":.25,"align":"left"})
        sns.distplot([x+1 for x in uwseats], kde=False, bins=[x+.25 for x in range(int(min(seats[0,:]))-1,int(max(seats[0,:]))+2)],color='orange',label='Large Dislocation',hist_kws={"rwidth":.25,"align":"left"})
        plt.legend()
        plt.savefig(newdir+"seats_comparison2all1sss_quad.png")

        plt.close()
            
        plt.figure()
        sns.distplot([x for x in lwseats], kde=False, bins=[x-.25 for x in range(int(min(seats[0,:]))-1,int(max(seats[0,:]))+2)],color='green', norm_hist = True, label='Small Dislocation',hist_kws={"rwidth":.25,"align":"left"})
        sns.distplot(seats, kde=False, bins = [x for x in range(int(min(seats[0,:]))-1,int(max(seats[0,:]))+2)], color='gray', norm_hist = True, label = 'All Plans',hist_kws={"rwidth":.25,"align":"left"})
        sns.distplot([x+1 for x in uwseats], kde=False, bins=[x+.25 for x in range(int(min(seats[0,:]))-1,int(max(seats[0,:]))+2)],color='orange', norm_hist = True, label='Large Dislocation',hist_kws={"rwidth":.25,"align":"left"})
        plt.legend()
        plt.savefig(newdir+"seats_comparison3all1sss_quad.png")

        plt.close()

        """
            
        lbound = np.percentile(qdlocs, 5)
        ubound = np.percentile(qdlocs, 95)
        
        #for i in range(max_steps):
        #    if
        
        lwseats = seats[(qdlocs<lbound)]    
        uwseats = seats[(qdlocs>ubound)]    
        
        plt.figure()
        sns.distplot(seats, kde=False, bins = [x for x in range(int(min(seats[0,:]))-1,int(max(seats[0,:]))+2)], color='gray',label = 'All Plans')
        sns.distplot(lwseats, kde=False, bins=[x for x in range(int(min(seats[0,:]))-1,int(max(seats[0,:]))+2)],color='green',label='Small Dislocation')
        plt.legend()
        plt.savefig(newdir+"seats_comparison2l5_quad.png")

        plt.close()
            
        
        plt.figure()
        sns.distplot(seats, kde=False, bins = [x for x in range(int(min(seats[0,:]))-1,int(max(seats[0,:]))+2)], color='gray',label = 'All Plans')
        sns.distplot(uwseats, kde=False, bins=[x for x in range(int(min(seats[0,:]))-1,int(max(seats[0,:]))+2)],color='orange',label='Large Dislocation')
        plt.legend()
        plt.savefig(newdir+"seats_comparison2u5_quad.png")

        plt.close()
            
        plt.figure()
        sns.distplot(seats, kde=False, bins = [x for x in range(int(min(seats[0,:]))-1,int(max(seats[0,:]))+2)], color='gray', norm_hist = True, label = 'All Plans')
        sns.distplot(lwseats, kde=False, bins=[x for x in range(int(min(seats[0,:]))-1,int(max(seats[0,:]))+2)],color='green', norm_hist = True, label='Small Dislocation')
        plt.legend()
        plt.savefig(newdir+"seats_comparison3l5_quad.png")

        plt.close()
            
        
        plt.figure()
        sns.distplot(seats, kde=False, bins = [x for x in range(int(min(seats[0,:]))-1,int(max(seats[0,:]))+2)], color='gray', norm_hist = True, label = 'All Plans')
        sns.distplot(uwseats, kde=False, bins=[x for x in range(int(min(seats[0,:]))-1,int(max(seats[0,:]))+2)],color='orange', norm_hist = True, label='Large Dislocation')
        plt.legend()
        plt.savefig(newdir+"seats_comparison3u5_quad.png")

        plt.close()
            
            
        plt.figure()
        sns.distplot(seats, kde=False, bins = [x-.15 for x in range(int(min(seats[0,:]))-1,int(max(seats[0,:]))+2)], color='gray',label = 'All Plans',hist_kws={"rwidth":.3,"align":"left"})
        sns.distplot([x+1 for x in lwseats], kde=False, bins=[x+.15 for x in range(int(min(seats[0,:]))-1,int(max(seats[0,:]))+2)],color='green',label='Small Dislocation',hist_kws={"rwidth":.3,"align":"left"})
        plt.legend()
        plt.savefig(newdir+"seats_comparison2l5ss_quad.png")

        plt.close()
            
        
        plt.figure()
        sns.distplot(seats, kde=False, bins = [x-.15 for x in range(int(min(seats[0,:]))-1,int(max(seats[0,:]))+2)], color='gray',label = 'All Plans',hist_kws={"rwidth":.3,"align":"left"})
        sns.distplot([x+1 for x in uwseats], kde=False, bins=[x+.15 for x in range(int(min(seats[0,:]))-1,int(max(seats[0,:]))+2)],color='orange',label='Large Dislocation',hist_kws={"rwidth":.3,"align":"left"})
        plt.legend()
        plt.savefig(newdir+"seats_comparison2u5ss_quad.png")

        plt.close()
            
        plt.figure()
        sns.distplot(seats, kde=False, bins = [x-.15 for x in range(int(min(seats[0,:]))-1,int(max(seats[0,:]))+2)], color='gray', norm_hist = True, label = 'All Plans',hist_kws={"rwidth":.3,"align":"left"})
        sns.distplot([x+1 for x in lwseats], kde=False, bins=[x+.15 for x in range(int(min(seats[0,:]))-1,int(max(seats[0,:]))+2)],color='green', norm_hist = True, label='Small Dislocation',hist_kws={"rwidth":.3,"align":"left"})
        plt.legend()
        plt.savefig(newdir+"seats_comparison3l5ss_quad.png")

        plt.close()
            
        
        plt.figure()
        sns.distplot(seats, kde=False, bins = [x-.15 for x in range(int(min(seats[0,:]))-1,int(max(seats[0,:]))+2)], color='gray', norm_hist = True, label = 'All Plans',hist_kws={"rwidth":.3,"align":"left"})
        sns.distplot([x+1 for x in uwseats], kde=False, bins=[x+.15 for x in range(int(min(seats[0,:]))-1,int(max(seats[0,:]))+2)],color='orange', norm_hist = True, label='Large Dislocation',hist_kws={"rwidth":.3,"align":"left"})
        plt.legend()
        plt.savefig(newdir+"seats_comparison3u5ss_quad.png")

        plt.close()
            
            
        plt.figure()
        sns.distplot(seats, kde=False, bins = [x for x in range(int(min(seats[0,:]))-1,int(max(seats[0,:]))+2)], color='gray',label = 'All Plans')
        sns.distplot(lwseats, kde=False, bins=[x for x in range(int(min(seats[0,:]))-1,int(max(seats[0,:]))+2)],color='green',label='Small Dislocation')
        sns.distplot(uwseats, kde=False, bins=[x for x in range(int(min(seats[0,:]))-1,int(max(seats[0,:]))+2)],color='orange',label='Large Dislocation')
        plt.legend()
        plt.savefig(newdir+"seats_comparison2all5_quad.png")

        plt.close()
        
            
        plt.figure()
        sns.distplot(seats, kde=False, bins = [x for x in range(int(min(seats[0,:]))-1,int(max(seats[0,:]))+2)], color='gray',label = 'All Plans', norm_hist = True)
        sns.distplot(lwseats, kde=False, bins=[x for x in range(int(min(seats[0,:]))-1,int(max(seats[0,:]))+2)],color='green',label='Small Dislocation', norm_hist = True)
        sns.distplot(uwseats, kde=False, bins=[x for x in range(int(min(seats[0,:]))-1,int(max(seats[0,:]))+2)],color='orange',label='Large Dislocation', norm_hist = True)
        plt.legend()
        plt.savefig(newdir+"seats_comparison3all5_quad.png")

        plt.close()
            
        plt.figure()
        sns.distplot([x for x in lwseats], kde=False, bins=[x-.25 for x in range(int(min(seats[0,:]))-1,int(max(seats[0,:]))+2)],color='green',label='Small Dislocation',hist_kws={"rwidth":.25,"align":"left"})
        sns.distplot(seats, kde=False, bins = [x for x in range(int(min(seats[0,:]))-1,int(max(seats[0,:]))+2)], color='gray',label = 'All Plans',hist_kws={"rwidth":.25,"align":"left"})
        sns.distplot([x+1 for x in uwseats], kde=False, bins=[x+.25 for x in range(int(min(seats[0,:]))-1,int(max(seats[0,:]))+2)],color='orange',label='Large Dislocation',hist_kws={"rwidth":.25,"align":"left"})
        plt.legend()
        plt.savefig(newdir+"seats_comparison2all5sss_quad.png")

        plt.close()
            
        plt.figure()
        sns.distplot([x for x in lwseats], kde=False, bins=[x-.25 for x in range(int(min(seats[0,:]))-1,int(max(seats[0,:]))+2)],color='green', norm_hist = True, label='Small Dislocation',hist_kws={"rwidth":.25,"align":"left"})
        sns.distplot(seats, kde=False, bins = [x for x in range(int(min(seats[0,:]))-1,int(max(seats[0,:]))+2)], color='gray', norm_hist = True, label = 'All Plans',hist_kws={"rwidth":.25,"align":"left"})
        sns.distplot([x+1 for x in uwseats], kde=False, bins=[x+.25 for x in range(int(min(seats[0,:]))-1,int(max(seats[0,:]))+2)],color='orange', norm_hist = True, label='Large Dislocation',hist_kws={"rwidth":.25,"align":"left"})
        plt.legend()
        plt.savefig(newdir+"seats_comparison3all5sss_quad.png")

        plt.close()
        
                   
        meds.append(np.percentile(qdlocs,50))
        p5.append(np.percentile(qdlocs,5))
        p25.append(np.percentile(qdlocs,25))
        p75.append(np.percentile(qdlocs,75))
        p95.append(np.percentile(qdlocs,95))
        mins.append(np.min(qdlocs))
        maxs.append(np.max(qdlocs))

        newdir = f"../../../Dropbox/dislocation_intermediate_files/Enacted_Stats/"

        with open(newdir + "Start_Values_"+str(state_fips)+".txt", "r") as f:
            for index, line in enumerate(f):
                if index == 19:
                #print(line[38:])
                    enacted.append(float(line[38:]))
        """

"""
newdir = f"../../../Dropbox/dislocation_intermediate_files/Enacted_Stats/"

plt.figure()

for i in range(len(meds)):
    plt.plot([i,i],[p5[i],p25[i]],'orange',linewidth=3)
    plt.plot([i,i],[p75[i],p95[i]],'orange',linewidth=3)
    plt.plot([i,i],[p25[i],p75[i]],'k',linewidth=6)
    plt.plot([i-.25,i+.25],[meds[i],meds[i]],'lime',linewidth=3)
plt.legend()
plt.xticks(range(len(meds)),names,rotation=90,fontsize=6)
plt.savefig(newdir+"compare_dislocations_quad.png")
plt.close()

plt.figure()
for i in range(len(meds)):
    plt.plot([i,i],[p5[i],mins[i]],'red',linewidth=1)
    plt.plot([i,i],[p95[i],maxs[i]],'red',linewidth=1)
    plt.plot([i,i],[p5[i],p25[i]],'orange',linewidth=3)
    plt.plot([i,i],[p75[i],p95[i]],'orange',linewidth=3)
    plt.plot([i,i],[p25[i],p75[i]],'k',linewidth=6)
    plt.plot([i-.25,i+.25],[meds[i],meds[i]],'lime',linewidth=3)
plt.legend()
plt.xticks(range(len(meds)),names,rotation=90,fontsize=6)
plt.savefig(newdir+"compare_dislocations_mm_quad.png")
plt.close()

plt.figure()

for i in range(len(meds)):
    plt.plot([i,i],[p5[i],p25[i]],'orange',linewidth=3)
    plt.plot([i,i],[p75[i],p95[i]],'orange',linewidth=3)
    plt.plot([i,i],[p25[i],p75[i]],'k',linewidth=6)
    plt.plot([i-.25,i+.25],[meds[i],meds[i]],'lime',linewidth=3)
    plt.plot([i],[enacted[i]],'o',color='magenta', markersize=4)
plt.plot([],[],'g',label='Median')
plt.plot([],[],'o',color='magenta',label='Enacted')
plt.legend()
plt.xticks(range(len(meds)),names,rotation=90,fontsize=6)
plt.savefig(newdir+"compare_dislocations_e_quad.png")
plt.close()

plt.figure()
for i in range(len(meds)):
    plt.plot([i,i],[p5[i],mins[i]],'red',linewidth=1)
    plt.plot([i,i],[p95[i],maxs[i]],'red',linewidth=1)
    plt.plot([i,i],[p5[i],p25[i]],'orange',linewidth=3)
    plt.plot([i,i],[p75[i],p95[i]],'orange',linewidth=3)
    plt.plot([i,i],[p25[i],p75[i]],'k',linewidth=6)
    plt.plot([i-.25,i+.25],[meds[i],meds[i]],'lime',linewidth=3)
    plt.plot([i],[enacted[i]],'o',color='magenta', markersize=4)
plt.plot([],[],'g',label='Median')
plt.plot([],[],'o',color='magenta',label='Enacted')
plt.legend()
plt.xticks(range(len(meds)),names,rotation=90,fontsize=6)
plt.savefig(newdir+"compare_dislocations_mm_e_quad.png")
plt.close()
"""







