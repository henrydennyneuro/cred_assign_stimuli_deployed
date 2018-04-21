#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Demo of gabors moving, using autodraw.

TO DO:
    Fix the arbitrary units... figure out what's what! :)
    Setup with SweepStim
"""

from __future__ import division

from psychopy import visual, core, event

from stim_mov_impr import MovStim

# Create a window to draw in
win = visual.Window(fullscr=True, allowGUI=False, # fullscreen does not appear to override the default 800 by 600 setting
                      monitor='testMonitor', units='deg')

# Initialize

n_stim = 30 # number of stimuli
fixPar={ # parameters that stay fixed during presentation
        'units': 'deg',
        'size': (3, 3), # in units, gaussian cov derived from these values
        'sf': 0.5, # spatial frequency (sin) (cycles per deg)
        'phase': 1, # (sin) (0 to 1)
        'ori': 45 # orientation of mask and texture
        }
# sweep parameters do not work well with clock below
sweepPar={ # parameters that change during presentation
        'Contrast': ([0.8], 0), # contrast is here as sweepPar must be passed later 
        'Ori': ([0, 90], 1), # orientation of mask and texture
         }
maskPar={ # parameters of the mask
        'sd': 3, # only supports one value
        }
gabor_shape = visual.GratingStim(win,
                                 tex='sin',
                                 mask='gauss',
                                 maskParams=maskPar,
#                                autoDraw=True, # use instead of gabors.draw()
                                 **fixPar
                                 )


dotPatch = MovStim(win, color='black',
    nDots=50,
    speed=0.001,
    stim=gabor_shape, name='gaborPatch')
message = visual.TextStim(win, text='Any key to quit', pos=(0, -5))

# always draw
dotPatch.autoDraw = True
message.autoDraw = True

while not event.getKeys():
    win.flip()  # redraw the buffer, autodraw does the rest

win.close()
core.quit()

# The contents of this file are in the public domain.