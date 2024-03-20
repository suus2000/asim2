
import pandas as pd
import matplotlib.pyplot as plt

# read CSV as dataframe
def graph_output(file_name):
    df_non_transposed = pd.read_csv(file_name)
    # Transpose theDataFrame
    df = df_non_transposed.transpose()
    # put the first row as column names
    df.columns = df.iloc[0]
    # delete the first row, as they are now the column names
    df = df[1:]
    # rename the columns
    df_new = df.rename(columns={'Index': 'Seed', 'Average Travel Time': 'Average_Travel_Time', 'Average Waiting Time': 'Average_Waiting_Time'})

    print(df_new)

    x = df_new['Average_Travel_Time'].mean()
    y = df_new['Average_Waiting_Time'].mean()
    print('the average travel time is', x, 'The average waiting time is', y)

   # Plot Average Travel Time per Seed for scenarios's
    plt.boxplot( df_new['Average_Travel_Time'])
    plt.xlabel('Seeds')
    plt.ylabel('Average Travel Time')
    plt.title('Average Travel Time per Seed ')
    plt.grid(True)
    plt.show()

    # Plot Average Waiting Time per Seed
    plt.boxplot(df_new['Average_Waiting_Time'])
    plt.xlabel('Seeds')
    plt.ylabel('Average Waiting Time')
    plt.title('Average Waiting Time per Seed ')
    plt.grid(True)
    plt.show()

graph_output('output/scenario_0.csv')
# graph_output('output/scenario_1.csv')
# graph_output('output/scenario_2.csv')
# graph_output('output/scenario_3.csv')
# graph_output('output/scenario_4.csv')
# graph_output('output/scenario_5.csv')
# graph_output('output/scenario_6.csv')
# graph_output('output/scenario_7.csv')
# graph_output('output/scenario_8.csv')


