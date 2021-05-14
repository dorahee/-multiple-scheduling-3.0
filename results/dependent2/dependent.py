import pandas as pd
from fw_ddsm.parameter import *

df_overview = pd.read_csv("2020-12-09_05-12-44_overview.csv")
required_columns = [x for x in df_overview.columns.tolist() if "diff" in x]
required_columns.insert(0, k_dependent_tasks_no)
df_overview = df_overview[required_columns]
df_overview = df_overview.dropna('index')
df_overview_desc = df_overview.groupby(k_dependent_tasks_no).agg(["min", "max", "mean"]).transpose()

for i in range(3, len(df_overview_desc)):
    df_overview_desc.iloc[i] = [f"{round(x * 100, 2)}%" for x in df_overview_desc.iloc[i].values.tolist()]

df_overview_desc.to_latex("overview.tex")
print("Done. ")


