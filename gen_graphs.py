import numpy as np
import matplotlib.pyplot as plt

def plot(path: str, reps: int, levels: list[int], period_adj: float):
    me = np.loadtxt(path, skiprows=1, delimiter=",")
    # split the exp up into blocks
    # (differing #s of trials per block so it looks weird)
    blocks = [me[reps*sum(levels[:i]) : reps*sum(levels[:i+1])] for i in range(0, 4)]
    for i in range(len(blocks)):
        # split each block up into series of trials
        # a series of trials contains one trial for each level
        # there are `reps` series in each block
        blocks[i] = np.reshape(blocks[i], (reps, levels[i], -1))
        for j in range(reps):
            # sort series according to the block's parameter
            # e.g., block 1's series are sorted by line length
            blocks[i][j] = blocks[i][j][blocks[i][j][:,i+1].argsort()]
    # generate average ratings per level, per block
    # yes it's a list comprehension inside a list comprehension.
    # shut up it's pythonic
    ratings = [np.sum([blocks[i][j,:,-1] for j in range(reps)], axis=0) / reps for i in range(len(blocks))]
    # normalize ratings: highest -> 100
    # norm = [[ratings[i][j] * 100/np.max(ratings[i]) for j in range(levels[i])] for i in range(len(blocks))]
    # generate standard errors per level, per block
    errors = [[np.std(blocks[i][:,j,5]) / np.sqrt(reps) for j in range(levels[i])] for i in range(len(blocks))]

    keys = [blocks[i][0,:,i+1] for i in range(len(blocks))]

    # period adjustment
    keys[3] = [i * 10/9 for i in keys[3]]

    plt.rcParams['figure.figsize'] = [10, 8]
    fig, axs = plt.subplots(2, 2)
    for i in range(len(blocks)):
        axs[i//2,i%2].errorbar(keys[i], ratings[i], errors[i], color="black", capsize=5)
    axs[0,0].set_title("Effect of line length on illusion strength")
    axs[0,0].set_xlabel("Line length, px")
    axs[0,1].set_title("Effect of line angle on illusion strength")
    axs[0,1].set_xlabel("Line angle from radius, °")
    axs[1,0].set_title("Effect of stimulus radius on illusion strength")
    axs[1,0].set_xlabel("Stimulus radius, px")
    axs[1,1].set_title("Effect of animation period on illusion strength")
    axs[1,1].set_xlabel("Animation period, f")
    for i in range(2):
        for j in range(2):
            axs[i,j].set_ylabel("Illusion strength, %")
            axs[i,j].set_ylim(top=100, bottom=0)
    plt.tight_layout()
    plt.show()

    print("Best:")
    for i in range(len(blocks)):
        print(keys[i][ratings[i].argsort()[-1]])

plot("data/ss2022-07-1511-06-13.775862.csv", reps=10, levels=[10, 10, 6, 10], period_adj=10/9)
plot("data/me.csv", reps=3, levels=[10, 10, 6, 10], period_adj=10/9)
plot("data/ec2022-07-1513-01-53.549794.csv", reps=10, levels=[10, 10, 6, 10], period_adj=10/9)
