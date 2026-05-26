import argparse
import importlib.util

import gavi

def import_config_from_path(config_path):
    spec = importlib.util.spec_from_file_location("config", config_path)
    config = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config)
    return config

def run_trial(args):
    config = import_config_from_path(args.config_file)

    with open(config.MODEL_FILE) as f:
        mod_text = f.read()
    with open(config.COMMANDS_FILE) as f:
        commands_text = f.read()
    with open(args.dat_file) as f:
        dat_text = f.read()

    neos = gavi.NEOSConnection(
        config.NEOS_EMAIL,
        config.NEOS_HOST,
        config.NEOS_PORT,
        args.verbose
    )
    neos.submit_job(mod_text, dat_text, commands_text)
    neos.wait_for_job()
    results_text = neos.get_final_results()

    print(results_text)

def main():
    parser = argparse.ArgumentParser()  
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument("--config_file", default="config.py")
    parser.add_argument("dat_file")

    args = parser.parse_args()
    run_trial(args)

if __name__ == "__main__":
    main()
