from glob import glob
import os.path as osp
import netCDF4 as nc
import numpy as np
import json
import sys


def ncdiff4(file1, file2, vars, do_print=1):
    """
    Compare two netcdf files
    :param file1: file name
    :param file2: file name
    :param vars: variables to test
    :param do_print: print if True
    :returns: max relative error
    """

    maxreldif = 0.0

    # Open netCDF files
    dataset1 = nc.Dataset(file1)
    dataset2 = nc.Dataset(file2)

    # Get times from both files
    times1 = dataset1.variables["Times"][:]
    times2 = dataset2.variables["Times"][:]

    # Iterate through all time steps in both files
    rows1, cols1 = times1.shape
    rows2, cols2 = times2.shape
    if rows1 != rows2 or cols1 != cols2:
        print("arrays Times are not the same size")
        return np.inf
    for time_index, (time1, time2) in enumerate(zip(times1, times2)):
        ntested = 0
        # Check if the times are equal
        if np.array_equal(time1, time2):
            if do_print > 2:
                print(f"Time step {time_index}: {time1.tobytes().decode().strip()}")

            # Compare variables
            for var_name in dataset1.variables.keys():
                # Skip the 'Times' variable and variables not in vars
                if var_name == "Times" or not len(vars) or var_name not in vars:
                    continue

                # Check if the variable exists in both files
                if var_name in dataset2.variables:
                    # print(var_name)
                    var1 = np.ravel(dataset1.variables[var_name])
                    var2 = np.ravel(dataset2.variables[var_name])

                    # Check if the dimensions are equal (ignoring unlimited time dimension)
                    if var1.shape[1:] == var2.shape[1:]:
                        ntested += 1
                        # Compute norms
                        max_norm1 = np.max(np.abs(var1[time_index]))
                        max_norm2 = np.max(np.abs(var2[time_index]))
                        two_norm1 = np.linalg.norm(var1[time_index])
                        two_norm2 = np.linalg.norm(var2[time_index])

                        # Compute relative differences
                        rel_diff_max = abs(max_norm1 - max_norm2) / max(
                            max_norm1, max_norm2, np.finfo(float).eps
                        )
                        rel_diff_two = abs(two_norm1 - two_norm2) / max(
                            two_norm1, two_norm2, np.finfo(float).eps
                        )

                        maxreldif = max(maxreldif, rel_diff_max)

                        if do_print > 2:
                            # Print the results
                            print(f"Variable {var_name}:")
                            print(
                                f"  max-norm: {max_norm1}, {max_norm2} | Relative difference: {rel_diff_max}"
                            )
                            print(
                                f"  2-norm: {two_norm1}, {two_norm2} | Relative difference: {rel_diff_two}"
                            )
                    else:
                        print(f"Variable {var_name} dimensions don't match. Exiting.")
                        return np.inf
                else:
                    if do_print > 1:
                        print(f"Variable {var_name} not present in both files. Skipping.")

        else:
            if do_print > 0:
                print(f"Time step {time_index} skipped due to different times.")

    # Close datasets
    dataset1.close()
    dataset2.close()

    return maxreldif


if __name__ == "__main__":
    reg_tests = json.load(open('reg_tests.json'))
    results = {}
    for js in reg_tests:
        wrfout_paths = sorted(glob(osp.join(js['case_path'], 'wrfout*')))
        rsl_path = osp.join(js['case_path'], 'rsl.out.0000')
        slurm_paths = sorted(glob(osp.join(js['case_path'], 'slurm*.out')))
        if not osp.exists(rsl_path) and not len(slurm_paths) \
            or osp.exists(rsl_path) and not 'SUCCESS COMPLETE WRF' in open(rsl_path).read() \
            or not osp.exists(rsl_path) and len(slurm_paths) and not 'SUCCESS COMPLETE WRF' in open(slurm_paths[0]).read() \
            or not len(wrfout_paths):
                if js['test_name'] not in results.keys():
                    results.update({
                        js['test_name']: {
                            js['commit']: {
                                'status': 'failed', 
                                'paths': None
                            }, 'vars': js['vars']
                        }
                    })
                else:
                    results[js['test_name']].update({
                        js['commit']: {
                            'status': 'failed', 
                            'paths': None, 
                        }
                    })
        else:
            if js['test_name'] not in results.keys():
                results.update({
                    js['test_name']: {
                        js['commit']: {
                            'status': 'success', 
                            'paths': wrfout_paths
                        }, 'vars': js['vars']
                    }
                })
            else:
                results[js['test_name']].update({
                    js['commit']: {
                        'status': 'success', 
                        'paths': wrfout_paths
                    }
                })
    for k in results.keys():
        if all([v['status'] == 'success' for v in results[k].values() if 'status' in v]):
            vars = results[k]['vars']
            diff = 0.0
            for p1,p2 in zip(*[v['paths'] for v in results[k].values() if 'paths' in v]):
                diff += ncdiff4(p1, p2, vars, do_print=2)
            results[k].update({'diff': diff})
        else:
            results[k].update({'diff': np.inf})
    
