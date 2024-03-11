# README File

Created by: EPA133a Group 16

|       Name        | Student Number |
|:-----------------:|:---------------|
|   Suzanne Wink    | 5130697        |
|  Merijn Beemster  | 5380421        |
|   Tarik Bousair   | 5331900        |
| Juliette van Alst | 5402409        |
|  Vera Vermeulen   | 5127661        |

## How to Run
This is a model that simulates traffic delays caused by broken bridges in Bangladesh. For this demo, only a part of the major road N1 is included. The files model.py, model_run.py, model_viz.py and components.py are included. model.py and components.py include the code of the model, while model_viz.py is the visualization module, which is incompatible with the current version of the model. To run the model, the file model_run.py should be run (in an IDE). The variables scen_dict and seed_list can be changed to include different scenarios or different seeds. The model will run for each seed for each scenario and the output will be saved as CSVs in the output folder. The model uses the dataset N1_data_v2.csv, which contains the data of the links and bridges on the relevant part of the N1. The data cleaning process is described in the included pdf. 

## Output
In the output folder, the model outputs a CSV per scenario that contains the average travel time and waiting time for each model run (so for each seed). Next to that, all_scenarios.csv gives the average travel and waiting time for each scenario (so the average across the runs). 
