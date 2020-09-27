OpenScope Credit Assignment Passive Training Stimuli
====================================================

- There is one habituation script per day, and it is fully contained (i.e., it does not depend on any other scripts we've written).
- There are 30 second grayscreen periods at the start and the end of the session, as well as between the 3 stimulus blocks (1 Gabor stimulus block and 2 Brick stimulus blocks).
- The Gabor stimulus block is about 1/2 of the habituation time, whereas the 2 Brick stimulus blocks are each about 1/4 of the habituation time. The order in which they occur is random for each session and each subject, other than the fact that the 2 Brick blocks will always follow one another.
- The 2 Brick stimulus blocks differ as follows: in one block, the Bricks move left, and in the other block, the Bricks move right. 
- None of the habituation stimuli contain any of the “mismatch” or “surprise” stimulus components, as described in the pilot experiment plan.
- The day numbers are described in accordance with the table circulated by Carol. So the amount of time for each script is:
(day6, 10mins); (day7, 20mins); (day8, 30mins); (day9, 40mins); (day10, 50mins)

Gabor Stimulus Description
--------------------------
- 30 Gabors with random locations in each of the frames (A,B,C,D).
- Each Gabor has size sampled uniformly from 10-20 vis deg (FWHM); width and height are the same.
- Contrast is 100%.
- Spatial frequency is 0.04 cycles/deg and phase is 0.25.
- Gabors come in 4 frames (A,B,C,D), each of which has a different set of positions and sizes for the Gabors.
- The same set of Gabor locations and sizes is maintained for an entire session, but changes between sessions and animals.
- Sequence is ABCD_ABCD_ABCD_..., where “_” is the blank grayscreen frame.
- Each frame lasts 0.3 seconds, and the sequence lasts 1.5 seconds.
- At each sequence repetition, the mean orientation is either {0, 45, 90, 135} degrees.
- At each sequence repetition, individual Gabor orientations are randomly drawn from circular Gaussian with mean set to the sequence mean, and standard deviation of 0.25 rad.

Bricks Stimulus Description
---------------------------
- Bricks are 64 deg squared (i.e., 8 on a side).
- Contrast is 100%.
- They flow L or R at 50 deg/s; this varies between blocks.
- There are 105 bricks generated at a time, chosen to be 0.75*screen_area/brick_area.

Day 6
-----
10 minutes of habituation stimulus, broken up as follows, depending on
whether gabors or bricks are randomly selected to occur first:
- Seconds 0-30: Grayscreen (30 sec)
- Seconds 30-270: Gabor Stimulus Block (240 sec)
- Seconds 270-300: Grayscreen (30 sec)
- Seconds 300-420: Brick Stimulus Block 1 (120 sec)
- Seconds 420-450: Grayscreen (30 sec)
- Seconds 450-570: Brick Stimulus Block 2 (120 sec)
- Seconds 570-600: Grayscreen (30 sec)

OR

- Seconds 0-30: Grayscreen (30 sec)
- Seconds 30-150: Brick Stimulus Block 1 (120 sec)
- Seconds 150-180: Grayscreen (30 sec)
- Seconds 180-300: Brick Stimulus Block 2 (120 sec)
- Seconds 300-330: Grayscreen (30 sec)
- Seconds 330-570: Gabor Stimulus Block (240 sec)
- Seconds 570-600: Grayscreen (30 sec)

Day 7
-----
20 minutes of habituation stimulus, broken up as follows, depending on
whether gabors or bricks are randomly selected to occur first:
- Seconds 0-30: Grayscreen (30 sec)
- Seconds 30-570: Gabor Stimulus Block (540 sec)
- Seconds 570-600: Grayscreen (30 sec)
- Seconds 600-870: Brick Stimulus Block 1 (270 sec)
- Seconds 870-900: Grayscreen (30 sec)
- Seconds 900-1170: Brick Stimulus Block 2 (270 sec)
- Seconds 1170-1200: Grayscreen (30 sec)

OR

- Seconds 0-30: Grayscreen (30 sec)
- Seconds 30-300: Brick Stimulus Block 1 (270 sec)
- Seconds 300-330: Grayscreen (30 sec)
- Seconds 330-600: Brick Stimulus Block  (270 sec)
- Seconds 600-630: Grayscreen (30 sec)
- Seconds 630-1170: Gabor Stimulus Block (540 sec)
- Seconds 1170-1200: Grayscreen (30 sec)

Day 8
-----
30 minutes of habituation stimulus, broken up as follows, depending on
whether gabors or bricks are randomly selected to occur first:
- Seconds 0-30: Grayscreen (30 sec)
- Seconds 30-870: Gabor Stimulus Block (840 sec)
- Seconds 870-900: Grayscreen (30 sec)
- Seconds 900-1320: Brick Stimulus Block 1 (420 sec)
- Seconds 1320-1350: Grayscreen (30 sec)
- Seconds 1350-1770: Brick Stimulus Block 2 (420 sec)
- Seconds 1770-1800: Grayscreen (30 sec)

OR

- Seconds 0-30: Grayscreen (30 sec)
- Seconds 30-450: Brick Stimulus Block 1 (420 sec)
- Seconds 450-480: Grayscreen (30 sec)
- Seconds 480-900: Brick Stimulus Block 2 (420 sec)
- Seconds 900-930: Grayscreen (30 sec)
- Seconds 930-1770: Gabor Stimulus Block (840 sec)
- Seconds 1770-1800: Grayscreen (30 sec)

Day 9
-----
40 minutes of habituation stimulus, broken up as follows, depending on
whether gabors or bricks are randomly selected to occur first:
- Seconds 0-30: Grayscreen (30 sec)
- Seconds 30-1170: Gabor Stimulus Block (1140 sec)
- Seconds 1170-1200: Grayscreen (30 sec)
- Seconds 1200-1770: Brick Stimulus Block 1 (570 sec)
- Seconds 1770-1800: Grayscreen (30 sec)
- Seconds 1800-2370: Brick Stimulus Block 2 (570 sec)
- Seconds 2370-2400: Grayscreen (30 sec)

OR

- Seconds 0-30: Grayscreen (30 sec)
- Seconds 30-600: Brick Stimulus Block 1 (570 sec)
- Seconds 600-630: Grayscreen (30 sec)
- Seconds 630-1200: Brick Stimulus Block 2 (570 sec)
- Seconds 1200-1230: Grayscreen (30 sec)
- Seconds 1230-2370: Gabor Stimulus Block (1140 sec)
- Seconds 2370-2400: Grayscreen (30 sec)

Day 10
------
50 minutes of habituation stimulus, broken up as follows, depending on
whether gabors or bricks are randomly selected to occur first:
- Seconds 0-30: Grayscreen (30 sec)
- Seconds 30-1470: Gabor Stimulus Block (1440 sec)
- Seconds 1470-1500: Grayscreen (30 sec)
- Seconds 1500-2220: Brick Stimulus Block 1 (720 sec)
- Seconds 2220-2250: Grayscreen (30 sec)
- Seconds 2250-2970: Brick Stimulus Block 2 (720 sec)
- Seconds 2970-3000: Grayscreen (30 sec)

OR

- Seconds 0-30: Grayscreen (30 sec)
- Seconds 30-750: Brick Stimulus Block 1 (720 sec)
- Seconds 750-780: Grayscreen (30 sec)
- Seconds 780-1500: Brick Stimulus Block 2 (720 sec)
- Seconds 1500-1530: Grayscreen (30 sec)
- Seconds 1530-2970: Gabor Stimulus Block (1440 sec)
- Seconds 2970-3000: Grayscreen (30 sec)