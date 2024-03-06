#!/data/jdas/anaconda3/bin/python3

from multiprocessing import Process, Value, Array
from multiprocessing import Pool
from functools import partial
import concurrent.futures
import subprocess
import itertools
import numpy as np
import math
import sys
import os

os.system("source /data/jroy/.bashrc_jerk")

fil_file = str(input("Give the input filterbank file:"))
start_DM = str(input("Give the value of start DM:"))
end_DM = str(input("Give the value of end DM:"))
low_period = float(input("Lowest candidate period you will consider in ms:"))
high_period = float(input("Highest candidate period you will consider in ms:"))
dm_step = float(input("Give the step size of dedispersion(equal or grater than 0.01):"))
r_tol = float(input("How many r bin shift you want to consider for same candidate:"))
num_dm = int(input("How many dms in one prepsubband command(multiples of 10 and maximum 100):"))
total_obs_time = np.float64(input("Give total observation time in seconds:"))
sampling_time = np.float64(input("Give sampling time in us:"))
workers = int(input("Give how many CPUs you want to use:"))
DM_filtering_cut = int(input("Give at how many DMs the candidate must show up to consider it as a candidate:"))
accel_bin0 = int(input("Give the integer value of zmax(maximum accel bin or zmax allowed values are 0, 50, and 200):"))
search_type = float(input("For pulsar search from begenning give 0 as input and for only sorting and folding the candidates give anything except 0 as input:"))

if accel_bin0 == 0:
    accel_bin = str(0)
elif accel_bin0 == 50:
    accel_bin = str(40)
elif accel_bin0 == 200:
    accel_bin = str(200)
else:
    print("Entered zmax value is not allowed due to laziness issue.")
    sys.exit()

file_name = fil_file.replace(".fil", "")

samp_time = sampling_time/1000000.0

#Inside this error lavel we will consider the candidates to be the same one.
z_tol = 1.0

N0 = int(math.floor((np.float64(end_DM)-np.float64(start_DM))/dm_step))
N = str(N0)

numout0 = int(total_obs_time/samp_time)
if (numout0 % 2) == 0:
    numout = str(numout0 - 2)
else:
    numout = str(numout0 - 1)

dm = np.linspace(np.float64(start_DM),np.float64(end_DM),N0,endpoint=False)
dm1 = []
for i in range(0,int(len(dm))):
    dm1.append("{:.2f}".format(dm[i]))
DM = np.array(dm1, dtype = str)

def ddp(string):
    os.system(string)

def fft(string):
    os.system(string)

def accelsearch(string):
    os.system(string)

def folding(string):
    os.system(string)

def consecutive(data, stepsize = 1):
    return np.split(data, np.where(np.diff(data) != stepsize)[0] + 1)

