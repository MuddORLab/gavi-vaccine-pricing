# gavi-vaccine-pricing
Code for the paper "Strategies for the Global Alliance for Vaccines and Immunization in International Vaccine Pricing and Procurement"

# GAVI Vaccine Pricing

### Run the code
1.  Confirm that dependencies in `requirements.txt` are met (`pip install -r requirements.txt`)
2.  Modify parameters in `params.py` (recommended to adjust file naming convention in line 52 of 'run_trials.py' when adding multiparams)
3.  Confirm correct directory (should be in `gavi-vaccine-pricing`)
4.  Use command `python run_trials.py -avs` to execute, which will generate dat file(s) in `experiments` named `date_YYYYMMDD`, submit to slurm, and output slurm job ID for each job
   * `-a` means save the generated ampl files
   * `-v` means verbose (prints out information in terminal)
   * `-s` means use Slurm (over SSH) instead of NEOS
   * `-d` means dry run (generate files, don't submit to server)

### Code
* **gavi** directory
    * `__init__.py`: initialize
    * `ampl_gen.py`: generate dat file for AMPL
    * `neos.py`: connect to NEOS server, submit job, retrieve results
    * `slurm.py`: specifications for connection to SLURM, memory/CPU requests, time limit
    * **params** directory
       * `params.py`: create param grid, construct data frame, generate demand curve coefficients (accesses `mi4a_public_database.xlsx`)
      * `excel_calculations.py`: separate outline of data frame construction from `params.py`
   * **trials** directory
      * `create_trials.py`: ties together code from `params.py`
      * `types.py`: specifies variable types, 
    
* **model** directory
  * `commands_gurobi.txt`: list of commands to use in AMPL execution
  * `hex.mod`: new/updated primary AMPL file
  


* `config.py.example`: example configuration
* `parse_results.py`: code to collect experiment results
* `requirements.txt`: requirements to run the model
* `run_manual_dat.py`: code for running an individual dat file manually (without automatic generation)
* `run_params.py`: code to debug `params.py` file, prints specified values in print statements
* `run_trials.py`: code for generating dat file with given parameters/connecting to NEOS

### Debugging
* To check the parameters in `params.py`:
    * Adjust print statements in `run_params.py` as needed
    * Confirm correct directory (should be in `gavi-vaccine-pricing`)
    * Use command `python run_params.py` to execute, which will print out the parameter values specified
