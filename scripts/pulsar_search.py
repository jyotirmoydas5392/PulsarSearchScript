import os
import sys
import subprocess
from multiprocessing import Pool

def ddp(command):
    """Execute ddp command."""
    try:
        print(f"Running ddp command: {command}")
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing ddp command: {e}")

def fft(command):
    """Execute fft command."""
    try:
        print(f"Running fft command: {command}")
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing fft command: {e}")

def accelsearch(command):
    """Execute accelsearch command."""
    try:
        print(f"Running accelsearch command: {command}")
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing accelsearch command: {e}")

def search_pulsar(input_dir, output_dir, fil_file, DM_array, dm_step, total_obs_time, sampling_time, num_dm, accel_bin, workers):
    # Extract file name by removing .fil extension
    file_name = os.path.splitext(os.path.basename(fil_file))[0]

    # Initialize lists for different string commands
    dedisp_strings = []
    fft_strings = []
    accel_strings = []

    # Calculate sampling time and number of outputs
    samp_time = sampling_time / 1000000.0
    numout0 = int(total_obs_time / samp_time)
    numout = str(numout0 - 2) if (numout0 % 2) == 0 else str(numout0 - 1)

    # Check if fil_file exists in input_dir
    fil_file_path = os.path.join(input_dir, fil_file)
    if not os.path.exists(fil_file_path):
        print(f"Error: The file {fil_file_path} does not exist in the input directory.")
        return

    # Loop over the entire DM_array list instead of limiting to 1000
    for j in range(0, len(DM_array), num_dm):
        # Using relative paths for output in output_dir
        dedisp_cmd = f"prepsubband -lodm {DM_array[j]} -dmstep {dm_step} -numdms {num_dm} -numout {numout} -nsub 1024 {fil_file_path} -o {file_name}"
        dedisp_strings.append(dedisp_cmd)

    # Loop through the entire DM_array list for FFT and Accelsearch commands
    for k in range(len(DM_array)):
        # Using relative paths for output in output_dir
        dat_file = f"{file_name}_DM{DM_array[k]}.dat"
        fft_file = f"{file_name}_DM{DM_array[k]}.fft"
        
        fft_cmd = f"realfft -fwd {dat_file}"
        accel_cmd = f"accelsearch -zmax {accel_bin} -numharm 8 {fft_file}"

        fft_strings.append(fft_cmd)
        accel_strings.append(accel_cmd)

    # Function for running all processes in parallel
    def main():
        # Store the current working directory (base directory)
        base_dir = os.getcwd()

        # Change directory to output_dir before running commands
        os.makedirs(output_dir, exist_ok=True)
        os.chdir(output_dir)
        
        # Execute the commands in parallel
        with Pool(workers) as pool:
            print("Running dedisp commands...")
            pool.map(ddp, dedisp_strings)

            print("Running fft commands...")
            pool.map(fft, fft_strings)

            print("Running accelsearch commands...")
            pool.map(accelsearch, accel_strings)

        # Cleanup after processing
        os.system("rm -rf *.fft")

        # After processing, change back to the base directory
        os.chdir(base_dir)

        print("Finished processing and cleaned up.")

    # Directly call the main function
    main()