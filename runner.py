#!usr/bin/env python3
"""Python script that runs the experiment."""

__author__ = "Chris Bao"
__version__ = "1.1"
__date__ = "7 Jul 2022"

# IMPORTS #
from datetime import datetime
from math import pi, cos, sin
from random import shuffle
from tracemalloc import start
from turtle import window_height
import numpy as np
from tkinter import CENTER, HORIZONTAL, Button, Entry, Event, Frame, IntVar,\
    Label, Scale, StringVar, Tk, Canvas, Toplevel, messagebox

# CONSTANTS #
# relative weights (sizes) of menubar and canvas
MENU_WEIGHT: int = 1
CANVAS_WEIGHT: int = 15

# NOT frames per second!
UPDATES_PER_SECOND: int = 100
# of one expansion and contraction, in frames (= 1 s)
STIM_PERIOD: int = UPDATES_PER_SECOND

# number of lines to show
N_STIM: int = 90
# inner radius of circle of lines
INNER_RADIUS_BASE: int = 200
LINE_WIDTH: int = 5

LINE_LENGTHS: tuple[int] = (50, 75, 100, 150, 200, 250, 300)
N_LINE_LENGTHS: int = len(LINE_LENGTHS)

LINE_ANGLES: tuple[int] = (12, 24, 36, 48, 60, 72, 84)
N_LINE_ANGLES: int = len(LINE_ANGLES)

# TODO trials only shown once for testing
# times to show each level
LEVEL_FREQ: int = 3

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
STATE_INTRO2 = 11
STATE_INTRO3 = 12
STATE_PLAY_INTRO = 13
STATE_PLAY_PRAC = 14
STATE_PLAY_EXP = 15
STATE_RATE_INTRO = 16
STATE_RATE_PRAC = 17
STATE_RATE_EXP = 18


# TODO play length shortened for testing
PLAY_LENGTH = 5  # trial length in seconds

MENU_BG: str = "#f0f0f0"
WIDGET_BG: str = "#e0e0e0"
WIDGET_ACTIVE_BG: str = "#d0d0d0"
WIDGET_FONT: tuple = ("Helvetica Neue", 16)

TEXT_ARGS: dict = {
    "font": "Helvetica 24",
    "fill": "black",
    "justify": CENTER,
}

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
next_btn: Button

initials_var: StringVar
cur_time: datetime

# store Canvas item id of text to display
text: int

# store Canvas item ids of fixation cross (2 rectangles)
fixation: list[int]

lines: list[int]

line_angle: int
line_length: int

inner_radius: int
frame_count: int

# in the current trial, whether the subject has rated the illusion or not
rated: bool

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


def mark_rated(e: Event) -> None:
    """
    Set the current trial as having been rated and updates the text.

    Parameters
    ----------
    e: Event given by tkinter event handler.

    Returns
    -------
    None.
    """
    global rated
    rated = True
    if state in [STATE_RATE_PRAC, STATE_RATE_EXP]:
        canvas.itemconfig(text, text="(Press the [Next] button to continue)")


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
        + np.array((screen_width / 2, canvas.winfo_height() / 2))


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
    global lines, inner_radius
    if frame_count % STIM_PERIOD < STIM_PERIOD/2:
        inner_radius += line_length * (1 / STIM_PERIOD)
    else:
        inner_radius -= line_length * (1 / STIM_PERIOD)
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
    Handle presses of the [Next] button.

    Parameters
    ----------
    None taken.

    Returns
    -------
    None.
    """
    global phase, state, trial, frame_count, results, line_length
    if phase == PHASE_START:
        if state == STATE_INTRO:
            state = STATE_INTRO2
            canvas.itemconfig(text, text="""On the upper left is the [Exit] button. You may press this at any time
to stop the experiment. Note that if you stop early, your results will not
be recorded.

On the upper middle is the slider, which you will use to rate the illusion
strength over the course of the experiment.

On the upper right is the [Next] button, which you will press to move
between stages of the experiment.

(Press the [Next] button to continue)""")
        elif state == STATE_INTRO2:
            phase = PHASE_LENGTH
            state = STATE_INTRO
            canvas.itemconfig(text, text="""Welcome to block 1 of the experiment. First you will be shown 7
illusions of varying strength, but you do not need to rate them.

(Press the [Next] button to continue)""")
    elif phase == PHASE_LENGTH:
        if state == STATE_INTRO:
            state = STATE_PLAY_INTRO
            trial = 0
            start_trial()
        elif state == STATE_RATE_INTRO:
            if trial == N_LINE_LENGTHS:
                state = STATE_INTRO2
                canvas.itemconfig(text, state="normal", text="""Next, you will be shown another 7 illusions.
