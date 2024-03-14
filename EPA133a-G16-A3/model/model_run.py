from model import BangladeshModel
import pandas as pd
import os

# Get the directory of the current file
current_file_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.abspath(os.path.join(current_file_directory, os.pardir))
output_directory = os.path.join(parent_directory, 'output')


"""
    Run simulation
    Outputs several CSVs containing data of the runs
"""

# ---------------------------------------------------------------
# DIY batchrunner

# USER INPUT:
# scen_list is the scenario list which contains a dictionary per scenario that contains which percentage of bridges
# with a certain condition should break, can be any length
scen_list = [{"A":0, "B":0, "C":0, "D":0}, {"A":100, "B":100, "C":100, "D":100}]

# seed_list is a list of seeds that are used in each scenario agai when running the model
seed_list = [0,1]

def run_model_batch(scen_list, seed_list):
    """
    Runs the model for each scenario, for each seed
    """
    # Collects the data per scenario, so it can be summarized to a 'final' df
    averages_per_scenario = []

    for index, scenario in enumerate(scen_list):
        scen_data = pd.DataFrame()
        print('Scenario:', index)
        # Multiple runs per scenario for each seed
        for i in seed_list:
            print('Seed:', i)
            seed = i
            scen_dict = scenario
            run_length = 7200
            model = BangladeshModel(seed=seed, scen_dict=scen_dict)
            for j in range(run_length):
                model.step()
            # Get data and add it to the dataframe
            run_data = model.get_data()
            scen_data = pd.concat([scen_data, run_data], axis=1)
        # Output csv file with averages per model run of one scenario to output folder
        filename = 'scenario_{}.csv'.format(index)
        output_file_path = os.path.join(output_directory, filename)
        scen_data.to_csv(output_file_path, index=True)

        # Calculate the averages of one scenario across the different runs
        scenario_averages = []
        scenario_averages.append(index)
        scenario_averages.append(scen_data.loc['Average Travel Time'].mean())
        scenario_averages.append(scen_data.loc['Average Waiting Time'].mean())
        averages_per_scenario.append(scenario_averages)

    # Outputs one CSV with the average per scenario for all scenarios
    df_all_scenarios = pd.DataFrame(averages_per_scenario)
    df_all_scenarios = df_all_scenarios.rename(columns={0: 'Scenario', 1: 'Average Travel Time', 2: 'Average Waiting Time'})
    filename = 'all_scenarios.csv'
    output_file_path = os.path.join(output_directory, filename)
    df_all_scenarios.to_csv(output_file_path, index=False)
    print('Model runs done and averages per scenario saved to all_scenarios.csv in output folder')

run_model_batch(scen_list=scen_list, seed_list=seed_list)





