# Yazdan Experiment: RLTI Extension Project

Base experiment: RLTI (Rotating Tilted Lines Illusion)

## Arcs

Switch lines to curves.

Variables:

* Orientation (angle) relative to circumference
* Curvature (intensity of curve); c = 1/r
* Arc length

## Lines

* Control for angle and find the length that maximizes the rotation effect.
* Control for length and find the angle that maximizes the rotation effect.
* OR combine these two at the same time: see if they are independent or not.

## Links

[Original paper](https://journals.sagepub.com/doi/10.1068/p5531)

## Keybinds

* fill out later

## Continuation

Uses only lines.

### Block 1

1. Orientation relative to circumference controlled: 45°
2. Randomize line segment length
    1. Selected from levels 1–7 (4 is optimal, 1 is half, 7 is double)
    2. Each level is shown 3 times
    3. Subject presses a button to rate illusion magnitude. Levels 1–4
        1. *Note: number keys or slider? Number keys are faster but slider is better for continuity and granularity*
3. Statistics
    1. Mean illusion strength of each length
    2. Find the best one (highest mean strength)

### Block 2

1. Line segment length controlled: uses the highest-strength length from block 1
2. Randomize line segment orientation
    1. Selected from levels 1–6 (angles 20–70°)
    2. Each level is shown 3 times
    3. Subject presses a button to rate illusion magnitude. See Block 1 § 2.3.1 above.
3. Statistics
    1. Mean illusion strength of each orientation given the optimal length
4. Idea: start with finding angle first and then try finding optimal length from there to confirm we found the optimal angle. Another approach is to find both at the same time, progressively making the pool of possible angles and lengths smaller and smaller.

### Notes

* Duration of trials: 2–3 s each
* Dilation/contraction frequency: find this (in the paper, it was every 0.5 s)
* Inter-stimulus interval for participants to enter their rating
* Optoma HD25 settings: HD, 1080p, 2000 ANSI lumens, 120 Hz projector
* Computer monitor: 60 Hz (approximated; frames are rendered to the nearest millisecond due to delays being multiples of 1 ms)
* 3 variables:
    * Radius of circle
    * Length of line
    * Angle of line
        * First!
            * Could just go with optimized angle.
            * Randomize length & radius?
                * Radius second.
                * Min length: find experimentally.
                * Max length: find by finding where the effect starts plateauing.
* Receptive field size varies with eccentricity (distance from center).
    * Min length of lines to create effect changes → dependent on radius.
