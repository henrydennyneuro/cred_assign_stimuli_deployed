from psychopy import visual

import pickle as pkl
import os
import numpy as np
import random
import itertools

from camstim import Stimulus
from ourstimuli import OurStims

""" Functions to initialize parameters for gabors or squares, load them if necessary,
save them, and create stimuli.

Parameters are set here.
"""

GABOR_PARAMS = {
                ### PARAMETERS TO SET
                'n_gabors': 100,
                # range of size of gabors to sample from (height and width set to same value)
                'size_ran': [10, 20], # in deg (regardless of units below), full-width half-max 
                'sf': 0.04, # spatial freq (cyc/deg) (regardless of units below)
                'phase': 0.25, #value 0-1
                
                'oris': [0.0, 45.0, 90.0, 135.0], # orientation means to use (deg)
                'ori_std': [0.25, 0.5], # orientation st dev to use (rad) (do not pass 0)
                
                'im_len': 0.3, # duration (sec) of each image (e.g., A)
                'reg_len': [30, 90], # range of durations (sec) for seq of regular sets
                'surp_len': [3, 6], # range of durations (sec) for seq of surprise sets
                'kap_len': 17*60, # duration (sec) of each kappa setting
                
                ### Changing these will require tweaking downstream...
                'units': 'pix', # avoid using deg, comes out wrong at least on my computer (scaling artifact? 1.7)
                'n_im': 4 # nbr of images per set (A, B, C, D/E)
                }

SQUARE_PARAMS = {
                ### PARAMETERS TO SET
                'sizes': [8, 16], # in deg (regardless of units below)
                'direcs': ['right', 'left'], # main direction 
                'speed': 50, # deg/sec (regardless of units below)
                'flipfrac':0.25, # fraction of elements that should be flipped (0 to 1)
                
                'seg_len': 1, # duration (sec) of each segment
                'reg_len': [30, 90], # range of durations (sec) for reg flow
                'surp_len': [2, 4], # range of durations (sec) for mismatch flow
                'set_len': 9*60, # duration (sec) of set (sizexdirec)
                
                ### Changing these will require tweaking downstream...
                'units': 'pix', # avoid using deg, comes out wrong at least on my computer (scaling artifact? 1.7)
                
                ## MAY CAUSE PROBLEMS. OTHER WAY TO GET THIS?
                'fps': 60 # frames per sec, default is 60 in camstim
                }


def winVar(win, units):
    """Returns width and height of the window in units as tuple.
    Takes window and units.
    """
    dist = win.monitor.getDistance()
    width = win.monitor.getWidth()
    
    # get values to convert deg to pixels
    deg_wid = np.rad2deg(np.arctan((0.5*width)/dist)) * 2 # about 120
    deg_per_pix = deg_wid/win.size[0] # about 0.07
    
    if units == 'deg':
        deg_hei = deg_per_pix * win.size[1] # about 67
        # Something is wrong with deg as this does not fill screen
        init_wid = deg_wid
        init_hei = deg_hei
        fieldSize = [init_wid, init_hei]

    elif units == 'pix':
        init_wid = win.size[0]
        init_hei = win.size[1]
        fieldSize = [init_wid, init_hei]
    
    else:
        raise ValueError('Only implemented for deg or pixel units so far.')
    
    return fieldSize, deg_per_pix
        
def posarray(fieldsize, n_elem, n_im):
    """Returns 2D array of positions in field.
    Takes fieldsize, number of elements (e.g., of gabors), and number of 
    images (e.g., A, B, C, D, E).
    """

    coords_wid = np.random.uniform(-fieldsize[0]/2, fieldsize[0]/2, [n_im, n_elem])[:, :, np.newaxis]
    coords_hei = np.random.uniform(-fieldsize[1]/2, fieldsize[1]/2, [n_im, n_elem])[:, :, np.newaxis]
    return np.concatenate((coords_wid, coords_hei), axis=2)

