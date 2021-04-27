OpenScope Credit Assignment Passive Training Stimuli
====================================================

- There is one habituation script for the ophys rig (day11) and one script for actual recordings on the ophys rig (ophys_record), and each is fully contained (i.e., it does not depend on any other scripts we've written).
- There are 30 s grayscreen periods at the start and the end of the session.
- The session comprises a Gabor stimulus block, only.
- During the actual ophys recordings, "mismatches" or "surprises" are introduced in the blocks: short changes in orientations and positions of the Gabors.
- These mismatches do not occur during the habituation session.
- The day numbers are described in accordance with the table circulated by Carol. So the amount of time for each script is: (day11, 60mins); (ophys_record, 70 mins)
- Day 11 is defined as the first habituation day on the OPhys rig.
- ophys_record.py is for all actual ophys recordings.

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
- At each sequence repetition, the mean orientation is either {0, 45, 90, 135, 180, 225, 270, 315} degrees.
- At each sequence repetition, individual Gabor orientations are randomly drawn from circular Gaussian with mean set to the sequence mean, and standard deviation of 0.25 rad.
- Mismatches are introduced for 3-6 sec, every 30-90 sec.
- For half of mismatches, D frames are replaced with U frames in the sequence (ABCU_ABCU_...). For the other half, D frames are retained.
- U frames are characterized by their own set of positions and sizes for the Gabors.
- All mismatches, whether U or D frames, are characterized by the fact that the Gabor orientations are shifted by 90 degrees with respect to the rest of the sequence (A,B,C).

Day 11
------
60 minutes of habituation stimulus, broken up as follows:
- Seconds 0-30: Grayscreen (30 sec)
- Seconds 30-3570: Gabor Stimulus Block (3540 sec)
- Seconds 3570-3600: Grayscreen (30 sec)


OPHYS_RECORD
------
70 minutes of ophys recording stimulus, broken up as follows:
- Seconds 0-30: Grayscreen (30 sec)
- Seconds 30-4170: Gabor Stimulus Block (4140 sec)
- Seconds 4170-4200: Grayscreen (30 sec)
