# -*- coding: cp1252 -*-
"""
This is example code to generate and run the discussed gabor, and brick stimuli. 

### Current problems:
- The new class OurStims works well, but is likely fragile (due to redundancies, boundary
conditions, reasonable conditions that haven't been implemented).
    e.g., only deg units have been implemented
- The screen values from psychopy come out wrong and the degrees come out wrong and have to
be multiplied by about 2... Check in ElementArrayStim draw() whether deg are in fact supported
for drawing.
- OurStims updates conditions by relying on counting frames. Probably not ideal given
the possibly cumulative effect of dropped frames? I think SweepStim may do the same?
- OurStims doesn't generate triggers when a variable is changed, which is important for syncing
(1) linking behavior/recordings to stimuli, and (2) sending triggers. SweepStim likely does this. 
- Haven't thoroughly documented OurStims so parts may be a bit obscure.

### Next steps:
- Rejig code as needed to produce desired stimuli.
- Consult AIBS people to find out whether some parameters (e.g., deg units)
are preferred or necessary.
- See if they can test run the code.
"""

from psychopy import monitors, event, visual

# camstim is the Allen Institute stimulus package built on psychopy
from camstim import Stimulus, SweepStim, MovieStim
from camstim import Foraging
from camstim import Window, Warp

import numpy as np
import random

from ourstimuli import OurStims

# create a monitor
dist_cm = 15.0
wid_cm = 52.0
monitor = monitors.Monitor("testMonitor", distance=dist_cm, width=wid_cm)

# Create display window
window = Window(fullscr=True, # Will return an error due to default size. Ignore.
                monitor=monitor,  # Will be set to a gamma calibrated profile by MPE
                screen=0,
                warp=Warp.Spherical,
                )

# Get pixel dimensions of monitor. Note, returns wrong values [1024, 768].
# Then warning is thrown that screen is actually [1536, 864]. Also wrong.
dim = monitor.getSizePix()

# Calculate screen size in degrees (flat screen)

wid_deg = np.rad2deg(np.arctan((wid_cm*0.5)/dist_cm))* 2 # about 143
deg_per_pix = wid_deg/dim[0] # about 0.14
hei_deg = deg_per_pix * dim[1] # about 107

fps_v = 60 # frames per sec (60 is the default for a camstim Stimulus)

fixParGab={ # parameters set by ElementArrayStim
        'units': 'deg', # only degrees implemented so far
        # no idea why I need to double fieldSize. Still falls short for width without warp, probably due to wrong monitor size
        'fieldSize': [wid_deg*2, hei_deg*2], # redundant - overwritten by explicit xy positions called by OurStims
        'nElements': 40, # number of stimuli on screen
        'sizes': (30, 30), # for gaussian mask, cov derived from these values
        'sfs': 0.06, # spatial frequencies (sin) (cycles per deg)
        'phases': 0.25, # (sin) (0 to 1)
        'elementTex': 'sin',
        'elementMask': 'gauss',
        'name': 'gabors',
        }

fixParSqu={
        'units': 'deg',
         'fieldSize': [wid_deg*2, hei_deg*2],
        'nElements': 200,
        'sizes': (10, 3),
        'elementTex': None,
        'elementMask': 'sqr',
        'name': 'bricks',
        }

specParGab={ # parameters set by OurStims
         'newpos':[2, 4, 6], # when to initialize new positions, in seconds
         'newori':[0, 2, 4, 6], # when to initialize new orientations
         'oriparamlist':[[90.0, 10.0], [90.0, 10.0], [90.0, 10.0], [180.0, 10.0]], # orientation init parameters [mu, std]
         'duration':-1, # duration in frames (-1 for no end)
         'initScr':True, # initialize elements on the screen
        }

specParSqu={
         'direc':0.0, # 0 is straight right (goes counter-clockwise) 
         'speed':3, # units sort of arbitrary right now
         'flipspeed':[[3, 5]], # when to flip direction
         'flipfrac':0.2, # fraction of elements that should be flipped (0 to 1)
         'duration':-1, # duration in frames (-1 for no end)
         'initScr':True, # initialize elements on the screen
        }

# Create the stimulus array
gabors = visual.ElementArrayStim(window, **fixParGab)
squares = visual.ElementArrayStim(window, **fixParSqu)

ourstimgab = OurStims(window, gabors, **specParGab)
ourstimsqu = OurStims(window, squares, **specParSqu)

gb = Stimulus(ourstimgab,
              sweep_params={
                      'Contrast': ([1.0], 0), # sweep_params is required, so this is a dummy sweep param.
                           },
              sweep_length=8.0,
              start_time=0.0,
              runs=1,
              shuffle=True,
              fps=fps_v, # default is 60
              save_sweep_table=True,
              )

sq = Stimulus(ourstimsqu,
              sweep_params={
                      'Contrast': ([1.0], 0), # same as above
                           },
              sweep_length=10.0,
              start_time=0.0,
              runs=1,
              fps=fps_v,
              save_sweep_table=False,
              )

gb_ds = [(0, 8.0)] # ranges to run in sec
sq_ds = [(8.0, 15.0)]

gb.set_display_sequence(gb_ds)
sq.set_display_sequence(sq_ds)

ss = SweepStim(window,
               stimuli=[gb, sq],
               pre_blank_sec=1,
               post_blank_sec=1,
               params={},  # will be set by MPE to work on the rig
               )

# run it
ss.run()

## DRAWING WITHOUT STIMSWEEP
#message = visual.TextStim(window, text='Any key to quit', pos=(0, -5))
#
## always draw
#wholestim.autoDraw = True
#message.autoDraw = True
#
#while not event.getKeys():
#    window.flip()  # redraw the buffer, autodraw does the rest
#
#window.close()