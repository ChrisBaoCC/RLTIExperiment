#!usr/bin/env python3
"""Python script that runs the experiment."""

__author__ = "Chris Bao"
__version__ = "0.1"
__date__ = "28 May 2022"

# Imports
from math import pi, cos, sin
import numpy as np
from tkinter import Tk, Canvas

# Constants
SCREEN_WIDTH: int = 1920
SCREEN_HEIGHT: int = 1080

N_STIM: int = 120   # number of stimuli to show
# radius of circle of stimuli.
# inner endpoints of lines are this distance from center.
INNER_RADIUS_BASE: int = 400
STIM_PERIOD: int = 50  # frames for one expansion/contraction (= 0.5 s)
LINE_WIDTH: int = 5

LINE_LENGTHS: list[int] = [200, 250, 300, 350, 400, 450, 500, 550, 600, 650]
N_LINE_LENGTHS: int = 10

LINE_ANGLES: list[int] = [8, 16, 24, 32, 40, 48, 56, 64, 72, 80]
N_LINE_ANGLES: int = 10

# Global variables
window: Tk
canvas: Canvas

line_angle: int = LINE_ANGLES[5]  # degrees
line_length: int = LINE_LENGTHS[5]

inner_radius: int = INNER_RADIUS_BASE
frame_count: int = 0


def pol_to_rect(r: float, theta: float) -> np.array:
    """
    Converts polar coordinates to rectangular coordinates.

    Parameters
    ----------
    r: float radius.
    theta: float angle in degrees.

    Returns
    -------
    np.array rectangular vector.
    """
    return np.array((r * cos(theta * pi / 180), r * sin(theta * pi / 180)))


def get_inner(i: int) -> np.array:
    """
    Returns the inner endpoint of the i-th line.

    Parameters
    ----------
    i: int index of the line.

    Returns
    -------
    np.array rectangular vector.
    """
    return pol_to_rect(inner_radius, i / N_STIM * 360)\
        + np.array((SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))


def get_outer(i: int) -> np.array:
    """
    Returns the outer endpoint of the i-th line.

    Parameters
    ----------
    i: int index of the line.

    Returns
    -------
    np.array rectangular vector.
    """
    # (stimulus line vector) + (inner endpoint vector)
    return pol_to_rect(line_length, line_angle + i / N_STIM * 360)\
        + get_inner(i)


def animate() -> None:
    """
    Animates the experiment.

    Parameters
    ----------
    none taken.

    Returns
    -------
    None
    """
    global frame_count, inner_radius
    canvas.delete("all")
    for i in range(N_STIM):
        canvas.create_line(
            *get_inner(i),
            *get_outer(i),
            fill="black",
            width=LINE_WIDTH
        )
    if frame_count < STIM_PERIOD/2:
        inner_radius += INNER_RADIUS_BASE * (1 / STIM_PERIOD)
    else:
        inner_radius -= INNER_RADIUS_BASE * (1 / STIM_PERIOD)
    frame_count += 1
    frame_count %= STIM_PERIOD
    canvas.after(10, animate)  # delay of 10 ms -> 100 fps


def main() -> None:
    """
    Entry point. Initializes the experiment.

    Parameters
    ----------
    none taken.

    Returns
    -------
    None
    """
    global window, canvas
    window = Tk()
    window.attributes('-fullscreen', True)  # note: requires Alt-F4 to exit

    canvas = Canvas(window, width=SCREEN_WIDTH, height=SCREEN_HEIGHT,
                    bg="white", highlightthickness=0)
    canvas.pack()

    # start animation
    animate()

    window.mainloop()


if __name__ == "__main__":
    main()
