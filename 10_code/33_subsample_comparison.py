# 
import os

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
sns.set_style('white')

# sns.set_style('darkgrid')
#sns.set_style("darkgrid", {"axes.facecolor": ".97"})


def draw_plot(data, offset, edge_color, fill_color):
    pos = 10*np.arange(data.shape[1])+offset
    #bp = ax.boxplot(data, positions= pos, widths=0.3, patch_artist=True, manage_xticks=False)
    bp = ax.boxplot(data, positions= pos,widths=.5, whis=[1,99],showfliers=False, patch_artist=True, zorder = 4) #backwards compatible#manage_ticks=False,zorder=4)
    for element in ['boxes', 'whiskers', 'medians', 'caps']:
        plt.setp(bp[element], color=edge_color,zorder=4)
    for patch in bp['boxes']:
        patch.set(facecolor=fill_color,zorder=0)



num_elections = 1


election_names = [
    "PRES2008"]

election_columns = [["P2008_D",  "P2008_R"]]

fips_list = ['01']

fips_list = ['01']

plan_name = "Enacted"




num_districts = 7 #replace this with length of vote vector

max_steps = 100000
step_size = 10000


burn = 1000

subsample = 100

ts = [x * step_size for x in range(1, int(max_steps / step_size) + 1)]


burn = 0
sub_sample = 1