def sizearray(size_ran, n_elem, n_im):
    """Returns array of sizes in range (1D).
    Takes start and end of range, number of elements (e.g., of gabors), and 
    number of images (e.g., A, B, C, D, E).
    """
    
    if len(size_ran) == 1:
        size_ran = [size_ran[0], size_ran[0]]
    
    return np.random.uniform(size_ran[0], size_ran[1], [n_im, n_elem])

def possizearrays(size_ran, fieldsize, n_elem, n_im):
    """Returns zip of list of pos and sizes for n_elem.
    Takes start and end of size range, fieldsize, number of elements (e.g., of 
    gabors), and number of images (e.g., A, B, C, D/E).
    """
    pos = posarray(fieldsize, n_elem, n_im + 1) # add one for E
    sizes = sizearray(size_ran, n_elem, n_im + 1) # add one for E
    
    return zip(pos, sizes)

def setkaps(ori_std):
    """Returns shuffled list of kappas based on standard deviation in radians
    """
    kaps = [1.0/x**2 for x in ori_std]
    random.shuffle(kaps)
    
    return kaps
    

def createseqlen(kap_sets, reg_sets, surp_sets, n_kap):
    """
    Takes nbr of sets per kappa, duration of seq of regular sets, duration of 
    seq of surprise sets, number of kappas.
    
    Returns a list of sublists for each kappa value. Each sublist contains
    a sublist of regular set durations and a sublist of surprise set durations.
    
    FYI, this may go on forever for problematic duration ranges.
    
    """
    minim = reg_sets[0]+surp_sets[0] # smallest possible reg + surp set
    maxim = reg_sets[1]+surp_sets[1] # largest possible reg + surp set
    
    # sample a few lengths to start, without going over kappa set length
    n = int(kap_sets/(reg_sets[1]+surp_sets[1]))
    kaps = list() # list of lists for each kappa with their seq lengths
    
    for i in range(n_kap):
        # mins and maxs to sample from
        reg_set_len = np.random.randint(reg_sets[0], reg_sets[1] + 1, n).tolist()
        surp_set_len = np.random.randint(surp_sets[0], surp_sets[1] + 1, n).tolist()
        reg_sum = sum(reg_set_len)
        surp_sum = sum(surp_set_len)
        
        while reg_sum + surp_sum < kap_sets:
            rem = kap_sets - reg_sum - surp_sum
            # Check if at least the minimum is left. If not, remove last. 
            while rem < minim:
                # can increase to remove 2 if ranges are tricky...
                reg_set_len = reg_set_len[0:-1]
                surp_set_len = surp_set_len[0:-1]
                rem = kap_sets - sum(reg_set_len) - sum(surp_set_len)
                
            # Check if what is left is less than the maximum. If so, use up.
            if rem <= maxim:
                # get new allowable ranges
                reg_min = max(reg_sets[0], rem - surp_sets[1])
                reg_max = min(reg_sets[1], rem - surp_sets[0])
                new_reg_set_len = np.random.randint(reg_min, reg_max + 1)
                new_surp_set_len = int(rem - new_reg_set_len)
            
            # Otherwise just get a new value
            else:
                new_reg_set_len = np.random.randint(reg_sets[0], reg_sets[1] + 1)
                new_surp_set_len = np.random.randint(surp_sets[0], surp_sets[1] + 1)
            
            reg_set_len.append(new_reg_set_len)
            surp_set_len.append(new_surp_set_len)
            
            reg_sum = sum(reg_set_len)
            surp_sum = sum(surp_set_len)     
            
        kaps.append([reg_set_len, surp_set_len])

    return kaps

