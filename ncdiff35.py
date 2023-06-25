import numpy as np
from netCDF4 import Dataset


def compare_netcdf_files(file1, file2):
    nc1 = Dataset(file1, "r")
    nc2 = Dataset(file2, "r")

    variables1 = nc1.variables.keys()
    variables2 = nc2.variables.keys()
    common_variables = set(variables1) & set(variables2)

    for var_name in common_variables:
        var1 = nc1.variables[var_name]
        var2 = nc2.variables[var_name]

        if var1.dimensions != var2.dimensions:
            # Ignore variables with different dimensions
            continue

        if "Time" in var1.dimensions and "Time" in var2.dimensions:
            time1 = nc1.variables["Times"]
            time2 = nc2.variables["Times"]

            if not np.array_equal(time1, time2):
                # Ignore time frames with different "Times" variable
                continue

        data1 = var1[:]
        data2 = var2[:]

        max_norm = np.max(np.abs(data1 - data2))
        two_norm = np.linalg.norm(data1 - data2, ord=2)

        if np.any(data1 == 0) or np.any(data2 == 0):
            relative_diff = np.inf
        else:
            relative_diff = two_norm / max_norm

        print(f"Variable: {var_name}")
        print(f"Max Norm: {max_norm}")
        print(f"2 Norm: {two_norm}")
        print(f"Relative Difference: {relative_diff}")
        print()

    nc1.close()
    nc2.close()


# Usage example
file1 = "path/to/first/file.nc"
file2 = "path/to/second/file.nc"
compare_netcdf_files(file1, file2)
