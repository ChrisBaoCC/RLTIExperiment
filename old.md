# RLTI Extension Project

Base experiment: RLTI (Rotating Tilted Lines Illusion)

## Arcs

Switch lines to curves.

Variables:

* Orientation relative to circumference (angle or rotation)
* Curvature (intensity of curve); c = 1/r
* Length

Create and test a simulation and write up an informal report.

## Lines

* Control for angle and find the length that maximizes the rotation effect
* Using this length, systematically find the angle that maximizes the rotation
* OR combine these two at the same time: see if they are independent or not

## Links

[Original description](https://journals.sagepub.com/doi/10.1068/p5531)

## Info about arc generation

* stroke thickness: 0.75 mm

* page: 500 mm

* generation: arc of a circle from $-x$ to $x$ degrees (i.e., total is $2x$ degrees)

| Angle ($\degree$) | Radius ($= 200\frac{\sin5}{\sin x}$ , mm) | Curvature ($=1/radius$) |
| ----------------- | ----------------------------------------- | ----------------------- |
| 5                 | 200.000                                   | 5.00e-3                 |
| 15                | 67.349                                    | 1.48e-2                 |
| 30                | 34.862                                    | 2.87e-2                 |
| 45                | 24.651                                    | 4.06e-2                 |
| 60                | 20.128                                    | 4.97e-2                 |
| 75                | 18.046                                    | 5.54e-2                 |
| 90                | 17.431                                    | 5.74e-2                 |

## Keybinds

* `space`: switch between line and arc mode
* Number keys: line/arc orientation (`1` = 0° to `7` = 90°)
* QWERTY keys:
    * Line mode: change length (`q` = 50 px to `p` = 500 px)
    * Arc mode: change curvature (`q` = 5° to `u` = 90°)
* ASDFG keys: circle radius (`a` = 200 px to `l` = 650 px)

## Findings

Default configuration: line mode, 45°, 150 px length, 400 px circle

Best angle: setting `5` = 60°

Best length at 60°: setting `u` = 350 px

​ Hypothesis: rotation effect diminished when enough of the stimulus goes off-screen.

Arcs do create the illusory rotation effect. Using default settings, the best arc was between `4` and `5` (arc measure between 45 and 60°)

## Notes

Distance between user and monitor: 24.5 in

Monitor: 93 ppi

1 inch = 2.43°

350 px / 93 ppi \* 2.43 in = 9.13°

middle temporal cortex receptive field size (motion detection): about 10 deg

### Continuations

1. Randomize length for block 1 (45° angle)
    1. Selected from levels 1–7 (find which ones to use: half of optimal length to twice optimal length)
    2. Each level 3–4 times
    3. Subject presses a button to rate illusion magnitude. Levels 1–4
2. Statistics
    1. Mean illusion strength of each length
    2. Find the best one

3. Randomize angle (optimal length based on block 1)
    1. Selected from levels 1–6 corresponding to angles 20–70°
    2. Each level 3–4 times
    3. Subject presses a button to rate illusion magnitude. Levels 1–4
4. Statistics
    1. Based on optimal length, find optimal angle
5. Idea: start with finding angle first and then try finding optimal length from there to confirm we found the optimal angle

Duration of trial: 2–3 s?

Dilation/contraction frequency: find this (in the paper, it was every 0.5 s)

Inter-stimulus interval for participants to enter their rating

Have this done by the summer?
