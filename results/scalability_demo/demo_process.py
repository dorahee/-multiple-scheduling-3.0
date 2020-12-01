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
k_demand_type= "Type"
k_repeat = "Repeat"
k_tpd = "TDP"

# combine data
df_all = pd.DataFrame()
for r in repeat_numbers:
    for h in household_numbers:
        for k, v in algorithms.items():
            folder_name = f"h{h}-w5-dt3-fft10-sft0-id{r}"

            # get before and after
            file_demands_name = f"{k}_aggregator_demands.csv"
            df = pd.read_csv(f"{folder_name}/{file_demands_name}").transpose()
            df = df.iloc[[1, -1], 1:].reset_index(drop=True)
            df[k_households_no] = h
            df[m_algorithm] = v
            df[s_demand] = ["Preferred", types[k]]
            df[k_demand_type] = types[k]
            df[k_repeat] = r
            df[k_tpd] = f"Preferred and {types[k].lower()}"
            df = df.set_index([k_repeat, m_algorithm, k_households_no, s_demand, k_demand_type, k_tpd]).stack().reset_index()
            df.columns = ["Repeat", "Method", "#Households", "Demand Profile", k_demand_type, k_tpd, "Period", "Demand (kWh)"]
            df_all = df_all.append(df)

            # get all samples
            file_final_name = f"{k}_aggregator_demands_final.csv"
            df = pd.read_csv(f"{folder_name}/{file_final_name}").transpose()
            df = df.iloc[2:, :].reset_index()
            df[k_households_no] = h
            df[m_algorithm] = v
            df[k_demand_type] = "Actual"
            df[k_repeat] = r
            df[k_tpd] = "Actual"
            df = df.set_index([k_repeat, m_algorithm, k_households_no, "index", k_demand_type, k_tpd]).stack().reset_index()
            df.columns = ["Repeat", "Method", "#Households", "Demand Profile", k_demand_type, k_tpd, "Period", "Demand (kWh)"]
            df_all = df_all.append(df)

# draw graphs for each repeat
for alg in algorithms.values():
    df_alg = df_all[df_all["Method"] == alg]
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
            # plt.show()
            print(f"Saved {alg}_demo_1000_{k}_r{r}.png.")

print("Done.")
