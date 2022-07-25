#!usr/bin/env python3
"""Python script that runs the experiment."""

__author__ = "Chris Bao"
__version__ = "2.1"
__date__ = "25 Jul 2022"

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

# frames per second CALCULATED, NOT DISPLAYED!
UPDATES_PER_SECOND: int = 100

# number of lines to show
N_STIM: int = 60
# maximum amount of dilation/contraction
MAX_DISPLACEMENT: int = 100
LINE_WIDTH: int = 5

# angle from radius to line
LINE_ANGLE: int = 45  # controlled

LINE_LENGTHS = tuple(range(30, 180, 30))  # tuple[int]
N_LINE_LENGTHS: int = len(LINE_LENGTHS)  # 5

STIM_RADII = tuple(range(150, 400, 50))  # tuple[int]
N_STIM_RADII: int = len(STIM_RADII)  # 5

STIM_PERIODS = (25, 50, 100, 150, 200)  # tuple[int]
N_STIM_PERIODS: int = len(STIM_PERIODS)  # 5

N_TRIALS: int = N_LINE_LENGTHS * N_STIM_RADII * N_STIM_PERIODS  # per block
N_BLOCKS: int = 5  # note that one of these is reserved as practice

# trial length in seconds
# NOTE: lab computer is slower (90% speed), so 2.7 s -> 3 s.
# actual periods are 10/9ths what they're recorded as.
PLAY_LENGTH: float = 2.7
# times to show each level per block
LEVEL_REPS: int = 10

SEIZURE_WARNING: str = "WARNING: participating may potentially trigger"\
    + " seizures for people with photosensitive epilepsy."\
    + " If you suspect you have photosensitive epilepsy or have a history"\
    + " of photosensitive epilepsy, please press the [No] button now."\
    + "\n\nDo you wish to proceed?"

with open("script.txt", "r") as f:
    script = tuple(f.read().split("==="))
(INTRO_TEXT,
 INTRO_TEXT2,
 INTRO_TEXT3,

 PRAC_INTRO_TEXT,
 EXP_INTRO_TEXT,

 REST_TEXT,

 END_TEXT,

 NEXT_PROMPT,
 RATE_PROMPT) = script

PHASE_START = 0
PHASE_PRAC = 1
PHASE_EXP = 2
PHASE_REST = 3
PHASE_END = 4

STATE_INTRO = 10
STATE_INTRO2 = 11
STATE_INTRO3 = 12
STATE_PLAY = 13
STATE_RATE = 14

MENU_BG: str = "#f0f0f0"
WIDGET_BG: str = "#e0e0e0"
WIDGET_ACTIVE_BG: str = "#d0d0d0"
WIDGET_FONT: tuple = ("Helvetica", 24, "bold")

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
# fixation: list[int]
fixation = []

# [canvas id, [inner_x, inner_y]]
# inner coords used for updating position of lines during animation
# lines: list[int, list[int]]
lines = []

# self-explanatory
line_length: int
# radius of circle of lines (through midpoints)
stim_radius: int
anim_radius: int

# of one expansion and contraction, in frames (= 1 s)
stim_period: int

frame_count: int

# in the current trial, whether the subject has rated the illusion or not
entered: bool
rated: bool

# current phase of program: start, practice, block, rest, end.
phase: int
# current state of program: what is being animated.
state: int
# stores index of line length, angle to use for each trial
trials = []  # list[list[int]]
# current trial index
trial: int
# line length, stim radius, stim period, user rating
practice_results = []  # for postmortem analysis
results = []  # list[tuple[int, int, int, int]]

# gets printed to console when experiment is closed
stop_message: str = "Experiment was closed early."


def mark_entered(_: Event) -> None:
    """
    Mark the slider as having been entered.

    Parameters
    ----------
    _: Event given by the tkinter event handler. Ignored.

    Returns
    -------
    None.
    """
    global entered
    entered = True


