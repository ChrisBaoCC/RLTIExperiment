#!usr/bin/env python3
"""Python script that runs the experiment."""

__author__ = "Chris Bao"
__version__ = "1.1.1"
__date__ = "8 Jul 2022"

# IMPORTS #
from datetime import datetime
from math import pi, cos, sin
from random import shuffle
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
N_STIM: int = 75
# radius of circle of lines (through midpoints)
RADIUS_BASE: int = 225
# maximum amount of dilation/contraction
MAX_DISPLACEMENT: int = 100
LINE_WIDTH: int = 5

LINE_LENGTHS: tuple[int] = tuple(range(40, 240, 20))
N_LINE_LENGTHS: int = len(LINE_LENGTHS)

LINE_ANGLES: tuple[int] = tuple(range(8, 88, 8))
N_LINE_ANGLES: int = len(LINE_ANGLES)
DEFAULT_ANGLE: int = 48

# trial length in seconds
PLAY_LENGTH = 1 # during experiment: 5 (10 sec total with rating)
# times to show each level per block
LEVEL_REPS: int = 3 # during experiment: 12 (14 total with intro/practice)

SEIZURE_WARNING: str = "WARNING: participating may potentially trigger"\
    + " seizures for people with photosensitive epilepsy."\
    + " If you suspect you have photosensitive epilepsy or have a history"\
    + " of photosensitive epilepsy, please press the [No] button now."\
    + "\n\nDo you wish to proceed?"

INTRO_TEXT: str = f"""Welcome!
This experiment consists of 2 blocks of {(LEVEL_REPS) * N_LINE_LENGTHS} trials.
In the middle you will be given a short break.

At the start of each block will be {N_LINE_LENGTHS} introduction trials.
These are to get you familiar with various illusion strengths.
Then will be {N_LINE_LENGTHS} practice trials, which you will rate.
The ratings of practice trials do not count and will not be recorded.
Last are the {LEVEL_REPS * N_LINE_LENGTHS} experimental trials.
These do count and the results will be recorded.

Thank you for your participation!"""
INTRO_TEXT2: str = """On the upper left is the [Exit] button. You may press
this at any time to stop the experiment. Note that if you stop early, your
results will NOT be recorded.

On the upper middle is the slider, which you will use to rate the illusion
strength over the course of the experiment.

On the upper right is the [Next] button, which you will press to move between
stages of the experiment."""

LENGTH_INTRO_TEXT: str = f"""Welcome to block 1 of the experiment.
First you will be shown {N_LINE_LENGTHS} illusions of varying strength,
but you do not need to rate them."""
ANGLE_INTRO_TEXT: str = f"""Welcome to block 2 of the experiment.
As before, there will be {N_LINE_LENGTHS} intro illusions,
{N_LINE_LENGTHS} practice illusions, and {LEVEL_REPS} sets of {N_LINE_LENGTHS}
experimental illusions."""

RATE_PRAC_TEXT: str = f"""Next, you will be shown another {N_LINE_LENGTHS}
illusions. You will rate these as practice for the experimental stage.
A rating of 0 indicates no illusion strength, while a rating of 100
indicates the illusion with highest strength."""
RATE_EXP_TEXT: str = f"""For the final stage of this block, you will be shown
{LEVEL_REPS} sets of {N_LINE_LENGTHS} illusions. Your ratings for these trials
will be recorded."""
REST_TEXT: str = """This marks the end of the first experimental block.
Feel free to take a short break, then press [Next] to continue to block 2."""

END_TEXT: str = """This marks the end of the experiment. Your data has been saved.
Press the [Exit] button to finish."""

NEXT_PROMPT: str = "\n\n(Press the [Next] button to continue)"

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

# [canvas id, [inner_x, inner_y]]
# inner coords used for updating position of lines during animation
lines: list[int, list[int]]

line_angle: int
line_length: int

radius: float
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


