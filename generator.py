import numpy as np
from scipy import stats
import pickle # load kdf
import csv
import time # for timestamp

kernel = pickle.load(open("output/BarometerKDE.pickle", "rb"))

raw_src_dat = np.genfromtxt("input/SkyPilotSimulation.csv", dtype=np.unicode_, delimiter=',')

#for now
assert raw_src_dat[0, 0] == "time_s"
assert raw_src_dat[0, 1] == "alt_ft"


src_dat = np.array(raw_src_dat[2:,:], dtype=np.float64)
src_dat[:, 1] *= 0.3048  #Convert to metres

#Todo - reuse the below uniform random distribution stretcher code
P_b = 1018 + np.random.random_sample() * 4 - 2  #mbar
#others should be SI units
R = 8.31432
T = 290 + np.random.random_sample() * 20 - 10
L_b = -0.006 + np.random.random_sample() / 1000 - 0.005
g = 9.808
M = 0.02896

def altToPres(alt):
    # Takes in altitude in metres, returns mbar (or whatever unit P_b is in)
    # https://www.mide.com/air-pressure-at-altitude-calculator
    return P_b * (1 + L_b / T * alt)**((g * M) / (R * L_b))

src_dat[:, 1] = altToPres(src_dat[:, 1]) # convert to mbar

# add measurement errors ============================================
with open(f"output/SkyPilotSimulation__gen_{time.time()}.csv", "w", newline="") as out_file:
    out_csver = csv.writer(out_file)
    out_csver.writerow((3,))
    out_csver.writerow((P_b, raw_src_dat[1, 0]))
    for i in range(src_dat.shape[0]):
        out_dat = src_dat[i,:]
        out_dat[1] += kernel.resample(1)
        out_csver.writerow(src_dat[i, :])



