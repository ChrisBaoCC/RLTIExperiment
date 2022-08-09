#!usr/bin/env/python3

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import LinearSegmentedColormap

paths = ["old_data/em2022-07-2515-45-11.880430.csv",
         "old_data/jm2022-07-2514-12-18.692662.csv",
         "old_data/jm2022-07-2814-16-17.947739.csv",
         "old_data/fh2022-07-2815-26-10.110517.csv"]

dfs = [pd.read_csv("../" + path) for path in paths]
df = pd.concat(dfs)

plt.rc('font', size=20) # 28 for 2d plots
plt.rcParams["font.family"] = "Helvetica Neue"
plt.rcParams["font.weight"] = "medium"

variables = [
    "line_length",
    "stim_radius",
    "stim_period"
]
names = [
    "line length",
    "stimulus radius",
    "animation speed"
]
labels = [
    "Line length (°)",
    "Stimulus radius (°)",
    "Animation period (s)"
]
X = [
    tuple(range(30, 180, 30)),
    tuple(range(150, 400, 50)),
    (25, 50, 100, 150, 200)
]
alt_ticklabels = [
    [0.52, 1.0, 1.6, 2.1, 2.6], # to 2 sig figs because that's what we have
    [2.62, 3.49, 4.36, 5.23, 6.09],
    np.array(X[2]) / 100
]
Y = [[df[df[variables[i]] == j]["rating"].sum()
      / len(df[df[variables[i]] == j])
      for j in X[i]] for i in range(3)]
# for violin plots
# 3d array: variable, x, and y
# V = [[df[df[variables[i]] == j]["rating"] for j in X[i]] for i in range(3)]
S = [[df[df[variables[i]] == j]["rating"].sem() for j in X[i]]
     for i in range(3)]

# 2d plots
# for VAR in range(3):
#     fig = plt.figure(figsize=(10, 8))
#     ax = fig.add_subplot(111)
#     ax.plot(X[VAR], Y[VAR], linewidth=5, color="#cc0000", solid_capstyle="butt")
#     ax.errorbar(X[VAR], Y[VAR], S[VAR], capsize=7, fmt="none", ecolor="#000000", linewidth=5, capthick=5, solid_capstyle="round")
#     # ax.violinplot(V[VAR], quantiles=[[0, 0.25, 0.5, 0.75] for _ in range(5)])
#     ax.set_title(chr(ord('A') + VAR) + ". Illusion strength vs. " + names[VAR],
#             weight="bold", pad=20)
#     ax.set_xlabel(labels[VAR], weight="medium")
#     ax.set_ylabel("Average strength (%)", weight="medium")

#     # change units on x-axis
#     ax.set_xticks(X[VAR])
#     ax.set_xticklabels(alt_ticklabels[VAR])

#     plt.tight_layout()
#     plt.show()

# 3d plot
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection="3d")

ax.xaxis.labelpad=18
ax.yaxis.labelpad=18
ax.zaxis.labelpad=18

var1 = 0
var2 = 1
matrix = []
for i in range(5):
    row = []
    for j in range(5):
        filtered = df[(df[variables[var1]] == X[var1][i])
                      & (df[variables[var2]] == X[var2][j])]
        row.append(filtered["rating"].sum() / len(filtered))
    matrix.append(row)

XX, YY = np.meshgrid(X[var1], X[var2])
Z = np.array(matrix).transpose()
colors = ["#ffaaaa", "#cc0000", "black"]
colormap = LinearSegmentedColormap.from_list("customreds", colors)
# colormap = cm.Reds
# colormap.set_gamma(0.8)
ax.plot_surface(XX, YY, Z, cmap=colormap, antialiased=True, linewidth=0)
ax.azim = 135
# ax.set_title("Effects of line length, stimulus radius",
#              weight="bold")
ax.set_xlabel(labels[var1], weight="medium")
ax.set_ylabel(labels[var2], weight="medium")
ax.set_zlabel("Average strength (%)", weight="medium")


# change units on x-axis
ax.set_xticks(X[0])
ax.set_yticks(X[1])
ax.set_xticklabels(alt_ticklabels[0])
ax.set_yticklabels(alt_ticklabels[1])

plt.tight_layout()
plt.show()
