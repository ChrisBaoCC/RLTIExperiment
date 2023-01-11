#!usr/bin/env/python3

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import LinearSegmentedColormap
import glob

paths = glob.glob("../data/*")

dfs = [pd.read_csv(path) for path in paths]
df = pd.concat(dfs)

plt.rc('font', size=20)  # 28 for 2d plots
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
    [0.52, 1.0, 1.6, 2.1, 2.6],  # to 2 sig figs because that's what we have
    [2.62, 3.49, 4.36, 5.23, 6.09],
    list(np.array(X[2]) / 100)
]
Y = [[df[df[variables[i]] == j]["rating"].sum()
      / len(df[df[variables[i]] == j])
      for j in X[i]] for i in range(3)]

# for violin plots
# 3d array: variable, x, and y
V = [[df[df[variables[i]] == j]["rating"] for j in X[i]] for i in range(3)]
q1 = []
q2 = []
q3 = []
for i in range(3):
    ps = np.percentile(V[i], [25, 50, 75], axis=1)
    q1.append(ps[0])
    q2.append(ps[1])
    q3.append(ps[2])
inds = [np.arange(1, len(q2[i]) + 1) for i in range(3)]

S = [[df[df[variables[i]] == j]["rating"].sem() for j in X[i]]
     for i in range(3)]
azim = [
    135,
    -45,
    225
]


def lin_reg(var, x):
    if var == 0:
        return 0.5032 + 0.4223 * x  # coefs from the table
    elif var == 1:
        return 71.43 - 0.1317 * x  # coefs from the table


def adjacent_values(vals, q1, q3):
    upper_adjacent_value = q3 + (q3 - q1) * 1.5
    upper_adjacent_value = np.clip(upper_adjacent_value, q3, vals[-1])

    lower_adjacent_value = q1 - (q3 - q1) * 1.5
    lower_adjacent_value = np.clip(lower_adjacent_value, vals[0], q1)
    return lower_adjacent_value, upper_adjacent_value


# derivative plot (pdf)
# normalize illusion strength vs. line length
normY = np.array(Y[0])
normY *= 100 / np.max(Y[0])
delta = [0] + [normY[i+1] - normY[i] for i in range(len(normY)-1)]
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111)
ax.plot(X[0], delta, linewidth=5, color="#cc0000", solid_capstyle="butt")
ax.set_title("RF size distribution", weight="bold", pad=20)
ax.set_xlabel("Size (°)", weight="medium")
ax.set_xticks(X[0])
ax.set_xticklabels(alt_ticklabels[0])
ax.set_ylabel("Probability density", weight="medium")
ax.set_yticklabels([])

plt.tight_layout()
plt.show()

# 2d plots
for VAR in range(3):
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111)

    # line plots
    # ax.plot(X[VAR], Y[VAR], linewidth=5, color="#cc0000",
    #         solid_capstyle="butt")  # normal plot (cdf)
    # ax.errorbar(X[VAR], Y[VAR], S[VAR], capsize=7, fmt="none",
    #             ecolor="#000000", linewidth=5, capthick=5, solid_capstyle="round")
    # set units on x-axis
    # ax.set_xticks(X[VAR])
    # ax.set_xticklabels(alt_ticklabels[VAR])
    # end line plots

    # violin plots (from matplotlib documentation)
    parts = ax.violinplot(V[VAR], showextrema=False)
    for (i, pc) in enumerate(parts['bodies']):
        pc.set_facecolor(plt.get_cmap("Pastel1").colors[i])
        pc.set_alpha(1)

    ax.scatter(inds[VAR], q2[VAR], color='black', s=150)
    ax.vlines(inds[VAR], q1[VAR], q3[VAR], color='black', lw=5)

    # set units on x-axis
    # i don't know why I need to add an empty value and I don't care
    ax.set_xticklabels([""] + alt_ticklabels[VAR])
    ax.set_title(chr(ord('A') + VAR) + ". Illusion strength vs. " + names[VAR],
                 weight="bold", pad=20)
    ax.set_xlabel(labels[VAR], weight="medium")
    ax.set_ylabel("Average strength (%)", weight="medium")
    # end line plots

    # linear regression
    # if VAR in [0, 1]:
    #     lineX = [X[VAR][0], X[VAR][-1]] # x-values used in linear regression
    #     plotX = [1, 5] # x-values to plot since we change the scale
    #     lineY = [lin_reg(VAR, x) for x in lineX]
    #     ax.plot(plotX, lineY, linestyle="dashed", color="grey", lw=5)

    plt.tight_layout()
    plt.show()

# 3d plot
# fig = plt.figure(figsize=(10, 8))
# ax = fig.add_subplot(111, projection="3d")

# ax.xaxis.labelpad=18
# ax.yaxis.labelpad=18
# ax.zaxis.labelpad=18

# var1 = 0
# var2 = 2
# matrix = []
# for i in range(5):
#     row = []
#     for j in range(5):
#         filtered = df[(df[variables[var1]] == X[var1][i])
#                       & (df[variables[var2]] == X[var2][j])]
#         row.append(filtered["rating"].sum() / len(filtered))
#     matrix.append(row)

# XX, YY = np.meshgrid(X[var1], X[var2])
# Z = np.array(matrix).transpose()
# colors = ["#ffaaaa", "#cc0000", "black"]
# colormap = LinearSegmentedColormap.from_list("customreds", colors)
# # colormap = cm.Reds
# # colormap.set_gamma(0.8)
# ax.plot_surface(XX, YY, Z, cmap=colormap, antialiased=True, linewidth=0)
# ax.azim = 225 # 135 for 0, 1; -45 for 1, 2; 225 for 0, 2
# # ax.set_title("Effects of line length, stimulus radius",
# #              weight="bold")
# ax.set_xlabel(labels[var1], weight="medium")
# ax.set_ylabel(labels[var2], weight="medium")
# ax.set_zlabel("Average strength (%)", weight="medium")


# change units on x-axis
# ax.set_xticks(X[0])
# ax.set_yticks(X[1])
# ax.set_xticklabels(alt_ticklabels[0])
# ax.set_yticklabels(alt_ticklabels[1])

# plt.tight_layout()
# plt.show()
