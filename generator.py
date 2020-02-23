import numpy as np
from scipy import stats
import pickle # load kdf
import csv
import time # for timestamp

kernel = pickle.load(open("output/BarometerKDE.pickle", "rb"))


def uniformRandom(mean, width):
    return mean + np.random.random_sample() * width - width / 2

def altToPres(alt, P_b, L_b, T):
    R = 8.31432 # SI units
    g = 9.808
    M = 0.02896
    # Takes in altitude in metres, returns mbar (or whatever unit P_b is in)
    # https://www.mide.com/air-pressure-at-altitude-calculator
    return P_b * (1 + L_b / T * alt)**((g * M) / (R * L_b))

# add measurement errors ============================================
def generalRound(a, MinClip):
    return round(a / MinClip) * MinClip

def runFile(filename):

    raw_src_dat = np.genfromtxt(f"input/{filename}.csv", dtype=np.unicode_, delimiter=',')

    #for now
    assert raw_src_dat[0, 0] == "time_s"
    assert raw_src_dat[0, 1] == "alt_ft"

    src_dat = np.array(raw_src_dat[2:,:], dtype=np.float64)
    src_dat[:, 1] *= 0.3048  #Convert to metres


    P_b = uniformRandom(1018, 4)  #mbar
    #others should be SI units
    L_b = uniformRandom(-0.006, 0.001)
    T = uniformRandom(290, 20)

    src_dat[:, 1] = altToPres(src_dat[:, 1], P_b, L_b, T) # convert to mbar

    with open(f"output/SkyPilotSimulation__gen_{time.time()}.csv", "w", newline="") as out_file:
        out_csver = csv.writer(out_file)
        out_csver.writerow((3,))
        out_csver.writerow((P_b, raw_src_dat[1, 0]))
        for i in range(src_dat.shape[0]):
            out_dat = src_dat[i,:]
            out_dat[1] += kernel.resample(1)
            out_dat[1] = generalRound(out_dat[1], 0.01) #Quantization
            out_csver.writerow(src_dat[i,:])

runFile('SkyPilotSimulation')



