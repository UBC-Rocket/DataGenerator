import pickle  # load kdf
import csv
import time  # for timestamp

import numpy as np
from scipy import stats

KERNEL = pickle.load(open("output/BarometerKDE.pickle", "rb"))


def uniform_random(mean: float, width: float) -> float:
    """ Returns a random number in the uniform distribution [mean + width/2, mean - width/2] """
    return mean + np.random.random_sample() * width - width / 2


def alt_to_pres(alt: float, P_b: float, L_b: float, T: float) -> float:
    """ returns pressure in mbar or Pa, depending on units of P_b.
        alt is in meters,
        P_b is pressure at sea level (Pa or mbar),
        L_b is the standard temperature lapse rate (K/m).
    """
    R = 8.31432  # universal gas constant - N*m/(mol*K)
    g = 9.808  # gravitational acceleration constant - m/s^2
    M = 0.02896  # molar mass of Earth's air - kg/mol

    # Takes in altitude in metres, returns mbar (or whatever unit P_b is in)
    # https://www.mide.com/air-pressure-at-altitude-calculator
    return P_b * (1 + L_b / T * alt) ** ((g * M) / (R * L_b))


# add measurement errors
def general_round(a: float, min_clip: float) -> float:
    """ Rounds a to nearest min_clip. """
    return round(a / min_clip) * min_clip


def run_file(filename: str) -> None:

    raw_src_dat = np.genfromtxt(
        f"input/{filename}.csv", dtype=np.unicode_, delimiter=","
    )

    # for now
    assert raw_src_dat[0, 0] == "time_s"
    assert raw_src_dat[0, 1] == "alt_ft"

    src_dat = np.array(raw_src_dat[2:, :], dtype=np.float64)
    src_dat[:, 1] *= 0.3048  # Convert to metres

    P_b = uniform_random(1018, 4)  # mbar
    # others should be SI units
    L_b = uniform_random(-0.006, 0.001)
    T = uniform_random(290, 20)

    src_dat[:, 1] = alt_to_pres(src_dat[:, 1], P_b, L_b, T)  # convert to mbar

    with open(
        f"output/SkyPilotSimulation__gen_{time.time()}.csv", "w", newline=""
    ) as out_file:
        out_csver = csv.writer(out_file)
        out_csver.writerow((3,))
        out_csver.writerow((P_b, raw_src_dat[1, 0]))
        for i in range(src_dat.shape[0]):
            out_dat = src_dat[i, :]
            out_dat[1] += KERNEL.resample(1)
            out_dat[1] = general_round(out_dat[1], 0.01)  # Quantization
            out_csver.writerow(src_dat[i, :])


run_file("SkyPilotSimulation")
