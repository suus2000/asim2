import pandas as pd
import matplotlib.pyplot as plt

# read the csv file
df1 = pd.read_csv('output/all_scenarios.csv')

print(df1)

# Plot Average Travel Time per Seed
plt.boxplot(df1['Average Travel Time'])
plt.xlabel('Scenario')
plt.ylabel('Average Travel Time')
plt.title('Average Travel Time per Scenario')
plt.grid(True)
plt.show()

# Plot Average Waiting Time per Seed
plt.boxplot( df1['Average Waiting Time'])
plt.xlabel('Scenario')
plt.ylabel('Average Waiting Time')
plt.title('Average Waiting Time per Scenario')
plt.grid(True)
plt.show()


