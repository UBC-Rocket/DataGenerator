import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import pickle

calib_dat = np.genfromtxt("input/MS5803BA_ground.csv")

calib_dat -= np.average(calib_dat)  # normalize (set average = 0)
sd = np.std(calib_dat)

# kernel density smoothing - get a probability density function (pdf) out of it
kernel = stats.gaussian_kde(calib_dat)

x = np.linspace(-4 * sd, 4 * sd, 200)
y = kernel.evaluate(x)

figure, axes = plt.subplots()

axes.clear()
axes.plot(x, y)

axes.set_title(f"PDF of barometer errors (on the ground)")
axes.set_xlabel("Error (mbar)")
figure.savefig(f"output/BarometerErrorPDF.png")

# import timeit
# print(timeit.timeit("kernel.resample()", number=100, globals=globals()))

with open("output/BarometerKDE.pickle", mode="wb") as kde_file:
    pickle.dump(kernel, kde_file)