You will rate these as practice for the experimental stage.""")
            else:
                state = STATE_PLAY_INTRO
                start_trial()
        elif state == STATE_INTRO2:
            state = STATE_PLAY_PRAC
            start_trial()
        elif state == STATE_RATE_PRAC:
            if rated:
                if trial == 2 * N_LINE_LENGTHS:
                    state = STATE_INTRO3
                    canvas.itemconfig(text, state="normal", text="""For the final stage of this block, you will be shown 3 sets of 7 illusions.
Your ratings for these trials will be recorded.""")
                else:
                    state = STATE_PLAY_PRAC
                    start_trial()
        elif state == STATE_INTRO3:
            state = STATE_PLAY_EXP
            start_trial()
        elif state == STATE_RATE_EXP:
            if rated:
                results.append((line_length, line_angle, slider_var.get()))
                if trial == (2+LEVEL_FREQ) * N_LINE_LENGTHS:
                    phase = PHASE_REST
                    state = STATE_INTRO
                    canvas.itemconfig(text, state="normal", text=
"""
This marks the end of the first experimental block.
Feel free to take a short break, then press [Next] to continue to block 2.""")
                else:
                    state = STATE_PLAY_EXP
                    start_trial()

    elif phase == PHASE_REST:
        phase = PHASE_ANGLE
        state = STATE_INTRO
        canvas.itemconfig(text, state="normal", text=
"""Welcome to block 2 of the experiment.
As before, you will be shown 7 intro illusions, 7 practice illusions,
and 3 sets of 7 experimental illusions.

(Press [Next] to continue)""")
        sums = {length: 0 for length in LINE_LENGTHS}
        for trial_result in results:
            sums[trial_result[0]] += trial_result[2]
        best_sum = 0
        best_length = 0
        for length, sum in sums.items():
            if sum > best_sum:
                best_sum = sum
                best_length = length
        line_length = best_length

    elif phase == PHASE_ANGLE:
        if state == STATE_INTRO:
            state = STATE_PLAY_INTRO
            start_trial()
        elif state == STATE_RATE_INTRO:
            if trial == (2+LEVEL_FREQ) * N_LINE_LENGTHS + N_LINE_ANGLES:
                state = STATE_INTRO2
                canvas.itemconfig(text, state="normal", text="""Next, you will be shown another 7 illusions.
You will rate these as practice for the experimental stage.""")
            else:
                state = STATE_PLAY_INTRO
                start_trial()
        elif state == STATE_INTRO2:
            state = STATE_PLAY_PRAC
            start_trial()
        elif state == STATE_RATE_PRAC:
            if rated:
                if trial == (2+LEVEL_FREQ) * N_LINE_LENGTHS\
                            + 2 * N_LINE_ANGLES:
                    state = STATE_INTRO3
                    canvas.itemconfig(text, state="normal", text="""For the final stage of this block, you will be shown 3 sets of 7 illusions.
