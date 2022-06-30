#!usr/bin/env python3
"""Python script that runs the experiment."""

__author__ = "Chris Bao"
__version__ = "0.1"
__date__ = "28 May 2022"

# Imports
from datetime import datetime
from math import pi, cos, sin
from random import shuffle
import numpy as np
from tkinter import Button, Entry, Event, Label, StringVar, Tk, Canvas, Toplevel, messagebox

# Constants
SCREEN_WIDTH: int = 1920
SCREEN_HEIGHT: int = 1080

FRAMES_PER_SECOND: int = 60 # 100 or 60 Hz
# frames for one expansion and contraction (= 0.5 s)
STIM_PERIOD: int = FRAMES_PER_SECOND // 2

N_STIM: int = 120   # number of stimuli to show
# Radius of stimuli. Inner endpoints of lines are this distance from center.
INNER_RADIUS_BASE: int = 200
LINE_WIDTH: int = 5

LINE_LENGTHS: list[int] = [50, 75, 100, 150, 200, 250, 300]
N_LINE_LENGTHS: int = 7

LINE_ANGLES: list[int] = [20, 30, 40, 50, 60, 70]
N_LINE_ANGLES: int = 6

SEIZURE_WARNING: str = "WARNING: participating may potentially trigger"\
        + " seizures for people with photosensitive epilepsy."\
        + " If you suspect you have photosensitive epilepsy or have a history"\
        + " of photosensitive epilepsy, please press the [No] button now."\
        + "\n\nDo you wish to proceed?"

STATE_PLAY = 0
STATE_RATE = 1
STATE_END = 2

# TODO play length shortened
PLAY_LENGTH = FRAMES_PER_SECOND * 5 # illusion up for 5 s

# Global variables
window: Tk
canvas: Canvas
dlg: Toplevel

initials_var: StringVar
cur_time: datetime

line_angle: int = LINE_ANGLES[2] # degrees
line_length: int =  LINE_LENGTHS[2]

inner_radius: int = INNER_RADIUS_BASE
frame_count: int = 0

state: int # either play or rate
# stores index of line length to use for each trial
trials: list[int]

trial: int = 0 # current trial number
# line length, line angle, user rating
results: list[tuple[int, int]] = []

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


def draw_fixation() -> None:
    """
    Draw a fixation dot in the center of the screen.
    
    Parameters
    ----------
    none taken.

    Returns
    -------
    None
    """
    # tkinter doesn't have antialiasing so I used a rectangle
    canvas.create_rectangle(SCREEN_WIDTH / 2 - 5, SCREEN_HEIGHT / 2 - 5,
            SCREEN_WIDTH / 2 + 5, SCREEN_HEIGHT / 2 + 5,
            fill="black", width=0, tags=["fixation","play"])


def save() -> None:
    """
    Save all data to file.
    
    Parameters
    ----------
    None taken.
    
    Returns
    -------
    None.
    """
    filename = "data/" + initials_var.get().lstrip().rstrip().lower()\
            + "-" + cur_time.__str__() + ".txt"
    with open(filename, "w") as f:
        f.write("trial,line_length,line_angle,rating\n")
        for trial in enumerate(results):
            f.write(
                ",".join(
                    [str(trial[0]), str(trial[1][0]), 
                    str(trial[1][1]), str(trial[1][2])]
                )
            )
            f.write("\n")


