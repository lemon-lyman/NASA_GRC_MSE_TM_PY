
"""
Creates plot of MSE trials. Marker data has been obtained from the BTS system, tracked in BTS SMART tacker, exported as
.emt, and saved as .csv, and stored in 'tracked_data/'.

Plot contains four subplots:
TL - viewing testing area from the front (-x)   TR - viewing testing area from the side (+z)
BL - viewing testing area from the top (-y)   BR - feet data only, viewing testing area from the top (-y)

Margins of the plots are created case-by-case so they will change between trials and the location of the
table/frame/origin will change with them.

Areas for improvement:
    Each time marker data is needed, a csv is read and the desired markers/columns are extracted. All of the get
    functions (get_feet, get_table...) read the csv every time they are called. A more streamlined script would read the
    csv once per execution and then the get functions would access this variable that's already been created and pull
    the columns they need. However, reading the csv multiple times takes very little time.

    Figure out how to make each subplot a true 1:1 ratio since we are representing spatial data. Currently the axes are
    slightly different. This is complicated because plots are being created over images that are being shown. The 1:1
    ratio might have to be created when the image is generated
"""


import numpy as np
import pandas as pd
from copy import copy
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from matplotlib import patches
from matplotlib.lines import Line2D
import matplotlib.patheffects as pe
from observation import get_observation


def plot_bounds(ax, bounds, view, bound_color, alpha=1.0):
    # Plot boundaries of body-marker data over heatmap. These bounds were found and stored as min/max x, y, and z as
    # opposed to 8 x, y, and z points. A rectangle patch is the easiest to create with data in this form

    x, y, z = bounds
    line_width = 3
    z_order = 10

    # Create then add patch
    if view == 'side':
        p = patches.Rectangle((x[0], y[0]), x[1]-x[0], y[1]-y[0],
                              zorder=z_order, fill=False, linewidth=line_width, edgecolor=bound_color)
        ax.add_patch(p)

    elif view == 'top':
        p = patches.Rectangle((z[0], x[0]), z[1]-z[0], x[1]-x[0],
                              zorder=z_order, fill=False, linewidth=line_width, edgecolor=bound_color, alpha=alpha)
        ax.add_patch(p)

    else:
        p = patches.Rectangle((z[0], y[0]), z[1]-z[0], y[1]-y[0],
                              zorder=z_order, fill=False, linewidth=line_width, color=bound_color)
        ax.add_patch(p)


def plot_table(ax, tab, tab_color, alpha=1.0):
    # Plot Table over heatmap

    line_width = 2
    edge_color = 'k'
    z_order = -1

    # Create then add patch
    p = patches.Rectangle((tab[5], tab[3]), tab[2]-tab[5], tab[6]-tab[3],
                          zorder=z_order, linewidth=line_width, edgecolor=edge_color, facecolor=tab_color, alpha=alpha)
    ax.add_patch(p)


def plot_part(part, part_color, ax1, ax2, ax3, ax4):
    # Plot partition over heatmap

    # Frame is 1.93 meters top to bottom. This height is subtracted from measured height of markers on top of the frame
    # to find the bottom of the frame on the ground. Measured y value is relative to origin (on force plate) not the
    # ground
    height_of_part = 1.93
    top_of_part = part[1::3].mean()
    ground = top_of_part - height_of_part
    line_width = 3
    transparency = 1

    ax1.plot([part[0, 2], part[0, 2]], [ground, part[0, 1]], c=part_color, linewidth=line_width, alpha=transparency)
    ax1.plot([part[2, 2], part[2, 2]], [ground, part[2, 1]], c=part_color, linewidth=line_width, alpha=transparency)
    ax2.plot([part[1, 0], part[1, 0]], [ground, part[1, 1]], c=part_color, linewidth=line_width, alpha=transparency)
    ax2.plot([part[2, 0], part[2, 0]], [ground, part[2, 1]], c=part_color, linewidth=line_width, alpha=transparency)
    ax3.plot(part[:, 2], part[:, 0], c=part_color, linewidth=line_width, alpha=transparency)
    ax3.plot([part[-1, 2], part[0, 2]], [part[-1, 0], part[0, 0]], c=part_color, linewidth=line_width, alpha=transparency)
    ax4.plot(part[:, 2], part[:, 0], c=part_color, linewidth=line_width, alpha=transparency)
    ax4.plot([part[-1, 2], part[0, 2]], [part[-1, 0], part[0, 0]], c=part_color, linewidth=line_width, alpha=transparency)


