#!/usr/bin/env python

# python run_trials.py -adv to run locally
# python run_trials.py -avs to run with slurm connection 

import argparse
from datetime import datetime
import importlib.util
import logging
import os

import numpy as np

# Folder/library containing relevant code
import gavi


def serialize_trial(trial):
    # Hack: manually grab params namespace
    import gavi.params.params as params
    
    def name_multi_param(names, key):
        index = None
        for search_index, value in enumerate(getattr(params, key).values):
            if isinstance(value, np.ndarray):
                equality_check = np.array_equal(value, getattr(trial, key))
            else:
                equality_check = value == getattr(trial, key)
            if equality_check:
                index = search_index
                break

        return names[index]
    # naming convention for saving files
    demand_projection_name = name_multi_param(
        ["original", "extrapolate"],
        "demand_projection"
    )
    historical_upper_price_limit_name = name_multi_param(
        ["1x", "10x"],
        "historical_upper_price_limit"
    )
    mfr_resources2_name = name_multi_param(
        ["hist", "pentIPV", "all"],
        "mfr_resources2"
    )
    profit_name = name_multi_param(
        [1],
        "profit_threshold"
    )

    # TODO: change to reflect parameters listed in file names
    return "_".join([
        f"hexprop={trial.hex_proportion}",
        f"opv={trial.opv_frac:.2f}",
        f"profitpct={profit_name}",
        f"hexcost={trial.hex_cost[0]}",
        f"demandproj={demand_projection_name}",
        f"histupperprice={historical_upper_price_limit_name}",
        f"hexmfrs={mfr_resources2_name}",
    ])

def import_config_from_path(config_path):
    """Magic to import a config file by a given path"""
    spec = importlib.util.spec_from_file_location("config", config_path)
    config = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config)
    return config

# Individual trials
def run_trial(trial, trial_id, config, args):
    # Read mod and commands text from files
    with open(config.MODEL_FILE) as f:
        mod_text = f.read()
    with open(config.COMMANDS_FILE) as f:
        commands_text = f.read()

    # Create dat text and saving if enabled
    dat_text = gavi.create_dat_text(trial)
    if args.save_ampl:
        dat_path = os.path.join(
            "experiments", 
            args.experiment,
            f"trial_{trial_id}.dat"
        )
        with open(dat_path, "w") as f:
            f.write(dat_text)

    # If dry run enabled, quit here
    if args.dry_run:
        return

    if args.use_slurm:
        # Create and submit Slurm job
        slurm = gavi.SlurmConnection(
            config.SLURM_SSH_LOGIN,
            config.SLURM_ACCOUNT,
            config.SLURM_EMAIL,
            args.verbose
        )

#         list_of_feasible = [177, 171, 180, 174, 84, 78, 75, 81, 189, 93, 192, 96, 132, 36, 126, 30, 130, 129, 33, 123, 27, 141, 45, 144, 48, 168, 156, 120, 108, 72, 60, 24, 12]
#         list_of_infeas = [175, 169, 178, 172, 176, 170, 179, 173]
#         cancelled = [165, 153, 117, 105, 69, 57, 21, 9, 163, 151, 115, 103, 67, 55, 19, 7, 164, 152, 116, 104, 68, 56, 20, 8, 159, 147, 111, 99, 63, 51, 15, 3, 162, 150, 114, 102, 66, 54, 18, 6, 157, 
# 145, 109, 97, 61, 49, 13, 1, 160, 148, 112, 100, 64, 52, 16, 4, 158, 146, 110, 98, 62, 50, 14, 2, 161, 149, 113, 101, 65, 53, 17, 5, 135, 39, 138, 42, 133, 37, 136, 40, 134, 38, 137, 41, 183, 87, 186, 90, 181, 85, 184, 88, 182, 86, 185, 89]
    if int(trial_id) > 0: # TODO specify trial id number
            slurm.submit_job(
                mod_text, dat_text, commands_text,
                # Name of job run directory in gavi_runs directory
                f"{args.experiment}/trial{trial_id}_{serialize_trial(trial)}",
                # Debug text
                args.experiment,
            )

    else:
        # Create and submit NEOS job
        neos = gavi.NEOSConnection(
            config.NEOS_EMAIL,
            config.NEOS_HOST,
            config.NEOS_PORT,
            args.verbose
        )
        neos.submit_job(mod_text, dat_text, commands_text)
        neos.wait_for_job()
        results_text = neos.get_final_results()
        if args.save_neos:
            results_path = os.path.join(
                "experiments",
                args.experiment,
                f"results_{trial_id}.txt"
            )
            with open(results_path, "w") as f:
                f.write(results_text)

# Set of (possibly parallel) trials
def run_trials(args):
    # Ensure experiment directory exists if need to save anything
    if args.save_ampl or args.save_neos:
        if not args.experiment:
            args.experiment = f"date_{datetime.now().strftime('%Y%m%d')}" 
        os.makedirs(
            os.path.join("experiments", args.experiment),
            exist_ok=True
        )

    # Load the NEOS config
    config = import_config_from_path(args.config_file)

    trials = gavi.create_trials()
    for i, trial in enumerate(trials):
        trial_id = str(i+1)
        logging.info(f"Starting trial {trial_id}")
        run_trial(trial, trial_id, config, args)
    
    logging.info("Finished running all trials!")

def main():
    # Declare arguments command line can take
    parser = argparse.ArgumentParser()  
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument("--dry_run", "-d", action="store_true")
    parser.add_argument("--config_file", default="config.py")
    parser.add_argument(
        "--experiment", "-e",
        help="Name of experiment. Defaults to timestamp"
    )
    parser.add_argument(
        "--save_ampl", "-a",
        action="store_true",
        help="Save the generated AMPL files"
    )
    parser.add_argument(
        "--save_neos", "-n",
        action="store_true",
        help="Save the NEOS results"
    )
    parser.add_argument(
        "--use_slurm", "-s",
        action="store_true",
        help="Use Slurm (over SSH) instead of NEOS"
    )

    args = parser.parse_args()
    run_trials(args)

if __name__ == "__main__":
    main()
