#!/bin/bash

#SBATCH --mail-user=nick@nickeubank.com  # email address
#SBATCH --mail-type=ALL  # Alerts sent when job begins, ends, or aborts
#SBATCH --ntasks=1
#SBATCH --mem-per-cpu=10G
#SBATCH --job-name=gerrychain_allbutflca
#SBATCH --array=0-8,12-23,27-143
#SBATCH --time=03-00:00:00  # Wall Clock time (dd-hh:mm:ss) [max of 14 days]
#SBATCH --output=slurm_reports/slurm_reports_%A_%a.output  # output and error messages go to this file

export STATE_RUN=$SLURM_ARRAY_TASK_ID

python 20_run_simulation.py