def animate() -> None:
    """
    Animates the illusion.

    Parameters
    ----------
    None taken.

    Returns
    -------
    None
    """
    global state, frame_count, inner_radius, trial, line_length

    if state == STATE_PLAY:
        if frame_count > PLAY_LENGTH:
            state = STATE_RATE
        else:
            canvas.delete("play")
            draw_fixation()
            line_length = LINE_LENGTHS[trials[trial]]
            for i in range(N_STIM):
                canvas.create_line(
                    *get_inner(i),
                    *get_outer(i),
                    fill="black",
                    width=LINE_WIDTH,
                    tags=["line", "play"]
                )

            # TODO: test
            canvas.create_text(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
                text=str(frame_count),
                font="Arial 24 bold",
                fill="black",
                tags=["play"])

            if frame_count % STIM_PERIOD < STIM_PERIOD/2:
                inner_radius += line_length * (1 / STIM_PERIOD)
            else:
                inner_radius -= line_length * (1 / STIM_PERIOD)
    elif state == STATE_RATE:
        canvas.delete("play")
        canvas.create_text(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
                text="Rate the illusion. Number keys 1–7",
                font="Arial 24 bold",
                fill="black",
                tags=["rate"])
    elif state == STATE_END:
        save()
        canvas.delete("play")
        canvas.create_text(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
                text="Your data has been saved. Press [Esc] to exit.",
                font="Arial 24 bold",
                fill="black",
                tags=["end"])
    
    # TODO for some reason tkinter delay is shorter than it actually is
    # so I increased the delays
    # delay of 10 ms -> 100 fps
    if FRAMES_PER_SECOND == 100:
        canvas.after(12, animate) # used to be 10
    # approximate 60 fps
    elif FRAMES_PER_SECOND == 60:
        if frame_count % 3 == 1:
            canvas.after(19, animate) # used to be 16
        else:
            canvas.after(20, animate) # used to be 17
    # fallback
    else:
        canvas.after(1200 // FRAMES_PER_SECOND, animate) # used to be 1000

    frame_count += 1

def handle_key(event: Event) -> None:
    """
    Handles keypresses by the user.
    For monitoring responses in the rate phase.
    
    Parameters
    ----------
    event: Event keypress event.

    Returns
    -------
    None
    """
    global state, trial, frame_count, results
    if state == STATE_RATE:
        if event.char in "1234567":
            results.append(
                (LINE_LENGTHS[trials[trial]], line_angle, int(event.char))
            )
            trial += 1
            canvas.delete("rate")
            if trial == N_LINE_LENGTHS:
                state = STATE_END
                return
            state = STATE_PLAY
            frame_count = 0

def stop(event: Event = None):
    """
    Stop the experiment.
    Note: does not log data!
    
    Parameters
    ----------
    event: Event given by tkinter event handler. Ignored.
    
    Returns
    -------
    None.
    """
    print("Experiment was closed early.")
    window.destroy()

def dismiss():
    """
    Handle closing of the dialog window.
    Taken from TkDocs.

    Parameters
    ----------
    None taken.

    Returns
    -------
    None.
    """
    dlg.grab_release()
    dlg.destroy()
    if initials_var.get().lstrip().rstrip() == "":
        stop()

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
    global window, canvas, trials, state, dlg, initials_var, cur_time
    window = Tk()
    window.attributes('-fullscreen', True)

    canvas = Canvas(window, width=SCREEN_WIDTH, height=SCREEN_HEIGHT,
                    bg="white", highlightthickness=0)
    canvas.pack()

    if not messagebox.askyesno(title="Epilepsy warning",
            message=SEIZURE_WARNING,
            icon="warning"):
        print("Experiment was closed early.")
        return

    # collect user initials and time
    # taken from TkDocs
    dlg = Toplevel(window)
    dlg.title("Logging")
    dlg.resizable(False, False)
    initials_var = StringVar(dlg)
    Label(dlg, text="Please enter your initials:").pack()
    Entry(dlg, textvariable=initials_var).pack()
    Label(dlg, text="You may also close this window to exit.").pack()
    Label(dlg, text="During the experiment, you may press"\
            + "[Esc] to stop at any time.").pack()
    Button(dlg, text="Done", command=dismiss).pack()
    dlg.protocol("WM_DELETE_WINDOW", dismiss) # intercept close button
    dlg.transient(window)   # dialog window is related to main
    dlg.wait_visibility() # can't grab until window appears, so we wait
    dlg.grab_set()        # ensure all input goes to our window
    dlg.wait_window()     # block until window is destroyed
    cur_time = datetime.now()

    try:
        window.bind("<Key>", handle_key)
        window.bind("<Escape>", stop)

        # each level is shown 3 times
        # TODO trials only shown once
        trials = [i for i in range(N_LINE_LENGTHS)] #* 3
        shuffle(trials)
        
        state = STATE_PLAY
        animate()
        window.mainloop()
    except:
        print("Experiment was closed early.")

if __name__ == "__main__":
    main()
