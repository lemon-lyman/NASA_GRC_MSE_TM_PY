import pandas as pd
import numpy as np
import warnings


def hr_2_np(name, subject):
    # Loads heart rate data as pandas DataFrame and returns numpy array

    file = 'heartrate_data/HeartRate_' + subject + '.csv'
    df = pd.read_csv(file, index_col=0, header=[0, 1, 2])
    df = df.loc['1':, :]

    trial = name[12:15]
    volume = name[16:19]
    attempt_number = name[20]

    hr = df.loc[:, (trial, volume, attempt_number)].values
    hr = hr[~np.isnan(hr)]

    return hr


def plot_hr(ax, name, subject):
    # Add heart rate plot to provided axis

    hr = hr_2_np(name, subject)

    # hmin and hmax have been hardcoded to the maximum and minimum found across both subjects and across all trials up
    # to Fall 2018 in order for the axes across all plots to be consistent. This range will probably suffice for future
    # trials.
    hmin = 55
    hmax = 126
    warnings.warn('Warning: heart rate range has been hardcoded to 55-126 BPM')

    ax.plot(hr, c='r', zorder=1, alpha=.7)
    ax.set_ylim(hmin, hmax)
