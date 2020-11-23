from multiprocessing import freeze_support
from fw_ddsm.iteration import *
from fw_ddsm.output import *
from pandas import DataFrame

algorithms = dict()
algorithms[m_minizinc] = dict()
algorithms[m_minizinc][m_before_fw] = m_minizinc
algorithms[m_minizinc][m_after_fw] = f"{m_minizinc}_fw"
algorithms[m_ogsa] = dict()
algorithms[m_ogsa][m_before_fw] = m_ogsa
algorithms[m_ogsa][m_after_fw] = f"{m_ogsa}_fw"

num_repeat = 1
# num_households_range = [50, 100, 500, 1000, 1500, 2000, 4000, 6000, 8000, 10000]
num_households_range = [5000]
penalty_weight_range = [1]
num_tasks_dependent_range = [0, 1, 3, 6, 9]
num_full_flex_tasks_min = 0
num_full_flex_tasks_max = 0
num_semi_flex_tasks = 10
num_fixed_tasks = 0
num_samples = 5
ensure_dependent = True
num_cpus = 100


def main():
    experiment_tracker = dict()
    num_experiment = -1
    out = Output(output_root_folder="results")

    for r in range(num_repeat):
        for num_households in num_households_range:
            new_data = True

            for penalty_weight in penalty_weight_range:

                for num_tasks_dependent in num_tasks_dependent_range:

                    print("----------------------------------------")
                    print(f"{num_households} households, "
                          f"{num_tasks_dependent} dependent tasks, "
                          f"at least {num_full_flex_tasks_min} fully flexible tasks, "
                          f"{num_semi_flex_tasks} semi-flexible tasks, "
                          f"{num_fixed_tasks} fixed tasks, "
                          f"{penalty_weight} penalty weight. ")
                    print("----------------------------------------")

                    new_iteration = Iteration()
                    output_folder, output_parent_folder, this_date_time \
                        = out.new_output_folder(num_households=num_households,
                                                num_dependent_tasks=num_tasks_dependent,
                                                num_full_flex_task_min=num_full_flex_tasks_min,
                                                num_semi_flex_task_min=num_semi_flex_tasks,
                                                inconvenience_cost_weight=penalty_weight,
                                                folder_id=r)
                    plots_demand_layout = []
                    plots_demand_finalised_layout = []
                    for alg in algorithms.values():
                        num_experiment += 1
                        experiment_tracker[num_experiment] = dict()
                        experiment_tracker[num_experiment][k_households_no] = num_households
                        experiment_tracker[num_experiment][k_penalty_weight] = penalty_weight
                        experiment_tracker[num_experiment][k_dependent_tasks_no] = num_tasks_dependent
                        experiment_tracker[num_experiment][h_tasks_no_ff_min] = num_full_flex_tasks_min
                        experiment_tracker[num_experiment][h_tasks_no_sf_min] = num_semi_flex_tasks
                        experiment_tracker[num_experiment][h_tasks_no_fixed_min] = num_fixed_tasks
                        experiment_tracker[num_experiment][m_algorithm] = alg[m_after_fw]
                        experiment_tracker[num_experiment]["id"] = r

                        # 1. iteration data
                        if new_data:
                            preferred_demand_profile, prices = \
                                preferred_demand_profile, prices = \
                                new_iteration.new(algorithm=alg, num_households=num_households,
                                                  max_demand_multiplier=maximum_demand_multiplier,
                                                  num_tasks_dependent=num_tasks_dependent,
                                                  ensure_dependent=ensure_dependent,
                                                  full_flex_task_min=num_full_flex_tasks_min,
                                                  full_flex_task_max=num_full_flex_tasks_max,
                                                  semi_flex_task_min=num_semi_flex_tasks, semi_flex_task_max=0,
                                                  fixed_task_min=num_fixed_tasks, fixed_task_max=0,
                                                  inconvenience_cost_weight=penalty_weight,
                                                  max_care_factor=care_f_max,
                                                  data_folder=output_parent_folder,
                                                  date_time=this_date_time)
                            new_data = False
                        else:
                            if m_ogsa in alg:
                                num_tasks_dependent = None
                            preferred_demand_profile, prices = \
                                new_iteration.read(algorithm=alg, inconvenience_cost_weight=penalty_weight,
                                                   new_dependent_tasks=num_tasks_dependent,
                                                   ensure_dependent=ensure_dependent,
                                                   read_from_folder=output_parent_folder,
                                                   date_time=this_date_time)

                        # 2. iteration begins
                        start_time_probability = new_iteration.begin_iteration(starting_prices=prices,
                                                                               num_cpus=num_cpus)
                        # 3. finalising schedules
                        new_iteration.finalise_schedules(num_samples=num_samples,
                                                         start_time_probability=start_time_probability)

                        # 4. preparing plots and writing results to CSVs
                        plots_demand, plots_demand_finalised, overview_dict \
                            = out.save_to_output_folder(algorithm=alg,
                                                        aggregator_tracker=new_iteration.aggregator.tracker,
                                                        aggregator_final=new_iteration.aggregator.final,
                                                        community_tracker=new_iteration.community.tracker,
                                                        community_final=new_iteration.community.final)
                        plots_demand_layout.append(plots_demand)
                        plots_demand_finalised_layout.append(plots_demand_finalised)
                        experiment_tracker[num_experiment].update(overview_dict)

                    # 5. drawing all plots
                    output_file(f"{output_folder}{this_date_time}_plots.html")
                    tab1 = Panel(child=layout(plots_demand_layout), title="FW-DDSM results")
                    tab2 = Panel(child=layout(plots_demand_finalised_layout), title="Actual schedules")
                    save(Tabs(tabs=[tab2, tab1]))

                    # 6. writing experiment overview
                    DataFrame.from_dict(experiment_tracker).transpose() \
                        .to_csv(r"{}{}_overview.csv".format(output_parent_folder, this_date_time))
                    with open(f"{out.output_parent_folder}data/{this_date_time}_{file_experiment_pkl}",
                              'wb+') as f:
                        pickle.dump(experiment_tracker, f, pickle.HIGHEST_PROTOCOL)
                    print("----------------------------------------")

    # print("------------------------------")
    print("Experiment is finished. ")
    print(experiment_tracker)

    # plots_experiment = []
    # df_experiments = DataFrame.from_dict(experiment_tracker).transpose()
    # df_scheduling_times = df_experiments[k_households_no, t_scheduling, k_penalty_weight, k_dependent_tasks_no]
    # df_pricing_times = df_experiments[k_households_no, t_pricing, k_penalty_weight, k_dependent_tasks_no]
    # df_par = df_experiments[k_households_no, s_par_init, s_par, k_penalty_weight, k_dependent_tasks_no]
    # df_demand_reductions = df_experiments[k_households_no, s_demand_reduction, k_penalty_weight, k_dependent_tasks_no]
    # df_cost_reductions = df_experiments[k_households_no, p_cost_reduction, k_penalty_weight, k_dependent_tasks_no]

    # time and reductions per number of household
    # time and reduction per care factors (same number of households)
    # time and reduction per number of h1000-sft10-dt039-r1 tasks (same number of households and same care factor)


if __name__ == '__main__':
    freeze_support()
    main()