def sorting_folding(file_name, DM, accel_bin, workers, DM_filtering_cut, r_tol, low_period, high_period):
    for m in range(0, 1000):
        if (1000*i + m) < len(dm):
            with open(file_name + "_DM" + DM[1000*i + m] + "_ACCEL_" + accel_bin) as f:
                lines = f.readlines()
            b = int(lines.index('------------------------------------------------------------------------------------------------------------------------------------------------------------------------\n'))
            cand_len.append(b)
    #print("Total number of candidates before filtering: ", sum(cand_len))
    os.system("sleep 5")

    max_cand_len = int(max(cand_len))

    if len(dm) < 1000:
        Sigma_array = np.empty((int(len(dm)), max_cand_len))
        Sigma_array[:] = np.nan

        Periodicity_array = np.empty((int(len(dm)), max_cand_len))
        Periodicity_array[:] = np.nan

        r_bin_array = np.empty((int(len(dm)), max_cand_len))
        r_bin_array[:] = np.nan

        z_bin_array = np.empty((int(len(dm)), max_cand_len))
        z_bin_array[:] = np.nan

    else:
        Sigma_array = np.empty((1000, max_cand_len))
        Sigma_array[:] = np.nan

        Periodicity_array = np.empty((1000, max_cand_len))
        Periodicity_array[:] = np.nan

        r_bin_array = np.empty((1000, max_cand_len))
        r_bin_array[:] = np.nan

        z_bin_array = np.empty((1000, max_cand_len))
        z_bin_array[:] = np.nan

    for m in range(0, 1000):
        if (1000*i + m) < len(dm):
            with open(file_name + "_DM" + DM[1000*i + m] + "_ACCEL_" + accel_bin) as f:
                lines = f.readlines()
            b = int(lines.index('------------------------------------------------------------------------------------------------------------------------------------------------------------------------\n'))
            for j in range(3, b-4):
                lines0 = lines[j].split(" ")
                lines1 = list(itertools.filterfalse(lambda x: x == "", lines0))
                Sigma_array[m][j] = float(lines1[1])
                Periodicity_array[m][j] = float(lines1[5].split("(")[0])
                r_bin_array[m][j] = float(lines1[7].split("(")[0])
                z_bin_array[m][j] = float(lines1[9].split("(")[0])

        else:
            continue

    #Flatten r_bin, z_bin array to find the redundent periodicity.
    r_bin_flatten = r_bin_array.flatten()
    z_bin_flatten = z_bin_array.flatten()

    '''
    if len(dm) < 1000:
        r_z_bin_flatten_array = np.empty((int(len(dm))*max_cand_len, 2))
        r_z_bin_flatten_array[:] = np.nan

        for i in range(0, int(len(dm))*max_cand_len):
            r_z_bin_flatten_array[i][0] = r_bin_flatten[i]
            r_z_bin_flatten_array[i][1] = z_bin_flatten[i]

    else:
        r_z_bin_flatten_array = np.empty((1000*max_cand_len, 2))
        r_z_bin_flatten_array[:] = np.nan

        for i in range(0, 1000*max_cand_len):
            r_z_bin_flatten_array[i][0] = r_bin_flatten[i]
            r_z_bin_flatten_array[i][1] = z_bin_flatten[i]
    '''

    filtered_r_bin_list0 = [x for x in np.unique(r_bin_flatten) if str(x) != 'nan']
    uniq_r_bin_list0 = []
    d = int(len(filtered_r_bin_list0))

    for m in range(0, d):
        if (len(filtered_r_bin_list0) > 0):
            indices = np.where(filtered_r_bin_list0 <= (filtered_r_bin_list0[0] + r_tol))
            uniq_r_bin_list0.append(filtered_r_bin_list0[0])
            filtered_r_bin_list0 = np.delete(filtered_r_bin_list0, indices[0])
        else:
            continue

    if len(dm) < 1000:
        Filtered_Sigma_array = np.empty((int(len(dm)), max_cand_len))

    else:
        Filtered_Sigma_array = np.empty((1000, max_cand_len))

    for k in range(1, int(len(uniq_r_bin_list0))):
        index = np.where((r_bin_array > uniq_r_bin_list0[k-1] + r_tol) & (r_bin_array <= uniq_r_bin_list0[k] + r_tol))
        DM_index = index[0]
        cand_index = index[1]

        Consecutive_DM_array = consecutive(DM_index)

        for p in range(0, int(len(Consecutive_DM_array))):
            #print(Consecutive_DM_array)
            if len(Consecutive_DM_array[p]) >= DM_filtering_cut:
                Filtered_Sigma_array[:] = np.nan

                for l in range(0, int(len(Consecutive_DM_array[p]))):
                    cand_index_pos = np.where(DM_index == Consecutive_DM_array[p][l])
                    for m in range(0, int(len(cand_index_pos))):
                        Filtered_Sigma_array[Consecutive_DM_array[p][l]][cand_index[cand_index_pos[m]]] = Sigma_array[Consecutive_DM_array[p][l]][cand_index[cand_index_pos[m]]]

                maxima_index = np.where(Filtered_Sigma_array == np.nanmax(Filtered_Sigma_array))

                if (low_period <= Periodicity_array[maxima_index[0][0]][maxima_index[1][0]] <= high_period):
                    print(Periodicity_array[maxima_index[0][0]][maxima_index[1][0]])
                    folding_strings.append("prepfold -accelcand " + str(int(maxima_index[1][0]) - 2) + " -accelfile " + file_name + "_DM" + DM[1000*i + maxima_index[0][0]] + "_ACCEL_" + accel_bin + ".cand -dm " + DM[1000*i + maxima_index[0][0]] + " -nodmsearch -noxwin -nosearch " + file_name + "_DM" + DM[1000*i + maxima_index[0][0]] + ".dat")

                else:
                    continue
            else:
                continue
        else:
            continue
    print("Total number of candidates after filtering:", len(folding_strings))

    def main():
        with Pool(workers) as pool:
            pool.map(folding, folding_strings)

    if __name__ == '__main__':
        main()

    #os.system("rm -rf *.dat")

for i in range(0, int(math.floor(len(DM)/1000.0) + 1)):
    dedisp_strings = []
    fft_strings = []
    accel_strings = []
    folding_strings = []
    cand_len = []

    if (search_type == 0):

        for j in range(0, int(1000/num_dm)):
            if (1000*i + num_dm*j) < len(dm):
                dedisp_strings.append("prepsubband -lodm " + DM[1000*i + int(num_dm)*j] + " -dmstep " + str(dm_step) + " -numdms " + str(num_dm) + " -numout " + numout + " -nsub 1024 " + fil_file + " -o " + file_name)
    
        for k in range(0, 1000):
            if (1000*i + k) < len(dm):

                fft_strings.append("realfft -fwd " + file_name + "_DM" + DM[1000*i + k] + ".dat")
                accel_strings.append("accelsearch -zmax " + accel_bin + " -numharm 8 " + file_name + "_DM" + DM[1000*i + k] + ".fft")

        def main():
            with Pool(workers) as pool:
                pool.map(ddp, dedisp_strings)
                pool.map(fft, fft_strings)
                pool.map(accelsearch, accel_strings)

        
        if __name__ == '__main__':
            main()

        os.system("rm -rf *.fft")

        sorting_folding(file_name, DM, accel_bin, workers, DM_filtering_cut, r_tol, low_period, high_period)

    else:
        sorting_folding(file_name, DM, accel_bin, workers, DM_filtering_cut, r_tol, low_period, high_period)
