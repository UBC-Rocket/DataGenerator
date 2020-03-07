from typing import List, Dict, Callable

import pandas as pd
import numpy as np
import pickle
import time


def generate(
    csv: str,
    generator_dict: Dict[List[str], Callable[[pd.DataFrame], pd.DataFrame]],
    default_func: Callable[[pd.DataFrame], pd.DataFrame] = lambda df: df.loc[
        :, df.columns != "time"
    ],
    time_name: str = "time",
) -> pd.DataFrame:
    """
    Generates data based off of a csv of real (or not) data.

    Args:
        csv: path to csv file of rocket data. Must at least include time entry.
        generator_dict: dictionary of generator functions to be used for generating
                        the data. Each function is passed the columns of the csv containing the headers supplied by the dict's key in a DataFrame
                        along with the time column. Columns other than time can only be used by a generator function once.
                        The columns of the DataFrame that are returned will be present in generate()'s return value along with time.
        default_func: The default function used if generator_dict does not contain an entry for a column. default behaviour
                      is to pass through columns untouched.
        time_name: Name of the time column in the csv.

    Returns:
        A dataframe of the newly generated data.
    """

    input_frame = pd.read_csv(csv)
    output_frame = input_frame[time_name].copy().to_frame()

    # evaluate all generator functions
    for headers, gen_func in generator_dict:
        output_frame.merge(gen_func(input_frame[[time_name] + headers]))
        output_frame.drop(columns=headers)

    # call default function on any leftover columns
    for column in [key for key in input_frame.keys() if key != time_name]:
        output_frame = pd.concat(
            [output_frame, default_func(input_frame[[time_name, column]])], axis=1
        )
        output_frame.drop(columns=column)

    return output_frame


# TODO: generate this on first run then cache as pickle
KERNEL = pickle.load(open("output/BarometerKDE.pickle", "rb"))


def gen_pres_from_alt(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generates pressure based on altitude. Takes a dataframe with columns time and alt_ft.
    Returns dataframe with column pressure.
    """
    # NOTE: the time column is completely ignored
    # TODO: possibly have the key set dynamically
    out_series = df["alt_ft"].copy().rename_axis("pressure")
    out_series *= 0.3048  # Convert to metres

    # TODO: also possibly have these set dynamically
    P_b = _uniform_random(1018, 4)  # mbar
    # others should be SI units
    L_b = _uniform_random(-0.006, 0.001)
    T = _uniform_random(290, 20)

    out_series["alt_ft"] = _alt_to_pres(
        out_series["alt_ft"], P_b, L_b, T
    )  # convert to mbar

    out_series["alt_ft"] = out_series["alt_ft"].apply(lambda a: a + KERNEL.resample(1))
    # Quantization
    out_series["alt_ft"] = out_series["alt_ft"].apply(lambda a: _general_round(a, 0.01))

    return out_series.to_frame()


def _alt_to_pres(alt: float, P_b: float, L_b: float, T: float) -> float:
    """
    returns pressure in mbar or Pa, depending on units of P_b.
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


# util functions
def _uniform_random(mean: float, width: float) -> float:
    """ Returns a random number in the uniform distribution [mean + width/2, mean - width/2] """
    return mean + np.random.random_sample() * width - width / 2


# add measurement errors
def _general_round(a: float, min_clip: float) -> float:
    """ Rounds a to nearest min_clip. """
    return round(a / min_clip) * min_clip


# TODO: create a cli
generate(
    "input/test-data.csv", {"alt_ft": gen_pres_from_alt}, time_name="time_s"
).to_csv(f"output/skypilot_gen_pres_{time.time()}.csv")
