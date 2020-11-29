import os
import pandas as pd
import seaborn as sns
from fw_ddsm.parameter import *

## traverse directory
# for root, dirs, files in os.walk("."):
#     for file in files:
#         if file.endswith(".csv"):
#             print(file)

label_names = {
    "no_iterations": "#Iterations",
    "pricing_time": "Pricing time per iteration (second)",
    "rescheduling_time": "Scheduling time per iteration (second)"
}
file_names = {
    "no_iterations": "iteration",
    "pricing_time": "runtime-pricing",
    "rescheduling_time": "runtime-scheduling"
}

folder = "results/scalability_demo"
df_overview = pd.read_csv("2020-11-28_04-11-03_overview.csv")
df_aggregate = df_overview.groupby(["no_households", "algorithm"]).mean()

for k, v in label_names.items():

    df_iteration = df_aggregate[k]
    df_iteration = df_iteration.reset_index()
    df_iteration.columns = ["#Households", "Method", v]
    df_iteration['Method'].mask(df_iteration['Method'] == 'ogsa_fw', 'FW-DDSM-OGSA', inplace=True)
    df_iteration['Method'].mask(df_iteration['Method'] == 'minizinc_fw', 'FW-DDSM-CP', inplace=True)


    desc = df_iteration.describe()
    desc[v] = desc[v].map('{:,.2f}'.format)
    desc.transpose().to_csv(f"{file_names[k]}_desc.csv")

    # colours = "tab20c"
    sns.set_theme()
    plot = sns.relplot(x="#Households",
                       y=v,
                       style="Method",
                       col="Method",
                       data=df_iteration,
                       aspect=1.5,
                       linewidth=3,
                       kind="line",
                       # palette=colours
                       )
    plot.savefig(f"{file_names[k]}.png")

print("Done.")
