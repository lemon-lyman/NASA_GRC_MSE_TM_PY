
"""
Creates event plot of both subjects involved in a dual-caregiver MSE trial.

Very similar to eventplot_single.py. Main difference is the style changes necessitated by stacking two plots on top of
each other. Another important difference: the program needs to know which subject has been labeled as which caregiver.
This effects what marker data is used in the cumulative_volume.py module in calculating cumulative convex volume.

Areas for improvement:
    This module is extremely similar to eventplot_single.py. There's a lot of duplicated code. There might be a better
    way to create single and dual caregiver plots within one module and cut down on number of files.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from observation import get_observation
from cumulative_volume import ongoing_vol
from heartrate import plot_hr


def find_cpr_levels(obv, cpr):
    # Finds that states during which CPR occurred so that the yellow compressions on the plot are overlaid at the same
    # vertical level

    levels = []
    for i in range(0, len(cpr), 2):
        height = [x for x in range(len(obv)-1) if (obv[x][0] <= cpr[i] and obv[x][1] >= cpr[i+1])]
        levels.append(height[0])
    return levels


def plot_event(file, calcs_per_second=3, top_subject='S07', bottom_subject='S08'):
    """
    Main Function
    """

    # Get data from BORIS observation. Only data pertaining to specified subject is returned
    states, obv = get_observation(file, specified_subject=top_subject)

    # If CPR occurred during trial, separate CPR into other variable
    cpr_exists = True
    try:
        try:
            cpr_ind = [states.index('CPR'), states.index('CPR single round')]
            del states[cpr_ind[1]]
            del obv[cpr_ind[1]]
        except ValueError:
            cpr_ind = [states.index('CPR')]
        cpr = obv[states.index('CPR')]

        del states[cpr_ind[0]]
        del obv[cpr_ind[0]]

    # CPR was not found in the BORIS data and did not occur during this trial
    except ValueError:
        cpr_exists = False
        print('ValueError: CPR is not in the list')

    color = ['b', 'm', 'peru', 'g', 'violet', 'orange', 'cyan']

    # Create figure
    fig, (ax1, ax3) = plt.subplots(2, 1, sharex='col', figsize=(15, 6))

    # Add horizontal lines representing the states
    for i in range(len(states)):

        # Retrieving/Returning is the only state that occurs more than once (so far) besides cpr. It needs its own
        # for-loop to iterate through all the instances of retrieving/returning.
        if i == len(states) - 1:
            for j in range(0, len(obv[-1]), 2):
                ax1.hlines(y=len(states) - i, xmin=obv[-1][j], xmax=obv[-1][j + 1], lw=28, colors='k', alpha=.8)

        # Plot all other states
        else:
            ax1.hlines(y=len(states) - i, xmin=obv[i][0], xmax=obv[i][1], lw=28, colors=color[i], alpha=.8)

    # Add yellow sections when cpr is being performed
    if cpr_exists:
        cpr_levels = find_cpr_levels(obv, cpr)
        for i in range(0, (2 * len(cpr_levels)) - 1, 2):
            ax1.hlines(y=len(states) - cpr_levels[int(i / 2)],
                       xmin=cpr[i], xmax=cpr[i + 1], lw=28, colors='yellow', alpha=.8)

    # Call ongoing_vol. Computationally expensive. As calcs_per_second is decreased, the convex volume will be
    # calculated less often and this function will execute more quickly.
    vol_arr, time_arr = ongoing_vol(file, calcs_per_second=calcs_per_second, caregiver=1)

    # Normalize volume so it fits just beneath the legend
    max_vol = max(vol_arr)
    vol_arr = [v * (len(states) - 1) for v in vol_arr]
    vol_arr = [v / max_vol for v in vol_arr]

    ax1.fill_between(time_arr, 0, vol_arr, alpha=.4, facecolor='blue', zorder=0, label='Convex Volume')

    # Plot heart rate on a duplicated axis
    try:
        ax2 = ax1.twinx()
        plot_hr(ax2, file, subject=top_subject)
        ax2.yaxis.label.set_color('r')
        ax2.tick_params('y', colors='r')
        ax2.set_ylabel('Heart Rate (BPM)', color='r')
    except KeyError:
        ax2.axis('off')
        print('Heart Rate plot unsuccessful')  # Most likely because heart rate wasn't gathered for this subject

    # Plotting parameters
    custom_lines = [Line2D([0], [0], color='blue', alpha=.4, lw=6),
                    Line2D([0], [0], color='r', lw=2),
                    Line2D([0], [0], color='yellow', alpha=.7, lw=9)]
    ax1.legend(custom_lines, ['Convex Volume', 'Heart Rate', 'Compressions'], loc='upper right')
    states[-1] = 'Retrieving/Returning' + '\n' + 'Equipment'  # Putting a newline in an excessively long string
    ax1.yaxis.set_ticks(np.arange(1, len(states)+1, 1))
    ax1.set_yticklabels(np.flip(states, axis=0), fontsize=10)
    ax1.margins(x=0)
    ax1.grid(True)
    ax1.set_ylim(0, len(states)+1)
    ax1.set_xlim(0, time_arr[-1])
    fig.suptitle(file)

    ax1.set_title(top_subject)

    ###########################################################################################################

    states, obv = get_observation(file, specified_subject=bottom_subject)

    # If CPR occurred during trial, separate CPR into other variable
    cpr_exists = True
    try:
        try:
            cpr_ind = [states.index('CPR'), states.index('CPR single round')]
            del states[cpr_ind[1]]
            del obv[cpr_ind[1]]
        except ValueError:
            cpr_ind = [states.index('CPR')]
        cpr = obv[states.index('CPR')]

        del states[cpr_ind[0]]
        del obv[cpr_ind[0]]
    except ValueError:
        cpr_exists = False
        print('ValueError: CPR is not in the list')

    # Add horizontal lines
    for i in range(len(states)):

        # Retrieving/Returning is the only state that occurs more than once (so far). It needs its own for-loop to
        # iterate through all the instances of retrieving/returning.
        if i == len(states) - 1:
            for j in range(0, len(obv[-1]), 2):
                ax3.hlines(y=len(states) - i, xmin=obv[-1][j], xmax=obv[-1][j + 1], lw=28, colors='k', alpha=.8)

        # Plot all other states
        else:
            ax3.hlines(y=len(states) - i, xmin=obv[i][0], xmax=obv[i][1], lw=28, colors=color[i], alpha=.8)

    # Add yellow sections when cpr is being performed
    if cpr_exists:
        cpr_levels = find_cpr_levels(obv, cpr)
        for i in range(0, (2 * len(cpr_levels)) - 1, 2):
            ax3.hlines(y=len(states) - cpr_levels[int(i / 2)],
                       xmin=cpr[i], xmax=cpr[i + 1], lw=28, colors='yellow', alpha=.8)

    # Call ongoing_vol. Computationally expensive. As calcs_per_second is decreased, the convex volume will be
    # calculated less often and this function will execute more quickly.
    vol_arr, time_arr = ongoing_vol(file, calcs_per_second=calcs_per_second, caregiver=2)

    # Normalize volume so it fits just beneath the legend
    max_vol = max(vol_arr)
    vol_arr = [v * (len(states) - 1) for v in vol_arr]
    vol_arr = [v / max_vol for v in vol_arr]

    ax3.fill_between(time_arr, 0, vol_arr, alpha=.4, facecolor='blue', zorder=0, label='Convex Volume')

    # Plot heart rate on a second axis
    try:
        ax4 = ax3.twinx()
        plot_hr(ax4, file, subject=bottom_subject)
        ax4.yaxis.label.set_color('r')
        ax4.tick_params('y', colors='r')
        ax4.set_ylabel('Heart Rate (BPM)', color='r')
    except KeyError:
        ax4.axis('off')
        print('Heart Rate plot unsuccessful')  # Most likely because heart rate wasn't gathered for this trial

    # Plotting parameters
    states[-1] = 'Retrieving/Returning' + '\n' + 'Equipment'  # Putting a newline in an excessively long string
    ax3.yaxis.set_ticks(np.arange(1, len(states)+1, 1))
    ax3.set_yticklabels(np.flip(states, axis=0), fontsize=10)
    ax3.margins(x=0)
    ax3.grid(True)
    ax3.set_ylim(0, len(states)+1)
    ax3.set_xlim(0, time_arr[-1])
    ax3.set_xlabel('Time (s)')
    ax3.set_title(bottom_subject)

    plt.show()


if __name__ == "__main__":

    # Times per second that the program stops to calculate cumulative convex volume. The lower the value, the faster
    # the program
    calcs_per_second = 2.0

    #############################################################################################################

    # Desired trial name goes here. A list of multiple trials can be used and program will iterate through trials
    # (plotting window must be closed in order for program to move on to the next trial).
    names = ['MVOL_S78_03_AC2_LSX_1']

    #############################################################################################################

    #############################################################################################################

    # Tell the program which subject acted as which caregiver. These will be the same assignments used when tracking
    # dual caregiver files in BTS.
    caregiver1 = 'S07'
    caregiver2 = 'S08'

    #############################################################################################################

    for name in names:
        plot_event(name, calcs_per_second=calcs_per_second, top_subject=caregiver1, bottom_subject=caregiver2)
