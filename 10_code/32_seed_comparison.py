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

ts = [x * step_size for x in range(1, int(max_steps / step_size) + 1)]


burn = 0
sub_sample = 1



for state_fips in fips_list:

    datadir1 = f"../../../Dropbox/US_Ensembles/{state_fips}_run0/"
    datadir2 = f"../../../Dropbox/US_Ensembles/{state_fips}_run1/"
    datadir3 = f"../../../Dropbox/US_Ensembles/{state_fips}_run2/"
    
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
                datadir1 + election_names[elect] + "_" + str(t) + ".csv", delimiter=","
            )
            for s in range(step_size):
                a.append(tempvotes[s, :])

            tempvotes = np.loadtxt(
                datadir2 + election_names[elect] + "_" + str(t) + ".csv", delimiter=","
            )
            for s in range(step_size):
                b.append(tempvotes[s, :])

            tempvotes = np.loadtxt(
                datadir3 + election_names[elect] + "_" + str(t) + ".csv", delimiter=","
            )
            for s in range(step_size):
                c.append(tempvotes[s, :])

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

