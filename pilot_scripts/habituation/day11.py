"""
openscope_credit_assignment_passive_training_pilot_order1_day11.py
This is code to generate and run a 60-minute habituation stimulus for day 11
order is: bricks, gabors, bricks, gabors. No mismatches induced.

Everything is randomized for each animal, except for: ordering of stim types (gabors vs bricks), and positions and sizes of Gabors
Gabor positions and sizes are permanently hard-coded (same for all animals, forever)
Stim type ordering is the same for all animals on a given day, but can vary between days
"""

import Tkinter as tk
import tkSimpleDialog
from psychopy import monitors

# camstim is the Allen Institute stimulus package built on psychopy
from camstim import SweepStim, Stimulus, Foraging
from camstim import Window, Warp

import pickle as pkl
import os
import random
import itertools
import time

# The following code blocks were external files but have been relocated inside the script due
# to how script running works during passive training

### ourstimuli.py code ###

"""
Created on Tue Apr 24 03:35:50 2018

@author: lyra7
"""

from psychopy import event, logging, core
from psychopy.visual import ElementArrayStim
from psychopy.tools.arraytools import val2array
from psychopy.tools.attributetools import attributeSetter, setAttribute

import numpy as np


class OurStims(ElementArrayStim):
    """
    This stimulus class allows what I want it to...
    """

    def __init__(self,
                 win,
                 elemParams,
                 fieldSize, # [wid, hei]
                 direc=0.0, # only supports a single value. Use speed to flip direction of some elements.
                 speed=0.0, # units are sort of arbitrary for now
                 sizeparams=None, # range from which to sample uniformly [min, max]. Height and width sampled separately from same range.
                 possizes=None, # zipped lists of pos and sizes (each same size as nStims) for A, B, C, D, E
                 cyc=None, # number of cycles visible (for Gabors)
                 newpos=[], # frames at which to reinitialize stimulus positions
                 newori=[0], # frames at which to change stimulus orientations (always include 0)
                 orimus=[0.0], # parameter (mu) to use when setting/changing stimulus orientations in deg
                 orikappa=None, # dispersion for sampling orientations (radians)
                 flipdirec=[], # intervals during which to flip direction [start, end (optional)]S
                 flipfrac=0.0, # fraction of elements that should be flipped (0 to 1)
                 duration=-1, # duration in seconds (-1 for no end)
                 currval=None, # pass some values for the first initialization (from flipdirecarray)
                 initScr=True, # initialize elements on the screen
                 fps=60, # frames per second
                 autoLog=None):
    
            #what local vars are defined (these are the init params) for use by __repr__
            self._initParams = locals().keys() # self._initParams = __builtins__['dir']() # jedp had to fix this when hacking
            self._initParams.remove('self')
            
            super(OurStims, self).__init__(win, autoLog=False, **elemParams) #set autoLog at end of init
            
            self._printed = False # useful for printing things once     
            self._needupdate = True # used to initiate any new draws
            
            self.elemParams = elemParams
            
            self._suppress = 0 # number of elements to suppress (keep out of field)
            
            self.setFieldSize(fieldSize)
            self.init_wid = fieldSize[0] * 1.1 # add a little buffer
            self.init_hei = fieldSize[1] * 1.1 # add a little buffer
            
            self.possizes = possizes
            
            if currval is not None:
                self.setSizes(currval[1])
                self._currsize = currval[1]
                self._suppress = self.nElements - currval[2]
                direc = currval[3]
                self._currdirec = currval[3]
            else:
                self._currsize = None
                self._currdirec = None
                self._suppress = 0

            self._sizeparams = sizeparams
            if self._sizeparams is not None:
                self._sizeparams = val2array(sizeparams) #if single value, returns it twice
                self._initSizes(self.nElements)
                
            self._cyc = cyc
            
            if 'sfs' in self.elemParams:
                self.sf = self.elemParams['sfs']
            else:
                self.sf = None
            
            self.setDirec(direc)
            self._stimOriginVar()
            if len(newpos) != 0: # get frames from sec
                newpos = [x * float(fps) for x in newpos]
            self._newpos = newpos
            
            self._flip=0
            self.defaultspeed = speed
            self._speed = np.ones(self.nElements)*speed
            self._flipdirec = flipdirec
            self._randel = None
            self.flipfrac = float(flipfrac)
            self.flipstart = list()
            self.flipend = list()
            if len(self._flipdirec) != 0: # get frames from sec
                self._flipdirec = [[y * float(fps) for y in x] for x in self._flipdirec]
                self._initFlipDirec()
            
            self._newori = [x * float(fps) for x in newori] # get frames from sec
            self._orimus = orimus
            self._orimu = self._orimus[0]
            self._orikappa = orikappa
            self._initOriArrays()
            
            self.duration = duration*float(fps)
            self.initScr = initScr
            
            self._countframes = 0
            self.last_frame = list([self._countframes]) # workaround so the final value can be logged
            
            self.starttime = core.getTime()
            
            if self.defaultspeed != 0.0:
                # initialize list to compile pos_x, pos_y by frame (as int16)
                self.posByFrame = list()
            else: # assuming if no speed, that it is gabors!
                # initialize list to compile orientations at every change (as int16)
                self.orisByImg = list()
                
            
            if possizes is None:
                self._newStimsXY(self.nElements) # update self._coords
                # start recording positions
                
                if self._suppress != 0: # update in case suppression is required
                    self._suppressExtraStims()
                self.setXYs(self._coords)
            
            else: 
                self.setXYs(possizes[0][0])
                self.setSizes(possizes[0][1])
                self._adjustSF(possizes[0][1])
            
            # set autoLog now that params have been initialised
            self.__dict__['autoLog'] = autoLog or autoLog is None and self.win.autoLog
            if self.autoLog:
                logging.exp("Created %s = %s" %(self.name, str(self)))

    def setContrast(self, contrast, operation='', log=None):
        """Usually you can use 'stim.attribute = value' syntax instead,
        but use this method if you need to suppress the log message."""
        self.setContrs(contrast, operation, log)
        self._needupdate = True
    
    def setDirec(self, direc):
        if direc == 'left':
            direc = 180
        elif direc == 'right':
            direc = 0
        elif direc == 'up':
            direc = 90
        elif direc == 'down':
            direc = 270
        
        direc = direc%360.0
        if direc < 0:
            direc = 360 - direc
        self._direc = direc


    def setFlipDirecSize(self, flipdirecarray, operation='', log=None):
        """Not used internally, but just to allows direction flips to occur, 
        new sizes and number of elements, and a new direction to be set.
        """
        # check if switching from reg to mismatch or back, and if so initiate
        # speed update
        if self._flip == 1 and flipdirecarray[0] == 0:
            self._flip=0
            self._update_stim_speed(self._flip)
        elif self._flip == 0 and flipdirecarray[0] == 1:
            self._flip=1
            self._update_stim_speed(self._flip)
        
        newInit = False
        # if new size (and number), change size (and number) and request reinitialization
        if self._currsize != flipdirecarray[1]:
            self._currsize = flipdirecarray[1]
            self.setSizes(flipdirecarray[1])
            if flipdirecarray[2] < self.nElements: # suppress stims?
                self._suppress = self.nElements - flipdirecarray[2]
            elif flipdirecarray[2] == self.nElements:
                self._suppress = 0
            newInit = True
        
        # if new direction, change direction and request reinitialization
        if self._currdirec != flipdirecarray[3]:
            self._currdirec = flipdirecarray[3]
            self.setDirec(flipdirecarray[3])
            self._stimOriginVar()
            newInit = True
        
        # reinitialize
        if newInit is True:
            self.initScr = True
            self._newStimsXY(self.nElements) # updates self._coords
            if self._suppress != 0: # update in case suppression is required
                self._suppressExtraStims()
            self.setXYs(self._coords)
            newInit = False
    
    def _suppressExtraStims(self):
        self._coords[self.nElements-self._suppress:,0] = -self.init_wid/2-self._buff/2
        self._coords[self.nElements-self._suppress:,1] = -self.init_hei/2-self._buff/2
    
    def setOriParSurp(self, oriparsurp, operation='', log=None):
        """Not used internally, but just to allow new sets of orientations to 
        be initialized based on a new mu, new kappa and set whether the 4th set 
        is a surprise (90 deg shift and E locations and sizes).
        """
        
        self._orimu = oriparsurp[0] # set orientation mu (deg)
        self._orikappa = oriparsurp[1] # set orientation kappa (rad)
        
        # set if surprise set
        self._surp = oriparsurp[2]
        
        # set orientations
        self.setOriParams(operation, log)

        # compile orientations at every sweep (as int16)
        self.orisByImg.extend([np.around(self.oris).astype(np.int16)])
        
        
    def setOriKappa(self, ori_kappa, operation='', log=None):
        """Not used internally, but just to allow new sets of orientations to 
        be initialized based on a new mu.
        """
        # update current kappa
        self._orikappa = ori_kappa
        
        # set orientations
        self.setOriParams(operation, log)
    
    def setOriParams(self, operation='', log=None):
        """Initialize new sets of orientations based on parameters using sweeps.
        No need to pass anything as long as self._orimu and self._orikappa are up to date.
        """
        if self._orikappa is None: # no dispersion
            ori_array = self._orimu
        else:
            ori_array_rad = np.random.vonmises(np.deg2rad(self._orimu), self._orikappa, self.nElements)
            ori_array = np.rad2deg(ori_array_rad)
        
        self.setOris(ori_array, operation, log)
        self._needupdate = True
    
    def setSizesAll(self, sizes, operation='', log=None):
        """Set new sizes.
        Pass list (same size as nStims)
        """
        
        self.setSizes(sizes, operation, log)
        self._adjustSF(sizes)
        self._needupdate = True
    
    def _adjustSF(self, sizes):
        # update spatial frequency to fit with set nbr of visible cycles
                
        if self._cyc is not None:
            sfs = self._cyc/sizes
            self.setSfs(sfs)
        
        # if units are pixels, assume sf was provided to elementarray as cyc/pix, 
        # update spatial frequency cyc/stim_wid (which is what elementarray expects)
        if self.sf is not None and self.units == 'pix':
            sfs = [self.sf * x for x in sizes]
            self.setSfs(sfs)
            
            
    def setSizeParams(self, size_params, operation='', log=None):
        """Allows Sweeps to set new sizes based on parameters (same width and height).
        Pass tuple [mu, std (optional)]
        """
        size_params = val2array(size_params) #if single value, returns it twice
        if size_params.size > 2:
            e = 'Too many parameters: ' + str(size_params.size)
            raise ValueError(e)
        elif size_params[0] == size_params[1]: # originally single value, no range
            sizes = np.ones(self.nElements)*size_params[0]
        elif self._sizeparams.size == 2:
            # sample uniformly from range
            sizes = np.random.uniform(size_params[0], size_params[1], self.nElements)
            # use instead if want to initialize width and height independently
