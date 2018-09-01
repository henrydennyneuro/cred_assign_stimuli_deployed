OpenScope Credit Assignment Passive Training Stimuli
====================================================

- There is one habituation script for the ophys rig (day11) and one script for actual recordings on the ophys rig (ophys_record), and each is fully contained (i.e., it does not depend on any other scripts we've written).
- There are 30 s grayscreen periods at the start and the end of the session, as well as between the 3 stimulus blocks (1 Gabor stimulus block and 2 Brick stimulus blocks).
- The Gabor stimulus block is about 1/2 of the session time, whereas the 2 Brick stimulus blocks are each about 1/4 of the session time. The order in which they occur is random for each session and each mouse, other than the fact that the 2 Brick blocks will always follow one another.
- The 2 Brick stimulus blocks differ as follows: in one block, the Bricks move left (except for mismatches, described below), and in the other block, the Bricks move right. 
- During the actual ophys recordings, 'mismatches' or 'surprises' are introduced in the blocks: short changes in orientations and positions of the Gabors and short changes in direction of some of the Bricks.
- These mismatches do not occur during the habituation session.
- The day numbers are described in accordance with the table circulated by Carol. So the amount of time for each script is: (day11, 60mins); (ophys_record, 70 mins)
- Day 11 is defined as the first habituation day on the OPhys rig.
- ophys_record is for all actual ophys recordings.

Gabor Stimulus Description
--------------------------
- 30 Gabors with random locations in each of the frames (A,B,C,D)
- Each Gabor has size sampled uniformly from 10-20 vis deg (FWHM); width and height are same
- The same set of Gabor locations and sizes is maintained for an entire session, but changes between sessions and animals.
- Contrast is 100%
- Spatial frequency is 0.04 cycles/deg
- Gabors come in 4 frames (A,B,C,D), each of which has a different mean Gabor orientation, and a different set of positions for the Gabors
- Individual Gabor orientations are randomly drawn from circular Gaussian with mean set to the frame mean, and standard deviation of 0.25 rad.
- Phases are 0.25 for all Gabors
- Each frame lasts 0.3 seconds, followed by a blank gray screen.	
- Sequence is ABCD_ABCD_ABCD_. . ., where “_” is the blank frame

Bricks Stimulus Description
---------------------------
- Bricks are 8 deg squares (i.e., 8 on a side)
- Contrast is 100%
- They flow L or R at 50 deg/s; this varies between blocks
- There are 113 bricks generated at a time (depends on the size), chosen to be 0.75*screen_area/brick_area.

Day 11
------
60 minutes of habituation stimulus, broken up as follows, depending on
whether gabors or bricks are randomly selected to occur first:
- Seconds 0-30: Grayscreen (30 sec)
- Seconds 30-1770: Gabor Stimulus Block (1740 sec)
- Seconds 1770-1800: Grayscreen (30 sec)
- Seconds 1800-2670: Brick Stimulus Block 1 (870 sec)
- Seconds 2670-2700: Grayscreen (30 sec)
- Seconds 2700-3570: Brick Stimulus Block 2 (870 sec)
- Seconds 3570-3600: Grayscreen (30 sec)

OR

- Seconds 0-30: Grayscreen (30 sec)
- Seconds 30-900: Brick Stimulus Block 1 (870 sec)
- Seconds 900-930: Grayscreen (30 sec)
- Seconds 930-1800: Brick Stimulus Block 2 (870 sec)
- Seconds 1800-1830: Grayscreen (30 sec)
- Seconds 1830-3570: Gabor Stimulus Block (1740 sec)
- Seconds 3570-3600: Grayscreen (30 sec)

OPHYS_RECORD
------
70 minutes of ophys recording stimulus, broken up as follows, depending on
whether gabors or bricks are randomly selected to occur first:
- Seconds 0-30: Grayscreen (30 sec)
- Seconds 30-2070: Gabor Stimulus Block (2040 sec)
- Seconds 2070-2100: Grayscreen (30 sec)
- Seconds 2100-3120: Brick Stimulus Block 1 (1020 sec)
- Seconds 3120-3150: Grayscreen (30 sec)
- Seconds 3150-4170: Brick Stimulus Block 2 (1020 sec)
- Seconds 4170-4200: Grayscreen (30 sec)

OR

- Seconds 0-30: Grayscreen (30 sec)
- Seconds 30-1050: Brick Stimulus Block 1 (1020 sec)
- Seconds 1050-1080: Grayscreen (30 sec)
- Seconds 1080-2100: Brick Stimulus Block 2 (1020 sec)
- Seconds 2100-2130: Grayscreen (30 sec)
- Seconds 2130-4170: Gabor Stimulus Block (2040 sec)
- Seconds 4170-4200: Grayscreen (30 sec)
