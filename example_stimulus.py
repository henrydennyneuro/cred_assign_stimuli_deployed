from psychopy import visual, monitors
# camstim is the Allen Institute stimulus package built on psychopy
from camstim import Stimulus, SweepStim, MovieStim
from camstim import Foraging
from camstim import Window, Warp
import numpy as np
import os

# create a monitor
monitor = monitors.Monitor("testMonitor", distance=15.0, width=52.0)

# Create display window
window = Window(fullscr=True,
                monitor=monitor,  # Will be set to a gamma calibrated profile by MPE
                screen=0,
                warp=Warp.Spherical,
                )

# Create stimuli
# first create a drifting gratings, which just uses psychopy GratingStim
# see: http://www.psychopy.org/api/visual/gratingstim.html
# psychopy stimuli should work as well as those developed by the Institute
# currently locked to version 1.82.01 of psychopy
dg = Stimulus(
    visual.GratingStim(window,
                       pos=(0, 0),
                       units='deg',
                       size=(250, 250),
                       mask="None",
                       texRes=256,
                       sf=0.1,
                       ),
    sweep_params={
               'Contrast': ([0.8], 0),
               'TF': ([1.0, 2.0, 4.0, 8.0, 15.0], 1),
               'SF': ([0.04], 2),
               'Ori': (range(0, 360, 45), 3),
               },
    sweep_length=2.0,
    start_time=0.0,
    blank_length=1.0,
    blank_sweeps=20,
    runs=15,
    shuffle=True,
    save_sweep_table=True,
    )
# now create a movie stimulus from a 3D numpy array
# this is required to be 8-bit greyscale (np.uint8 or np.ubyte)
# I'm going to create one here, but normally the movie file will
# just be sitting at the prescribed path
# camstim expects movies in dimension (t, h, w)
moviesource = os.path.abspath("./example_movie.npy")


def create_movie(path):
    if os.path.exists(path):
        return
    xx, yy = np.meshgrid(np.linspace(-10, 10, 192), np.linspace(-10, 10, 120))
    t = np.linspace(0, 100, 6000)[:, np.newaxis, np.newaxis]
    data = np.sin(np.sqrt((xx[np.newaxis, :, :])**2 + (yy[np.newaxis, :, :])**2) + t)
    data = data - data.min()
    np.save(path, ((data / data.max()) * 255.0).astype(np.uint8))


create_movie(moviesource)
movie = MovieStim(movie_path=moviesource,
                  window=window,
                  frame_length=2.0/60.0,
                  size=(1920, 1200),
                  start_time=0.0,
                  stop_time=None,
                  flip_v=True,
                  runs=10,)

# set display sequences as ranges of time to run in seconds
movie_ds = [(0, 5), (400, 600)]
dg_ds = [(6, 390), (610, 800)]

dg.set_display_sequence(dg_ds)
movie.set_display_sequence(movie_ds)

# create SweepStim instance
# contains all the different stimulus types arranged by display sequence
ss = SweepStim(window,
               stimuli=[dg, movie],
               pre_blank_sec=1,
               post_blank_sec=1,
               params={},  # will be set by MPE to work on the rig
               )

# add in foraging so we can track wheel, potentially give rewards, etc
f = Foraging(window=window,
             auto_update=False,
             params={},
             nidaq_tasks={'digital_input': ss.di,
                          'digital_output': ss.do})
ss.add_item(f, "foraging")

# run it
ss.run()
