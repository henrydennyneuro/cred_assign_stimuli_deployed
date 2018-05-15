# -*- coding: cp1252 -*-
"""
This is code to generate and run the brick stimuli.

Currently it is set to run a 36 min session.

"""

import Tkinter as tk
import tkSimpleDialog
from psychopy import monitors

# camstim is the Allen Institute stimulus package built on psychopy
from camstim import SweepStim
from camstim import Window, Warp

import stim_params

    
if __name__ == "__main__":
    
    dist = 15.0
    wid = 52.0
    
    # load and record parameters. Leave False.
    promptID = False
    # Save an extra copy of parameters under ./config
    extrasave = False
    
    # Record positions of squares at all times (LEAVE AS TRUE)
    recordPos = True
    
    # create a monitor
    monitor = monitors.Monitor("testMonitor", distance=dist, width=wid)

    # get animal ID and session ID
    if promptID == True: # using a prompt
        myDlg = tk.Tk()
        myDlg.withdraw()
        subj_id = tkSimpleDialog.askstring("Input", 
                                           "Subject ID (only nbrs, letters, _ ): ", 
                                           parent=myDlg)
        sess_id = tkSimpleDialog.askstring("Input", 
                                           "Session ID (only nbrs, letters, _ ): ", 
                                           parent=myDlg)
        
        if subj_id is None or sess_id is None:
            raise ValueError('No Subject and/or Session ID entered.')
    
    else: # Could also just enter it here.
        # if subj_id is left as None, will skip loading subj config
        subj_id = None
        sess_id = None
    
    # Create display window
    window = Window(fullscr=True, # Will return an error due to default size. Ignore.
                    monitor=monitor,  # Will be set to a gamma calibrated profile by MPE
                    screen=0,
                    warp=Warp.Spherical,
                    )
  
    sq = stim_params.init_run_squares(window, subj_id, sess_id, extrasave, recordPos)
        
    ss = SweepStim(window,
                   stimuli=[sq],
                   pre_blank_sec=1,
                   post_blank_sec=1,
                   params={},  # will be set by MPE to work on the rig
                   )
    
    # run it
    ss.run()