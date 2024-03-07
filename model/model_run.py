from model import BangladeshModel
import pandas as pd
import os

# Get the directory of the current file
current_file_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.abspath(os.path.join(current_file_directory, os.pardir))
output_directory = os.path.join(parent_directory, 'output')


"""
    Run simulation
    Print output at terminal
"""

# ---------------------------------------------------------------
# DIY batchrunner
scen_list = [{"A":0, "B":0, "C":0, "D":0}, {"A":0, "B":0, "C":0, "D":5},{"A":0, "B":0, "C":0, "D":10},{"A":0, "B":0, "C":5, "D":10},
             {"A":0, "B":0, "C":10, "D":20},{"A":0, "B":5, "C":10, "D":20},{"A":0, "B":10, "C":20, "D":40},{"A":5, "B":10, "C":20, "D":40},
             {"A":10, "B":20, "C":40, "D":80}]
seed_list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

def run_model_batch(scen_list, seed_list):
    averages_per_scenario = []
    for index, scenario in enumerate(scen_list):
        scen_data = pd.DataFrame()
        print('Scenario:', index)
        for i in seed_list:
            print('Seed:', i)
            seed = i
            scen_dict = scenario
            run_length = 7200
            model = BangladeshModel(seed=seed, scen_dict=scen_dict)
            for j in range(run_length):
                model.step()
            run_data = model.get_data(seed)
            scen_data = pd.concat([scen_data, run_data], axis=1)
        filename = 'scenario_{}.csv'.format(index)
        output_file_path = os.path.join(output_directory, filename)
        scen_data.to_csv(output_file_path, index=True)

        scenario_averages = []
        scenario_averages.append(index)
        scenario_averages.append(scen_data.loc['Average Travel Time'].mean())
        scenario_averages.append(scen_data.loc['Average Waiting Time'].mean())
        averages_per_scenario.append(scenario_averages)

    df_all_scenarios = pd.DataFrame(averages_per_scenario)
    df_all_scenarios = df_all_scenarios.rename(columns={0: 'Scenario', 1: 'Average Travel Time', 2: 'Average Waiting Time'})
    filename = 'all_scenarios.csv'
    output_file_path = os.path.join(output_directory, filename)
    df_all_scenarios.to_csv(output_file_path, index=False)
    print('Model runs done and averages per scenario saved to all_scenarios.csv in output folder')

run_model_batch(scen_list=scen_list, seed_list=seed_list)