#            size_w = np.random.uniform(size_params[0], size_params[1], self.nElements)
#            size_h = np.random.uniform(size_params[0], size_params[1], self.nElements)
#            sizes = zip(size_w, size_h)
        
        self.setSizes(sizes, operation, log)
        self._adjustSF(sizes)
        self._needupdate = True
                
    def setPosAll(self, pos, operation='', log=None):
        """Set new positions.
        Pass list (same size as nStims)
        """
        
        self.setXYs(pos, operation, log)
        self._needupdate = True
    
    def setPosSizesAll(self, combo, operation='', log=None):
        """Allows Sweeps to set which pos/size combo to use where
        0, 1, 2, 3 = A, B, C, D.
        4 is set manually below (E)
        """
        
        # if it's the D (4th set) of a surprise round, switch orientation mu
        # and switch positions to E
        # note: this is done here because the sweep visits the highest level param last
        if self._surp == 1 and combo == 3:
            pos = self.possizes[4][0]
            sizes = self.possizes[4][1]
            self._orimu = (self._orimu + 90)%360
        
        else:
            pos = self.possizes[combo][0]
            sizes = self.possizes[combo][1]
        
        self.setXYs(pos, operation, log)
        self.setSizes(sizes, operation, log)
        self._adjustSF(sizes)
    
        # resample orientations each time new positions and sizes are set
        self.setOriParams(operation, log)
        self._needupdate = True
    
