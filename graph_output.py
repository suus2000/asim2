
import pandas as pd
import matplotlib.pyplot as plt

# read CSV as dataframe
df_non_transposed = pd.read_csv('output/scenario_0.csv')

# Transposeer het DataFrame
df = df_non_transposed.transpose()

# Zet de eerste rij als kolomnamen
df.columns = df.iloc[0]

# Verwijder de eerste rij, omdat deze nu de kolomnamen zijn
df = df[1:]

# Hernoem de kolommen
df_new = df.rename(columns={'Index': 'Seed', 'Average Travel Time': 'Average_Travel_Time', 'Average Waiting Time': 'Average_Waiting_Time'})

# Toon het DataFrame
print(df_new)

# Plot Average Travel Time per Seed
plt.bar(df_new.index, df_new['Average_Travel_Time'])
plt.xlabel('Seeds')
plt.ylabel('Average Travel Time')
plt.title('Average Travel Time per Seed')
plt.grid(True)
plt.show()

# Plot Average Waiting Time per Seed
plt.bar(df_new.index, df_new['Average_Waiting_Time'])
plt.xlabel('Seeds')
plt.ylabel('Average Waiting Time')
plt.title('Average Waiting Time per Seed')
plt.grid(True)
plt.show()


