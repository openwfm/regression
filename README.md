# WRF-SFIRE Regression Tests

This repository contains the regression tests for WRF-SFIRE. The tests ensure the correctness and stability of the software by comparing the output of different versions or configurations.

## Dependencies

To run the regression tests, you need to have the following dependencies installed:

- GNU compilers
- NetCDF and HDF5 (as needed by WRF)
- Python >= 3.8 with the following libraries:
  - f90nml
  - netCDF4 < 2.0
  - NumPy < 2.0
  - Pandas
 
To install the dependencies using conda:

    conda env create -f install/regression.yml

## Usage

To use the tools provided by this library, you need to follow these steps:

1. **Activate the conda environment**

   conda activate regression

2. **Copy the Configuration Template**

   Copy the `config.json_template` file to `config.json`. This file will be used to configure the regression tests according to your specific needs. You can find the template file in the root directory of the library.
   ```shell
    cp config.json_template config.json
    ```

3. **Edit the Configuration File**

   Open the `config.json` file using a text editor and replace the words in **CAPITALS** with the appropriate values for your use case. While replacing other parameters in the file is optional, it is recommended only if you have a good understanding of their purpose and implications.

4. **Run the Regression Test**

    To run the regression test, run the following command:
    ```shell
    python regression.py config.json >& regression.log &
    ```
    The code will create a file `reg_tests.json` describing metadata for the regression tests.

5. **Validate the Regression Test**

    To validate the results of the regression test, first wait until all the jobs finish running, then use the following command:
    ```shell
    python ncdiff4.py
    ```
    The code will create a table comparing the results in the file `reg_test_results.csv`.

