#!/usr/bin/env python3
import statsmodels.api as sm
from statsmodels.formula.api import ols
from statsmodels.regression.linear_model import OLS
from scipy.stats import kruskal
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import cm
import glob

# this file is to compare the original four data files we had
# to the total data we have now (as of 25 Nov).

old_paths = [
    "../data/em2022-07-2515-45-11.880430.csv",
    "../data/jm2022-07-2814-16-17.947739.csv",
    # I spliced JM's data together (they were originally
    # 2 files since it was collected on 2 different days)
    "../data/fh2022-07-2815-26-10.110517.csv"
]
new_paths = [
    "../data/cd2022-10-1313-31-45.457695.csv",
    "../data/da2022-10-1314-48-29.454029.csv",
    "../data/es2022-10-1811-04-40.793284.csv",
    "../data/fb2022-10-2513-30-47.435680.csv",
    "../data/gl2022-10-1814-51-40.116265.csv",
    "../data/gs2022-10-0615-58-48.460297.csv",
    "../data/jr2022-10-0417-25-11.012646.csv",
    "../data/jrc2022-10-0414-58-10.918166.csv",
    "../data/kc2022-10-1813-20-55.967878.csv",
    "../data/kt2022-10-0614-11-46.191964.csv",
    "../data/lae2022-10-0716-01-58.313954.csv",
    "../data/ml2022-11-0314-16-02.529894.csv",
    "../data/tl2022-08-0513-05-29.891560.csv",
]

# Old data first
old_dfs = [pd.read_csv(path) for path in old_paths]
old_df = pd.concat(old_dfs)

# New data
new_dfs = [pd.read_csv(path) for path in new_paths]
new_df = pd.concat(new_dfs)

# Manipulate data
variables = [
    "line_length",
    "stim_radius",
    "stim_period"
]

# shape (3, 5) array of x-coords for each variable
X = [
    list(range(30, 180, 30)),
    list(range(150, 400, 50)),
    [25, 50, 100, 150, 200]
]

Y_old = [[old_df[old_df[variables[i]] == j]["rating"]
          for j in X[i]] for i in range(3)]
Y_new = [[new_df[new_df[variables[i]] == j]["rating"]
          for j in X[i]] for i in range(3)]

titles = [
    "illusion strength vs. line length",
    "illusion strength vs. stim radius",
    "illusion strength vs. anim speed"
]

ax_labels = [
    "line length (dva)",
    "stim radius (dva)",
    "animation period (s)"
]

# Plot data

fig = plt.figure(figsize=(14, 4))
axs: list[plt.Axes] = [
    fig.add_subplot(131),
    fig.add_subplot(132),
    fig.add_subplot(133),
]

# plt.rc('font', size=15)
# plt.rc('xtick', labelsize=20)  # fontsize of the x tick labels
# plt.rc('ytick', labelsize=20)  # fontsize of the y tick labels


for i in range(3):
    # plot distribution
    # print(np.array(Y_old[i]).shape)
    # axs[i].violinplot(Y_old[i])
    # axs[i].violinplot(Y_new[i])

    # for j in range(5):
    # axs[i].scatter([j]*250, Y_old[i][j])  # looks REALLY bad

    axs[i].violinplot(Y_old[i])

    axs[i].set_title(titles[i])  # , fontsize=18)
    axs[i].set_xlabel(ax_labels[i])  # , fontsize=14)
    axs[i].set_ylabel("Average strength (%)")  # , fontsize=14)
plt.show()

fig = plt.figure(figsize=(14, 4))
axs: list[plt.Axes] = [
    fig.add_subplot(131),
    fig.add_subplot(132),
    fig.add_subplot(133),
]
for i in range(3):
    # plot distribution
    # print(np.array(Y_old[i]).shape)
    # axs[i].violinplot(Y_old[i])
    # axs[i].violinplot(Y_new[i])

    # for j in range(5):
    # axs[i].scatter([j]*250, Y_old[i][j])  # looks REALLY bad

    axs[i].violinplot(Y_new[i])

    axs[i].set_title(titles[i])  # , fontsize=18)
    axs[i].set_xlabel(ax_labels[i])  # , fontsize=14)
    axs[i].set_ylabel("Average strength (%)")  # , fontsize=14)

plt.show()