def get_markers(file):
    # Load marker data as Pandas DataFrame. Returns DataFrame so that remove_reach can still be run

    # Possible area for improvement: .emt files were used to create .csv files for all our trials in the Fall of 2018.
    # However, .trc files could've been used. Main difference between .trc and .emt files when stored as .csv files are
    # the headers. Someone familiar with multi-indexing in Pandas could take advantage of the headers in .trc to
    # immediately read data into orderly 5dimensional (time, marker_name, [x, y, z]) data that might be easier to work
    # with and would avoid all the reshaping, stacking etc. that is necessary later on
    data = pd.read_csv(file, header=10, delimiter=',', index_col=1, skipinitialspace=True, encoding="utf-8-sig")

    return data


def get_feet(file):
    # Load marker data for feet as Pandas DataFrame. Returns DataFrame so that remove_reach can still be run

    data = pd.read_csv(file, header=10, delimiter=',', index_col=1, skipinitialspace=True, encoding="utf-8-sig")

    # Searches headers for any header containing one of these string which are only found in feet names (for the moment)
    # Quick and pythonic way to obtain all the names of feet columns without explicitly listing them
    feet_types = ['HEE', 'ANM', 'ANL', 'TOT']
    cols = data.columns
    feet_names = [col for col in cols if any(ftype in col for ftype in feet_types)]

    return data[feet_names]


def get_part(file):
    # Load marker data for partitions as Pandas DataFrame. Returns Numpy array.

    # Explicitly list names here unlike get_feet since we don't need all columns containing 'FRM', just the four markers
    # on the top of the frame.
    part = ['FRM9.X', 'FRM9.Y', 'FRM9.Z', 'FRM10.X', 'FRM10.Y', 'FRM10.Z',
            'FRM11.X', 'FRM11.Y', 'FRM11.Z', 'FRM12.X', 'FRM12.Y', 'FRM12.Z']
    partf = ['FRM9f.X', 'FRM9f.Y', 'FRM9f.Z', 'FRM10f.X', 'FRM10f.Y', 'FRM10f.Z',
             'FRM11f.X', 'FRM11f.Y', 'FRM11f.Z', 'FRM12f.X', 'FRM12f.Y', 'FRM12f.Z']
    try:
        data = pd.read_csv(file, header=10, delimiter=',', index_col=False,
                           skipinitialspace=True, usecols=part, encoding="utf-8-sig")[part]
    except ValueError:
        data = pd.read_csv(file, header=10, delimiter=',', index_col=False,
                           skipinitialspace=True, usecols=partf, encoding="utf-8-sig")[partf]

    # The partitions should be fixed but in practice they can be bumped around and sometimes at the beginning or end of
    # trials they are moved while BTS is still recording mocap data. For this reason, the average of all x, y, z for the
    # partition is returned here to give a better representation of where the partitions were
    return np.nanmean(data.values, axis=0)


def get_table(file):
    # Load marker data for table as Pandas DataFrame. Returns Numpy array

    data = pd.read_csv(file, header=10, delimiter=',', index_col=1, skipinitialspace=True, encoding="utf-8-sig")

    # Searches headers for any header containing 'TAB'. Same approach as get_feet
    cols = data.columns
    table = [col for col in cols if 'TAB' in col]

    # For the same reason as the partitions in get_part(), the average values are returned here
    return np.nanmean(data[table].values, axis=0)


def get_bounds(name, subject, care_only=False):
    # Load bounding box (min/max x, y, z) for subject as Pandas DataFrame

    if care_only:
        file = 'volume_data/S' + str(subject) + '_VOL_CareOnly.csv'
    else:
        file = 'volume_data/S' + str(subject) + '_VOL.csv'

    df = pd.read_csv(file, delimiter=',', header=0, index_col=0)

    df.loc[name]['Xmin':'Zmax'].apply(float)  # Otherwise a string is returned
    bounds_df = df.loc[name]['Xmin':'Zmax']
    bounds_np = bounds_df.values
    bounds_stacked = np.stack((bounds_np[:3], bounds_np[3:]), axis=1)
    bounds = bounds_stacked.astype(np.float)/1000  # Convert from millimeters

    return bounds