Your ratings for these trials will be recorded.""")
                else:
                    state = STATE_PLAY_PRAC
                    start_trial()
        elif state == STATE_INTRO3:
            state = STATE_PLAY_EXP
            start_trial()
        elif state == STATE_RATE_EXP:
            if rated:
                results.append((line_length, line_angle, slider_var.get()))
                if trial == (2+LEVEL_FREQ) * N_LINE_LENGTHS\
                        + (2+LEVEL_FREQ) * N_LINE_ANGLES:
                    phase = PHASE_END
                    state = STATE_INTRO
                    canvas.itemconfig(text, state="normal", text=
"""
This marks the end of the experiment. Your data has been saved.
Press the [Exit] button to finish.""")
                    save()
                else:
                    state = STATE_PLAY_EXP
                    start_trial()


def stop_trial() -> None:
    """
    Removes trial animations (stimulus and fixation) from the screen.

    Parameters
    ----------
    None taken.

    Returns
    -------
    None.
    """
    global trial
    canvas.delete("line")
    for i in fixation:
        canvas.itemconfig(i, state="hidden")
    trial += 1

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
    global state, frame_count, inner_radius, trial, line_length,\
        line_angle, text, rated

    if phase == PHASE_LENGTH or phase == PHASE_ANGLE:
        if state == STATE_PLAY_INTRO:
            if frame_count > PLAY_LENGTH * UPDATES_PER_SECOND:
                stop_trial()
                state = STATE_RATE_INTRO
                canvas.itemconfig(text, state="normal",
                                  text="(Press the [Next] button to continue)")
            else:
                update_stimulus()
                frame_count += 1
        elif state == STATE_PLAY_PRAC:
            if frame_count > PLAY_LENGTH * UPDATES_PER_SECOND:
                stop_trial()
                state = STATE_RATE_PRAC
                rated = False
                canvas.itemconfig(text, state="normal",
                                  text="Please rate the illusion strength with the slider.")
            else:
                update_stimulus()
                frame_count += 1
        elif state == STATE_PLAY_EXP:
            if frame_count > PLAY_LENGTH * UPDATES_PER_SECOND:
                stop_trial()
                state = STATE_RATE_EXP
                rated = False
                canvas.itemconfig(text, state="normal",
                        text="Please rate the illusion strength with the slider.")
            else:
                update_stimulus()
                frame_count += 1

    canvas.after(10, animate)


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
    global lines, line_length, line_angle, frame_count, inner_radius
    inner_radius = INNER_RADIUS_BASE

    canvas.itemconfig(text, state="hidden")
    for i in fixation:
        canvas.itemconfigure(i, state="normal")

    lines = []
    if phase == PHASE_LENGTH:
        line_length = LINE_LENGTHS[trials[trial]]
        line_angle = LINE_ANGLES[2]
    elif phase == PHASE_ANGLE:
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
    dlg.geometry("+720+500")
    dlg.resizable(False, False)
    initials_var = StringVar(dlg)
    Label(dlg, text="Please enter your initials:").pack()
    Entry(dlg, textvariable=initials_var).pack()
    Label(dlg, text="You may also close this window to exit.").pack()
    Label(dlg, text="During the experiment, you may press"
          + " the [Exit] button to stop at any time.").pack()
    Button(dlg, text="Next", command=dismiss).pack()
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
        slider, next_btn, text, trials
    window = Tk()
    window.attributes('-fullscreen', True)
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    frame = Frame(window, highlightthickness=0, bg=MENU_BG)
    exit_btn = Button(frame, text="Exit", command=stop, font=WIDGET_FONT,
                      bg=WIDGET_BG, activebackground=WIDGET_ACTIVE_BG, relief="flat",
                      highlightthickness=0)
    slider_var = IntVar(frame)
    slider = Scale(frame, orient=HORIZONTAL, showvalue=0, variable=slider_var,
                   length=500, width=30, bg=MENU_BG, fg="black", resolution=-1,
                   highlightthickness=0, relief="flat", troughcolor=WIDGET_BG,
                   activebackground=WIDGET_ACTIVE_BG, command=mark_rated)
    next_btn = Button(frame, text="Next", command=handle_button,
                      font=WIDGET_FONT, bg=WIDGET_BG, highlightthickness=0,
                      activebackground=WIDGET_ACTIVE_BG, relief="flat")

    exit_btn.grid(row=1, column=1, sticky="nsew")
    slider.grid(row=1, column=3, sticky="nsew")
    next_btn.grid(row=1, column=5, sticky="nsew")
    for r in range(3):
        frame.rowconfigure(r, weight=1)
    for c in range(0, 7, 2):
        frame.columnconfigure(c, weight=1)
    frame.columnconfigure(1, weight=1)
    frame.columnconfigure(3, weight=1)
    frame.columnconfigure(5, weight=1)
    frame.grid(row=0, column=0, sticky="nsew")

    canvas = Canvas(window, bg="white", highlightthickness=0)
    canvas.grid(row=1, column=0, sticky="nsew")

    window.rowconfigure(0, weight=MENU_WEIGHT)
    window.rowconfigure(1, weight=CANVAS_WEIGHT)
    window.columnconfigure(0, weight=1)

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
        phase = PHASE_START
        state = STATE_INTRO
        results = []
        fixation = [
            canvas.create_rectangle(screen_width / 2 - 10,
                                    canvas.winfo_height() / 2 - 3,
                                    screen_width / 2 + 10,
                                    canvas.winfo_height() / 2 + 3,
                                    fill="black", width=0,
                                    tags=["fixation", "play"],
                                    state="hidden"),
            canvas.create_rectangle(screen_width / 2 - 3,
                                    canvas.winfo_height() / 2 - 10,
                                    screen_width / 2 + 3,
                                    canvas.winfo_height() / 2 + 10,
                                    fill="black", width=0,
                                    tags=["fixation", "play"],
                                    state="hidden")
        ]

        trials = []
        # block 1; note the `+2` because of intro and practice trials
        for _ in range(LEVEL_FREQ + 2):
            series = [i for i in range(N_LINE_LENGTHS)]
            shuffle(series)
            trials += series[:]
        # block 2
        for _ in range(LEVEL_FREQ + 2):
            series = [i for i in range(N_LINE_ANGLES)]
            shuffle(series)
            trials += series[:]

        text = canvas.create_text(screen_width / 2, screen_height / 2, text="""Welcome!
This experiment consists of 2 blocks of 21 trials.
In the middle you will be given a short break.

At the beginning of each block, there will be 7 introduction trials.
These are to get you familiar with various illusion strengths.
Then will be 7 practice trials, where you will rate them accordingly.
The ratings of practice trials do not count and will not be recorded.
Last are the 21 experimental trials.
These do count and the results will be recorded.

Thank you for your participation!

(Press the [Next] button to continue)""",
                                  tags=["start"], **TEXT_ARGS)
        animate()
        window.mainloop()
    except:
        print(stop_message)


if __name__ == "__main__":
    main()