#    def _check_keys(self):
#        for keys in event.getKeys(timeStamped=True):
#            if keys[0]in ['escape', 'q']:
#                self._escape_pressed = True
#                self.win.close()
    
    def _stimOriginVar(self):
        """Get variables relevant to determining where to initialize stimuli
        """
        self._dirRad = self._direc*np.pi/180.0
        
        # set values to calculate new stim origins
        quad = int(self._direc/90.0)%4
        if quad == 0:
            self._buffsign = np.array([1, 1])
        elif quad == 1:
            self._buffsign = np.array([-1, 1])
        elif quad == 2:
            self._buffsign = np.array([-1, -1])
        elif quad == 3:
            self._buffsign = np.array([1, -1])
        basedirRad = np.arctan(1.0*self.init_hei/self.init_wid)
        self._buff = (self.init_wid+self.init_hei)/10 # size of initialization area (10 is arbitrary)
        
        if self._direc%90.0 != 0.0:
            self._ratio = self._dirRad%(np.pi/2)/basedirRad
            self._leng = self.init_wid*self._ratio + self.init_hei/self._ratio
        
        
    def _initFlipDirec(self):      
        self.flipstart = list()
        self.flipend = list()
        
        for i, flip in enumerate(self._flipdirec):
            flip = val2array(flip) #if single value, returns it twice
            if flip.size > 2:
                raise ValueError('Too many parameters.')
            else:
                self.flipstart.append(flip[0])
            if flip[0] == flip[1]: # assume last end possible if same value (originally single value)
                if i == len(self._flipdirec) - 1:
                    self.flipend.append(-1)
                else:
                    self.flipend.append(self._flipdirec[i+1][0] - 1)
            else:
                self.flipend.append(flip[1])
        
    def _newStimsXY(self, newStims):
        
        # initialize on screen (e.g., for first initialization)
        if self.initScr:
            if self._speed[0] == 0.0: # initialize on screen
                coords_wid = np.random.uniform(-self.init_wid/2, self.init_wid/2, newStims)[:, np.newaxis]
                coords_hei = np.random.uniform(-self.init_hei/2, self.init_hei/2, newStims)[:, np.newaxis]
                self._coords = np.concatenate((coords_wid, coords_hei), axis=1)
                return self._coords
        
            else: # initialize on screen and in buffer areas
                if self._direc%180.0 == 0.0: # I stim origin case:
                    coords_wid = np.random.uniform(-self.init_wid/2-self._buff, self.init_wid/2+self._buff, newStims)[:, np.newaxis]
                    coords_hei = np.random.uniform(-self.init_hei/2, self.init_hei/2, newStims)[:, np.newaxis]
                elif self._direc%90.0 == 0.0:
                    coords_wid = np.random.uniform(-self.init_wid/2, self.init_wid/2, newStims)[:, np.newaxis]
                    coords_hei = np.random.uniform(-self.init_hei/2-self._buff, self.init_hei/2+self._buff, newStims)[:, np.newaxis]
                else:
                    coords_wid = np.random.uniform(-self.init_wid/2-self._buff, self.init_wid/2+self._buff, newStims)[:, np.newaxis]
                    coords_hei = np.random.uniform(-self.init_hei/2-self._buff, self.init_hei/2+self._buff, newStims)[:, np.newaxis]
                self._coords = np.concatenate((coords_wid, coords_hei), axis=1)
                self.initScr = False
                return self._coords
        
        # subsequent initializations from L around window (or I if mult of 90)
        elif self._speed[0] != 0.0:            
            # initialize for buffer area
            coords_buff = np.random.uniform(-self._buff, 0, newStims)[:, np.newaxis]
            
            if self._direc%180.0 == 0.0: # I stim origin case
                coords_hei = np.random.uniform(-self.init_hei/2, self.init_hei/2, newStims)[:, np.newaxis]
                coords = np.concatenate((self._buffsign[0]*(coords_buff - self.init_wid/2), coords_hei), axis=1)
            elif self._direc%90.0 == 0.0: # flat I stim origin case
                coords_wid = np.random.uniform(-self.init_wid/2, self.init_wid/2, newStims)[:, np.newaxis]
                coords = np.concatenate((coords_wid, self._buffsign[1]*(coords_buff - self.init_hei/2)), axis=1)
            else:
                coords_main = np.random.uniform(-self._buff, self._leng, newStims)[:, np.newaxis]
                coords = np.concatenate((coords_main, coords_buff), axis=1)
                for i, val in enumerate(coords):
                    if val[0] > self.init_wid*self._ratio: # samples in the height area
                        new_main = val[0] - self.init_wid*self._ratio # for val over wid -> hei
                        coords[i][0] = (val[1] - self.init_wid/2)*self._buffsign[0] 
                        coords[i][1] = new_main*self._ratio - self.init_hei/2
                    elif val[0] < 0.1: # samples in the corner area
                        coords[i][0] = (val[0] - self.init_wid/2)*self._buffsign[0]
                        coords[i][1] = (val[1] - self.init_hei/2)*self._buffsign[1]
                    else: # samples in the width area
                        coords[i][0] = val[0]*self._ratio - self.init_wid/2
                        coords[i][1] = (val[1] - self.init_hei/2)*self._buffsign[1]
            return coords
        
        else:
            raise ValueError('Stimuli have no speed, but are not set to initialize on screen.')
    
    def _update_stim_mov(self):
        """
        The user shouldn't call this - it gets done within draw()
        """
    
        """Find out of bound stims, update positions, get new positions
        """
        
        dead = np.zeros(self.nElements, dtype=bool)
    
        # stims that have exited the field
        dead = dead+(np.abs(self._coords[:,0]) > (self.init_wid/2 + self._buff))
        dead = dead+(np.abs(self._coords[:,1]) > (self.init_hei/2 + self._buff))

        # if there is speed flipping, update stimulus speeds to be flipped
        if len(self._flipdirec) != 0:
            self._update_stim_speed()
        
        if self._randel is not None and dead[self._randel].any():
            dead = self._revive_flipped_stim(dead)
        
        ##update XY based on speed and dir (except for those being suppressed)
        self._coords[:self.nElements-self._suppress,0] += self._speed[:self.nElements-self._suppress]*np.cos(self._dirRad)
        self._coords[:self.nElements-self._suppress,1] += self._speed[:self.nElements-self._suppress]*np.sin(self._dirRad)# 0 radians=East!
        
        #update any dead stims
        if dead.any():
            self._coords[dead,:] = self._newStimsXY(sum(dead))
        
        self.setXYs(self._coords)

    def _update_stim_speed(self, signal=None):        
        # flip speed (i.e., direction) if needed
        if signal==1 or self._countframes in self.flipstart:
            self._randel = np.where(np.random.rand(self.nElements-self._suppress) < self.flipfrac)[0]
            self._speed[self._randel] = -self.defaultspeed
            if self._randel.size == 0: # in case no elements are selected
                self._randel = None
        elif signal==0 or self._countframes in self.flipend:
            if self._randel is not None:
                self._speed[self._randel] = self.defaultspeed
            self._randel = None
    
    def _revive_flipped_stim(self, dead):
        # revive and flip direction on flipped stimuli out of bounds
        self._speed[self._randel[np.where(dead[self._randel])[0]]] = self.defaultspeed
        dead[self._randel]=False
        
        return dead
    
    def _update_stim_ori(self):
        # change orientations
        self.oris = self._oriarrays[self._newori.index(self._countframes)]
    
    def _update_stim_pos(self):
        # get new positions
        self.initScr = True
        self.setXYs(self._newStimsXY(self.nElements))
    
    def _initOriArrays(self):
        """
        Initialize the list of arrays of orientations and set first orientations.
        """
        if len(self._newori) != len(self._orimus):
            raise ValueError('Length of newori must match length of oriparamList.')
        
        self._oriarrays = list()
        for i in self._orimus:
            if self._orikappa is None: # no dispersion
                self._oriarrays.append(np.ones(self.nElements)*i)
            else:
                neworisrad = np.random.vonmises(np.deg2rad(i), self._orikappa, self.nElements)
                self._oriarrays.append(np.rad2deg(neworisrad))
        
        self.oris = self._oriarrays[0]
        
    def _initSizes(self, nStims):
        """
        Initialize the sizes uniformly from range (height and width same).
        """
          
        if self._sizeparams.size > 2:
            raise ValueError('Too many parameters.')
        elif self._sizeparams[0] == self._sizeparams[1]: # assume last end possible if same value (originally single value)
            sizes = np.ones(nStims)*self._sizeparams[0]
        else:
            # sample uniformly from range
            sizes = np.random.uniform(self._sizeparams[0], self._sizeparams[1], nStims)
            # use instead if want to initialize width and height independently
