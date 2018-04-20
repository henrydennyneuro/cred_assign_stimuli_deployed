from psychopy import visual, monitors, core
# camstim is the Allen Institute stimulus package built on psychopy
from camstim import Stimulus, SweepStim, MovieStim
from camstim.sweepstim import StimulusArray
from camstim import Foraging
from camstim import Window, Warp
import numpy as np
from scipy import sin, stats
import os

# create a monitor
dist = 15.0
wid = 52.0
monitor = monitors.Monitor("testMonitor", distance=dist, width=wid)

# Create display window
window = Window(fullscr=True,
                monitor=monitor,  # Will be set to a gamma calibrated profile by MPE
                screen=0,
                #warp=Warp.Spherical, # Spherical/Disabled
                )

# Obtain monitor dimensions in degrees
# Appears a bit off - possibly related to flat vs round degrees?
# Also, I get this warning: User requested fullscreen with size [800 600], but 
# screen is actually [1536, 864]. Using actual size.

dim = window.monitor.getSizePix() # 1024, 768

# flat screen
deg_wid = np.rad2deg(np.arctan((wid)/dist)) * 2
deg_per_pix = deg_wid/dim[0]
deg_hei = deg_per_pix * dim[1]

# settings
# HAVEN'T FIGURED OUT HOW TO ROTATE GAUSSIAN AND SINE SEPARATELY
# Not sure how to pass a covariance matrix to maskParams
# Not clear whether stimuli can move during presentation

n_stim = 30 # number of stimuli
fixPar={ # parameters that stay fixed during presentation
        'units': 'deg',
        'size': (30, 30), # in units
        'sf': 0.06, # spatial frequency (sin) (cycles per deg)
        'phase': (1, 0), # (sin) only set first dim (0 to 1)
#        'ori': 0 # orientation of mask and texture
        }
sweepPar={ # parameters that change during presentation
        'Contrast': ([0.8], 0), # contrast is here as sweepPar must be passed later 
        'Ori': ([0, 90], 0), # orientation of mask and texture
         }
maskPar={ # parameters of the mask
        'sd': 3, # np.identity(2)*3 for cov matrix?
                             # nbr of sd on each side of mean in window. 
                             # Default seems to be 3. Better to change stim
                             # size
        }
sl = 2 # sweep length (in sec)
r = 8 # number of runs

# Create stimuli
# first create a drifting gratings, which just uses psychopy GratingStim
# see: http://www.psychopy.org/api/visual/gratingstim.html
# psychopy stimuli should work as well as those developed by the Institute
# currently locked to version 1.82.01 of psychopy

# sweep parameters are the parameters that will change during presentation

stims = list()

for i in range(n_stim):
    pos_x = (np.random.random_sample() - 0.5) * deg_wid #* 2 # haven't quite worked out why this needs to be doubled if no warping
    # testing edge
    # pos_x = 0.5*deg_wid
    pos_y = (np.random.random_sample() - 0.5) * deg_hei #* 2 # same
    # pos_y = 0.5*deg_hei
    
    stims.append(Stimulus(visual.GratingStim(window,
                                             pos=(pos_x, pos_y),
                                             tex='sin',
                                             mask='gauss',
#                                             maskParams=maskPar,
                                             autoLog=False,
                                             **fixPar
                                             ),
                        sweep_params=sweepPar,
                        sweep_length=sl,
                        runs=r))
    
# sweep_length here will overwrite earlier setting, but is required
gabors = StimulusArray(stims, sweep_length=sl)

# now create a movie stimulus from a 3D numpy array
# this is required to be 8-bit greyscale (np.uint8 or np.ubyte)
# I'm going to create one here, but normally the movie file will
# just be sitting at the prescribed path
# camstim expects movies in dimension (t, h, w)

moviesource = os.path.abspath("./example_gabor_mul.npy")


