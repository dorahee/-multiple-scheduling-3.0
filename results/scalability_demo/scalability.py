import pandas as pd
import seaborn as sns
# sns.set_theme()
sns.set(font_scale=1.5)

## traverse directory
# for root, dirs, files in os.walk("."):
#     for file in files:
#         if file.endswith(".csv"):
#             print(file)

label_names = {
    "no_iterations": "#Iterations",
    "pricing_time": "Pricing time per iteration (second)",
    "rescheduling_time": "Scheduling time per iteration (second)",
    "rescheduling_time_household": "Scheduling time household per iteration (second)",
    "demand_reduction": "Demand reduction",
    "cost_reduction": "Cost reduction",
    "PAR": "PAR",
}
file_names = {
    "no_iterations": "iteration",
    "pricing_time": "runtime-pricing",
    "rescheduling_time": "runtime-scheduling",
    "rescheduling_time_household": "runtime-scheduling-household",
    "demand_reduction": "demand-reduction",
    "cost_reduction": "cost-reduction",
    "PAR": "par",
}

folder = "results/scalability_demo"
df_overview = pd.read_csv("2020-11-28_04-11-03_overview.csv")
df_overview["rescheduling_time_household"] = df_overview["rescheduling_time"] / df_overview["no_households"]
df_aggregate = df_overview.groupby(["no_households", "algorithm"]).mean()

df_desc_all = pd.DataFrame()
for k, v in label_names.items():

    df_iteration = df_aggregate[k]
    df_iteration = df_iteration.reset_index()
    df_iteration.columns = ["#Households", "Method", v]
    df_iteration['Method'].mask(df_iteration['Method'] == 'ogsa_fw', 'FW-DDSM-OGSA', inplace=True)
    df_iteration['Method'].mask(df_iteration['Method'] == 'minizinc_fw', 'FW-DDSM-CP', inplace=True)

    df_desc = df_iteration.groupby(['Method'])[v].describe()
    # df_desc = df_desc.map('{:,.2f}'.format)
    # df_desc = df_desc.transpose()
    df_desc = df_desc.loc[:, ["mean", "min", "max"]]
    for c in ["mean", "min", "max"]:
        df_desc[c] = df_desc[c].map('{:,.2f}'.format)
    df_desc.columns = ["Mean", "Min", "Max"]
    df_desc.insert(0, "Results", v)
    df_desc.to_csv(f"{file_names[k]}_desc.csv")

    df_desc_all = df_desc_all.append(df_desc)

    # colours = "tab20c"
    plot = sns.relplot(x="#Households",
                       y=v,
                       style="Method",
                       col="Method",
                       data=df_iteration,
                       aspect=1.3,
                       linewidth=3,
                       kind="line",
                       # palette=colours
                       )
    if "reduction" in k:
        yticks = plot.axes[0][0].get_yticks()
        ylabels = ['{:,.0f}%'.format(x * 100) for x in yticks]
        plot.set_yticklabels(ylabels)

    plot.savefig(f"{file_names[k]}.png", dpi=600)
df_desc_all = df_desc_all.reset_index()
df_desc_all.to_csv("desc.csv")
df_desc_all.to_latex("desc.tex")
print("Done.")