def oriparsurpgenerator(oris, kaps, seqperkap):
    """
    
    """
    n_oris = float(len(oris)) # number of orientations
    orisurplist = list()
    
    for k, kap in enumerate(seqperkap): # kappa 
        orisublist = list()
        surpsublist = list()
        for i, (reg, surp) in enumerate(zip(kap[0], kap[1])):     
            # deal with gen
            oriadd = list()
            for j in range(int(np.ceil(reg/n_oris))):
                random.shuffle(oris) # in place
                oriadd.extend(oris[:])
            oriadd = oriadd[:reg] # chop!
            surpadd = np.zeros_like(oriadd) # keep track of not surprise (0)
            orisublist.extend(oriadd)
            surpsublist.extend(surpadd)
            
            # deal with surp
            oriadd = list()
            for j in range(int(np.ceil(surp/n_oris))):
                random.shuffle(oris) # in place
                oriadd.extend(oris[:])
            oriadd = oriadd[:surp]
            surpadd = np.ones_like(oriadd) # keep track of surprise (1)
            orisublist.extend(oriadd)
            surpsublist.extend(surpadd)
        kapsublist = np.ones_like(surpsublist) * kaps[k]
        
        orisurplist.extend(zip(orisublist, kapsublist, surpsublist))
        
    
    return orisurplist
    

def oriparsurporder(oris, n_im, im_len, reg_len, surp_len, kaps, kap_len):
    """
    Takes desired orientations, number of images (e.g., A, B, C, D/E), 
    duration of each image, duration of seq of regular sets, duration of seq 
    of surprise sets, number of kappas, duration for each kappa (one value).
    
    Return an amazing list
    
    """
    seq_len = im_len * (n_im + 1.0) # duration of set (incl. one blank per set)
    reg_sets = [x/seq_len for x in reg_len] # range of nbr of sets per regular seq, e.g. 20-60
    surp_sets = [x/seq_len for x in surp_len] # range of nbr of sets per surprise seq, e.g., 2-4
    kap_sets = kap_len/seq_len # nbr of sets per kappa, e.g. 680
    n_kap = len(kaps) # nbr of kappas
    
    # get seq lengths
    seqperkap = createseqlen(kap_sets, reg_sets, surp_sets, n_kap)
    
    # from seq durations get a list each kappa or (ori, surp=0 or 1)
    oriparsurplist = oriparsurpgenerator(oris, kaps, seqperkap)

    return oriparsurplist


def flipdirecgenerator(flipcode, setorder, segperset):
    """
    Flipcode should have a length of 2. Should be [0, 1] with 0 for regular
    flow and 1 for mismatch flow.
    Setorder contains a list of ((size, n_Squares), direc)
    """
    flipdireclist = list()
    
    for s, thisset in enumerate(segperset): # each set (sizexdirec)
        surpsublist = list()
        for i, (reg, surp) in enumerate(zip(thisset[0], thisset[1])):     
            # deal with gen
            regadd = [flipcode[0]] * reg
            surpadd = [flipcode[1]] * surp
            surpsublist.extend(regadd)
            surpsublist.extend(surpadd)
            
        sizesublist = [setorder[s][0][0]] * len(surpsublist)
        nsqusublist = [setorder[s][0][1]] * len(surpsublist)
        direcsublist = [setorder[s][1]] * len(surpsublist)
        
        flipdireclist.extend(zip(surpsublist, sizesublist, nsqusublist,
                                 direcsublist))
    
    return flipdireclist


def flipdirecorder(seg_len, reg_len, surp_len, set_len, setorder):
    """    
    Return an amazing list of when direction should be regular and 
    when to flip
    
    """
    seg_len # duration of set (incl. one blank per set)
    reg_segs = [x/seg_len for x in reg_len] # range of nbr of segs per regular seq, e.g. 30-90
    surp_segs = [x/seg_len for x in surp_len] # range of nbr of segs per surprise seq, e.g., 2-4
    set_segs = set_len/seg_len # nbr of segs per set, e.g. 540
    n_sets = len(setorder)
    
    # get seg lengths
    segperset = createseqlen(set_segs, reg_segs, surp_segs, n_sets)
    
    # flip code: [reg, flip]
    flipcode = [0, 1]
    
    # from seq durations get a list each kappa or (ori, surp=0 or 1)
    flipdireclist = flipdirecgenerator(flipcode, setorder, segperset)

    return flipdireclist


def load_config(stimtype, subj_id):
    config_root = '.\config'
    config_name = '{}_subj{}_config.pkl'.format(stimtype, subj_id)
    config_file = os.path.join(config_root, config_name)
    
    # if they exist, retrieve the parameters specific to the subject.
    # otherwise, create them
    if subj_id is not None and os.path.exists(config_file):
        with open(config_file, 'r') as f:
            subj_params = pkl.load(f)
            print('Existing subject config used: {}.'.format(config_file))
        return subj_params
    else:
        return None


