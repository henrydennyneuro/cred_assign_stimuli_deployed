"""
This is code to generate and run a 35-minute stimulus for 2P recordings
for mouse I
order is: gabors, bricks

Mismatches are included. These are every 30-90 seconds, and last 2-4 seconds
for the bricks, and 3-6 seconds for the Gabors

Everything is randomized for each animal, except for: ordering of stim types (gabors vs bricks), and positions and sizes of Gabors
Gabor positions and sizes are permanently hard-coded (same for all animals, forever)
Stim type ordering is the same for all animals on a given day, but can vary between days
"""

# FOR TESTING
SESSION_PARAMS = {'type': 'ophys', # type of session (habituation or ophys)
                  'session_dur': 85, # total session duration (sec)
                  'pre_blank': 5, # blank before stim starts (sec)
                  'post_blank': 5, # blank after all stims end (sec)
                  'inter_blank': 5, # blank between all stims (sec)
                  'gab_dur': 33, # duration of gabor block (sec)
                  'sq_dur': 32, # duration of each brick block (total=2) (sec)
                  }

# SESSION_PARAMS = {'type': 'ophys', # type of session (habituation or ophys)
#                   'session_dur': 70*60, # total session duration (sec)
#                   'pre_blank': 30, # blank before stim starts (sec)
#                   'post_blank': 30, # blank after all stims end (sec)
#                   'inter_blank': 30, # blank between all stims (sec)
#                   'gab_dur': 34*60, # duration of gabor block (sec)
#                   'sq_dur': 17*60, # duration of each brick block (total=2) (sec)
#                  }

import random
import sys

import numpy as np

from psychopy import monitors

# camstim is the Allen Institute stimulus package built on psychopy
from camstim import SweepStim
from camstim import Window, Warp

import stim_params as stim_params

    
if __name__ == "__main__":
    
    dist = 15.0
    wid = 52.0
    
    # Record orientations of gabors at each sweep (LEAVE AS TRUE)
    recordOris = True

    # Record positions of squares at all times (LEAVE AS TRUE)
    recordPos = True
            
    # create a monitor
    monitor = monitors.Monitor("testMonitor", distance=dist, width=wid)
    
    # randomly set a seed for the session and create a dictionary
    seed = random.choice(range(0, 48000))
    #seed = # override by manually setting seed
    rng = np.random.RandomState(seed)

    seed_info = {'seed': seed,
                 'rng': rng}
    
    # Create display window
    window = Window(fullscr=True, # Will return an error due to default size. Ignore.
                    monitor=monitor,  # Will be set to a gamma calibrated profile by MPE
                    screen=0,
                    warp=Warp.Spherical
                    )

    # check session params add up to correct total time
    tot_calc = SESSION_PARAMS['pre_blank'] + SESSION_PARAMS['post_blank'] + \
               2*SESSION_PARAMS['inter_blank'] + SESSION_PARAMS['gab_dur'] + \
               2*SESSION_PARAMS['sq_dur']
    if tot_calc != SESSION_PARAMS['session_dur']:
        print('Session should last {} s, but adds up to {} s.'
              .format(SESSION_PARAMS['session_dur'], tot_calc))

    # initialize the stimuli
    gb = stim_params.init_run_gabors(window, seed_info, SESSION_PARAMS, recordOris)
    sq_left = stim_params.init_run_squares(window, seed_info, 'left', SESSION_PARAMS, recordPos)
    sq_right = stim_params.init_run_squares(window, seed_info, 'right', SESSION_PARAMS, recordPos)

    # initialize display order and times
    stim_order = ['g', 'b']
    seed_info['rng'].shuffle(stim_order) # in place shuffling
    sq_order = ['l', 'r']
    seed_info['rng'].shuffle(sq_order) # in place shuffling

    start = SESSION_PARAMS['pre_blank'] # initial blank
    stimuli = []
    for i in stim_order:
        if i == 'g':
            stimuli.append(gb)
            gb.set_display_sequence([(start, start+SESSION_PARAMS['gab_dur'])])
            # update the new starting point for the next stim
            start += SESSION_PARAMS['gab_dur'] + SESSION_PARAMS['inter_blank'] 
        elif i == 'b':
            for j in sq_order:
                if j == 'l':
                    stimuli.append(sq_left)
                    sq_left.set_display_sequence([(start, start+SESSION_PARAMS['sq_dur'])])
                elif j == 'r':
                    stimuli.append(sq_right)
                    sq_right.set_display_sequence([(start, start+SESSION_PARAMS['sq_dur'])])
                # update the new starting point for the next stim
                start += SESSION_PARAMS['sq_dur'] + SESSION_PARAMS['inter_blank'] 
        
    ss = SweepStim(window,
                   stimuli=stimuli,
                   post_blank_sec=SESSION_PARAMS['post_blank'],
                   params={},  # will be set by MPE to work on the rig
                   )
    
    # run it
    ss.run()