def mark_rated(_: Event) -> None:
    """
    Set the current trial as having been rated and updates the text.
    Should not be manually called; bound to the slider.

    Parameters
    ----------
    _: Event given by tkinter event handler. Ignored.

    Returns
    -------
    None.
    """
    global rated
    if state in [STATE_RATE, STATE_PLAY] and entered:
        rated = True
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
        + pol_to_rect(anim_radius, i / N_STIM * 360)\
        - pol_to_rect(line_length, LINE_ANGLE + i / N_STIM * 360) * 0.5


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
        + pol_to_rect(anim_radius, i / N_STIM * 360)\
        + pol_to_rect(line_length, LINE_ANGLE + i / N_STIM * 360) * 0.5


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
    global lines, anim_radius
    cur_frame = frame_count % stim_period
    if cur_frame < stim_period / 2:
        anim_radius = stim_radius + (MAX_DISPLACEMENT * 2
                                     * cur_frame / stim_period)
    else:
        anim_radius = stim_radius + (MAX_DISPLACEMENT * 2
                                     * (stim_period - cur_frame) / stim_period)
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
    filename = "data/" + initials_var.get().lower()\
        + cur_time.__str__() + ".csv"
    filename = filename.replace(" ", "").replace(":", "-")
    with open(filename, "w") as f:
        f.write("trial,line_length,stim_radius,stim_period,rating")
        f.write("\n")
        for trial_result in enumerate(results):
            f.write(
                ",".join(
                    [str(trial_result[0]), str(trial_result[1][0]),
                     str(trial_result[1][1]), str(trial_result[1][2]),
                     str(trial_result[1][3])]
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
    global phase, state, trial
    if phase == PHASE_START:
        if state == STATE_INTRO:
            state = STATE_INTRO2
            canvas.itemconfig(text, text=INTRO_TEXT2 + NEXT_PROMPT)
        elif state == STATE_INTRO2:
            state = STATE_INTRO3
            canvas.itemconfig(text, text=INTRO_TEXT3 + NEXT_PROMPT)
        elif state == STATE_INTRO3:
            phase = PHASE_PRAC
            state = STATE_INTRO
            canvas.itemconfig(text, text=PRAC_INTRO_TEXT + NEXT_PROMPT)
    elif phase == PHASE_PRAC:
        if state == STATE_INTRO:
            state = STATE_PLAY
            trial = 0
            start_trial()
        elif state == STATE_RATE:
            if not rated:
                return
            practice_results.append((line_length, stim_radius, stim_period,
                                     slider_var.get()))
            if trial == N_TRIALS:
                phase = PHASE_REST
                state = STATE_INTRO
                canvas.itemconfig(text, state="normal", text=REST_TEXT)
            else:
                state = STATE_PLAY
                start_trial()
    elif phase == PHASE_REST:
        phase = PHASE_EXP
        state = STATE_INTRO
        canvas.itemconfig(text, state="normal", text=EXP_INTRO_TEXT
                          + NEXT_PROMPT)
    elif phase == PHASE_EXP:
        if state == STATE_INTRO:
            state = STATE_PLAY
            start_trial()
        elif state == STATE_RATE:
            if not rated:
                return
            results.append((line_length, stim_radius, stim_period,
                            slider_var.get()))
            if trial == N_TRIALS * N_BLOCKS:
                phase = PHASE_END
                state = STATE_INTRO
                save()
                canvas.itemconfig(text, state="normal", text=END_TEXT)
            elif trial % N_TRIALS == 0:
                phase = PHASE_REST
                state = STATE_INTRO
                canvas.itemconfig(text, state="normal", text=REST_TEXT)
            else:
                state = STATE_PLAY
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
    global state, frame_count

    if state == STATE_PLAY:
        if frame_count > PLAY_LENGTH * UPDATES_PER_SECOND:
            stop_trial()
            state = STATE_RATE
            if not rated:
                canvas.itemconfig(text, state="normal", text=RATE_PROMPT)
            else:
                # text already configured to "Press next"
                canvas.itemconfig(text, state="normal")
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
    global line_length, stim_radius, stim_period, frame_count, rated,\
        anim_radius

    canvas.itemconfig(text, state="hidden")
    for i in fixation:
        canvas.itemconfigure(i, state="normal")

    line_length = LINE_LENGTHS[trials[trial][0]]
    stim_radius = STIM_RADII[trials[trial][1]]
    anim_radius = stim_radius
    stim_period = STIM_PERIODS[trials[trial][2]]

    lines.clear()

    for i in range(N_STIM):
        line_id = canvas.create_line(
            *get_inner(i),
            *get_outer(i),
            fill="black",
            width=LINE_WIDTH,
            tags=["line", "play"]
        )
        lines.append([line_id, list(get_inner(i))])

    slider.set(0)
    frame_count = 0
    entered = False
    rated = False


def stop(_: Event = None):
    """
    Stop the experiment.

    Parameters
    ----------
    _: Event given by tkinter event handler. Ignored.

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
                      bg=WIDGET_BG, activebackground=WIDGET_ACTIVE_BG,
                      relief="flat", highlightthickness=0)
    slider_var = IntVar(frame)
    slider = Scale(frame, orient=HORIZONTAL, showvalue=0, variable=slider_var,
                   length=500, width=30, bg=MENU_BG, fg="black",
                   resolution=-1, highlightthickness=0, relief="flat",
                   troughcolor=WIDGET_BG, activebackground=WIDGET_ACTIVE_BG)
    slider.bind("<Enter>", mark_entered)
    slider.bind("<Leave>", mark_rated)
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

        block = []
        for i in range(N_LINE_LENGTHS):
            for j in range(N_STIM_RADII):
                for k in range(N_STIM_PERIODS):
                    block.append((i, j, k))
        for _ in range(N_BLOCKS):
            shuffle(block)
            trials += block[:]

        text = canvas.create_text(screen_width / 2, screen_height / 2,
                                  text=INTRO_TEXT + NEXT_PROMPT,
                                  tags=["start"], **TEXT_ARGS)
        animate()
        window.mainloop()
    except:
        print(stop_message)


if __name__ == "__main__":
    main()
