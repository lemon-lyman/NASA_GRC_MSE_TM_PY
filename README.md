# NASA_GRC_MSE_TM_PY

MSE_Scripts is a project that generates plots of various data collected during MSE
trials


SUMMARY:

'heatmap.py', 'eventplot_single.py', and 'eventplot_dual.py' are the three 'top-level'
scripts and are the only ones that should be opened and changed unless modifications
are needed. The other .py files are supporting modules.

'heatmap.py' creates one plot with three heatmaps from different viewpoints of an MSE
trial and a fourth heatmap of feet-only.
The 'eventplot' scripts create event plots for an MSE trial that display a subject's
behaviors (states) as horizontal bars as well as cumulative volume and heart rate.

'observation.py' gets the observations from BORIS stored in csv's.
'heartrate.py' plots the heart rate of a subject on a given axis.
'cumulative_volume.py' gets the cumulative convex volume of a trial.

RUNNING THE SCRIPTS:

Open one of the three 'top-level' scripts. Underneath the line

'if __name__ == "__main__":'

near the bottom of the script, find the variable 'name'. Replace the string inside
this list with the trial name you wish to plot. Multiple file names can be placed inside
'name' and the script will generate multiple plots.

DATA:

The folders 'boris_data', 'heartrate_data', 'tracked_data', and 'volume_data' must 
exist in the same directory as the scripts and modules. boris_data is unaltered
after being exported from BORIS as a csv. tracked_data is unaltered with the exception
of '_tracked' being placed at the end of the file name. tracked_data files must be .emt
files exported from BTS then saved as .csv files. volume_data and heartrate_data files
are .csv's that are manually created and the modules depend on the format used during
Fall 2018 testing. See S07 and S08 files within volume_data and heartrate_data for
examples of the format.



Python 3 is required but the other package versions listed here are simply the versions
I have used and are not necessarily required. I wouldn't expect any problems with any
stable, up-to-date version of these packages.

Dependency 		Just_A_Successful_Version

Python 			3.6.6

NumPy 			1.14.5

SciPy 			1.1.0

Pandas 			0.23.4

Matplotlib  		2.2.3

Guide to installing packages with pip:
https://packaging.python.org/tutorials/installing-packages/#use-pip-for-installing
p.s. if troubleshooting, try 'pip3 install... ' instead of 'pip install... '

- NW, Fall 2018