def save_config(stimtype, subj_id, subj_params):
    config_root = '.\config'
    config_name = '{}_subj{}_config.pkl'.format(stimtype, subj_id)
    config_file = os.path.join(config_root, config_name)
    
    # if config directory does not exist, create it
    if not os.path.exists(config_root):
        os.makedirs(config_root)
    
    with open(config_file, 'w') as f:
        pkl.dump(subj_params, f)
        print('New subject config saved under: {}'.format(config_file))

    
def save_session_config(stimtype, subj_id, sess_id, subj_params):
    config_root = '.\config'
    all_config_name = '{}_subj{}_sess{}_config'.format(stimtype, subj_id, sess_id)
    all_config_ext = '.pkl'
    all_config_file = os.path.join(config_root, all_config_name + all_config_ext)
    
    # if config directory does not exist, create it
    if not os.path.exists(config_root):
        os.makedirs(config_root)
    
    # save the parameters for this subject and session
    if os.path.exists(all_config_file):
        i = 0
        all_config = '{}_{}{}'.format(all_config_name, i, all_config_ext)
        all_config_file = os.path.join(config_root, all_config)
        while os.path.exists(all_config_file):
           i +=1
           all_config = '{}_{}{}'.format(all_config_name, i, all_config_ext)
           all_config_file = os.path.join(config_root, all_config)
    
    with open(all_config_file, 'w') as f:
        pkl.dump(subj_params, f)
        print('Session parameters saved under: {}'.format(all_config_file))


def init_run_squares(window, subj_id, sess_id, square_params=SQUARE_PARAMS):
     # get fieldsize in units and deg_per_pix
    fieldsize, deg_per_pix = winVar(window, square_params['units'])
    
    # convert values to pixels if necessary
    if square_params['units'] == 'pix':
        sizes = [np.around(x/deg_per_pix) for x in square_params['sizes']]
        speed = square_params['speed']/deg_per_pix
    else:
        sizes = square_params['size']
        speed = square_params['speed']
    
    # convert speed for units/s to units/frame
    speed = np.around(speed/square_params['fps'], decimals=4)
    
    # calculate number of squares for each square size
    area = fieldsize[0]*fieldsize[1]
    squarea = [np.square(x) for x in sizes]
    n_Squares = [int(0.5*area/x) for x in squarea]
    
    # parameter loading and recording steps are only done if a subj_id
    # is passed.
    # find whether parameters have been saved for this animal
    if subj_id is not None:
        subj_params = load_config('sq', subj_id)
    
    if subj_id is None or subj_params is None:
        subj_params = {}
        
        # set set order for each subject
        basic = list(itertools.product(zip(sizes, n_Squares), 
                                       square_params['direcs']))
        random.shuffle(basic)
        setorder = basic[:]
        
        subj_params['set_order'] = setorder
    
        if subj_id is not None:
            save_config('sq', subj_id, subj_params)
    
    # establish a pseudorandom array of when to switch from reg to mismatch
    # flow and back    
    flipdirecarray = flipdirecorder(square_params['seg_len'], 
                                  square_params['reg_len'], 
                                  square_params['surp_len'], 
                                  square_params['set_len'],
                                  subj_params['set_order'])
    
    
    # create file name to save parameters for subject and session
    if subj_id is not None:    
        save_session_config('sq', subj_id, sess_id, subj_params)
    
    fixPar={ # parameters set by ElementArrayStim
            'units': square_params['units'],
            'nElements': max(n_Squares), # initialize with max
            'fieldShape': 'sqr',
            'contrs': 1.0,
            'elementTex': None,
            'elementMask': None,
            'name': 'bricks',
            }
    
    sweepPar={ # parameters to sweep over (0 is outermost parameter)
            'FlipDirecSize': (flipdirecarray, 0),
            }
    
    # Create the stimulus array
    squares = visual.ElementArrayStim(window, **fixPar)
    
    ourstimsq = OurStims(squares.win, squares, fieldsize, speed=speed,
                         flipfrac=square_params['flipfrac'],
                         currval=flipdirecarray[0])
    
    sq = Stimulus(ourstimsq,
                  sweepPar,
                  sweep_length=square_params['seg_len'], 
                  start_time=0.0,
                  blank_sweeps=square_params['set_len']/square_params['seg_len'], # blank sweep at the end of every set
                  runs=1,
                  shuffle=False,
                  fps=square_params['fps'],
                  )
    
    return sq