#            size_w = np.random.uniform(self._sizeparams[0], self._sizeparams[1], nStims)
#            size_h = np.random.uniform(self._sizeparams[0], self._sizeparams[1], nStims)
#            sizes = zip(size_w, size_h)
        
        self.sizes = sizes
    
    
    def draw(self, win=None):
        """Draw the stimulus in its relevant window. You must call
        this method after every MyWin.flip() if you want the
        stimulus to appear on that frame and then update the screen
        again.
        """
        
        # update if new positions (newpos)
        if len(self._newpos) > 0 and self._countframes in self._newpos:
            self._update_stim_pos()
        
        # update if new orientations (newori)
        if len(self._newori) > 1 and self._countframes in self._newori[1:]:
            self._update_stim_ori()
        
        # log current posx, posy (rounded to int16) if stim is moving
        # shape is n_frames x n_elements x 2
        if self.defaultspeed != 0.0:
            self.posByFrame.extend([np.around(self._coords).astype(np.int16)])
        
        super(OurStims, self).draw()
        
        # check for end
#        self._check_keys()
#        if self._countframes == self.duration:
#            self.win.close()
        
        # count frames
        self.last_frame[0] = [self._countframes]
        self._countframes += 1
        
        
        # update based on speed
        if self.defaultspeed != 0.0:
            self._update_stim_mov()

