import pandas as pd
import seaborn as sns
from fw_ddsm.parameter import *
import matplotlib.pyplot as plt

# sns.set_theme()
sns.set(font_scale=1.5)

## traverse directory
# for root, dirs, files in os.walk("."):
#     for file in files:
#         if file.endswith(".csv"):
#             print(file)

DRAW = False
DESC = True

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

household_numbers = [50, 100, 500, 1000, 2000, 4000, 6000, 8000, 10000]
repeat_numbers = [0, 1, 2, 3, 4]
algorithms = {
    "minizinc_fw": "FW-DDSM-CP",
    "ogsa_fw": "FW-DDSM-OGSA",
}
types = {
    "minizinc_fw": "Optimised",
    "ogsa_fw": "Improved",
}
k_repeat = "Repeat"
k_tpd = "TDP"

# combine data
df_all_demands = pd.DataFrame()
df_all_others = pd.DataFrame()
for r in repeat_numbers:
    for h in household_numbers:
        for k, v in algorithms.items():
            folder_name = f"h{h}-w5-dt3-fft10-sft0-id{r}"

            # get before and after demands
            file_demands_name = f"{k}_aggregator_demands.csv"
            df = pd.read_csv(f"{folder_name}/{file_demands_name}").transpose()
            df = df.iloc[[1, -1], 1:].reset_index(drop=True)
            df[k_households_no] = h
            df[m_algorithm] = v
            df[s_demand] = ["Preferred", types[k]]
            df[k_repeat] = r
            df[k_tpd] = f"Preferred and {types[k].lower()}"
            df = df.set_index([k_repeat, m_algorithm, k_households_no, s_demand, k_tpd]).stack().reset_index()
            df.columns = ["Repeat", "Method", "#Households", "Demand Profile", k_tpd, "Period", "Demand (kWh)"]
            df_all_demands = df_all_demands.append(df)

            # get all sampled demands
            file_final_name = f"{k}_aggregator_demands_final.csv"
            df = pd.read_csv(f"{folder_name}/{file_final_name}").transpose()
            df = df.iloc[2:, :].reset_index()
            df[k_households_no] = h
            df[m_algorithm] = v
            df[k_repeat] = r
            df[k_tpd] = "Actual"
            df = df.set_index([k_repeat, m_algorithm, k_households_no, "index", k_tpd]).stack().reset_index()
            df.columns = ["Repeat", "Method", "#Households", "Demand Profile", k_tpd, "Period", "Demand (kWh)"]
            df_all_demands = df_all_demands.append(df)

            # get before and after others
            file_demands_name = f"{k}_aggregator_others.csv"
            df = pd.read_csv(f"{folder_name}/{file_demands_name}")
            df = df.loc[:, [s_demand_reduction, p_cost_reduction, s_par]]
            df[k_households_no] = h
            df[k_repeat] = r
            df = df.iloc[[0, -1], :].reset_index(drop=True)
            df[s_demand] = ["Preferred", types[k]]
            df_all_others = df_all_others.append(df)

            # get all sampled others
            file_demands_name = f"{k}_aggregator_others_final.csv"
            df = pd.read_csv(f"{folder_name}/{file_demands_name}")
            df = df.loc[:, [s_demand_reduction, p_cost_reduction, s_par]]
            df[k_households_no] = h
            df[k_repeat] = r
            df = df.iloc[1:, :].reset_index(drop=True)
            df[s_demand] = "Actual"
            df_all_others = df_all_others.append(df)

if DRAW:
    # draw graphs for each repeat
    for alg in algorithms.values():
        df_alg = df_all_demands[df_all_demands["Method"] == alg]
        for r in repeat_numbers:
            df = df_alg[df_alg["Repeat"] == r]
            df_filtered = dict()
            df_filtered["less"] = df[df["#Households"] <= 1000]
            df_filtered["greater"] = df[df["#Households"] > 1000]
            for k, v in df_filtered.items():
                plot = sns.relplot(x="Period",
                                   y="Demand (kWh)",
                                   style="Demand Profile",
                                   hue="Demand Profile",
                                   col=k_tpd,
                                   row="#Households",
                                   data=v,
                                   aspect=1.7,
                                   linewidth=3,
                                   kind="line",
                                   # palette=colours
                                   )
                plot.savefig(f"{alg}_demo_1000_{k}_r{r}.png", dpi=600)
                print(f"Saved {alg}-demo-1000-{k}-r{r}.png.")

if DESC:
    # df_all_others = df_all_others.set_index([k_repeat, k_households_no, s_demand]).stack().reset_index()
    # df_all_others.columns = ["Repeat", "#Households", "Demand Profile", "Result", "Value"]
    s_demand_reduction_diff = s_demand_reduction + " distance"
    p_cost_reduction_diff = p_cost_reduction + " distance"
    s_par_diff = s_par + " distance"

    df_all_others_ext = pd.DataFrame()
    opt_demand_red = 0
    opt_cost_red = 0
    opt_par = 0
    for index, row in df_all_others.iterrows():
        this_demand_reduction = row[s_demand_reduction]
        this_cost_reduction = row[p_cost_reduction]
        this_par = row[s_par]
        if "Opt" in row[s_demand] or "Imp" in row[s_demand]:
            opt_demand_red = this_demand_reduction
            opt_cost_red = this_cost_reduction
            opt_par = this_par
        elif "Act" in row[s_demand]:
            val = abs(opt_demand_red - this_demand_reduction)
            row[s_demand_reduction_diff] = "{0:.0f}%".format(val * 100)
            val = abs(opt_cost_red - this_cost_reduction)
            row[p_cost_reduction_diff] = "{0:.0f}%".format(val * 100)
            val = abs(opt_par - this_par)
            row[s_par_diff] = "{0:.2f}".format(val)
        df_all_others_ext = df_all_others_ext.append(row)

    # df_all_others_ext[s_par] \
    #     = pd.Series(["{0:.2f}".format(val) for val in df_all_others_ext[s_par]], index=df_all_others_ext.index)
    # df_all_others_ext[s_demand_reduction] \
    #     = pd.Series(["{0:.0f}%".format(val * 100) for val in df_all_others_ext[s_demand_reduction]],
    #                 index=df_all_others_ext.index)
    # df_all_others_ext[p_cost_reduction] \
    #     = pd.Series(["{0:.0f}%".format(val * 100) for val in df_all_others_ext[p_cost_reduction]],
    #                 index=df_all_others_ext.index)
    df_all_others_ext = df_all_others_ext.set_index([k_households_no, k_repeat, s_demand])
    df_all_others_ext.columns \
        = ["PAR", "Cost Reduction", "Demand Reduction",
           "PAR Distance", "Cost Reduction Distance", "Demand Reduction Distance"]
    df_all_others_ext = df_all_others_ext.stack().reset_index()

    df_all_others_ext.columns = ["#Households", "Repeat", "Demand Profile", "Result", "Value"]
    # df_all_others_ext.to_csv(f"combined_others.csv")
    # df_all_others_ext.to_latex(f"combined_others.tex", longtable=True,
    #                            caption=f"Schedule demonstration, reductions",
    #                            label=f"tab:multiple:exp:demon")

    df_all_others_desc = df_all_others_ext.groupby(["#Households", "Repeat", "Demand Profile", "Result"])\
        .agg(['min', 'mean', 'max'])

    print("Aggregated data. ")

print("Done.")