def init_run_gabors(window, subj_id, sess_id, gabor_params=GABOR_PARAMS):

    # get fieldsize in units and deg_per_pix
    fieldsize, deg_per_pix = winVar(window, gabor_params['units'])
    
    # convert values to pixels if necessary
    if gabor_params['units'] == 'pix':
        size_ran = [np.around(x/deg_per_pix) for x in gabor_params['size_ran']]
        sf = gabor_params['sf']*deg_per_pix
    else:
        size_ran = gabor_params['size_ran']
        sf = gabor_params['sf']
    
    # size is set as where gauss std=3 on each side (so size=6 std). 
    # Convert from full-width half-max
    gabor_modif = 6/2*np.sqrt(2*np.log(2))
    size_ran = [np.around(x * gabor_modif) for x in size_ran]
    
    # parameter loading and recording steps are only done if a subj_id
    # is passed.
    # find whether parameters have been saved for this animal
    if subj_id is not None:
        subj_params = load_config('gab', subj_id)
    
    if subj_id is None or subj_params is None:
        subj_params = {}
        # get positions and sizes for each image (A, B, C, D, E)
        subj_params['possize'] = possizearrays(size_ran, 
                                               fieldsize, 
                                               gabor_params['n_gabors'], 
                                               gabor_params['n_im'])
    
        # get shuffled kappas: approximately 1/std**2 where std is in radians
        subj_params['kaps'] = setkaps(gabor_params['ori_std'])
        if subj_id is not None:
            save_config('gab', subj_id, subj_params)
    
    # establish a pseudorandom order of orientations to cycle through
    # (surprise and current kappa integrated as well)    
    oriparsurps = oriparsurporder(gabor_params['oris'], 
                                  gabor_params['n_im'], 
                                  gabor_params['im_len'], 
                                  gabor_params['reg_len'], 
                                  gabor_params['surp_len'], 
                                  subj_params['kaps'], 
                                  gabor_params['kap_len'])
    
    subj_params['windowpar'] = [fieldsize, deg_per_pix]
    subj_params['oriparsurps'] = oriparsurps   
    
    # create file name to save parameters for subject and session
    if subj_id is not None:    
        save_session_config('gab', subj_id, sess_id, subj_params)
            
    fixPar={ # parameters set by ElementArrayStim
            'units': gabor_params['units'],
            'nElements': gabor_params['n_gabors'], # number of stimuli on screen
            'fieldShape': 'sqr',
            'contrs': 1.0,
            'phases': gabor_params['phase'],
            'elementTex': 'sin',
            'elementMask': 'gauss',
            'name': 'gabors',
            }
    
    sweepPar={ # parameters to sweep over (0 is outermost parameter)
            'OriParSurp': (oriparsurps, 0), # contains (ori in degrees, surp=0 or 1, kappa)
            'PosSizesAll': ([0, 1, 2, 3], 1), # pass sets of positions and sizes
            }
    
    # Create the stimulus array
    gabors = visual.ElementArrayStim(window, **fixPar)
    
    ourstimgab = OurStims(gabors.win, gabors, fieldsize, sf=sf, 
                          possizes=subj_params['possize'])
    
    gb = Stimulus(ourstimgab,
                  sweepPar,
                  sweep_length=gabor_params['im_len'], 
                  blank_sweeps=gabor_params['n_im'], # present a blank screen after every set of images
                  start_time=0.0,
                  runs=1,
                  shuffle=False,
                  fps=60, # frames per sec, default is 60 in camstim
                  )
    
    return gb