import os
import pandas as pd
from fw_ddsm.parameter import *

## traverse directory
# for root, dirs, files in os.walk("."):
#     for file in files:
#         if file.endswith(".csv"):
#             print(file)


## os.listdir
df_overview = pd.DataFrame()
for file in os.listdir("."):
    if file.endswith(".csv"):
        df_overview = df_overview.append(pd.read_csv(file))
df_overview = df_overview.reset_index(drop=True)
df_overview.to_csv("combined_overview.csv")
df_aggregate = df_overview.groupby(["no_dependent_tasks", "algorithm"]).mean()
df_aggregate = df_aggregate.loc[:, ["PAR", "demand_reduction", "cost_reduction"]]
df_aggregate.to_csv("aggregate.csv")
print("Done.")
