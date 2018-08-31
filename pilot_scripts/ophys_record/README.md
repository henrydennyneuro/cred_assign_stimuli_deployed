OpenScope Credit Assignment 2P Pilot Imaging Experiment Stimuli
====================================================

- There is one script for mouse II and one for mouse IV. Those contain 67.5 minutes of stimulus.
- Mice I and III each have scripts with 32.5 minutes of stimulus. (To be repeated twice each recording day) 
- Each animal should get the same stimulus script(s) on each of their 2 days of recording.
- The scripts all call  stim_params_2p parameter file. The same one applies for all animals.
 - The Gabor stimulus blocks are each ~900 seconds long, whereas the Bricks stimulus blocks are each ~450 seconds long. These alternate as: G,B,B,G,B,B for mice I and IV or B,B,G,B,B,G for mice II and III (total time is roughly evenly between the stimuli).
- The Gabor stimulus blocks go through two different standard deviations for the orientations (e.g., one standard deviation value per Gabor block).
- The Bricks stimulus blocks go through the 4 different possibilities from {2 brick sizes}x{2 brick directions}. 
- (Within the pilot experiments, we will present these same sets of stimulus parameters, to try and pick out the ones that drive the strongest effects.)
- The seeds for Gabor locations are set to match those from the habituation days.
- Within each stimulus type, there is first the "default" stimulus for 30-90 seconds, then a mismatch that lasts 2-4 seconds for the Bricks, and 3-6 seconds for the Gabors. This process then repeats until the block duration is over. Actual durations in each instance are uniformly and randomly drawn within their ranges.

Gabor Stimulus Description
--------------------------
- 30 Gabors with random locations in each of the frames (A,B,C,D)
- Each Gabor has size sampled uniformly from 10-20 vis deg (FWHM); width and height are same
- The same set of Gabor locations and sizes is maintained for all animals and days (RNG seed is set to 1)
- Contrast is 100%
- Spatial frequency is 0.04 cycles/deg
- Gabors come in 4 frames (A,B,C,D), each of which has a different mean Gabor orientation, and a different set of positions for the Gabors
- Individual Gabor orientations are randomly drawn from circular Gaussian with mean set to the frame mean, and standard deviation of 0.25 or 0.5 rad, depending on the Block
- Phases are 0.25 for all Gabors
- Each frame lasts 0.3 seconds, followed by a blank grey screen.	
- Sequence is ABCD_ABCD_ABCD_. . ., where “_” is the blank frame

Bricks Stimulus Description
---------------------------
- Bricks are 8 or 16 deg squares (e.g., 8 or 16 deg on a side); this varies between blocks
- Contrast is 100%
- They flow L or R at 50 deg/s; this varies between blocks
- There are 28 or 113 bricks generated at a time (depends on the size), chosen to be 0.75*screen_area/brick_area.

Mouse I
-----
32.5 minutes of stimulus, broken up as follows:
- Seconds 0-900: Gabor Stimulus Block 1
- Seconds 900-1050 : Blank Screen
- Seconds 1050-1500: Bricks Stimulus Block 1
- Second 1500-1501: Blank Screen
- Seconds 1501-1951: Bricks Stimulus Block 2

Mouse II
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

Mouse III
-----
32.5 minutes of stimulus (to be repeated twice), broken up as follows:
- Seconds 0-450: Bricks Stimulus Block 1
- Seconds 450-451 : Blank Screen
- Seconds 451-901: Bricks Stimulus Block 2
- Second 901-1050: Blank Screen
- Seconds 1050-1950: Gabor Stimulus Block 1

Mouse IV
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


