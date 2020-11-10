import seaborn as sns
import pandas as pd
import pandas_bokeh as bk
from fw_ddsm.parameter import *
import matplotlib.pyplot as plt

def draw_graph(df_result, x_label, category_label, y_label, colours):
    df_result.columns = [x_label, category_label, y_label]
    plot = sns.relplot(x=x_label,
                       y=y_label,
                       # hue=category,
                       # style=category,
                       col=category_label,
                       col_wrap=2,
                       data=df_result,
                       aspect=1.5,
                       linewidth=3,
                       kind="line",
                       palette=colours)
    return plot

file = "02-50-32_overview.csv"

x_key = k_penalty_weight
category = m_algorithm
colours = "tab20c"

y_demand_reduction = s_demand_max + " reduction"
y_cost_reduction = p_cost + " reduction"
y_iteration = k_iteration_no
y_time = t_average
result_types = [y_demand_reduction, y_cost_reduction, y_iteration, y_time]
sns.set(font_scale=1.2)

df = pd.read_csv(f"{file}")
for y_key in result_types:

    x_label = "Inconvenience cost weight"
    category_label = "Algorithm"
    y_label = y_key.replace("_", " ").capitalize()

    category_values = set([x for x in df[category].values if "FW" in x])
    df_result = df[[x_key, category, y_key]].loc[(df[category].isin(category_values)) & (df[x_key] >= 1)]
    if y_key == y_time:
        y_label = "Pricing time (seconds)"
    plot = draw_graph(df_result, x_label, category_label, y_label, colours)
    plot.savefig(f"important/{y_key}.png")

    if y_key == y_time:
        category_values = set([x for x in df[category].values if "FW" not in x])
        df_result = df[[x_key, category, y_key]].loc[(df[category].isin(category_values)) & (df[x_key] >= 1)]
        y_label = "Scheduling time (seconds)"
        plot = draw_graph(df_result, x_label, category_label, y_label, colours)
        plot.savefig(f"important/{y_key}_scheduling.png")

    plt.show()

print("Done. ")
