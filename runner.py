#!usr/bin/env python3
"""Python script that runs the experiment."""

__author__ = "Chris Bao"
__version__ = "1.1"
__date__ = "6 Jul 2022"

# IMPORTS #
from datetime import datetime
from math import pi, cos, sin
from random import shuffle
from turtle import window_height
import numpy as np
from tkinter import HORIZONTAL, Button, Entry, Event, Frame, IntVar, Label, Scale, StringVar, Tk, Canvas,\
    Toplevel, messagebox

# CONSTANTS #
# fraction of window height given to menubar
MENUBAR_WINDOW_RATIO: float = 1/8

# NOT frames per second!
UPDATES_PER_SECOND: int = 100
# of one expansion and contraction, in frames (= 0.5 s)
STIM_PERIOD: int = UPDATES_PER_SECOND // 2

# number of lines to show
N_STIM: int = 120
# inner radius of circle of lines
INNER_RADIUS_BASE: int = 200
LINE_WIDTH: int = 5

LINE_LENGTHS: tuple[int] = (50, 75, 100, 150, 200, 250, 300)
N_LINE_LENGTHS: int = len(LINE_LENGTHS)

LINE_ANGLES: tuple[int] = (12, 24, 36, 48, 60, 72, 84)
N_LINE_ANGLES: int = len(LINE_ANGLES)

# TODO trials only shown once for testing
# times to show each level
LEVEL_FREQ: int = 1

SEIZURE_WARNING: str = "WARNING: participating may potentially trigger"\
    + " seizures for people with photosensitive epilepsy."\
    + " If you suspect you have photosensitive epilepsy or have a history"\
    + " of photosensitive epilepsy, please press the [No] button now."\
    + "\n\nDo you wish to proceed?"

PHASE_START = 0
PHASE_LENGTH = 1
PHASE_REST = 2
PHASE_ANGLE = 3
PHASE_END = 4

STATE_INTRO = 10
STATE_PLAY = 11
STATE_RATE = 12

# TODO play length shortened for testing
PLAY_LENGTH = 1  # trial length in seconds

WIDGET_FONT: tuple = ("Helvetica Neue", 16, "bold")

# GLOBALS #
screen_width: int
screen_height: int

window: Tk
frame: Frame
canvas: Canvas
dlg: Toplevel

exit_btn: Button
slider: Scale
slider_var: IntVar
done_btn: Button

initials_var: StringVar
cur_time: datetime

# store Canvas item ids of fixation cross (2 rectangles)
fixation: list[int]

lines: list[int]

line_angle: int
line_length: int

inner_radius: int
frame_count: int

# current phase of program: start, rest, end, or block.
phase: int
# current state of program: what is being animated.
state: int
# stores index of line length, angle to use for each trial
trials: list[list[int]]
# current trial index
trial: int
# line length, line angle, user rating
results: list[tuple[int, int, int]]

# gets printed to console when experiment is closed
stop_message: str = "Experiment was closed early."


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
        + np.array((screen_width / 2, screen_height / 2))


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


def update_stimulus() -> None:
    """
    Redraw the stimulus (lines) to their new positions.

    Parameters
    ----------
    None taken.

    Returns
    -------
    None
    """
    global lines
    for i in range(N_STIM):
        cur_inner = lines[i][1]
        new_inner = list(get_inner(i))
        canvas.move(
            lines[i][0],
            new_inner[0] - cur_inner[0],
            new_inner[1] - cur_inner[1]
        )
        lines[i][1] = new_inner


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
        + " " + cur_time.__str__() + ".csv"
    with open(filename, "w") as f:
        f.write("trial,line_length,line_angle,rating\n")
        for trial_result in enumerate(results):
            f.write(
                ",".join(
                    [str(trial_result[0]), str(trial_result[1][0]),
                     str(trial_result[1][1]), str(trial_result[1][2])]
                )
            )
            f.write("\n")


def handle_button() -> None:
    """
    Handle presses of the Done button.

    Parameters
    ----------
    None taken.

    Returns
    -------
    None.
    """
    # TODO: implement


