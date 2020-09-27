OpenScope Credit Assignment 2P Pilot Imaging Experiment Stimuli
====================================================

- There is one script for subject 2 and one for subject 4. Those contain 67.5 minutes of stimulus.
- Subject 1 and 3 each have scripts with 32.5 minutes of stimulus. (To be repeated twice each recording day) 
- Each animal should get the same stimulus script(s) on each of their 2 days of recording.
- The scripts all call  stim_params_2p parameter file. The same one applies for all animals.
 - The Gabor stimulus blocks are each ~900 seconds long, whereas the Bricks stimulus blocks are each ~450 seconds long. These alternate as: G,B,B,G,B,B for subjects 1 and 4 or B,B,G,B,B,G for subjects 2 and 3 (total time is roughly evenly between the stimuli).
- The Gabor stimulus blocks go through two different standard deviations for the orientations (e.g., one standard deviation value per Gabor block).
- The Bricks stimulus blocks go through the 4 different possibilities from {2 brick sizes}x{2 brick directions}. 
- (Within the pilot experiments, we will present these same sets of stimulus parameters, to try and pick out the ones that drive the strongest effects.)
- During the actual ophys recordings, "mismatches" or "surprises" are introduced in the blocks: short changes in orientations and positions of the Gabors and short changes in direction of some of the Bricks.
- The Gabor locations and sizes are the same across days for each subject: the RNG seed for subjects 1 and 4 is 100, for subjects 2 and 3, it is 103.
- Within each stimulus type, there is first the "default" stimulus for 30-90 seconds, then a mismatch that lasts 2-4 seconds for the Bricks, and 3-6 seconds for the Gabors. This process then repeats until the block duration is over. Actual durations in each instance are uniformly and randomly drawn within their ranges.

Gabor Stimulus Description
--------------------------
- 30 Gabors with random locations in each of the frames (A,B,C,D).
- Each Gabor has size sampled uniformly from 10-20 vis deg (FWHM); width and height are the same.
- Contrast is 100%
- Spatial frequency is 0.04 cycles/deg and phase is 0.25.
- The same set of Gabor locations and sizes is maintained for each animal across all days.
- Gabors come in 4 frames (A,B,C,D), each of which has a different mean Gabor orientation, and a different set of positions for the Gabors
- Subjects 1 and 4 Gabor locations and sizes are randomly set with the seed 100. For subjects 2 and 3, it is seed 103.
- Sequence is ABCD_ABCD_ABCD_..., where “_” is the blank grayscreen frame.
- Each frame lasts 0.3 seconds, and the sequence lasts 1.5 seconds.
- At each sequence repetition, the mean orientation is either {0, 45, 90, 135} degrees.
- Individual Gabor orientations are randomly drawn from circular Gaussian with mean set to the sequence mean, and standard deviation of 0.25 or 0.5 rad, depending on the block.
- Mismatches are introduced by having replacing D with E in the sequence (ABCE_ABCE_...), for 3-6 sec, every 30-90 sec.
- E frames are characterized by their own set of positions and sizes for the Gabors, and by the fact that the Gabor orientations are shifted by 90 degrees with respect to the rest of the sequence (A,B,C).

Bricks Stimulus Description
---------------------------
- Bricks are 64 or 256 deg squared (i.e., 8 or 16 deg on a side); this varies between blocks.
- Contrast is 100%.
- They flow L or R at 50 deg/s; this varies between blocks.
- There are 105 or 26 bricks generated at a time, depending on the block's Brick size, chosen to be 0.75*screen_area/brick_area.
- Mismatches are introduced by having 25% of the Bricks reverse direction for 2-4 sec, every 30-90 sec.

Subject 1
-----
32.5 minutes of stimulus, broken up as follows:
- Seconds 0-900: Gabor Stimulus Block 1
- Seconds 900-1050 : Blank Screen
- Seconds 1050-1500: Bricks Stimulus Block 1
- Second 1500-1501: Blank Screen
- Seconds 1501-1951: Bricks Stimulus Block 2

Subject 2
-----
67.5 minutes of stimulus, broken up as follows:
- Seconds 0-450: Bricks Stimulus Block 1
- Seconds 450-451 : Blank Screen
- Seconds 451-901: Bricks Stimulus Block 2
- Second 901-1050: Blank Screen
- Seconds 1050-1950: Gabor Stimulus Block 1
- Second 1950-2100: Blank Screen
- Seconds 2100-2550: Bricks Stimulus Block 3
- Seconds 2550-2551 : Blank Screen
- Seconds 2551-3001: Bricks Stimulus Block 4
- Second 3001-3150: Blank Screen
- Seconds 3150-4050: Gabor Stimulus Block 2

Subject 3
-----
32.5 minutes of stimulus (to be repeated twice), broken up as follows:
- Seconds 0-450: Bricks Stimulus Block 1
- Seconds 450-451 : Blank Screen
- Seconds 451-901: Bricks Stimulus Block 2
- Second 901-1050: Blank Screen
- Seconds 1050-1950: Gabor Stimulus Block 1

Subject 4
-----
67.5 minutes of stimulus, broken up as follows:
- Seconds 0-900: Gabor Stimulus Block 1
- Seconds 900-1050 : Blank Screen
- Seconds 1050-1500: Bricks Stimulus Block 1
- Second 1500-1501: Blank Screen
- Seconds 1501-1951: Bricks Stimulus Block 2
- Second 1951-2100: Blank Screen
- Seconds 2100-3000: Gabor Stimulus Block 2
- Seconds 3000-3150 : Blank Screen
- Seconds 3150-3600: Bricks Stimulus Block 3
- Second 3600-3601: Blank Screen
- Seconds 3601-4051: Bricks Stimulus Block 4


