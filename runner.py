#!usr/bin/env python3
"""Python script that runs the experiment."""

__author__ = "Chris Bao"
__version__ = "0.1"
__date__ = "28 May 2022"

# Imports
from math import pi, cos, sin
import numpy as np
from tkinter import Tk, Canvas, messagebox

# Constants
SCREEN_WIDTH: int = 1920
SCREEN_HEIGHT: int = 1080

FRAME_RATE: int = 60 # 100 or 60 Hz
STIM_PERIOD: int = FRAME_RATE / 2 # frames for one expansion/contraction (= 0.5 s)

N_STIM: int = 120   # number of stimuli to show
# Radius of stimuli. Inner endpoints of lines are this distance from center.
INNER_RADIUS_BASE: int = 200
LINE_WIDTH: int = 5

LINE_LENGTHS: list[int] = [50, 75, 100, 150, 200, 250, 300]
N_LINE_LENGTHS: int = 10

LINE_ANGLES: list[int] = [8, 16, 24, 32, 40, 48, 56, 64, 72, 80]
N_LINE_ANGLES: int = 10

SEIZURE_WARNING: str = "WARNING: participating may potentially trigger"\
        + " seizures for people with photosensitive epilepsy."\
        + " If you suspect you have photosensitive epilepsy or have a history"\
        + " of photosensitive epilepsy, please press the [No] button now."\
        + "\n\nDo you wish to proceed?"

# Global variables
window: Tk
canvas: Canvas

line_angle: int = LINE_ANGLES[5] # degrees
line_length: int =  LINE_LENGTHS[2]

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
    Animates the illusion.

    Parameters
    ----------
    none taken.

    Returns
    -------
    None
    """
    global frame_count, inner_radius
    canvas.delete("line")
    for i in range(N_STIM):
        canvas.create_line(
            *get_inner(i),
            *get_outer(i),
            fill="black",
            width=LINE_WIDTH,
            tags="line"
        )

    if frame_count < STIM_PERIOD/2:
        inner_radius += line_length * (1 / STIM_PERIOD)
    else:
        inner_radius -= line_length * (1 / STIM_PERIOD)

    # delay of 10 ms -> 100 fps
    if FRAME_RATE == 100:
        canvas.after(10, animate)
    # approximate 60 fps
    elif FRAME_RATE == 60:
        if frame_count % 3 == 1:
            canvas.after(16, animate)
        else:
            canvas.after(17, animate)
    # fallback
    else:
        canvas.after(1000 / FRAME_RATE, animate)

    frame_count += 1
    frame_count %= STIM_PERIOD

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

    if messagebox.askyesno(title="Epilepsy warning",
            message=SEIZURE_WARNING,
            icon="warning"):
        canvas.create_oval(SCREEN_WIDTH / 2 - 5, SCREEN_HEIGHT / 2 - 5,
                SCREEN_WIDTH / 2 + 5, SCREEN_HEIGHT / 2 + 5,
                fill="black", width=0)
        animate()
        window.mainloop()

if __name__ == "__main__":
    main()
