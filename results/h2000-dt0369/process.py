import os
import pandas as pd
from fw_ddsm.parameter import *

## traverse directory
# for root, dirs, files in os.walk("."):
#     for file in files:
#         if file.endswith(".csv"):
#             print(file)


## os.listdir
df_overview = pd.read_csv("overview_all_tests.csv")
df_aggregate = df_overview.groupby(["no_dependent_tasks", "algorithm"]).mean()
df_aggregate = df_aggregate.loc[:, ["PAR", "demand_reduction", "cost_reduction"]]
df_aggregate.to_csv("aggregate.csv")
print("Done.")
