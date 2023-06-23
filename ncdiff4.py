import netCDF4 as nc
import numpy as np

def compare_netcdf_files(file1, file2):
    # Open netCDF files
    dataset1 = nc.Dataset(file1)
    dataset2 = nc.Dataset(file2)

    # Get times from both files
    times1 = dataset1.variables["Times"][:]
    times2 = dataset2.variables["Times"][:]
    
    # Iterate through all time steps in both files
    for time_index, (time1, time2) in enumerate(zip(times1, times2)):
        # Check if the times are equal
        if np.array_equal(time1, time2):
            print(f"Time step {time_index}: {time1.tobytes().decode().strip()}")
            
            # Compare variables
            for var_name, variable in dataset1.variables.items():
                # Skip the 'Times' variable
                if var_name == "Times":
                    continue
                
                # Check if the variable exists in both files
                if var_name in dataset2.variables:
                    var1 = variable[:]
                    var2 = dataset2.variables[var_name][:]
                    
                    # Check if the dimensions are equal (ignoring unlimited time dimension)
                    if var1.shape[1:] == var2.shape[1:]:
                        # Compute norms
                        max_norm1 = np.max(np.abs(var1[time_index]))
                        max_norm2 = np.max(np.abs(var2[time_index]))
                        two_norm1 = np.linalg.norm(var1[time_index])
                        two_norm2 = np.linalg.norm(var2[time_index])

                        # Compute relative differences
                        rel_diff_max = abs(max_norm1 - max_norm2) / max(max_norm1, max_norm2, 1e-10)
                        rel_diff_two = abs(two_norm1 - two_norm2) / max(two_norm1, two_norm2, 1e-10)
                        
                        # Print the results
                        print(f"Variable {var_name}:")
                        print(f"  max-norm: {max_norm1}, {max_norm2} | Relative difference: {rel_diff_max}")
                        print(f"  2-norm: {two_norm1}, {two_norm2} | Relative difference: {rel_diff_two}")
                    else:
                        print(f"Variable {var_name} dimensions don't match. Skipping.")
                else:
                    print(f"Variable {var_name} not present in both files. Skipping.")

        else:
            print(f"Time step {time_index} skipped due to different times.")

    # Close datasets
    dataset1.close()
    dataset2.close()

# Example usage
file1 = 'path_to_your_first_netcdf_file'
file2 = 'path_to_y