def create_movie(path):
    if os.path.exists(path):
        return
    x_dim = 192 # use only even numbers for later screen splitting
    y_dim = 120 # use only even numbers for later screen splitting
    int_sin = 0.13
    int_gau = 0.1
    blank = np.ones((y_dim, x_dim))
    rang_xs = np.linspace(0, int_sin*x_dim, x_dim)[np.newaxis, :]
    sine = sin(rang_xs)
    wave = blank * sine
    
    rang_xg = np.linspace(0, int_gau*x_dim, x_dim)[np.newaxis, :]
    rang_y = np.linspace(0, int_gau*y_dim, y_dim)[:, np.newaxis]
    gauss = np.array(blank)
    count = 0
    
    for i in range(1, 4):
        for j in range(1, 4):
            if (i != 2 and j != 2) or (i == 2 and j == 2):
                norm_x = stats.norm.pdf(rang_xg - int_gau * i * x_dim/4)
                norm_y = stats.norm.pdf(rang_y - int_gau * j * y_dim/4)
                prod = norm_x * norm_y
                gauss += prod
                count += 1
    
    # stretch gaussian
    gauss = (gauss - gauss.min())
    gauss *= stats.norm.pdf(0)/gauss.max()

    gabor = wave * gauss
    gabor_pos = gabor - gabor.min()
    neut = 0 - gabor.min() # neutral value (previously 0)
    
    # no point making time longer than longest dimension/2
    time = 192
    
    # fixed image movie
    # video = np.broadcast_to(gabor_pos, (time, gabor_pos.shape[0], gabor_pos.shape[1]))
        
    # split screen into 4 for the time component
    upleft = gabor_pos[: y_dim/2, : x_dim/2][np.newaxis, :, :]
    upright = gabor_pos[: y_dim/2, x_dim/2 :][np.newaxis, :, :]
    lowleft = gabor_pos[y_dim/2 :, : x_dim/2][np.newaxis, :, :]
    lowright = gabor_pos[y_dim/2 :, x_dim/2 :][np.newaxis, :, :]
    
    # Assign space for large temporary arrays
    temp = np.empty_like(upleft)
    
    for i in range(time):
        temp = upleft[i:i+1, : y_dim/2 - 1, : x_dim/2 - 1]
        temp = np.append(np.ones((1, 1, temp.shape[2]))*neut, temp, axis=1) #rows
        temp = np.append(np.ones((1, temp.shape[1], 1))*neut, temp, axis=2) #cols
        upleft = np.concatenate((upleft, temp), axis=0)
        
        temp = upright[i:i+1, : y_dim/2 - 1, 1 :]
        temp = np.append(np.ones((1, 1, temp.shape[2]))*neut, temp, axis=1)
        temp = np.append(temp, np.ones((1, temp.shape[1], 1))*neut, axis=2)
        upright = np.concatenate((upright, temp), axis=0)
        
        temp = lowleft[i:i+1, 1 :, : x_dim/2 - 1]
        temp = np.append(temp, np.ones((1, 1, temp.shape[2]))*neut, axis=1)
        temp = np.append(np.ones((1, temp.shape[1], 1))*neut, temp, axis=2)
        lowleft = np.concatenate((lowleft, temp), axis=0)
        
        temp = lowright[i:i+1, 1 :, 1 :]
        temp = np.append(temp, np.ones((1, 1, temp.shape[2]))*neut, axis=1)
        temp = np.append(temp, np.ones((1, temp.shape[1], 1))*neut, axis=2)
        lowright = np.concatenate((lowright, temp), axis=0)
        
    # reknit the pieces
    upvid = np.concatenate((upleft, upright), axis=2)
    lowvid = np.concatenate((lowleft, lowright), axis=2)
    video = np.concatenate((upvid, lowvid), axis=1)
    
    # average down the middle
#    video[:, y_dim/2 - 1 : y_dim/2 + 1, :] = np.average(video[:, y_dim/2 - 1 : y_dim/2 + 1, :], axis=1)[:, np.newaxis, :]
#    video[:, :, x_dim/2 - 1 : x_dim/2 + 1] = np.average(video[:, :, x_dim/2 - 1 : x_dim/2 + 1], axis=2)[:, :, np.newaxis]
    
    np.save(path, ((video / video.max()) * 255.0).astype(np.uint8))


create_movie(moviesource)
movie = MovieStim(movie_path=moviesource,
                  window=window,
                  frame_length=1.0/60.0,
                  size=(1920, 1200),
                  start_time=0.0,
                  stop_time=None,
                  flip_v=True,
                  runs=10,)

# set display sequences as ranges of time to run in seconds
movie_ds = [(16, 80)]
gabors_ds = [(0, 15)]

gabors.set_display_sequence(gabors_ds)
movie.set_display_sequence(movie_ds)

# create SweepStim instance
# contains all the different stimulus types arranged by display sequence
ss = SweepStim(window,
               stimuli=[gabors, movie],
               pre_blank_sec=1,
               post_blank_sec=1,
               params={},  # will be set by MPE to work on the rig
               )

## add in foraging so we can track wheel, potentially give rewards, etc
#f = Foraging(window=window,
#             auto_update=False,
#             params={},
#             nidaq_tasks={'digital_input': ss.di,
#                          'digital_output': ss.do})
#ss.add_item(f, "foraging")

# run it
ss.run()
