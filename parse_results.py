# Code to collect experiment results
#
# Note this only works on trials in an experiment that have at least started.
# And maybe it will only work on trials that have completed. (TBD)

# Example path:
# /home/zxmeie/gavi_runs/date_20230625/trial1_hexprop=0.01_opv=0.33_profitpct=0.45_hexcost=100_demandproj=original_histupperprice=1x_hexmfrs=hist/results.csv

# import csv
from datetime import datetime

from fabric import Connection

# Login used to ssh into the RIT login machine. In this cases uses ssh
# shortcut set up earlier.
REMOTE_SSH_LOGIN = "rit"

# By default, use the experiment folder corresponding to today. Otherwise,
# comment out the following line and replace remote_base_directory_date with
# desired date formatted like '20230101'.
base_directory_date = datetime.now().strftime('%Y%m%d')

# Grab results from all the trial folders in REMOTE_BASE_DIRECTORY on the RIT
# server.
REMOTE_BASE_DIRECTORY = f"/home/zxmeie/gavi_runs/date_{base_directory_date}"

# Copy results files into the following directory
LOCAL_BASE_DIRECTORY = f"saved_results/date_{base_directory_date}"

# Parse the name of a trial directory into a dictionary. For example:
#   Input: "trial1_hexprop=0.01_opv=0.33"
#   Output: {"trial": 1, "hexprop": "0.01", "opv": "0.33"}
def parse_trial_directory_name(directory_name):
    name_split = directory_name.split("_")
    values = {}

    # Special handling for trial number
    trial_number = name_split[0].removeprefix("trial")
    values["trial"] = trial_number

    # Everything else
    for name_item in name_split[1:]:
        name_item_split = name_item.split("=")
        values[name_item_split[0]] = name_item_split[1]

    return values


# Wrapper around a ssh connection to the remote server.
class ConnController:
    def __init__(self):
        self.conn = Connection(REMOTE_SSH_LOGIN)

    def get_directory_names(self):
        result = self.conn.run(f"cd {REMOTE_BASE_DIRECTORY} && ls", hide="stdout")
        self.directory_names = sorted(
            result.stdout.split(),
            key=lambda directory_name: int(
                directory_name.split("_")[0].removeprefix("trial")
            )
        )

    def copy_results(self, directory_name):
        try:
            self.conn.get(
                remote=f"{REMOTE_BASE_DIRECTORY}/{directory_name}/results.csv",
                local=f"{LOCAL_BASE_DIRECTORY}/{directory_name}.txt",
            )
        except FileNotFoundError:
            return False
        return True


    def run(self):
        self.get_directory_names()
        for directory_name in self.directory_names:
            results_exists = self.copy_results(directory_name)
            if not results_exists:
                continue

            # trial_name_values = parse_trial_directory_name(directory_name)
            # x = self.parse_trial_results(directory_name)

c = ConnController()



# input_file = 'output.txt'
# output_file = 'output.csv'

# with open(input_file, 'r') as file:
#     data = file.readlines()

# # Parse the data and extract values
# parsed_data = []
# for line in data:
#     line = line.strip()
#     if line:
#         row = [value.strip() for value in line.split()]
#         parsed_data.append(row)

# # Write the data to a CSV file
# with open(output_file, 'w', newline='') as file:
#     writer = csv.writer(file)
#     writer.writerows(parsed_data)

# print(f"CSV file '{output_file}' created successfully.")

# # var_names = []
# # var_values = []

# # for var in test.getVars():
# #     if var.X > 0: 
# #         var_names.append(str(var.varName))
# #         var_values.append(var.X)

# # # Write to csv
# # with open('testout.csv', 'wb') as myfile:
# #     wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
# #     wr.writerows(zip(var_names, var_values))