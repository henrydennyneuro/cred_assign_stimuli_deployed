import pickle as pkl
import os
import numpy as np
import random
import itertools
import time

from camstim import Stimulus
from ourstimuli import OurStims

""" Functions to initialize parameters for gabors or squares, load them if necessary,
save them, and create stimuli.

Parameters are set here.
"""

GABOR_PARAMS = {
                ### PARAMETERS TO SET
                'n_gabors': 30,
                # range of size of gabors to sample from (height and width set to same value)
                'size_ran': [10, 20], # in deg (regardless of units below), full-width half-max 
                'sf': 0.04, # spatial freq (cyc/deg) (regardless of units below)
                'phase': 0.25, #value 0-1
                
                'oris': [0.0, 45.0, 90.0, 135.0], # orientation means to use (deg)
                'ori_std': [0.25, 0.5], # orientation st dev to use (rad) (do not pass 0)
                
                ###FOR NO SURPRISE, enter [0, 0] for surp_len and [block_len, block_len] for reg_len
                'im_len': 0.3, # duration (sec) of each image (e.g., A)
                'reg_len': [30, 90], # range of durations (sec) for seq of regular sets
                'surp_len': [3, 6], # range of durations (sec) for seq of surprise sets
                'block_len': 900, # duration (sec) of each block (1 per kappa (or ori_std) value, i.e. 2)
                'sd': 3, # nbr of st dev (gauss) to edge of gabor (default is 6)
                
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
                
                'seg_len': 1, # duration (sec) of each segment (somewhat arbitrary)
                
                ###FOR NO SURPRISE, enter [0, 0] for surp_len and [block_len, block_len] for reg_len
                'reg_len': [30, 90], # range of durations (sec) for reg flow
                'surp_len': [2, 4], # range of durations (sec) for mismatch flow
                'block_len': 450, # duration (sec) of each block (1 per direc/size combo, i.e. 4)
                
                ### Changing these will require tweaking downstream...
                'units': 'pix', # avoid using deg, comes out wrong at least on my computer (scaling artifact? 1.7)
                
                ## ASSUMES THIS IS THE ACTUAL FRAME RATE 
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
        
def posarray(rng, fieldsize, n_elem, n_im):
    """Returns 2D array of positions in field.
    Takes fieldsize, number of elements (e.g., of gabors), and number of 
    images (e.g., A, B, C, D, E).
    
    Seeding (using rng) can be used to ensure it is consistent for each animal.
    """
    if rng is not None:
        coords_wid = rng.uniform(-fieldsize[0]/2, fieldsize[0]/2, [n_im, n_elem])[:, :, np.newaxis]
        coords_hei = rng.uniform(-fieldsize[1]/2, fieldsize[1]/2, [n_im, n_elem])[:, :, np.newaxis]
    else:
        coords_wid = np.random.uniform(-fieldsize[0]/2, fieldsize[0]/2, [n_im, n_elem])[:, :, np.newaxis]
        coords_hei = np.random.uniform(-fieldsize[1]/2, fieldsize[1]/2, [n_im, n_elem])[:, :, np.newaxis]
        
    return np.concatenate((coords_wid, coords_hei), axis=2)

def sizearray(rng, size_ran, n_elem, n_im):
    """Returns array of sizes in range (1D).
    Takes start and end of range, number of elements (e.g., of gabors), and 
    number of images (e.g., A, B, C, D, E).
    
    Seeding (using rng) can be used to ensure it is consistent for each animal.
    """
    if len(size_ran) == 1:
        size_ran = [size_ran[0], size_ran[0]]
    
    if rng is not None:
        sizes = rng.uniform(size_ran[0], size_ran[1], [n_im, n_elem])
    else:
        sizes = np.random.uniform(size_ran[0], size_ran[1], [n_im, n_elem])
    np.random.seed(None)
    
    return np.around(sizes)

def possizearrays(rng, size_ran, fieldsize, n_elem, n_im):
    """Returns zip of list of pos and sizes for n_elem.
    Takes start and end of size range, fieldsize, number of elements (e.g., of 
    gabors), and number of images (e.g., A, B, C, D/E).
    
     Seeding (using rng) can be used to ensure it is consistent for each animal.
    """
    pos = posarray(rng, fieldsize, n_elem, n_im + 1) # add one for E
    sizes = sizearray(rng, size_ran, n_elem, n_im + 1) # add one for E
    
    return zip(pos, sizes)

def setblock_order(rng, ori_std):
    """Returns shuffled list of kappas based on standard deviation in radians.
       Seeding (using rng) can be used to ensure it is consistent for each animal.
    """
    block_order = [1.0/x**2 for x in ori_std]
    
    if rng is not None:
        rng.shuffle(block_order)
    else:
        np.random.shuffle(block_order)
    print(block_order)    
    return block_order
    

def createseqlen(block_segs, regs, surps, n_blocks):
    """
    Arg:
        block_segs: number of segs per block
        regs: duration of each regular set/seg 
        surps: duration of each regular set/seg
        n_blocks: number of blocks.
    
    Returns:
         list of sublists for each block. Each sublist contains a sublist of 
         regular set durations and a sublist of surprise set durations.
    
    FYI, this may go on forever for problematic duration ranges.
    
    """
    minim = regs[0]+surps[0] # smallest possible reg + surp set
    maxim = regs[1]+surps[1] # largest possible reg + surp set
    
    # sample a few lengths to start, without going over kappa set length
    n = int(block_segs/(regs[1]+surps[1]))
    blocks = list() # list of lists for each kappa with their seq lengths
    
    for i in range(n_blocks):
        # mins and maxs to sample from
        reg_block_len = np.random.randint(regs[0], regs[1] + 1, n).tolist()
        surp_block_len = np.random.randint(surps[0], surps[1] + 1, n).tolist()
        reg_sum = sum(reg_block_len)
        surp_sum = sum(surp_block_len)
        
        while reg_sum + surp_sum < block_segs:
            print(reg_sum)
            print(surp_sum)
            print(block_segs)
            rem = block_segs - reg_sum - surp_sum
            # Check if at least the minimum is left. If not, remove last. 
            while rem < minim:
                # can increase to remove 2 if ranges are tricky...
                reg_block_len = reg_block_len[0:-1]
                surp_block_len = surp_block_len[0:-1]
                rem = block_segs - sum(reg_block_len) - sum(surp_block_len)
                
            # Check if what is left is less than the maximum. If so, use up.
            if rem <= maxim:
                # get new allowable ranges
                reg_min = max(regs[0], rem - surps[1])
                reg_max = min(regs[1], rem - surps[0])
                new_reg_block_len = np.random.randint(reg_min, reg_max + 1)
                new_surp_block_len = int(rem - new_reg_block_len)
            
            # Otherwise just get a new value
            else:
                new_reg_block_len = np.random.randint(regs[0], regs[1] + 1)
                new_surp_block_len = np.random.randint(surps[0], surps[1] + 1)
            
            reg_block_len.append(new_reg_block_len)
            surp_block_len.append(new_surp_block_len)
            
            reg_sum = sum(reg_block_len)
            surp_sum = sum(surp_block_len)     
            
        blocks.append([reg_block_len, surp_block_len])

    return blocks

def oriparsurpgenerator(oris, block_order, block_segs):
    """
    Args:
        oris: mean orientations
        block_order: order of block parameters (kappas for gabors, direc x size for squares)
        block_segs: list of sublists for each block. Each sublist contains a sublist of 
                    regular set durations and a sublist of surprise set durations.
    
    Returns:
        a zipped list of sublists with the mean orientation, kappa value
        and surprise value for each image (each 300 ms for example).
    
    FYI, this may go on forever for problematic duration ranges.
    """
    n_oris = float(len(oris)) # number of orientations
    orisurplist = list()
    
    for k, kap in enumerate(block_segs): # kappa 
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
        block_segsublist = np.ones_like(surpsublist) * block_order[k]
        
        orisurplist.extend(zip(orisublist, block_segsublist, surpsublist))
        
    
    return orisurplist
    

def oriparsurporder(oris, n_im, im_len, reg_len, surp_len, block_order, block_len):
    """
    Args:
        oris: orientations
        n_im: number of images (e.g., A, B, C, D/E)
        im_len: duration of each image
        reg_len: range of durations of reg seq
        surp_len: range of durations of surp seq
        block_order: order of block parameters (kappas for gabors)
        block_len: duration of each block (single value)
    
    Returns:
        a zipped list of sublists with the mean orientation, kappa value
        and surprise value (0 or 1) for each image (each 300 ms for example).
    
    """
    set_len = im_len * (n_im + 1.0) # duration of set (incl. one blank per set)
    reg_sets = [x/set_len for x in reg_len] # range of nbr of sets per regular seq, e.g. 20-60
    surp_sets = [x/set_len for x in surp_len] # range of nbr of sets per surprise seq, e.g., 2-4
    block_segs = block_len/set_len # nbr of segs per block, e.g. 680
    n_blocks = len(block_order) # nbr of blocks (kappas)
    
    # get seq lengths
    block_segs = createseqlen(block_segs, reg_sets, surp_sets, n_blocks)
    
    # from seq durations get a list each kappa or (ori, surp=0 or 1)
    oriparsurplist = oriparsurpgenerator(oris, block_order, block_segs)

    return oriparsurplist


def flipdirecgenerator(flipcode, block_order, segperblock):
    """
    Args:
        flipcode: should be [0, 1] with 0 for regular flow and 1 for mismatch flow.
        block_order: order of block parameters (direc x size for squares)
        segperblock: list of sublists for each block. Each sublist contains a sublist of 
                     regular seg durations and a sublist of surprise seg durations.
    
    Returns:
        a zipped list of sublists with the surprise value (0 or 1), size, 
        number of squares, direction for each kappa value
        and surprise value (0 or 1) for each segment (each 1s for example).
    
    """
    flipdireclist = list()
    
    for s, thisblock in enumerate(segperblock): # each block (sizexdirec)
        surpsublist = list()
        for i, (reg, surp) in enumerate(zip(thisblock[0], thisblock[1])):     
            # deal with gen
            regadd = [flipcode[0]] * reg
            surpadd = [flipcode[1]] * surp
            surpsublist.extend(regadd)
            surpsublist.extend(surpadd)
            
        sizesublist = [block_order[s][0][0]] * len(surpsublist)
        nsqusublist = [block_order[s][0][1]] * len(surpsublist)
        direcsublist = [block_order[s][1]] * len(surpsublist)
        
        flipdireclist.extend(zip(surpsublist, sizesublist, nsqusublist,
                                 direcsublist))
    
    return flipdireclist


def flipdirecorder(seg_len, reg_len, surp_len, block_order, block_len):
    """ 
    Args:
        seg_len: duration of each segment (arbitrary minimal time segment)
        reg_len: range of durations of reg seq
        surp_len: range of durations of surp seq
        block_order: order of block parameters (direc x size for squares)
        block_len: duration of each block (single value)
    
    Returns:
        a zipped list of sublists with the surprise value (0 or 1), size, 
        number of squares, direction for each kappa value
        and surprise value (0 or 1) for each segment (each 1s for example).
    
    """
    reg_segs = [x/seg_len for x in reg_len] # range of nbr of segs per regular seq, e.g. 30-90
    surp_segs = [x/seg_len for x in surp_len] # range of nbr of segs per surprise seq, e.g., 2-4
    block_segs = block_len/seg_len # nbr of segs per block, e.g. 540
    n_blocks = len(block_order)
    
    # get seg lengths
    segperblock = createseqlen(block_segs, reg_segs, surp_segs, n_blocks)
    
    # flip code: [reg, flip]
    flipcode = [0, 1]
    
    # from seq durations get a list each kappa or (ori, surp=0 or 1)
    flipdireclist = flipdirecgenerator(flipcode, block_order, segperblock)

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
            print(subj_params['block_order'])
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

    
def save_session_params(stimtype, subj_id, sess_id, stim_params, subj_params):
    params_root = '.\config'
    time_info = {
                'timestr': time.strftime("%Y%m%d-%H%M%S")
                }
    if subj_id is not None:
        all_params_name = '{}_subj{}_sess{}_params'.format(stimtype, subj_id, sess_id)
    else:
        all_params_name = '{}_{}_params'.format(stimtype, time_info['timestr'])
    all_params_ext = '.pkl'
    all_params_file = os.path.join(params_root, all_params_name + all_params_ext)
    
    # if params directory does not exist, create it
    if not os.path.exists(params_root):
        os.makedirs(params_root)
    
    # save the parameters for this subject and session
    if os.path.exists(all_params_file):
        i = 0
        all_params = '{}_{}{}'.format(all_params_name, i, all_params_ext)
        all_params_file = os.path.join(params_root, all_params)
        while os.path.exists(all_params_file):
           i +=1
           all_params = '{}_{}{}'.format(all_params_name, i, all_params_ext)
           all_params_file = os.path.join(params_root, all_params)
    
    with open(all_params_file, 'w') as f:
        pkl.dump(time_info, f)
        pkl.dump(stim_params, f)
        pkl.dump(subj_params, f)
        print('Session parameters saved under: {}'.format(all_params_file))


def init_run_squares(window, subj_id, sess_id, seed, extrasave, recordPos, square_params=SQUARE_PARAMS):
    
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
    speed = speed/square_params['fps']
    
    # to get actual frame rate
    act_fps = window.getMsPerFrame() # returns average, std, median
    
    # calculate number of squares for each square size
    area = fieldsize[0]*fieldsize[1]
    squarea = [np.square(x) for x in sizes]
    n_Squares = [int(0.75*area/x) for x in squarea] #JZ Changed from 0.5*area/x on May 17
    
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
        if seed is not None:
            rng = np.random.RandomState(seed)
            rng.shuffle(basic)
        else:
            np.random.shuffle(basic)

        block_order = basic[:]
        
        subj_params['block_order'] = block_order
        print(block_order)    

    
        if subj_id is not None:
            save_config('sq', subj_id, subj_params)
    
    # establish a pseudorandom array of when to switch from reg to mismatch
    # flow and back    
    flipdirecarray = flipdirecorder(square_params['seg_len'],
                                    square_params['reg_len'], 
                                    square_params['surp_len'],
                                    subj_params['block_order'],
                                    square_params['block_len'])
    
    subj_params['windowpar'] = [fieldsize, deg_per_pix]
    subj_params['flipdirecarray'] = flipdirecarray
    subj_params['seed'] = seed
    subj_params['subj_id'] = subj_id
    subj_params['sess_id'] = sess_id
    
    # save parameters for subject and session under ./config
    if extrasave:
        save_session_params('sq', subj_id, sess_id, square_params, subj_params)
    
    elemPar={ # parameters set by ElementArrayStim
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
    squares = OurStims(window, elemPar, fieldsize, speed=speed,
                         flipfrac=square_params['flipfrac'],
                         currval=flipdirecarray[0])
    
    # Add these attributes for the logs
    squares.square_params = square_params
    squares.subj_params = subj_params
    squares.actual_fps = act_fps
    
    sq = Stimulus(squares,
                  sweepPar,
                  sweep_length=square_params['seg_len'], 
                  start_time=0.0,
                  blank_sweeps=square_params['block_len']/square_params['seg_len'],
                  runs=1,
                  shuffle=False,
                  )
    
    # record attributes from OurStims
    attribs = ['elemParams', 'fieldSize', 'tex', 'colors', 'square_params',
               'initScr', 'possizes', 'autoLog', 'units','actual_fps', 
               'subj_params', 'last_frame']
    
    if recordPos:
        attribs.extend(['posByFrame']) # potentially large array
    
    sq.stimParams = {key:sq.stim.__dict__[key] for key in attribs}
    
    return sq

def init_run_gabors(window, subj_id, sess_id, seed, extrasave, recordOris, gabor_params=GABOR_PARAMS):
    
    if seed is not None:
        rng = np.random.RandomState(seed)
    else:
        rng = None
    
    rng_possize = np.random.RandomState(1) #JZ: use seed of 1 for pos and size: ensure consistency forever

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
    gabor_modif = 1.0/(2*np.sqrt(2*np.log(2))) * gabor_params['sd']
    size_ran = [np.around(x * gabor_modif) for x in size_ran]
    
    # parameter loading and recording steps are only done if a subj_id
    # is passed.
    # find whether parameters have been saved for this animal
    if subj_id is not None:
        subj_params = load_config('gab', subj_id)
    
    if subj_id is None or subj_params is None:
        subj_params = {}
        # get positions and sizes for each image (A, B, C, D, E)
        subj_params['possize'] = possizearrays(rng_possize,
                                               size_ran, 
                                               fieldsize, 
                                               gabor_params['n_gabors'], 
                                               gabor_params['n_im'])
    
        # get shuffled kappas: approximately 1/std**2 where std is in radians
        subj_params['block_order'] = setblock_order(rng, gabor_params['ori_std'])
        if subj_id is not None:
            save_config('gab', subj_id, subj_params)
    
    # establish a pseudorandom order of orientations to cycle through
    # (surprise and current kappa integrated as well)    
    oriparsurps = oriparsurporder(gabor_params['oris'], 
                                  gabor_params['n_im'], 
                                  gabor_params['im_len'], 
                                  gabor_params['reg_len'], 
                                  gabor_params['surp_len'], 
                                  subj_params['block_order'], 
                                  gabor_params['block_len'])
    
    subj_params['windowpar'] = [fieldsize, deg_per_pix]
    subj_params['oriparsurps'] = oriparsurps   
    subj_params['seed'] = seed
    subj_params['subj_id'] = subj_id
    subj_params['sess_id'] = sess_id
    
    # save parameters for subject and session under ./config
    if extrasave:
        save_session_params('gab', subj_id, sess_id, gabor_params, subj_params)
            
    elemPar={ # parameters set by ElementArrayStim
            'units': gabor_params['units'],
            'nElements': gabor_params['n_gabors'], # number of stimuli on screen
            'fieldShape': 'sqr',
            'contrs': 1.0,
            'phases': gabor_params['phase'],
            'sfs': sf,
            'elementTex': 'sin',
            'elementMask': 'gauss',
            'texRes': 48,
            'maskParams': {'sd': gabor_params['sd']},
            'name': 'gabors',
            }
    
    sweepPar={ # parameters to sweep over (0 is outermost parameter)
            'OriParSurp': (oriparsurps, 0), # contains (ori in degrees, surp=0 or 1, kappa)
            'PosSizesAll': ([0, 1, 2, 3], 1), # pass sets of positions and sizes
            }
    
    # Create the stimulus array 
    gabors = OurStims(window, elemPar, fieldsize,
                          possizes=subj_params['possize'])
    
    # Add these attributes for the logs
    gabors.gabor_params = gabor_params
    gabors.subj_params = subj_params
    
    gb = Stimulus(gabors,
                  sweepPar,
                  sweep_length=gabor_params['im_len'], 
                  blank_sweeps=gabor_params['n_im'], # present a blank screen after every set of images
                  start_time=0.0,
                  runs=1,
                  shuffle=False,
                  )
    
    # record attributes from OurStims
    attribs = ['elemParams', 'fieldSize', 'tex', 'colors', 'gabor_params',
               'initScr', 'possizes', 'autoLog', 'units', 'subj_params', 
               'last_frame']
    
    if recordOris:
        attribs.extend(['orisByImg']) # potentially large array
    
    gb.stimParams = {key:gb.stim.__dict__[key] for key in attribs}
    
    return gb