for state_fips in fips_list:
    for run_num in ['0','1','2']:

    datadir = f"../../../Dropbox/US_Ensembles/{state_fips}_run{run_num}/"
    
    newdir = f"../20_intermediate_files/initial_chain_plots/{state_fips}_comparison/"


    os.makedirs(os.path.dirname(newdir + "init.txt"), exist_ok=True)
    with open(newdir + "init.txt", "w") as f:
        f.write("Created Folder")





    for elect in range(num_elections):
        a = []
        b = []
        c = []
        for t in ts:
            tempvotes = np.loadtxt(
                datadir + election_names[elect] + "_" + str(t) + ".csv", delimiter=","
            )
            for s in range(step_size):
                a.append(tempvotes[s, :])


        a = np.array(a)
        b = np.array(b)
        c = np.array(c)
        
        a=a[:,burn::sub_sample]

        #medianprops = dict(color="black")

        fig, ax = plt.subplots()
        draw_plot(a, -2, 'r', 'None')
        draw_plot(b, 0, 'y', 'None')
        draw_plot(c, 2, 'b', 'None')

        plt.plot([], [], color='r', label='Seed 0')
        plt.plot([], [], color='y', label='Seed 1')
        plt.plot([], [], color='b', label='Seed 2')

        plt.legend()

        #plt.xticks([5,10,15,20,25,30],[5,10,15,20,25,30])
        plt.xticks([],[])
        #plt.xlim([.5,34])
        plt.xlabel("Indexed Districts")
        plt.ylabel("BVAP %")

        plt.legend()

        plt.savefig(newdir +"seed_compare.png")
        fig = plt.gcf()
        fig.set_size_inches((12,8), forward=False)
        fig.savefig(newdir +"seed_compare2.png", dpi=500)
        plt.close()
        
        a = []
        b = []
        c = []
        
        cuts1 = np.zeros([1, max_steps])
        cuts2 = np.zeros([1, max_steps])
        cuts3 = np.zeros([1, max_steps])
        
        for t in ts:
            temp = np.loadtxt(datadir1 + "cuts" + str(t) + ".csv", delimiter=",")
            cuts1[0, t - step_size  : t] = temp
            temp = np.loadtxt(datadir2 + "cuts" + str(t) + ".csv", delimiter=",")
            cuts2[0, t - step_size  : t] = temp
            temp = np.loadtxt(datadir3 + "cuts" + str(t) + ".csv", delimiter=",")
            cuts3[0, t - step_size  : t] = temp
            
         
            
        cuts1 = cuts1[burn::sub_sample]
        cuts2 = cuts2[burn::sub_sample]
        cuts3 = cuts3[burn::sub_sample]
        
        sns.distplot(cuts1[0, :], kde=False, color="blue")
        sns.distplot(cuts2[0, :], kde=False, color="yellow")
        sns.distplot(cuts3[0, :], kde=False, color="red")
        
        #plt.axvline(x=1402, color="orange", label="Enacted")
        plt.axvline(x=np.mean(cuts1[0, :]), color="b", label="Ensemble 1 Mean")
        plt.axvline(x=np.mean(cuts2[0, :]), color="y", label="Ensemble 2 Mean")
        plt.axvline(x=np.mean(cuts3[0, :]), color="r", label="Ensemble 3 Mean")
        plt.legend()
        # plt.xlim([400,800])
        plt.ylabel("Frequency")
        plt.xlabel("# Cut Edges")
        plt.savefig(newdir + "cut_hist.png")
        plt.close()

        cuts1 = []
        cuts2 = []
        cuts3 = []

        egs1 = np.zeros([1, max_steps])
        egs2 = np.zeros([1, max_steps])
        egs3 = np.zeros([1, max_steps])
        
        for t in ts:
            temp = np.loadtxt(datadir1 + "egs" + str(t) + ".csv", delimiter=",")
            egs1[0, t - step_size  : t] = temp
            temp = np.loadtxt(datadir2 + "egs" + str(t) + ".csv", delimiter=",")
            egs2[0, t - step_size  : t] = temp
            temp = np.loadtxt(datadir3 + "egs" + str(t) + ".csv", delimiter=",")
            egs3[0, t - step_size  : t] = temp
            
         
            
        egs1 = egs1[burn::sub_sample]
        egs2 = egs2[burn::sub_sample]
        egs3 = egs3[burn::sub_sample]
        
        sns.distplot(egs1[0, :], kde=False, color="blue")
        sns.distplot(egs2[0, :], kde=False, color="yellow")
        sns.distplot(egs3[0, :], kde=False, color="red")
        
        #plt.axvline(x=1402, color="orange", label="Enacted")
        plt.axvline(x=np.mean(egs1[0, :]), color="b", label="Ensemble 1 Mean")
        plt.axvline(x=np.mean(egs2[0, :]), color="y", label="Ensemble 2 Mean")
        plt.axvline(x=np.mean(egs3[0, :]), color="r", label="Ensemble 3 Mean")
        plt.legend()
        # plt.xlim([400,800])
        plt.ylabel("Frequency")
        plt.xlabel("Efficiency Gap")
        plt.savefig(newdir + "egs_hist.png")
        plt.close()

        egs1 = []
        egs2 = []
        egs3 = []

        mms1 = np.zeros([1, max_steps])
        mms2 = np.zeros([1, max_steps])
        mms3 = np.zeros([1, max_steps])
        
        for t in ts:
            temp = np.loadtxt(datadir1 + "mms" + str(t) + ".csv", delimiter=",")
            mms1[0, t - step_size  : t] = temp
            temp = np.loadtxt(datadir2 + "mms" + str(t) + ".csv", delimiter=",")
            mms2[0, t - step_size  : t] = temp
            temp = np.loadtxt(datadir3 + "mms" + str(t) + ".csv", delimiter=",")
            mms3[0, t - step_size  : t] = temp
            
         
            
        mms1 = mms1[burn::sub_sample]
        mms2 = mms2[burn::sub_sample]
        mms3 = mms3[burn::sub_sample]
        
        sns.distplot(mms1[0, :], kde=False, color="blue")
        sns.distplot(mms2[0, :], kde=False, color="yellow")
        sns.distplot(mms3[0, :], kde=False, color="red")
        
        #plt.axvline(x=1402, color="orange", label="Enacted")
        plt.axvline(x=np.mean(mms1[0, :]), color="b", label="Ensemble 1 Mean")
        plt.axvline(x=np.mean(mms2[0, :]), color="y", label="Ensemble 2 Mean")
        plt.axvline(x=np.mean(mms3[0, :]), color="r", label="Ensemble 3 Mean")
        plt.legend()
        # plt.xlim([400,800])
        plt.ylabel("Frequency")
        plt.xlabel("Mean Median")
        plt.savefig(newdir + "mms_hist.png")
        plt.close()

        mms1 = []
        mms2 = []
        mms3 = []
        
        pbs1 = np.zeros([1, max_steps])
        pbs2 = np.zeros([1, max_steps])
        pbs3 = np.zeros([1, max_steps])
        
        for t in ts:
            temp = np.loadtxt(datadir1 + "pbs" + str(t) + ".csv", delimiter=",")
            pbs1[0, t - step_size  : t] = temp
            temp = np.loadtxt(datadir2 + "pbs" + str(t) + ".csv", delimiter=",")
            pbs2[0, t - step_size  : t] = temp
            temp = np.loadtxt(datadir3 + "pbs" + str(t) + ".csv", delimiter=",")
            pbs3[0, t - step_size  : t] = temp
            
         
            
        pbs1 = pbs1[burn::sub_sample]
        pbs2 = pbs2[burn::sub_sample]
        pbs3 = pbs3[burn::sub_sample]
        
        sns.distplot(pbs1[0, :], kde=False, color="blue")
        sns.distplot(pbs2[0, :], kde=False, color="yellow")
        sns.distplot(pbs3[0, :], kde=False, color="red")
        
        #plt.axvline(x=1402, color="orange", label="Enacted")
        plt.axvline(x=np.mean(pbs1[0, :]), color="b", label="Ensemble 1 Mean")
        plt.axvline(x=np.mean(pbs2[0, :]), color="y", label="Ensemble 2 Mean")
        plt.axvline(x=np.mean(pbs3[0, :]), color="r", label="Ensemble 3 Mean")
        plt.legend()
        # plt.xlim([400,800])
        plt.ylabel("Frequency")
        plt.xlabel("Partisan Bias")
        plt.savefig(newdir + "pbs_hist.png")
        plt.close()

        pbs1 = []
        pbs2 = []
        pbs3 = []
        
        pgs1 = np.zeros([1, max_steps])
        pgs2 = np.zeros([1, max_steps])
        pgs3 = np.zeros([1, max_steps])
        
        for t in ts:
            temp = np.loadtxt(datadir1 + "pgs" + str(t) + ".csv", delimiter=",")
            pgs1[0, t - step_size  : t] = temp
            temp = np.loadtxt(datadir2 + "pgs" + str(t) + ".csv", delimiter=",")
            pgs2[0, t - step_size  : t] = temp
            temp = np.loadtxt(datadir3 + "pgs" + str(t) + ".csv", delimiter=",")
            pgs3[0, t - step_size  : t] = temp
            
         
            
        pgs1 = pgs1[burn::sub_sample]
        pgs2 = pgs2[burn::sub_sample]
        pgs3 = pgs3[burn::sub_sample]
        
        sns.distplot(pgs1[0, :], kde=False, color="blue")
        sns.distplot(pgs2[0, :], kde=False, color="yellow")
        sns.distplot(pgs3[0, :], kde=False, color="red")
        
        #plt.axvline(x=1402, color="orange", label="Enacted")
        plt.axvline(x=np.mean(pgs1[0, :]), color="b", label="Ensemble 1 Mean")
        plt.axvline(x=np.mean(pgs2[0, :]), color="y", label="Ensemble 2 Mean")
        plt.axvline(x=np.mean(pgs3[0, :]), color="r", label="Ensemble 3 Mean")
        plt.legend()
        # plt.xlim([400,800])
        plt.ylabel("Frequency")
        plt.xlabel("Partisan Gini")
        plt.savefig(newdir + "pgs_hist.png")
        plt.close()

        pgs1 = []
        pgs2 = []
        pgs3 = []
        
        hmss1 = np.zeros([1, max_steps])
        hmss2 = np.zeros([1, max_steps])
        hmss3 = np.zeros([1, max_steps])
        
        for t in ts:
            temp = np.loadtxt(datadir1 + "hmss" + str(t) + ".csv", delimiter=",")
            hmss1[0, t - step_size  : t] = temp
            temp = np.loadtxt(datadir2 + "hmss" + str(t) + ".csv", delimiter=",")
            hmss2[0, t - step_size  : t] = temp
            temp = np.loadtxt(datadir3 + "hmss" + str(t) + ".csv", delimiter=",")
            hmss3[0, t - step_size  : t] = temp
            
         
            
        hmss1 = hmss1[burn::sub_sample]
        hmss2 = hmss2[burn::sub_sample]
        hmss3 = hmss3[burn::sub_sample]
        
        sns.distplot(hmss1[0, :],bins=[x-.25 for x in range(int(min(hmss1[0, :]))-1,int(max(hmss1[0, :]))+2)],hist_kws={"rwidth":.2,"align":"left"}, kde=False, color="blue")
        sns.distplot(hmss2[0, :],bins=[x for x in range(int(min(hmss2[0, :]))-1,int(max(hmss2[0, :]))+2)],hist_kws={"rwidth":.2,"align":"left"}, kde=False, color="yellow")
        sns.distplot([x+1 for x in hmss3[0, :]],bins=[x+.25 for x in range(int(min(hmss3[0, :]))-1,int(max(hmss3[0, :]))+2)],hist_kws={"rwidth":.2,"align":"left"}, kde=False, color="red")
        
        #plt.axvline(x=1402, color="orange", label="Enacted")
        plt.axvline(x=np.mean(hmss1[0, :]), color="b", label="Ensemble 1 Mean")
        plt.axvline(x=np.mean(hmss2[0, :]), color="y", label="Ensemble 2 Mean")
        plt.axvline(x=np.mean(hmss3[0, :]), color="r", label="Ensemble 3 Mean")
        plt.legend()
        # plt.xlim([400,800])
        plt.ylabel("Frequency")
        plt.xlabel("Dem Seats")
        plt.savefig(newdir + "hmss_hist.png")
        plt.close()

        hmss1 = []
        hmss2 = []
        hmss3 = []