def remove_reach(name, df):
    # Removes marker data during period when subject was observed retrieving/returning supplies. Observations are made
    # in BORIS and stored in .csv's. Returns DataFrame with periods during retrieving/returning removed.

    states, time_list = get_observation(name)
    reach = time_list[-1]
    raw_ind = np.array(df.index)
    ind = []

    for r in reach:
        ind.append(np.where(raw_ind < r)[0][-1])

    full = np.array([])

    for i in range(0, len(ind), 2):
        full = np.append(full, np.arange(ind[i], ind[i + 1] + 1))

    data = df.drop(df.index[full.astype(int)])

    return data


def create_heatmap(ax, x, y, resolution, x_range, y_range, palette, v_max):
    # Creates numpy histogram from x, y data and shows that on given axis as an image.

    heatmap, x_edges, y_edges = np.histogram2d(x, y, bins=resolution, range=[x_range, y_range])

    extent = [x_edges[0], x_edges[-1], y_edges[0], y_edges[-1]]

    ax.imshow(heatmap.T, cmap=palette, extent=extent, origin='lower', aspect="auto",
              norm=colors.SymLogNorm(linthresh=0.01, vmin=1, vmax=v_max))


def plot_heatmap(name, care_only=False):
    """
    Main Function
    """

    print(name)

    # Path to tracked data
    file = 'tracked_data/' + name + '_tracked.csv'
    df = get_markers(file)

    # Remove reach
    if care_only:
        rws1, cls1 = df.shape
        df = remove_reach(name, df)
        rws2, cls2 = df.shape
        print('Reach loss: %' + str(100 * (rws1 - rws2) / rws1)[:5] + ' -', (rws1 - rws2))

    # DataFrame has structure (time, columns) where columns are individual dimensions of markers: [HEAD.X, HEAD.Y,
    # HEAD.Z, RFHD.X, ...]. Therefore, DataFrame has to be sliced, stacked, and shaped in order to get data into x, y,
    # and z columns. As mentioned before, this is an area for improvement. However, it is not computationally expensive.
    raw_values = df.values[:, 1:]
    rws1, cls1 = raw_values.shape

    raw_x = raw_values[:, 0::3].flatten()
    raw_y = raw_values[:, 1::3].flatten()
    raw_z = raw_values[:, 2::3].flatten()

    # All x, y, z points containing a nan value are removed from data. To this, data is separated into x, y, z vectors
    # and then stacked shaped into (n, 3) where n is the number of points across the whole trial. Nan values are mostly
    # a problem with unfiltered data.
    data = np.stack((raw_x, raw_y, raw_z), axis=-1)
    data = data[~np.any(np.isnan(data), axis=1)]

    rws2, cls2 = data.shape
    print('Nan loss: %' + str(100 * ((rws1 * cls1) - (rws2 * cls2)) / (rws1 * cls1))[:5] + ' -',
          ((rws1 * cls1)-(rws2 * cls2)), 'points')
    print()

    # Back into x, y, z vectors
    x = data[:, 0]
    y = data[:, 1]
    z = data[:, 2]

    tab = get_table(file)  # Get row of table data fom trial
    boundaries = get_bounds(name, name[6:8], care_only=care_only)  # Get bounding box of subject for trial

    # Max x, y, and z coordinates are found, whether it be the table, partition, or body marker, and are padded by
    # margin_pad. To make the x and z axes equal, the minimum min and the maximum max between the two are found and
    # used for both the x and z axes.
    margin_pad = .15
    x_range, y_range, z_range = [[np.array([x.min(), z.min()]).min()-margin_pad,
                                  np.array([x.max(), z.max()]).max()+margin_pad],

                                 [y.min()-margin_pad,
                                  y.max()+margin_pad],

                                 [np.array([x.min(), z.min()]).min()-margin_pad,
                                  np.array([x.max(), z.max()]).max()+margin_pad]]

    # Create figure
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, sharex='col', sharey='row', figsize=(9, 8))

    if care_only:
        fig.suptitle(name[:21] + ' Care Only', x=.5, y=1)
    else:
        fig.suptitle(name[:21], x=.5, y=1)

    # Style parameters
    resolution = 200

    # v_max sets a maximum 'brightness' to heat map. Some markers stay in same place for entire trial (table, partition)
    # becoming extremely bright and the spectrum becomes compressed and less detailed at the lower end: body-markers,
    # the important end. v_max forces all values above v_max down to v_max and more diversity is seen in the lower
    # ranges
    v_max = 400
    
    table_color = 'silver'
    part_color = 'blue'
    bound_color = 'r'

    # viridis is the choice of color scale for the marker data.
    # See https://matplotlib.org/examples/color/colormaps_reference.html
    palette = copy(plt.cm.viridis)

    # Sets the background (all bins with zero occurrences) to white
    palette.set_under('w', 0)

    # Front
    create_heatmap(ax1, z, y, resolution, z_range, y_range, palette, v_max)

    ax1.set_title('Front')
    ax1.set_ylabel('Y (m)')
    ax1.plot([tab[2], tab[5]], [tab[7], tab[10]], c=table_color, linewidth=3,
             path_effects=[pe.Stroke(linewidth=6, foreground='k'), pe.Normal()])
    plot_bounds(ax1, boundaries, view='front', bound_color=bound_color)

    # Side
    create_heatmap(ax2, x, y, resolution, x_range, y_range, palette, v_max)

    ax2.set_title('Side')
    ax2.xaxis.labelpad = 3
    ax2.plot([tab[0], tab[-3]], [tab[1], tab[-2]], zorder=0, c=table_color, linewidth=3,
             path_effects=[pe.Stroke(linewidth=6, foreground='k'), pe.Normal()])
    plot_bounds(ax2, boundaries, view='side', bound_color=bound_color)
    ax2.xaxis.set_tick_params(labelbottom=True)
    ax2.set_xlabel('X (m)')

    # Top
    create_heatmap(ax3, z, x, resolution, z_range, x_range, palette, v_max)

    ax3.set_title('Top')
    ax3.set_ylabel('X (m)')
    ax3.set_xlabel('Z (m)')
    plot_table(ax3, tab, table_color)
    plot_bounds(ax3, boundaries, view='top', bound_color=bound_color)
    ax3.yaxis.set_tick_params(labelbottom=True)

    # Re-gathering data for feet-only
    df = get_feet(file)

    if care_only:
        df = remove_reach(name, df)

    # Same process for removing nan values as before
    raw_values = df.values
    raw_x = raw_values[:, 0::3].flatten()
    raw_y = raw_values[:, 1::3].flatten()
    raw_z = raw_values[:, 2::3].flatten()
    data = np.stack((raw_x, raw_y, raw_z), axis=-1)
    data = data[~np.any(np.isnan(data), axis=1)]
    x = data[:, 0]
    y = data[:, 1]
    z = data[:, 2]

    # Top - feet-only
    create_heatmap(ax4, z, x, resolution, z_range, x_range, palette, v_max)
    ax4.set_title('Top - Feet Only')
    ax4.get_xaxis().set_visible(False)
    ax4.get_yaxis().set_visible(False)
    plot_table(ax4, tab, table_color, alpha=.2)
    plot_bounds(ax4, boundaries, view='top', bound_color=bound_color, alpha=.2)

    # Plot partitions if partitions were used in trial
    if (name[16:19] != 'URV') and (name[16:19] != 'RFT') and (name[5:8] != 'S78'):
        part = get_part(file=file)
        part.shape = (4, 3)
        plot_part(part, part_color, ax1, ax2, ax3, ax4)

    # Manually define lines used for legend
    custom_lines = [Line2D([0], [0], color=table_color, lw=4,
                           path_effects=[pe.Stroke(linewidth=6, foreground='k'), pe.Normal()]),
                    Line2D([0], [0], color=part_color, lw=2),
                    Line2D([0], [0], color=bound_color, lw=2)]

    fig.legend(custom_lines, ['Table', 'Partition', 'Bounding Box'], loc='lower right')

    # Images were flipped when created and this was the easiest fix
    ax1.invert_xaxis()
    ax4.invert_yaxis()
    ax4.invert_xaxis()

    fig.tight_layout()

    plt.show()


if __name__ == "__main__":

    #############################################################################################################

    # Desired trial name goes here. A list of multiple trials can be used and program will iterate through trials
    # (plotting window must be closed in order for program to move on to the next trial).
    trials = ['MVOL_S08_07_APR_RVL_1']

    #############################################################################################################

    for trial in trials:
        plot_heatmap(trial)
