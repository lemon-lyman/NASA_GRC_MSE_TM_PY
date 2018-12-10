from scipy.spatial import ConvexHull
import numpy as np
import pandas as pd


def find_second_start(df):
    # Only for dual caregiver trials. Finds the beginning of the second caregiver data in the csv. Assumes that columns
    # are ordered first caregiver markers, followed by table markers, followed by second caregiver markers. Returns int
    # index

    cols = df.columns
    try:
        end_ind = cols.get_loc('TAB4f.Z')
    except KeyError:
        end_ind = cols.get_loc('TAB4.Z')

    start_ind = end_ind + 1

    return start_ind


def get_cols(file, caregiver):
    # Load marker data as Pandas DataFrame. This is similar to get_markers() in heatmap.py but more verbose because
    # table and frame markers cannot be loaded with body-markers. We are only interested in the volume created by body-
    # markers so everything else is cut off.
    
    df = pd.read_csv(file, header=10, delimiter=',', skipinitialspace=True, encoding="utf-8-sig")

    # Assumes columns are ordered body-markers, then frame, then table. Or, if there was no frame, body-markers, then
    # table.
    try:
        try:
            boundary = df.columns.get_loc("FRM1f.X")
        except KeyError:
            boundary = df.columns.get_loc("TAB1f.X")
    except KeyError:
        try:
            boundary = df.columns.get_loc("FRM1.X")
        except KeyError:
            boundary = df.columns.get_loc("TAB1.X")

    # Use boundaries to extract relevant marker data
    if caregiver:
        if caregiver == 2:
            data = df.values[:, find_second_start(df):]
        else:
            data = df.values[:, 2:boundary]
    else:
        data = df.values[:, 2:boundary]

    # Replace all nan values with mean of body markers at that time step. These replacement values will not breach the
    # convex hull.
    x = data[:, 0::3]
    y = data[:, 1::3]
    z = data[:, 2::3]

    # Find mean of dimension at every time step
    x_mean = np.nanmean(x, axis=1)
    y_mean = np.nanmean(y, axis=1)
    z_mean = np.nanmean(z, axis=1)

    # Find indices of all nan values
    ind_x = np.where(np.isnan(x))
    ind_y = np.where(np.isnan(y))
    ind_z = np.where(np.isnan(z))

    # Replace all nans with mean
    x[ind_x] = np.take(x_mean, ind_x[1])
    y[ind_y] = np.take(y_mean, ind_y[1])
    z[ind_z] = np.take(z_mean, ind_z[1])

    # Reshape to (n, 3) where n is number of
    data = np.dstack((x, y, z))
    row, col, *rest = data.shape
    data = data.reshape(row*col, 3)
    
    dt = float(df.iloc[1]['Time'])
    
    return data, col, row, dt


def ongoing_vol(name, calcs_per_second=5, caregiver=False):
    # Main function. Takes in trial name, how many times a second convex volume should be calculated, and caregiver: a
    # parameter only to be used in dual caregiver trials. Returns list of cumulative volume calculations over time array

    # Get marker data
    file = 'tracked_data/' + name + '_tracked.csv'
    data, col, row, dt = get_cols(file, caregiver)

    # Convert calculations per second to the index interval at which the convex volume algorithm must be run. Not exact.
    time_between = 1 / calcs_per_second
    interval = round(time_between / dt)

    # Create convexhull at each interval and calculate its volume. This is the computationally expensive part.
    vol = [ConvexHull(data[0:i:int(1/dt)]).volume for i in range(interval*col, len(data) + interval*col, interval*col)]

    # Create corresponding time array to be plotted against
    time = np.arange(0, int(len(data)/col), interval)
    time = time * dt
    return vol, time