### params code ###

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
                'reg_len': [900, 900], # range of durations (sec) for seq of regular sets
                'surp_len': [0, 0], # range of durations (sec) for seq of surprise sets
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
                'reg_len': [449, 449], # range of durations (sec) for reg flow
                'surp_len': [0, 0], # range of durations (sec) for mismatch flow
                'block_len': 449, # duration (sec) of each block (1 per direc/size combo, i.e. 4)
                
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

    
if __name__ == "__main__":
    
    dist = 15.0
    wid = 52.0
    
    # load and record parameters. Leave False.
    promptID = False
    # Save an extra copy of parameters under ./config
    extrasave = False
    
    # Record orientations of gabors at each sweep (LEAVE AS TRUE)
    recordOris = True

    # Record positions of squares at all times (LEAVE AS TRUE)
    recordPos = True
            
    # create a monitor
    monitor = "Gamma1.Luminance50" # monitors.Monitor("testMonitor", distance=dist, width=wid)

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
        # if subj_id is left as None, will skip loading subj config.
        subj_id = None
        sess_id = None
    
    # alternatively to using animal ID, use a seed per animal.
    # Note, animal ID will override seed IF there is a config file for the animal!
    seed = 11 #CHANGE THIS TO MATCH DAY ID
    
    # Create display window
    window = Window(fullscr=True, # Will return an error due to default size. Ignore.
                    monitor=monitor,  # Will be set to a gamma calibrated profile by MPE
                    screen=0,
                    warp=Warp.Spherical
                    )

    # initialize the simuli
    gb = init_run_gabors(window, subj_id, sess_id, seed, extrasave, recordOris)
    sq = init_run_squares(window, subj_id, sess_id, seed, extrasave, recordPos)

    gb_ds = [(900, 1800), (2701, 3601)] #1 x block length for each chunk here
    sq_ds = [(0, 899), (1801,2700)] #2x block length + 1 here
    gb.set_display_sequence(gb_ds);
    sq.set_display_sequence(sq_ds);
        
    ss = SweepStim(window,
                   stimuli=[sq, gb],
                   pre_blank_sec=1,
                   post_blank_sec=1,
                   params={},  # will be set by MPE to work on the rig
                   )

    # add in foraging so we can track wheel, potentially give rewards, etc
    f = Foraging(window=window,
                auto_update=False,
                params={},
                nidaq_tasks={'digital_input': ss.di,
                            'digital_output': ss.do,})  #share di and do with SS
    ss.add_item(f, "foraging")

    # run it
    ss.run()
