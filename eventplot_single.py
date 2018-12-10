
"""
Creates event plot of a single subject MSE trial.

Videos are played and annotated in BORIS software. These observations are exported as csv's. The csv's are not altered
before being used in this program. Plot includes heart rate, behaviors, and cumulative convex volume therefore it uses
heart rate data, BORIS observation data, and mo-cap data from BTS. It will work without heart rate and/or mo-cop data.
x axis is time. y axis are the different behaviors or 'states' that the subject is observed exhibiting.

Areas for improvement:
    The method for obtaining just the CPR states and then removing them from the states and time_list is not optimal.
    The states have to be defined in BORIS as the exact strings that the plot_events() functions is looking for
    e.g. 'CPR', and 'CPR single round'.

    Variable 'color', the list of colors, was filled with an arbitrary number of options for colors. It's possible that
    a procedure with a large number of sub-processes could exhaust these colors which would raise an error
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from observation import get_observation
from cumulative_volume import ongoing_vol
from heartrate import plot_hr


def find_cpr_levels(obv, cpr):
    # Finds the states during which CPR occurred so that the yellow compressions on the plot are overlaid at the same
    # vertical level

    levels = []
    for i in range(0, len(cpr), 2):
        height = [x for x in range(len(obv)-1) if (obv[x][0] <= cpr[i] and obv[x][1] >= cpr[i+1])]
        levels.append(height[0])
    return levels


def plot_events(name, calcs_per_second=5.0):
    """
    Main Function
    """

    subject = name[5:8]

    # Get data from BORIS observation. Only data pertaining to specified subject is returned
    states, time_list = get_observation(name)

    # If CPR occurred during trial, separate CPR into other variable
    cpr_exists = True
    try:
        try:
            cpr_ind = [states.index('CPR'), states.index('CPR single round')]
            del states[cpr_ind[1]]
            del time_list[cpr_ind[1]]
        except ValueError:
            cpr_ind = [states.index('CPR')]
        cpr = time_list[states.index('CPR')]

        del states[cpr_ind[0]]
        del time_list[cpr_ind[0]]

    # CPR was not found in the BORIS data and did not occur during this trial
    except ValueError:
        cpr_exists = False
        print('ValueError: CPR is not in the list')

    color = ['b', 'm', 'peru', 'g', 'violet', 'orange', 'cyan', 'dimgrey', 'r', 'lime', 'magenta']

    # Create figure
    fig, ax1 = plt.subplots(figsize=(15, 6))

    # Add horizontal lines representing the states
    for i in range(len(states)):

        # Retrieving/Returning is the only state that occurs more than once (so far). It needs its own for-loop to
        # iterate through all the instances of retrieving/returning.
        if i == len(states)-1:
            for j in range(0, len(time_list[-1]), 2):
                ax1.hlines(y=len(states)-i, xmin=time_list[-1][j], xmax=time_list[-1][j+1], lw=28, colors='k', alpha=.8)

        # Plot all other states
        else:
            ax1.hlines(y=len(states)-i, xmin=time_list[i][0], xmax=time_list[i][1], lw=28, colors=color[i], alpha=.8)

    # Add yellow sections when cpr is being performed
    if cpr_exists:
        cpr_levels = find_cpr_levels(time_list, cpr)
        for i in range(0, (2*len(cpr_levels))-1, 2):
            ax1.hlines(y=len(states)-cpr_levels[int(i/2)],
                       xmin=cpr[i], xmax=cpr[i+1], lw=28, colors='yellow', alpha=.8)

    # Call ongoing_vol. Computationally expensive. As calcs_per_second is decreased, the convex volume will be
    # calculated less often and this function will execute more quickly.
    try:
        vol_arr, time_arr = ongoing_vol(name, calcs_per_second=calcs_per_second)

        # Normalize volume so it fits just beneath the legend
        max_vol = max(vol_arr)
        vol_arr = [v*(len(states)-1) for v in vol_arr]
        vol_arr = [v/max_vol for v in vol_arr]

        ax1.fill_between(time_arr, 0, vol_arr, alpha=.4, facecolor='blue', zorder=0, label='Convex Volume')
    # In case tracked mo cop file is not found
    except FileNotFoundError:
        print('FileNotFoundError: Tracked marker data file not found')

    # Plot heart rate on a second axis
    try:
        ax2 = ax1.twinx()
        plot_hr(ax2, name, subject=subject)
        ax2.yaxis.label.set_color('r')
        ax2.tick_params('y', colors='r')
        ax2.set_ylabel('Heart Rate (BPM)', color='r')
    except KeyError:
        ax2.axis('off')
        print('Heart Rate plot unsuccessful')  # Most likely because heart rate wasn't gathered for this trial

    # Plotting parameters
    custom_lines = [Line2D([0], [0], color='blue', alpha=.4, lw=6),
                    Line2D([0], [0], color='r', lw=2),
                    Line2D([0], [0], color='yellow', alpha=.7, lw=9)]
    ax1.legend(custom_lines, ['Convex Volume', 'Heart Rate', 'Compressions'], loc='upper right')
    ax1.set_title(name)
    ax1.set_xlabel('Time (s)')
    ax1.yaxis.set_ticks(np.arange(1, len(states)+1, 1))
    states[-1] = 'Retrieving/Returning' + '\n' + 'Equipment'  # Putting a newline in an excessively long string
    ax1.set_yticklabels(np.flip(states, axis=0), fontsize=10)
    ax1.margins(x=0)
    ax1.grid(True)
    ax1.set_ylim(0, len(states)+1)
    try:
        ax1.set_xlim(0, time_arr[-1])
    except NameError:
        print('Warning: no tracked marker data file found. x axis has default margins')

    plt.show()


if __name__ == "__main__":

    # Times per second that the program stops to calculate cumulative convex volume. The lower the value, the faster
    # the program
    calcs_per_second = 1.5

    #############################################################################################################

    # Desired trial name goes here. A list of multiple trials can be used and program will iterate through trials
    # (plotting window must be closed in order for program to move on to the next trial).
    names = ['MVOL_S08_02_CPU_RFT_1', 'MVOL_S08_05_ADA_RVL_1']

    #############################################################################################################

    for name in names:
        plot_events(name, calcs_per_second=calcs_per_second)