# TODO: overhaul
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
    global state, frame_count, inner_radius, trial, line_length, line_angle

    # if state == STATE_START:
    #     canvas.create_text(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
    #                        text="Press [Space] to continue to block 1.",
    #                        font="Arial 24 bold",
    #                        fill="black",
    #                        tags=["start"])
    # elif state == STATE_PLAY:
    #     if frame_count > PLAY_LENGTH * UPDATES_PER_SECOND:
    #         state = STATE_RATE
    #     else:
    #         # canvas.delete("line")
            
    #         update_stimulus()
    #         if frame_count % STIM_PERIOD < STIM_PERIOD/2:
    #             inner_radius += line_length * (1 / STIM_PERIOD)
    #         else:
    #             inner_radius -= line_length * (1 / STIM_PERIOD)
    # elif state == STATE_RATE:
    #     canvas.delete("play")
    #     canvas.create_text(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
    #                        text="Rate the illusion with a" +
    #                        " number key from 1–7.",
    #                        font="Arial 24 bold",
    #                        fill="black",
    #                        tags=["rate"])
    # elif state == STATE_REST:
    #     canvas.delete("play")
    #     canvas.create_text(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
    #                        text="This marks the end of block 1." +
    #                        " Press [space] to move on to block 2.",
    #                        font="Arial 24 bold",
    #                        fill="black",
    #                        tags=["rest"])
    # elif state == STATE_END:
    #     save()
    #     canvas.delete("play")
    #     canvas.create_text(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
    #                        text="Your data has been saved. Press [Esc] to exit.",
    #                        font="Arial 24 bold",
    #                        fill="black",
    #                        tags=["end"])

    # canvas.after(10, animate)
    # frame_count += 1


def start_trial() -> None:
    """
    Sets up the beginning of each trial.

    Parameters
    ----------
    None taken.

    Returns
    -------
    None.
    """
    global lines, line_length, line_angle, frame_count
    for i in fixation:
        canvas.itemconfigure(i, state="normal")
    
    lines.clear()
    if trial < N_LINE_LENGTHS * LEVEL_FREQ:
        line_length = LINE_LENGTHS[trials[trial]]
    elif trial >= N_LINE_LENGTHS * LEVEL_FREQ:
        line_angle = LINE_ANGLES[trials[trial]]
    for i in range(N_STIM):
        line_id = canvas.create_line(
            *get_inner(i),
            *get_outer(i),
            fill="black",
            width=LINE_WIDTH,
            tags=["line", "play"]
        )
        lines.append([line_id, list(get_inner(i))])
    
    frame_count = 0


# TODO: remove
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
    global state, trials, trial, frame_count, results, stop_message,\
        line_length
    # if state == STATE_START:
    #     if event.char in " ":
    #         canvas.delete("start")
    #         state = STATE_PLAY
    #         begin_play()
    #         frame_count = 0
    # elif state == STATE_RATE:
    #     if event.char in "1234567":
    #         if trial < N_LINE_LENGTHS * LEVEL_FREQ:
    #             results.append((LINE_LENGTHS[trials[trial]],
    #                             LINE_ANGLES[2], int(event.char)))
    #         else:
    #             results.append((line_length,
    #                             LINE_ANGLES[trials[trial]], int(event.char)))
    #         trial += 1
    #         canvas.delete("rate")

    #         if trial == N_LINE_LENGTHS * LEVEL_FREQ:
    #             state = STATE_REST
    #             return
    #         if trial == (N_LINE_LENGTHS + N_LINE_ANGLES) * LEVEL_FREQ:
    #             state = STATE_END
    #             stop_message = "Experiment closed."
    #             return
    #         state = STATE_PLAY
    #         begin_play()
    #         frame_count = 0
    # elif state == STATE_REST:
    #     if event.char in " ":
    #         canvas.delete("rest")

    #         # calculate optimal line length from trial 1 ratings
    #         sums = {length: 0 for length in LINE_LENGTHS}
    #         for trial_result in results:
    #             sums[trial_result[0]] += trial_result[2]
    #         best_sum = 0
    #         best_length = 0
    #         for length, sum in sums.items():
    #             if sum > best_sum:
    #                 best_sum = sum
    #                 best_length = length
    #         line_length = best_length

    #         state = STATE_PLAY
    #         begin_play()
    #         frame_count = 0


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
    print(stop_message)
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


