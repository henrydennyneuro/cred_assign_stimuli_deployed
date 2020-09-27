OpenScope Credit Assignment Passive Training Stimuli
====================================================

- There is one habituation script per day.
- These scripts call their day-specific parameter files. The differences between days in these files come down to the block lengths, as defined within these parameter files. 
- The Gabor stimulus blocks are each ~1/4 of the habituation time, whereas the Bricks stimulus blocks are each ~1/8 of the habituation time. These alternate as: G,B,B,G,B,B or B,B,G,B,B,G, depending on the day. (Total time is split roughly evenly between the stimuli).
- The Gabor stimulus blocks go through two different standard deviations for the orientations (e.g., one standard deviation value per Gabor block).
- The Bricks stimulus blocks go through the 4 different possibilities from {2 brick sizes}x{2 brick directions}. 
- (Within the pilot experiments, we will present these same sets of stimulus parameters, to try and pick out the ones that drive the strongest effects.)
- None of the habituation stimuli contain any of the “mismatch” or “surprise” stimulus components, as described in the pilot experiment plan.
- The Gabor locations and sizes are the same on each day for all subjects: the RNG seed for determining the locations and sizes is set to be the habituation day number, i.e. 6-11.
- The day numbers are described in accordance with the table circulated by Carol. So the amount of time for each script is:
(day6, 10mins); (day7, 20mins); (day8, 30mins); (day9, 40mins); (day10, 50mins); (day11; 60mins).
- Day 11 is defined as the first habituation day on the OPhys rig.

Gabor Stimulus Description
--------------------------
- 30 Gabors with random locations in each of the frames (A,B,C,D).
- Each Gabor has size sampled uniformly from 10-20 vis deg (FWHM); width and height are the same.
- Contrast is 100%
- Spatial frequency is 0.04 cycles/deg and phase is 0.25.
- The same set of Gabor locations and sizes is maintained for each animal across all days.
- Gabors come in 4 frames (A,B,C,D), each of which has a different mean Gabor orientation, and a different set of positions for the Gabors
- Gabor locations and sizes are randomly set with a seed corresponding to the habituation day, i.e. 6-11.
- Sequence is ABCD_ABCD_ABCD_..., where “_” is the blank grayscreen frame.
- Each frame lasts 0.3 seconds, and the sequence lasts 1.5 seconds.
- At each sequence repetition, the mean orientation is either {0, 45, 90, 135} degrees.
- Individual Gabor orientations are randomly drawn from circular Gaussian with mean set to the sequence mean, and standard deviation of 0.25 or 0.5 rad, depending on the block.

Bricks Stimulus Description
---------------------------
- Bricks are 64 or 256 deg squared (i.e., 8 or 16 deg on a side); this varies between blocks.
- Contrast is 100%.
- They flow L or R at 50 deg/s; this varies between blocks.
- There are 105 or 26 bricks generated at a time, depending on the block's Brick size, chosen to be 0.75*screen_area/brick_area.

Day 6
-----
10 minutes of habituation stimulus, broken up as follows:
- Seconds 0-150: Gabor Stimulus Block 1
- Seconds 150-151 : Blank Screen
- Seconds 151-225: Bricks Stimulus Block 1
- Second 225-226: Blank Screen
- Seconds 226-300: Bricks Stimulus Block 2
- Second 300-301: Blank Screen
- Seconds 301-451: Gabor Stimulus Block 2
- Seconds 451-452 : Blank Screen
- Seconds 452-526: Bricks Stimulus Block 3
- Second 526-527: Blank Screen
- Seconds 527-601: Bricks Stimulus Block 4

Day 7
-----
20 minutes of habituation stimulus, broken up as follows:
- Seconds 0-149: Bricks Stimulus Block 1
- Seconds 149-150: Blank Screen
- Seconds 150-299: Bricks Stimulus Block 2
- Second 299-300: Blank Screen
- Seconds 300-600: Gabor Stimulus Block 1
- Second 600-601: Blank Screen
- Seconds 601-750: Bricks Stimulus Block 3
- Seconds 750-751 : Blank Screen
- Seconds 751-900: Bricks Stimulus Block 4
- Second 900-901: Blank Screen
- Seconds 901-1201: Gabor Stimulus Block 2

Day 8
-----
30 minutes of habituation stimulus, broken up as follows:
- Seconds 0-450: Gabor Stimulus Block 1
- Seconds 450-451 : Blank Screen
- Seconds 451-775: Bricks Stimulus Block 1
- Second 775-776: Blank Screen
- Seconds 776-900: Bricks Stimulus Block 2
- Second 900-901: Blank Screen
- Seconds 901-1351: Gabor Stimulus Block 2
- Seconds 1351-1352 : Blank Screen
- Seconds 1352-1576: Bricks Stimulus Block 3
- Second 1576-1577: Blank Screen
- Seconds 1577-1801: Bricks Stimulus Block 4

Day 9
-----
40 minutes of habituation stimulus, broken up as follows:
- Seconds 0-299: Bricks Stimulus Block 1
- Seconds 299-300: Blank Screen
- Seconds 300-599: Bricks Stimulus Block 2
- Second 599-600: Blank Screen
- Seconds 600-1200: Gabor Stimulus Block 1
- Second 1200-1201: Blank Screen
- Seconds 1201-1500: Bricks Stimulus Block 3
- Seconds 1500-1501 : Blank Screen
- Seconds 1501-1800: Bricks Stimulus Block 4
- Second 1800-1801: Blank Screen
- Seconds 1801-2401: Gabor Stimulus Block 2

Day 10
------
50 minutes of habituation stimulus, broken up as follows:
- Seconds 0-750: Gabor Stimulus Block 1
- Seconds 750-751 : Blank Screen
- Seconds 751-1125: Bricks Stimulus Block 1
- Second 1125-1126: Blank Screen
- Seconds 1126-1500: Bricks Stimulus Block 2
- Second 1500-1501: Blank Screen
- Seconds 1501-2251: Gabor Stimulus Block 2
- Seconds 2251-2252 : Blank Screen
- Seconds 2252- 2626: Bricks Stimulus Block 3
- Second 2626-2627: Blank Screen
- Seconds 2627- 3001: Bricks Stimulus Block 4

Day 11
------
60 minutes of habituation stimulus, broken up as follows:
- Seconds 0-449: Bricks Stimulus Block 1
- Seconds 449-450: Blank Screen
- Seconds 450-899: Bricks Stimulus Block 2
- Second 899-900: Blank Screen
- Seconds 900-1800: Gabor Stimulus Block 1
- Second 1800-1801: Blank Screen
- Seconds 1801-2250: Bricks Stimulus Block 3
- Seconds 2250-2251 : Blank Screen
- Seconds 2251-2700: Bricks Stimulus Block 4
- Second 2700-2701: Blank Screen
- Seconds 2701-3601: Gabor Stimulus Block 2
