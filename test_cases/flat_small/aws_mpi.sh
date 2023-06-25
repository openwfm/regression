#!/bin/bash
# based on templates/aws_mpi.sh
#SBATCH --job-name=flat_625_sim
#SBATCH --partition=compute
#SBATCH --time=2:00:00                    # Max wall-clock time
#SBATCH --ntasks=16                       # Total number of MPI processe

rm -f rsl.*
mpirun -np 1 ideal.exe
mpirun wrf.exe 