def info_dialog() -> None:
    """
    Create a dialog to collect the user's initials.
    Taken from TkDocs.

    Parameters
    ----------
    None taken.

    Returns
    -------
    None.
    """
    global dlg, initials_var
    dlg = Toplevel(window)
    dlg.title("Logging")
    dlg.geometry("+750+500")
    dlg.resizable(False, False)
    initials_var = StringVar(dlg)
    Label(dlg, text="Please enter your initials:").pack()
    Entry(dlg, textvariable=initials_var).pack()
    Label(dlg, text="You may also close this window to exit.").pack()
    Label(dlg, text="During the experiment, you may press"
          + " [Esc] to stop at any time.").pack()
    Button(dlg, text="Done", command=dismiss).pack()
    dlg.protocol("WM_DELETE_WINDOW", dismiss)  # intercept close button
    dlg.transient(window)  # dialog window is related to main
    dlg.wait_visibility()  # can't grab until window appears, so we wait
    dlg.grab_set()  # ensure all input goes to our window
    dlg.wait_window()  # block until window is destroyed


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
    global window, canvas, frame, phase, state, cur_time, fixation,\
        screen_width, screen_height, lines, results, exit_btn, slider_var,\
        slider, done_btn
    window = Tk()
    window.attributes('-fullscreen', True)
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    frame = Frame(window, width=screen_width,
                  height=screen_height*MENUBAR_WINDOW_RATIO,
                  highlightthickness=0)
    exit_btn = Button(frame, text="Exit", command=stop, font=WIDGET_FONT)
    slider_var = IntVar(frame)
    slider = Scale(frame, orient=HORIZONTAL, showvalue=0, variable=slider_var)
    done_btn = Button(frame, text="Done", command=handle_button)

    # TODO: left off here adjusting widgets

    exit_btn.grid(row=1, column=1, sticky="nsew")
    # slider.grid(row=1, column=3, sticky="nsew")
    # done_btn.grid(row=1, column=5, sticky="nsew")
    for r in range(3):
        frame.rowconfigure(r, weight=1)
    for c in range(0, 7, 2):
        frame.columnconfigure(c, weight=1)
    frame.columnconfigure(1, weight=10)
    frame.columnconfigure(3, weight=10)
    frame.columnconfigure(5, weight=10)
    frame.pack()

    canvas = Canvas(window, width=screen_width,
                    height=1 - screen_height*MENUBAR_WINDOW_RATIO,
                    bg="white", highlightthickness=0)
    canvas.pack()

    if not messagebox.askyesno(title="Epilepsy warning",
                               message=SEIZURE_WARNING,
                               icon="warning"):
        print(stop_message)
        return

    # collect initials and time
    info_dialog()
    cur_time = datetime.now()

    try:
        # setup
        # TODO: set `trial` to 0 when entering PHASE_LENGTH or PHASE_ANGLE
        phase = PHASE_START
        state = STATE_INTRO
        results = []
        fixation = [
            canvas.create_rectangle(screen_width / 2 - 10,
                                    screen_height / 2 - 3,
                                    screen_width / 2 + 10,
                                    screen_height / 2 + 3,
                                    fill="black", width=0,
                                    tags=["fixation", "play"],
                                    state="hidden"),
            canvas.create_rectangle(screen_width / 2 - 3,
                                    screen_height / 2 - 10,
                                    screen_width / 2 + 3,
                                    screen_height / 2 + 10,
                                    fill="black", width=0,
                                    tags=["fixation", "play"],
                                    state="hidden")
        ]

        trials = []
        # block 1
        for _ in range(LEVEL_FREQ):
            series = [i for i in range(N_LINE_LENGTHS)]
            shuffle(series)
            trials += series[:]
        # block 2
        for _ in range(LEVEL_FREQ):
            series = [i for i in range(N_LINE_ANGLES)]
            shuffle(series)
            trials += series[:]

        animate()
        window.mainloop()
    except:
        print(stop_message)


if __name__ == "__main__":
    main()
