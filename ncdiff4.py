from glob import glob
import os.path as osp
import netCDF4 as nc
import pandas as pd
import numpy as np
import json
import sys
import logging

_metadata = ['test_name', 'case_name', 'config_option', 'config_optim', 'nesting', 'n_cpus']

def ncdiff4(file1, file2, vars):
    """
    Compare two netcdf files
    :param file1: file name
    :param file2: file name
    :param vars: variables to test
    :returns: max relative error
    """

    # Initialize maximum relative differences
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
        logging.warning("arrays Times are not the same size")
        return np.inf
    for time_index, (time1, time2) in enumerate(zip(times1, times2)):
        ntested = 0
        # Check if the times are equal
        if np.array_equal(time1, time2):
            logging.debug(f"Time step {time_index}: {time1.tobytes().decode().strip()}")

            # Compare variables
            for var_name in dataset1.variables.keys():
                # Skip the 'Times' variable and variables not in vars
                if var_name == "Times" or not len(vars) or var_name not in vars:
                    continue

                # Check if the variable exists in both files
                if var_name in dataset2.variables:
                    logging.debug(var_name)
                    var1 = dataset1.variables[var_name][time_index]
                    var2 = dataset2.variables[var_name][time_index]

                    # Check if the dimensions are equal (ignoring unlimited time dimension)
                    if var1.shape[1:] == var2.shape[1:]:
                        ntested += 1
                        # Compute relative differences
                        rel_diff_max = np.max(np.abs(var1 - var2)) / max(
                            np.max(np.abs(var1)), np.max(np.abs(var2)), np.finfo(float).eps
                        )
                        # Print the results
                        logging.debug(f"Variable {var_name} {var1.shape}: relative difference: {rel_diff_max}")
                        maxreldif = max(maxreldif, rel_diff_max)
                    else:
                        logging.debug(f"Variable {var_name} dimensions don't match. Exiting.")
                        return np.inf
                else:
                    logging.debug(f"Variable {var_name} not present in both files. Skipping.")

        else:
            logging.warning(f"Time step {time_index} skipped due to different times.")

    # Close datasets
    dataset1.close()
    dataset2.close()

    return maxreldif

def validate_reg_tests(reg_tests):
    """
    Validate regression tests from json metadata
    :param js: json metadata with information of the tests to compare
    :returns: dictionary with 
    """
    results = {}
    for js in reg_tests:
        wrfout_paths = sorted(glob(osp.join(js['case_path'], 'wrfout*')))
        rsl_path = osp.join(js['case_path'], 'rsl.out.0000')
        slurm_paths = sorted(glob(osp.join(js['case_path'], 'slurm*.out')))
        if not osp.exists(rsl_path) and not len(slurm_paths) \
            or osp.exists(rsl_path) and not 'SUCCESS COMPLETE WRF' in open(rsl_path).read() \
            or not osp.exists(rsl_path) and len(slurm_paths) and not 'SUCCESS COMPLETE WRF' in open(slurm_paths[0]).read() \
            or not len(wrfout_paths):
                if js['test_id'] not in results.keys():
                    results.update({
                        js['test_id']: {
                                'output': {
                                    js['commit']: {
                                        'status': 'failed', 
                                        'paths': None
                                }
                            }, 'vars': js['vars']
                        }
                    })
                else:
                    results[js['test_id']]['output'].update({
                        js['commit']: {
                            'status': 'failed', 
                            'paths': None, 
                        }
                    })
        else:
            if js['test_id'] not in results.keys():
                results.update({
                    js['test_id']: {
                        'output': {
                            js['commit']: {
                                'status': 'success', 
                                'paths': wrfout_paths
                            }
                        }, 'vars': js['vars']
                    }
                })
            else:
                results[js['test_id']]['output'].update({
                    js['commit']: {
                        'status': 'success', 
                        'paths': wrfout_paths
                    }
                })
        for m in _metadata:
            results[js['test_id']].update({m: js[m]})
    return results

def summary_table(results):
    """
    Create summary table with the results.
    :param results: dictionary with results from the regression test.
    :returns: pandas dataframe with the summary of the results.
    """
    table = {'test_id': []}
    table.update({m: [] for m in _metadata})
    table.update({'relmaxdiff': []})
    table.update({k.lower() + '_run': [] for k in results[next(iter(results))]['output'].keys()})
    for k in results.keys():
        print(k)
        table['test_id'].append(k)
        for m in _metadata:
            table[m].append(results[k][m])
        vars = results[k]['vars']
        for run in results[k]['output'].keys():
            table[run.lower() + '_run'].append(results[k]['output'][run]['status'])
        if all([v['status'] == 'success' for v in results[k]['output'].values()]):
            relmaxdiff = 0.0
            for p1,p2 in zip(*[v['paths'] for v in results[k]['output'].values()]):
                relmaxdiff = max(relmaxdiff, ncdiff4(p1, p2, vars))
            print(relmaxdiff)
            results[k].update({'relmaxdiff': relmaxdiff})
            table['relmaxdiff'].append(relmaxdiff)
        else:
            results[k].update({'relmaxdiff': None})
            table['relmaxdiff'].append(None)
            print(None)
    df = pd.DataFrame(table)
    return df

def test_ncdiff():
    """
    Add test for checking differences against the same case.
    """
    logging.info('testing ncdiff with two identical cases')
    reg_tests = json.load(open('reg_tests.json'))
    results = validate_reg_tests(reg_tests)
    id = next(iter(results))
    k_ = next(iter(results[id]['output']))
    results = {id: results[id]}
    for k in results[id]['output'].keys():
        results[id]['output'].update({k: results[id]['output'][k_]})
    table = summary_table(results)
    assert table.loc[0, 'relmaxdiff'] == 0
    
if __name__ == "__main__":
    if len(sys.argv) > 1 and '-v' in sys.argv[1:]:
        logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
    else:
        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    if len(sys.argv) > 1 and '-t' in sys.argv[1:]:
        test_ncdiff()
        
    logging.info('start using ncdiff to test all regression cases')
    reg_tests = json.load(open('reg_tests.json'))
    results = validate_reg_tests(reg_tests)
    table = summary_table(results)
    table.to_csv('reg_test_results.csv', index=False)
    print(table)
    print()