def mark_rated(_: Event) -> None:
    """
    Set the current trial as having been rated and updates the text.
    Should not be manually called; tied to the slider's update command.

    Parameters
    ----------
    _: Event given by tkinter event handler. Ignored.

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
    # (center of screen) + (radius vector) - 1/2 (line vector)
    return np.array((screen_width / 2, canvas.winfo_height() / 2))\
            + pol_to_rect(radius, i / N_STIM * 360)\
            - pol_to_rect(line_length, line_angle + i / N_STIM * 360) * 0.5

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
    # (center of screen) + (radius vector) + 1/2 (line vector)
    return np.array((screen_width / 2, canvas.winfo_height() / 2))\
            + pol_to_rect(radius, i / N_STIM * 360)\
            + pol_to_rect(line_length, line_angle + i / N_STIM * 360) * 0.5
    

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
    global lines, radius
    if frame_count % STIM_PERIOD < STIM_PERIOD/2:
        radius += MAX_DISPLACEMENT * (2 / STIM_PERIOD)
    else:
        radius -= MAX_DISPLACEMENT * (2 / STIM_PERIOD)
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
            canvas.itemconfig(text, text=INTRO_TEXT2 + NEXT_PROMPT)
        elif state == STATE_INTRO2:
            phase = PHASE_LENGTH
            state = STATE_INTRO
            canvas.itemconfig(text, text=LENGTH_INTRO_TEXT + NEXT_PROMPT)
    elif phase == PHASE_LENGTH:
        if state == STATE_INTRO:
            state = STATE_PLAY_INTRO
            trial = 0
            start_trial()
        elif state == STATE_RATE_INTRO:
            if trial == N_LINE_LENGTHS:
                state = STATE_INTRO2
                canvas.itemconfig(text, state="normal", text=RATE_PRAC_TEXT
                                  + NEXT_PROMPT)
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
                    canvas.itemconfig(text, state="normal",
                                      text=RATE_EXP_TEXT + NEXT_PROMPT)
                else:
                    state = STATE_PLAY_PRAC
                    start_trial()
        elif state == STATE_INTRO3:
            state = STATE_PLAY_EXP
            start_trial()
        elif state == STATE_RATE_EXP:
            if rated:
                results.append((line_length, line_angle, slider_var.get()))
                if trial == (2+LEVEL_REPS) * N_LINE_LENGTHS:
                    phase = PHASE_REST
                    state = STATE_INTRO
                    canvas.itemconfig(text, state="normal", text=REST_TEXT)
                else:
                    state = STATE_PLAY_EXP
                    start_trial()

    elif phase == PHASE_REST:
        phase = PHASE_ANGLE
        state = STATE_INTRO
        canvas.itemconfig(text, state="normal", text=ANGLE_INTRO_TEXT
                          + NEXT_PROMPT)
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
            if trial == (2+LEVEL_REPS) * N_LINE_LENGTHS + N_LINE_ANGLES:
                state = STATE_INTRO2
                canvas.itemconfig(text, state="normal", text=RATE_PRAC_TEXT
                                  + NEXT_PROMPT)
            else:
                state = STATE_PLAY_INTRO
                start_trial()
        elif state == STATE_INTRO2:
            state = STATE_PLAY_PRAC
            start_trial()
        elif state == STATE_RATE_PRAC:
            if rated:
                if trial == (2+LEVEL_REPS) * N_LINE_LENGTHS\
                        + 2 * N_LINE_ANGLES:
                    state = STATE_INTRO3
                    canvas.itemconfig(text, state="normal", text=RATE_EXP_TEXT
                                      + NEXT_PROMPT)
                else:
                    state = STATE_PLAY_PRAC
                    start_trial()
        elif state == STATE_INTRO3:
            state = STATE_PLAY_EXP
            start_trial()
        elif state == STATE_RATE_EXP:
            if rated:
                results.append((line_length, line_angle, slider_var.get()))
                if trial == (2+LEVEL_REPS) * N_LINE_LENGTHS\
                        + (2+LEVEL_REPS) * N_LINE_ANGLES:
                    phase = PHASE_END
                    state = STATE_INTRO
                    canvas.itemconfig(text, state="normal", text=END_TEXT)
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
    global state, frame_count, radius, trial, line_length,\
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

    canvas.after(1000 // UPDATES_PER_SECOND, animate)


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
    global lines, line_length, line_angle, frame_count, radius
    radius = RADIUS_BASE

    canvas.itemconfig(text, state="hidden")
    for i in fixation:
        canvas.itemconfigure(i, state="normal")

    lines = []
    if phase == PHASE_LENGTH:
        line_length = LINE_LENGTHS[trials[trial]]
        line_angle = DEFAULT_ANGLE
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
        for _ in range(LEVEL_REPS + 2):
            series = [i for i in range(N_LINE_LENGTHS)]
            shuffle(series)
            trials += series[:]
        # block 2
        for _ in range(LEVEL_REPS + 2):
            series = [i for i in range(N_LINE_ANGLES)]
            shuffle(series)
            trials += series[:]

        text = canvas.create_text(screen_width / 2, screen_height / 2,
                                  text=INTRO_TEXT + NEXT_PROMPT,
                                  tags=["start"], **TEXT_ARGS)
        animate()
        window.mainloop()
    except:
        print(stop_message)


if __name__ == "__main__":
    main()
