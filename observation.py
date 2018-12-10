import pandas as pd
import numpy as np


def get_observation(name, specified_subject=False):
    # Load observations made in BORIS. Returns list containing names of all the states and list containing start/stop
    # times of all the states

    file = 'boris_data/' + name + '.csv'
    df = pd.read_csv(file, header=15, delimiter=',', skipinitialspace=True,
                     encoding="utf-8-sig")[['Time', 'Subject', 'Behavior']]

    # Specified subject == 'None' when plot for single caregiver trial is being created. In that case, all the BORIS
    # data applies to the plot. However, in dual caregiver trials, a subject has to be specified so that just the
    # relevant data can be pulled from the BORIS observation.
    if specified_subject:
        data = df.loc[df['Subject'] == specified_subject][['Time', 'Behavior']]
    else:
        data = df.loc[:, ['Time', 'Behavior']]

    states = np.unique(data.values[:, 1])  # Get name of states. np.unique() avoids duplicates

    temp_list = data.values.tolist()
    
    values = sorted(set(map(lambda x: x[1], temp_list)))
    time_list = [[y[0] for y in temp_list if y[1] == x] for x in values]

    # Format of states: [state, state, state, state...]
    # Format of time_list: [[start_time, stop_time], [start_time, stop_time, start_time, stop_time... ]... ]
    return states.tolist(), time_list
