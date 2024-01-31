import os
import json
import matplotlib.pyplot as plt
import numpy as np
import sys


#iterate over all the folders in /res
for folder in os.listdir("res/"):
    path="res/"+folder+"/"

    data = {}

    for instance in os.listdir(path):
        if instance.endswith('.json'):
            with open(path+instance, 'r') as f:
                data[instance] = json.load(f)

    # Create a dictionary to store data
    data_dict = {}

    # Populate the dictionary with data
    for instance in data:
        for solver in data[instance]:
            if solver not in data_dict:
                data_dict[solver] = {'instances': [], 'times': []}
            if data[instance][solver]['optimal']: #save result ONLY FOR OPTIMAL SOLUTIONS (remove if you want to save all results)
                data_dict[solver]['instances'].append(str(instance).removesuffix('.json'))
                data_dict[solver]['times'].append(data[instance][solver]['time'])

    # Create a bar plot for each solver
    # Calculate the number of solvers
    num_solvers = len(data_dict.keys())
    # Adjust the bar width based on the number of solvers
    bar_width = 1.2 / (num_solvers + 1)

    opacity = 0.8
    index = np.arange(len(data_dict[list(data_dict.keys())[0]]['instances']))

    for i, solver in enumerate(data_dict.keys()):
        # Fill missing values with 300
        if len(data_dict[solver]['times']) < len(index):
            data_dict[solver]['times'].extend([300] * (len(index) - len(data_dict[solver]['times'])))
        plt.bar(index + i * bar_width, data_dict[solver]['times'], bar_width, alpha=opacity, label=solver)

    plt.xlabel('Instance')
    plt.ylabel('Time')
    plt.xticks(index + bar_width, data_dict[list(data_dict.keys())[0]]['instances'])
    plt.legend()
    plt.title('Time plot for ' + folder+"\n(only instances with at least one optimal solution)")

    plt.tight_layout()
    plt.savefig('time_plots/time_plot_'+folder+'.png')  # Save the plot before showing it
    print('time_plot_'+folder+'.png saved')

    #clear dictionaries and plot for next iteration
    data_dict.clear()
    data.clear()
    plt.clf()

