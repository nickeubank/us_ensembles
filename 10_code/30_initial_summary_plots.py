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
        '11',
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
    for run in ['0','1','2']:
        
        datadir = f"../../../Dropbox/dislocation_intermediate_files/100_ensembles/{state_fips}_run{run}/"        
        newdir = f"../../../Dropbox/dislocation_intermediate_files/100_ensembles/{state_fips}_run{run}/Plots/"
        
        os.makedirs(os.path.dirname(newdir + "init.txt"), exist_ok=True)
        with open(newdir + "init.txt", "w") as f:
            f.write("Created Folder")
        

        
        cuts = np.zeros([1, max_steps])
        
        for t in ts:
            temp = np.loadtxt(datadir + "cuts" + str(t) + ".csv", delimiter=",")
            cuts[0, t - step_size  : t] = temp
            
         
            
        cuts = cuts[burn::sub_sample]
        
        
        plt.plot(cuts[0, :])
        
        plt.plot(
            [0, max_steps],
            [np.mean(cuts[0, :]), np.mean(cuts[0, :])],
            color="g",
            label="Ensemble Mean",
        )
        
        plt.ylabel("# Cut Edges")
        plt.xlabel("Step")
        plt.legend()
        plt.savefig(newdir + "cut_trace.png")
        plt.close()
            

        sns.distplot(cuts[0, :], kde=False, color="gray")
        
        #plt.axvline(x=1402, color="orange", label="Enacted")
        plt.axvline(x=np.mean(cuts[0, :]), color="g", label="Ensemble Mean")
        plt.legend()
        # plt.xlim([400,800])
        plt.ylabel("Frequency")
        plt.xlabel("# Cut Edges")
        plt.savefig(newdir + "cut_hist.png")
        plt.close()

        cuts = []
        
        egs = np.zeros([num_elections, max_steps])
        pbs = np.zeros([num_elections, max_steps])
        pgs = np.zeros([num_elections, max_steps])  
        hmss = np.zeros([num_elections, max_steps])
        mms = np.zeros([num_elections, max_steps])           
                        

        for t in ts:
            temp = np.loadtxt(datadir + "egs" + str(t) + ".csv", delimiter=",")
            egs[:, t - step_size : t] = temp.T
            temp = np.loadtxt(datadir + "pgs" + str(t) + ".csv", delimiter=",")
            pgs[:, t - step_size : t] = temp.T
            temp = np.loadtxt(datadir + "pbs" + str(t) + ".csv", delimiter=",")
            pbs[:, t - step_size : t] = temp.T
            temp = np.loadtxt(datadir + "hmss" + str(t) + ".csv", delimiter=",")
            hmss[:, t - step_size : t] = temp.T
            temp = np.loadtxt(datadir + "mms" + str(t) + ".csv", delimiter=",")
            mms[:, t - step_size : t] = temp.T


        egs = egs[burn::sub_sample]
        pgs = pgs[burn::sub_sample]
        pbs = pbs[burn::sub_sample]
        hmss = hmss[burn::sub_sample]
        mms = mms[burn::sub_sample]
            
        for j in range(num_elections):
        
            plt.plot(egs[j, :])
            plt.plot(
                [0, max_steps],
                [np.mean(egs[j, :]), np.mean(egs[j, :])],
                color="g",
                label="Ensemble Mean",
            )
            plt.title(plan_name + "Plan" + election_names[j])
            # plt.axhline(y=.104,color='orange',label="Enacted")
            plt.ylabel("Efficiency Gap")
            plt.xlabel("Step")
            plt.legend()
            plt.savefig(newdir + election_names[j] + "eg_trace.png")
            plt.close()
        
            sns.distplot(np.negative(egs[j, :]), bins=1000, kde=False, color="gray",hist_kws={"alpha":.99})
            plt.title(plan_name + "Plan" + election_names[j])
            #plt.axvline(x=regs[j], color="orange", label="Remedial")
            plt.axvline(x=-np.mean(egs[j, :]), color="g", label="Ensemble Mean")
            plt.ylabel("Frequency")
            plt.xlabel("Efficiency Gap")
            # plt.xlim([-.15,.25])
            # plt.plot([],[],color='green',label='Ensemble Mean')
            # plt.plot([],[],color='red',label='Enacted')
            plt.legend()
            plt.savefig(newdir + election_names[j] + "eg_hist.png")
        
            plt.close()
        
            plt.plot(mms[j, :])
            #plt.plot([0, max_steps], [-rmms[j], -rmms[j]], color="orange", label="Remedial")
            plt.plot(
                [0, max_steps],
                [np.mean(mms[j, :]), np.mean(mms[j, :])],
                color="g",
                label="Ensemble Mean",
            )
            # plt.title(plan_name + "Plan" + election_names[j])
            plt.ylabel("Mean-Median")
            plt.xlabel("Step")
            plt.legend()
            plt.savefig(newdir + election_names[j] + "mm_trace.png")
            plt.close()
        
            sns.distplot(np.negative(mms[j, :]), bins=400, kde=False, color="gray")
            plt.title(plan_name + "Plan" + election_names[j])
            #plt.axvline(x=rmms[j], color="orange", label="Remedial")
            plt.axvline(x=-np.mean(mms[j, :]), color="g", label="Ensemble Mean")
            plt.ylabel("Frequency")
            plt.xlabel("Mean-Median")
            # plt.xlim([-.06,.06])
            # plt.plot([],[],color='green',label='Ensemble Mean')
            # plt.plot([],[],color='red',label='Initial Value')
            plt.legend()
            plt.savefig(newdir + election_names[j] + "mm_hist.png")
            plt.close()
        
            plt.plot(hmss[j, :])
            #plt.plot([0, max_steps], [ehmss[j], ehmss[j]], color="purple", label="2011")
            #plt.plot([0, max_steps], [rhmss[j], rhmss[j]], color="orange", label="Remedial")
            plt.plot(
                [0, max_steps],
                [np.mean(hmss[j, :]), np.mean(hmss[j, :])],
                color="g",
                label="Ensemble Mean",
            )
            # plt.axhline(y=hmss[j,0],color='orange',label="SM-Cong")
            # plt.title(plan_name + "Plan" + election_names[j])
            plt.ylabel("# Dem Seats")
            plt.xlabel("Step")
            plt.legend()
            plt.savefig(newdir + election_names[j] + "seats_trace.png")
            plt.close()
        
            fig1 = plt.figure()
            ax1 = fig1.add_subplot(111)
            # sns.distplot(hmss[j,:],kde=False,color='gray',bins=list(range(4,10)),hist_kws={"rwidth":.8,"align":"left"})
            sns.distplot(hmss[j, :], bins = [x for x in range(int(min(hmss[j, :]))-1,int(max(hmss[j, :]))+2)], kde=False, color="gray")
            plt.title(plan_name + "Plan" + election_names[j])
            #plt.axvline(x=rhmss[j], color="orange", label="Remedial")
            plt.axvline(x=np.mean(hmss[j, :]), color="g", label="Ensemble Mean")
            # plt.plot([],[],color='green',label='Ensemble Mean')
            # plt.plot([],[],color='red',label='Initial Value')
            # plt.xlim([4,10])
            # plt.xticks(list(range(4,11)))
            # ax1.set_xticklabels([str(x) for x in range(4,11)])
            plt.ylabel("Frequency")
            plt.xlabel("# Dem Seats")
            plt.legend()
            plt.savefig(newdir + election_names[j] + "seats_hist.png")
            plt.close()



            #egs = []
            #pbs = []
            #pgs = [] 
            #hmss = []
            #mms = []


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
            
            a=a[:,burn::sub_sample]
            medianprops = dict(color="black")
        
            fig1 = plt.figure()
            ax1 = fig1.add_subplot(111)
            # ax1.add_patch(patches.Rectangle((0, .37), 35, .18,color='honeydew'))
            # plt.plot([0,34], [.55, .55], 'lightgreen')
            # plt.plot([0,34], [.37, .37], 'lightgreen')

            plt.boxplot(
                a,
                whis=[1, 99],
                showfliers=False,
                patch_artist=True,
                boxprops=dict(facecolor="None", color=c),
                capprops=dict(color=c),
                whiskerprops=dict(color=c),
                flierprops=dict(color=c, markeredgecolor=c),
                medianprops=dict(color=c),
            )
            
            plt.ylabel("Dem %")
            plt.ylim([0.25, 0.95])
        
            plt.axhline(.5, color="green", label="50%")
            # plt.plot([],[],color=c,label="ReCom Ensemble")
        
            # fig, ax = plt.subplots()
            # draw_plot(a, 1, "black", "white")
            # plt.xticks(range(1,num_districts+1))
            # plt.plot(range(1,num_districts+1),a[0,:],'o',color='r',label='Initial Plan', markersize=3)
            # plt.plot([1,num_districts+1],[np.mean(a[0,:]),np.mean(a[0,:])],color='blue',label='Initial Mean')
            # plt.plot([1,num_districts+1],[np.median(a[0,:]),np.median(a[0,:])],color='yellow',label='Initial Median')
        
            plt.xlabel("Sorted Districts")
            plt.legend()
            plt.savefig(newdir + election_names[elect] + "_box.png")
            fig = plt.gcf()
            fig.set_size_inches((12, 6), forward=False)
            fig.savefig(newdir + election_names[elect] + "_box2.png", dpi=600)
        
            plt.close()



        with open(newdir + "Average_Values.txt", "w") as f:
            f.write("Values for Starting Plan: " + plan_name + " \n\n")

            f.write("\n")
            f.write("\n")
            for elect in range(num_elections):
                print(elect)

                f.write(election_names[elect] + " Initial Mean-Median: " + str(mms[ 0]))

                f.write("\n")
                f.write("\n")
                f.write(
                    election_names[elect]
                    + " Average Mean-Median: "
                    + str(np.mean(mms[elect, :]))
                )

                f.write("\n")
                f.write("\n")
                f.write(
                    election_names[elect]
                    + " Number Mean-Median Higher: "
                    + str((mms[elect, :] > mms[elect, 0]).sum())
                )

                f.write("\n")
                f.write("\n")

                f.write("\n")
                f.write("\n")

                f.write(
                    election_names[elect] + " Initial Efficiency Gap: " + str(egs[ 0])
                )

                f.write("\n")
                f.write("\n")
                f.write(
                    election_names[elect]
                    + " Average Efficiency Gap: "
                    + str(np.mean(egs[elect, :]))
                )

                f.write("\n")
                f.write("\n")
                f.write(
                    election_names[elect]
                    + " Number Efficiency Gap Higher: "
                    + str((egs[elect, :] > egs[ 0]).sum())
                )

                f.write("\n")
                f.write("\n")

                f.write("\n")
                f.write("\n")

                f.write(election_names[elect] + " Initial Dem Seats: " + str(hmss[ 0]))

                f.write("\n")
                f.write("\n")
                f.write(
                    election_names[elect]
                    + " Average Dem Seats: "
                    + str(np.mean(hmss[elect, :]))
                )

                f.write("\n")
                f.write("\n")
                f.write(
                    election_names[elect]
                    + " Number Dem Seats Higher: "
                    + str((hmss[elect, :] > hmss[ 0]).sum())
                )

                f.write("\n")
                f.write("\n")

                f.write("\n")
                f.write("\n")
         
