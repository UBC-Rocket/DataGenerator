Input data (which doesn't necessarily need to be used - e.g. excel sheets) goes in this folder

Input data should be a CSV, with two columns and one header row.
The header row should be text; all other numbers should be interpretable as floats.
The first column should be time, and the 2nd should be data. (More details later)

The header row tells the data generator how to interpret each column. For the time column, the valid headers are:
- time_s --> indicates time is measured in seconds.

For the data column, the valid headers are:
- alt_ft --> indicates data is altitude above ground level, measured in feet

Next row of data should look like "t_max, 0" where t_max is the time of apogee.
