"""
This is code to generate and run a 60-minute stimulus for habituation on rig.
Stimuli include gabors only.

Everything is randomized for each session for each animal (positions, sizes and 
orientations of Gabors).
"""

import random
import os
import sys
import copy
import itertools
import time

import numpy as np
import pickle as pkl

from psychopy import monitors, event, logging, core
from psychopy.visual import ElementArrayStim
from psychopy.tools.arraytools import val2array
from psychopy.tools.attributetools import attributeSetter, setAttribute

# camstim is the Allen Institute stimulus package built on psychopy
from camstim import SweepStim, Stimulus
from camstim import Window, Warp


SESSION_PARAMS = {'type': 'hab', # type of session (hab or ophys)
                                   # entering 'hab' will remove any surprises

                  # 'session_dur' is just used to double check that the
                  # components add up to the proper session length.
                  # A message is printed if they do not but no error is thrown.
                  # AMENDED FOR PRODUCTION V2
                  'session_dur': 60*60, # expected total session duration (sec)
                  'pre_blank': 30, # blank before stim starts (sec)
                  'post_blank': 30, # blank after all stims end (sec)
                  'inter_blank': 30, # blank between all stims (sec)
                  'gab_dur': 14.75*60, # duration of gabor block (total=2) (sec)
                  'rot_gab_dur': 14.75*60, #34.25*60
                  'sq_dur': 0*60, # duration of each brick block (total=2) (sec)
                  }

class OurStims(ElementArrayStim):
    """
    This stimulus class allows what I want it to...
    """

    def __init__(self,
                 win,
                 elemParams,
                 fieldSize, # [wid, hei]
                 direc=0.0, # only supports a single value (including 'right' or 'left'). Use speed to flip direction of some elements.
                 speed=0.0, # units are sort of arbitrary for now
                 sizeparams=None, # range from which to sample uniformly [min, max]. Height and width sampled separately from same range.
                 possizes=None, # zipped lists of pos and sizes (each same size as nStims) for A, B, C, D, U
                 cyc=None, # number of cycles visible (for Gabors)
                 rotate = [0], # If object has this attribute, run rotating ctrl gabors
                 newpos=[], # frames at which to reinitialize stimulus positions
                 newori=[0], # frames at which to change stimulus orientations (always include 0)
                 orimus=[0.0], # parameter (mu) to use when setting/changing stimulus orientations in deg
                 orikappa=None, # dispersion for sampling orientations (radians)
                 flipdirec=[], # intervals during which to flip direction [start, end (optional)]S
                 flipfrac=0.0, # fraction of elements that should be flipped (0 to 1)
                 duration=-1, # duration in seconds (-1 for no end)
                 currval=None, # pass some values for the first initialization (from fliparray)
                 initScr=True, # initialize elements on the screen
                 rng=None,
                 fps=60, # frames per second
                 autoLog=None):
    
            #what local vars are defined (these are the init params) for use by __repr__
            self._initParams = locals().keys() # self._initParams = __builtins__['dir']() # jedp had to fix this when hacking
            self._initParams.remove('self')
            
            super(OurStims, self).__init__(win, autoLog=False, **elemParams) #set autoLog at end of init
            
            self._printed = False # useful for printing things once     
            self._needupdate = True # used to initiate any new draws
            
            self.elemParams = elemParams
            
            self.setFieldSize(fieldSize)
            self.init_wid = fieldSize[0] * 1.1 # add a little buffer
            self.init_hei = fieldSize[1] * 1.1 # add a little buffer
            
            self.possizes = possizes

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
            if currval is not None:
                self._flip=currval
            self.defaultspeed = speed
            self._speed = np.ones(self.nElements)*speed
            self._flipdirec = flipdirec
            self._randel = None
            self.rng = rng
            self.flipfrac = float(flipfrac)
            self.flipstart = list()
            self.flipend = list()
            if len(self._flipdirec) != 0: # get frames from sec
                self._flipdirec = [[y * float(fps) for y in x] for x in self._flipdirec]
                self._initFlipDirec()
            
            self._ctrl = True # If True, run rotating ctl gabors
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


    def setFlip(self, fliparray, operation='', log=None):
        """Not used internally, but just to allows direction flips to occur, 
        new sizes and number of elements, and a new direction to be set.
        """
        # check if switching from reg to mismatch or back, and if so initiate
        # speed update
        if self._flip == 1 and fliparray == 0:
            self._flip=0
            self._update_stim_speed(self._flip)
        elif self._flip == 0 and fliparray == 1:
            self._flip=1
            self._update_stim_speed(self._flip)
        
        newInit = False
        # reinitialize
        if newInit is True:
            self.initScr = True
            self._newStimsXY(self.nElements) # updates self._coords
            self.setXYs(self._coords)
            newInit = False
    
    def setOriSurp(self, oriparsurp, operation='', log=None):
        """Not used internally, but just to allow new sets of orientations to 
        be initialized based on a new mu, and set whether the 4th set 
        is a surprise (90 deg shift and U locations and sizes).
        """
        
        self._orimu = oriparsurp[0] # set orientation mu (deg)
        
        # set if surprise set
        self._surp = oriparsurp[1]
        
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
            if self.rng is not None:
                ori_array_rad = self.rng.vonmises(np.deg2rad(self._orimu), self._orikappa, self.nElements)
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
            if self.rng is not None:
                sizes = self.rng.uniform(size_params[0], size_params[1], self.nElements)
            else:
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
        4 is set manually below (U)
        """

        # AMENDED FOR PRODUCTION V2
        # if it's the D (4th set) of a surprise round, either switch orientation mu
        # and switch positions to U (surp type 1) or switch orientation mu and keep D 
        # positions (surp type 2)
        # note: this is done here because the sweep visits the highest level param last

        # Set whether this is a rotating trial or a fixed-mu trial

        #if rotate == 1:
        #    self.ctrl = True
        #else:
        #    self.ctrl = False

        # Determine trial type and rotate mu's accordingly

        if self._ctrl == True: 
            if self._surp != 0 and combo == 3:

                if self._surp == 1:
                    possize_idx = 4
                elif self._surp == 2:
                    possize_idx = 3
                else:
                    raise ValueError("self._surp must be 0, 1 or 2.")

                pos = self.possizes[possize_idx][0]
                sizes = self.possizes[possize_idx][1]
                self._orimu = (self._orimu + 180)%360
            else:
                pos = self.possizes[combo][0]
                sizes = self.possizes[combo][1]
                self._orimu = (self._orimu + combo*90)%360
        
        if self._ctrl == False:
            if self._surp != 0 and combo == 3:
                if self._surp == 1:
                    possize_idx = 4
                elif self._surp == 2:
                    possize_idx = 3
                else:
                    raise ValueError("self._surp must be 0, 1 or 2.")

                pos = self.possizes[possize_idx][0]
                sizes = self.possizes[possize_idx][1]
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
                if self.rng is not None:
                    coords_wid = self.rng.uniform(-self.init_wid/2, self.init_wid/2, newStims)[:, np.newaxis]
                    coords_hei = self.rng.uniform(-self.init_hei/2, self.init_hei/2, newStims)[:, np.newaxis]
                else:
                    coords_wid = np.random.uniform(-self.init_wid/2, self.init_wid/2, newStims)[:, np.newaxis]
                    coords_hei = np.random.uniform(-self.init_hei/2, self.init_hei/2, newStims)[:, np.newaxis]

                self._coords = np.concatenate((coords_wid, coords_hei), axis=1)
                return self._coords
        
            else: # initialize on screen and in buffer areas
                if self._direc%180.0 == 0.0: # I stim origin case:
                    if self.rng is not None:
                        coords_wid = self.rng.uniform(-self.init_wid/2-self._buff, self.init_wid/2+self._buff, newStims)[:, np.newaxis]
                        coords_hei = self.rng.uniform(-self.init_hei/2, self.init_hei/2, newStims)[:, np.newaxis]
                    else:
                        coords_wid = np.random.uniform(-self.init_wid/2-self._buff, self.init_wid/2+self._buff, newStims)[:, np.newaxis]
                        coords_hei = np.random.uniform(-self.init_hei/2, self.init_hei/2, newStims)[:, np.newaxis]
                elif self._direc%90.0 == 0.0:
                    if self.rng is not None:
                        coords_wid = self.rng.uniform(-self.init_wid/2, self.init_wid/2, newStims)[:, np.newaxis]
                        coords_hei = self.rng.uniform(-self.init_hei/2-self._buff, self.init_hei/2+self._buff, newStims)[:, np.newaxis]
                    else:
                        coords_wid = np.random.uniform(-self.init_wid/2, self.init_wid/2, newStims)[:, np.newaxis]
                        coords_hei = np.random.uniform(-self.init_hei/2-self._buff, self.init_hei/2+self._buff, newStims)[:, np.newaxis]
                else:
                    if self.rng is not None:
                        coords_wid = self.rng.uniform(-self.init_wid/2-self._buff, self.init_wid/2+self._buff, newStims)[:, np.newaxis]
                        coords_hei = self.rng.uniform(-self.init_hei/2-self._buff, self.init_hei/2+self._buff, newStims)[:, np.newaxis]
                    else:
                        coords_wid = np.random.uniform(-self.init_wid/2-self._buff, self.init_wid/2+self._buff, newStims)[:, np.newaxis]
                        coords_hei = np.random.uniform(-self.init_hei/2-self._buff, self.init_hei/2+self._buff, newStims)[:, np.newaxis]

                self._coords = np.concatenate((coords_wid, coords_hei), axis=1)
                self.initScr = False
                return self._coords
        
        # subsequent initializations from L around window (or I if mult of 90)
        elif self._speed[0] != 0.0:            
            # initialize for buffer area
            if self.rng is not None:
                coords_buff = self.rng.uniform(-self._buff, 0, newStims)[:, np.newaxis]
            else:
                coords_buff = np.random.uniform(-self._buff, 0, newStims)[:, np.newaxis]
            
            if self._direc%180.0 == 0.0: # I stim origin case
                if self.rng is not None:
                    coords_hei = self.rng.uniform(-self.init_hei/2, self.init_hei/2, newStims)[:, np.newaxis]            
                else:
                    coords_hei = np.random.uniform(-self.init_hei/2, self.init_hei/2, newStims)[:, np.newaxis]
                coords = np.concatenate((self._buffsign[0]*(coords_buff - self.init_wid/2), coords_hei), axis=1)
            elif self._direc%90.0 == 0.0: # flat I stim origin case
                if self.rng is not None:
                    coords_wid = self.rng.uniform(-self.init_wid/2, self.init_wid/2, newStims)[:, np.newaxis]
                else:
                    coords_wid = np.random.uniform(-self.init_wid/2, self.init_wid/2, newStims)[:, np.newaxis]
                coords = np.concatenate((coords_wid, self._buffsign[1]*(coords_buff - self.init_hei/2)), axis=1)
            else:
                if self.rng is not None:
                    coords_main = self.rng.uniform(-self._buff, self._leng, newStims)[:, np.newaxis]
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
        
        ##update XY based on speed and dir
        self._coords[:self.nElements,0] += self._speed[:self.nElements]*np.cos(self._dirRad)
        self._coords[:self.nElements,1] += self._speed[:self.nElements]*np.sin(self._dirRad)# 0 radians=East!
        
        #update any dead stims
        if dead.any():
            self._coords[dead,:] = self._newStimsXY(sum(dead))
        
        self.setXYs(self._coords)

    def _update_stim_speed(self, signal=None):        
        # flip speed (i.e., direction) if needed
        if signal==1 or self._countframes in self.flipstart:
            if self.rng is not None:
                self._randel = np.where(self.rng.rand(self.nElements) < self.flipfrac)[0]
            else:
                self._randel = np.where(np.random.rand(self.nElements) < self.flipfrac)[0]
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
                if self.rng is not None:
                    neworisrad = self.rng.vonmises(np.deg2rad(i), self._orikappa, self.nElements)
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
            if self.rng is not None:
                sizes = self.rng.uniform(self._sizeparams[0], self._sizeparams[1], nStims)
            else:
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


""" Functions to initialize parameters for gabors or squares, load them if necessary,
save them, and create stimuli.

Parameters are set here.
"""

GABOR_PARAMS = {
                ### PARAMETERS TO SET
                'n_gabors': 45,
                # range of size of gabors to sample from (height and width set to same value)
                'size_ran': [10, 20], # in deg (regardless of units below), full-width half-max 
                'sf': 0.04, # spatial freq (cyc/deg) (regardless of units below)
                'phase': 0.25, #value 0-1
                
                'oris': range(0, 360, 45), # orientation means to use (deg) # AMENDED FOR PRODUCTION V2
                'ori_std': 0.25, # orientation st dev to use (rad) (single value)
                
                ###FOR NO SURPRISE, enter [0, 0] for surp_len and [block_len, block_len] for reg_len
                'im_len': 0.3, # duration (sec) of each image (e.g., A)
                'reg_len': [30, 90], # range of durations (sec) for seq of regular sets
                'surp_len': [3, 6], # range of durations (sec) for seq of surprise sets
                'sd': 3, # nbr of st dev (gauss) to edge of gabor (default is 6)
                
                ### Changing these will require tweaking downstream...
                'units': 'pix', # avoid using deg, comes out wrong at least on my computer (scaling artifact? 1.7)
                'n_im': 4 # nbr of images per set (A, B, C, D/U)
                }

SQUARE_PARAMS = {
                ### PARAMETERS TO SET
                'size': 8, # in deg (regardless of units below)
                'speed': 50, # deg/sec (regardless of units below)
                'flipfrac': 0.25, # fraction of elements that should be flipped (0 to 1)
                'density': 0.75,
                'seg_len': 1, # duration (sec) of each segment (somewhat arbitrary)
                
                ###FOR NO SURPRISE, enter [0, 0] for surp_len and [block_len, block_len] for reg_len
                'reg_len': [30, 90], # range of durations (sec) for reg flow
                'surp_len': [2, 4], # range of durations (sec) for mismatch flow
                
                ### Changing these will require tweaking downstream...
                'units': 'pix', # avoid using deg, comes out wrong at least on my computer (scaling artifact? 1.7)
                
                ## ASSUMES THIS IS THE ACTUAL FRAME RATE 
                'fps': 60 # frames per sec, default is 60 in camstim
                }


def winVar(win, units, small_angle_approx=True):
    """Returns width and height of the window in units as tuple.
    Takes window and units.
    Uses small angle approximation, by default # AMENDED FOR PILOT V2
    """
    dist = win.monitor.getDistance()
    width = win.monitor.getWidth()
    
    # get values to convert deg to pixels
    if small_angle_approx:
        pix_wid = float(width)/win.size[0]
        deg_per_pix = np.rad2deg(pix_wid/dist) # about 0.10 if width is 1920
    else:
        deg_wid = np.rad2deg(np.arctan((0.5*width)/dist)) * 2 # about 120
        deg_per_pix = deg_wid/win.size[0] # about 0.06 if width is 1920
    
    if units == 'deg':
        if small_angle_approx:
            raise NotImplementedError('fieldSize in degrees is ill-defined, if using small angle approximation.')
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
    Takes a seeded numpy random number generator, 
    fieldsize, number of elements (e.g., of gabors), 
    and number of images (e.g., A, B, C, D, U).
    """
    coords_wid = rng.uniform(-fieldsize[0]/2, fieldsize[0]/2, [n_im, n_elem])[:, :, np.newaxis]
    coords_hei = rng.uniform(-fieldsize[1]/2, fieldsize[1]/2, [n_im, n_elem])[:, :, np.newaxis]
        
    return np.concatenate((coords_wid, coords_hei), axis=2)

def sizearray(rng, size_ran, n_elem, n_im):
    """Returns array of sizes in range (1D).
    Takes a seeded numpy random number generator, 
    start and end of range, number of elements 
    (e.g., of gabors), and number of images (e.g., A, B, C, D, U).
    """
    if len(size_ran) == 1:
        size_ran = [size_ran[0], size_ran[0]]
    
    sizes = rng.uniform(size_ran[0], size_ran[1], [n_im, n_elem])
    
    return np.around(sizes)

def possizearrays(rng, size_ran, fieldsize, n_elem, n_im):
    """Returns zip of list of pos and sizes for n_elem.
    Takes a seeded numpy random number generator,
    start and end of size range, fieldsize, number of elements (e.g., of 
    gabors), and number of images (e.g., A, B, C, D/U).
    """
    pos = posarray(rng, fieldsize, n_elem, n_im + 1) # add one for U
    sizes = sizearray(rng, size_ran, n_elem, n_im + 1) # add one for U
    
    return zip(pos, sizes)  

def createseqlen(rng, block_segs, regs, surps):
    """
    Arg:
        block_segs: number of segs per block
        regs: duration of each regular set/seg 
        surps: duration of each regular set/seg
    
    Returns:
         list comprising a sublist of regular set durations 
         and a sublist of surprise set durations, both of equal
         lengths.
    
    FYI, this may go on forever for problematic duration ranges.
    
    """
    minim = regs[0]+surps[0] # smallest possible reg + surp set
    maxim = regs[1]+surps[1] # largest possible reg + surp set
    
    # sample a few lengths to start, without going over block length
    n = int(block_segs/(regs[1]+surps[1]))
    # mins and maxs to sample from
    reg_block_len = rng.randint(regs[0], regs[1] + 1, n).tolist()
    surp_block_len = rng.randint(surps[0], surps[1] + 1, n).tolist()
    reg_sum = sum(reg_block_len)
    surp_sum = sum(surp_block_len)
    
    while reg_sum + surp_sum < block_segs:
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
            new_reg_block_len = rng.randint(reg_min, reg_max + 1)
            new_surp_block_len = int(rem - new_reg_block_len)
        
        # Otherwise just get a new value
        else:
            new_reg_block_len = rng.randint(regs[0], regs[1] + 1)
            new_surp_block_len = rng.randint(surps[0], surps[1] + 1)
 
        reg_block_len.append(new_reg_block_len)
        surp_block_len.append(new_surp_block_len)
        
        reg_sum = sum(reg_block_len)
        surp_sum = sum(surp_block_len)     

    return [reg_block_len, surp_block_len]

def orisurpgenerator(rng, oris, block_segs, surp=1): # AMENDED FOR PRODUCTION V2
    """
    Args:
        oris: mean orientations
        block_segs: list comprising a sublist of regular set durations 
                    and a sublist of surprise set durations, both of equal
                    lengths
    
    Optional:
        surp: type of surprise to use (1, 2, "both")

    Returns:
        zipped lists, one of mean orientation, and one of surprise value 
        for each image sequence.
    
    FYI, this may go on forever for problematic duration ranges.
    """
    n_oris = float(len(oris)) # number of orientations

    # preselect surprise types (1: U + 90 or 2: D + 90) # AMENDED FOR PRODUCTION V2
    if surp == "both":
        surp_types = np.ones(len(block_segs[1])) * 2
        surp_types[: len(surp_types) // 2] = 1
        rng.shuffle(surp_types)
    elif surp == 1:
        surp_types = np.ones(len(block_segs[1]))
    elif surp == 2:
        surp_types = np.ones(len(block_segs[1])) * 2
    else:
        raise ValueError("surp value {} not recognized. Should be 1, 2 or 'both'.".format(surp))

    orilist = list()
    surplist = list()
    for i, (reg, surp) in enumerate(zip(block_segs[0], block_segs[1])):     
        # deal with reg
        oriadd = list()
        for _ in range(int(np.ceil(reg/n_oris))):
            rng.shuffle(oris) # in place
            oriadd.extend(oris[:])
        oriadd = oriadd[:reg] # chop!
        surpadd = np.zeros_like(oriadd) # keep track of not surprise (0)
        orilist.extend(oriadd)
        surplist.extend(surpadd)
        
        # deal with surp
        oriadd = list()
        for _ in range(int(np.ceil(surp/n_oris))):
            rng.shuffle(oris) # in place
            oriadd.extend(oris[:])
        oriadd = oriadd[:surp]

        # AMENDED FOR PRODUCTION V2
        surpadd = np.ones_like(oriadd) * surp_types[i] # keep track of surprise (1 or 2)
        orilist.extend(oriadd)
        surplist.extend(surpadd)

    return zip(orilist, surplist)


def orisurporder(rng, oris, n_im, im_len, reg_len, surp_len, block_len, surp=1): # AMENDED FOR PRODUCTION V2
    """
    Args:
        oris: orientations
        n_im: number of images (e.g., A, B, C, D/U)
        im_len: duration of each image
        reg_len: range of durations of reg seq
        surp_len: range of durations of surp seq
        block_len: duration of the block (single value)

    Optional:
        surp: type of surprise to use (1, 2, "both")
    
    Returns:
        zipped lists, one of mean orientation, and one of surprise value 
        for each image sequence.
    """
    set_len = im_len * (n_im + 1.0) # duration of set (incl. one blank per set)
    reg_sets = [x/set_len for x in reg_len] # range of nbr of sets per regular seq, e.g. 20-60
    surp_sets = [x/set_len for x in surp_len] # range of nbr of sets per surprise seq, e.g., 2-4
    block_segs = block_len/set_len # nbr of segs per block, e.g. 680
    
    # get seq lengths
    block_segs = createseqlen(rng, block_segs, reg_sets, surp_sets)
    
    # from seq durations get zipped lists, one of oris, one of surp=0, 1 or 2
    # for each image
    orisurplist = orisurpgenerator(rng, oris, block_segs, surp=surp)

    return orisurplist


def flipgenerator(flipcode, segperblock):
    """
    Args:
        flipcode: should be [0, 1] with 0 for regular flow and 1 for mismatch 
                  flow.
        segperblock: list comprising a sublist of regular set durations 
                     and a sublist of surprise set durations, both of equal
                     lengths.
    
    Returns:
        a list of surprise value (0 or 1), for each segment 
        (each 1s for example).
    
    """

    fliplist = list()
    for _, (reg, surp) in enumerate(zip(segperblock[0], segperblock[1])):
        regadd = [flipcode[0]] * reg
        surpadd = [flipcode[1]] * surp
        fliplist.extend(regadd)
        fliplist.extend(surpadd)
        
    return fliplist


def fliporder(rng, seg_len, reg_len, surp_len, block_len):
    """ 
    Args:
        seg_len: duration of each segment (arbitrary minimal time segment)
        reg_len: range of durations of reg seq
        surp_len: range of durations of surp seq
        block_len: duration of each block (single value)
    
    Returns:
        a zipped list of sublists with the surprise value (0 or 1), size, 
        number of squares, direction for each kappa value
        and surprise value (0 or 1) for each segment (each 1s for example).
    
    """

    reg_segs = [x/seg_len for x in reg_len] # range of nbr of segs per regular seq, e.g. 30-90
    surp_segs = [x/seg_len for x in surp_len] # range of nbr of segs per surprise seq, e.g., 2-4
    block_segs = block_len/seg_len # nbr of segs per block, e.g. 540
    
    # get seg lengths
    segperblock = createseqlen(rng, block_segs, reg_segs, surp_segs)
    
    # flip code: [reg, flip]
    flipcode = [0, 1]
    
    # from seq durations get a list each kappa or (ori, surp=0 or 1)
    fliplist = flipgenerator(flipcode, segperblock)

    return fliplist


def init_run_squares(window, direc, session_params, recordPos, square_params=SQUARE_PARAMS):

    # get fieldsize in units and deg_per_pix
    fieldsize, deg_per_pix = winVar(window, square_params['units'])
    
    # convert values to pixels if necessary
    if square_params['units'] == 'pix':
        size = np.around(square_params['size']/deg_per_pix)
        speed = square_params['speed']/deg_per_pix
    else:
        size = square_params['size']
        speed = square_params['speed']
    
    # convert speed for units/s to units/frame
    speed = speed/square_params['fps']
    
    # to get actual frame rate
    act_fps = window.getMsPerFrame() # returns average, std, median
    
    # calculate number of squares for each square size
    n_Squares = int(square_params['density']*fieldsize[0]*fieldsize[1] \
                /np.square(size))
    
    # check whether it is a habituation session. If so, remove any surprise
    # segments
    if session_params['type'] == 'hab':
        square_params['reg_len'] = [session_params['sq_dur'], session_params['sq_dur']]
        square_params['surp_len'] = [0, 0]

    # establish a pseudorandom array of when to switch from reg to mismatch
    # flow and back    
    fliparray = fliporder(session_params['rng'],
                          square_params['seg_len'],
                          square_params['reg_len'], 
                          square_params['surp_len'],
                          session_params['sq_dur'])
    
    session_params['windowpar'] = [fieldsize, deg_per_pix]
    
    elemPar={ # parameters set by ElementArrayStim
            'units': square_params['units'],
            'nElements': n_Squares,
            'sizes': size,
            'fieldShape': 'sqr',
            'contrs': 1.0,
            'elementTex': None,
            'elementMask': None,
            'name': 'bricks',
            }
    
    sweepPar={ # parameters to sweep over (0 is outermost parameter)
            'Flip': (fliparray, 0),
            }
    
    # Create the stimulus array
    squares = OurStims(window, elemPar, fieldsize, direc=direc, speed=speed,
                         flipfrac=square_params['flipfrac'],
                         currval=fliparray[0],
                         rng=session_params['rng'])
    
    # Add these attributes for the logs
    squares.square_params = square_params
    squares.actual_fps = act_fps
    squares.direc = direc
    
    sq = Stimulus(squares,
                  sweepPar,
                  sweep_length=square_params['seg_len'], 
                  start_time=0.0,
                  runs=1,
                  shuffle=False,
                  )

    # record attributes from OurStims
    if recordPos: # potentially large arrays
        session_params['posbyframe'] = squares.posByFrame
    
    # add more attribute for the logs
    squares.session_params = session_params

    # record attributes from OurStims
    attribs = ['elemParams', 'fieldSize', 'tex', 'colors', 'square_params',
               'initScr', 'autoLog', 'units','actual_fps', 'direc', 
               'session_params', 'last_frame']
    
    sq.stim_params = {key:sq.stim.__dict__[key] for key in attribs}
    
    return sq

def init_run_gabors(window, session_params, recordOris, gabor_params=GABOR_PARAMS, surp=1): # AMENDED FOR PRODUCTION V2

    # get fieldsize in units and deg_per_pix
    fieldsize, deg_per_pix = winVar(window, gabor_params['units'])
    
    # convert values to pixels if necessary
    if gabor_params['units'] == 'pix':
        size_ran = [np.around(x/deg_per_pix) for x in gabor_params['size_ran']]
        sf = gabor_params['sf']*deg_per_pix
    else:
        size_ran = gabor_params['size_ran']
        sf = gabor_params['sf']
    
    # get kappa from orientation std
    kap = 1.0/gabor_params['ori_std']**2

    # size is set as where gauss std=3 on each side (so size=6 std). 
    # Convert from full-width half-max
    gabor_modif = 1.0/(2*np.sqrt(2*np.log(2))) * gabor_params['sd']
    size_ran = [np.around(x * gabor_modif) for x in size_ran]
    
    # get positions and sizes for each image (A, B, C, D, U)
    if 'possize' not in session_params.keys():
        session_params['possize'] = possizearrays(session_params['rng'],
                                                size_ran, 
                                                fieldsize, 
                                                gabor_params['n_gabors'], 
                                                gabor_params['n_im'])
    
    # check whether it is a habituation session. If so, remove any surprise
    # segments
    if session_params['type'] == 'hab':
        gabor_params['reg_len'] = [session_params['gab_dur'], session_params['gab_dur']]
        gabor_params['surp_len'] = [0, 0]

    # establish a pseudorandom order of orientations to cycle through
    # (surprise integrated as well)    
    orisurps = orisurporder(session_params['rng'],
                            gabor_params['oris'], 
                            gabor_params['n_im'], 
                            gabor_params['im_len'], 
                            gabor_params['reg_len'], 
                            gabor_params['surp_len'],
                            session_params['gab_dur'],
                            surp=surp)
    
    session_params['windowpar'] = [fieldsize, deg_per_pix]
            
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
            'OriSurp': (orisurps, 0), # contains (ori in degrees, surp=0, 1 (U) or 2 (D surp))  # AMENDED FOR PRODUCTION V2
            'PosSizesAll': ([0, 1, 2, 3], 1), # pass sets of positions and sizes
            }
    
    # Create the stimulus array 
    gabors = OurStims(window, elemPar, fieldsize, orikappa=kap,
                          possizes=session_params['possize'],
                          rng=session_params['rng'])
    
    # Add these attributes for the logs
    gabors.gabor_params = gabor_params
    gabors.surp = surp
    gabors._ctrl = False
    
    gb = Stimulus(gabors,
                  sweepPar,
                  sweep_length=gabor_params['im_len'], 
                  blank_sweeps=gabor_params['n_im'], # present a blank screen after every set of images
                  start_time=0.0,
                  runs=1,
                  shuffle=False,
                  )
    
    # record attributes from OurStims
    if recordOris: # potentially large array
        session_params['orisbyimg'] = gabors.orisByImg
    
    # add more attribute for the logs
    gabors.session_params = session_params

    attribs = ['elemParams', 'fieldSize', 'tex', 'colors', 'gabor_params',
               'initScr', 'autoLog', 'units', 'session_params', 'last_frame', 
               'surp']
    
    gb.stim_params = {key:gb.stim.__dict__[key] for key in attribs}
    
    return gb

def init_rotate_gabors(window, session_params, recordOris, gabor_params=GABOR_PARAMS, surp=1): # AMENDED FOR PRODUCTION V2

    # get fieldsize in units and deg_per_pix
    fieldsize, deg_per_pix = winVar(window, gabor_params['units'])
    
    # convert values to pixels if necessary
    if gabor_params['units'] == 'pix':
        size_ran = [np.around(x/deg_per_pix) for x in gabor_params['size_ran']]
        sf = gabor_params['sf']*deg_per_pix
    else:
        size_ran = gabor_params['size_ran']
        sf = gabor_params['sf']
    
    # get kappa from orientation std
    kap = 1.0/gabor_params['ori_std']**2

    # size is set as where gauss std=3 on each side (so size=6 std). 
    # Convert from full-width half-max
    gabor_modif = 1.0/(2*np.sqrt(2*np.log(2))) * gabor_params['sd']
    size_ran = [np.around(x * gabor_modif) for x in size_ran]
    
    # get positions and sizes for each image (A, B, C, D, U)
    if 'possize' not in session_params.keys():
        session_params['possize'] = possizearrays(session_params['rng'],
                                                size_ran, 
                                                fieldsize, 
                                                gabor_params['n_gabors'], 
                                                gabor_params['n_im'])
    
    # check whether it is a habituation session. If so, remove any surprise
    # segments
    if session_params['type'] == 'hab':
        gabor_params['reg_len'] = [session_params['rot_gab_dur'], session_params['rot_gab_dur']]
        gabor_params['surp_len'] = [0, 0]

    # establish a pseudorandom order of orientations to cycle through
    # (surprise integrated as well)    
    orisurps = orisurporder(session_params['rng'],
                            gabor_params['oris'], 
                            gabor_params['n_im'], 
                            gabor_params['im_len'], 
                            gabor_params['reg_len'], 
                            gabor_params['surp_len'],
                            session_params['rot_gab_dur'],
                            surp=surp)
    
    session_params['windowpar'] = [fieldsize, deg_per_pix]
            
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
            'OriSurp': (orisurps, 0), # contains (ori in degrees, surp=0, 1 (U) or 2 (D surp))  # AMENDED FOR PRODUCTION V2
            'PosSizesAll': ([0, 1, 2, 3], 1), # pass sets of positions and sizes
            }

    list(sweepPar['PosSizesAll'])

    # Create the stimulus array 
    gabors = OurStims(window, elemPar, fieldsize, orikappa=kap,
                          possizes=session_params['possize'],
                          rng=session_params['rng'])

    gabors._ctrl = True
    
    # Add these attributes for the logs
    gabors.gabor_params = gabor_params
    gabors.surp = surp
    
    rgb = Stimulus(gabors,
                  sweepPar,
                  sweep_length=gabor_params['im_len'], 
                  blank_sweeps=gabor_params['n_im'], # present a blank screen after every set of images
                  start_time=0.0,
                  runs=1,
                  )
    
    # record attributes from OurStims
    if recordOris: # potentially large array
        session_params['orisbyimg'] = gabors.orisByImg
    
    # add more attribute for the logs
    gabors.session_params = session_params

    attribs = ['elemParams', 'fieldSize', 'tex', 'colors', 'gabor_params',
               'initScr', 'autoLog', 'units', 'session_params', 'last_frame', 
               'surp']
    
    rgb.stim_params = {key:rgb.stim.__dict__[key] for key in attribs}
    
    return rgb
    
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
    SESSION_PARAMS['seed'] = random.choice(range(0, 48000))
    # SESSION_PARAMS['seed'] = # override by setting seed manually
    SESSION_PARAMS['rng'] = np.random.RandomState(SESSION_PARAMS['seed'])
    
    # Create display window
    window = Window(fullscr=True, # Will return an error due to default size. Ignore.
                    monitor=monitor,  # Will be set to a gamma calibrated profile by MPE
                    screen=0,
                    warp=Warp.Spherical
                    )

    # check session params add up to correct total time
    # AMENDED FOR PRODUCTION V2
    n_stim = (SESSION_PARAMS['sq_dur'] != 0) * 2 + (SESSION_PARAMS['gab_dur'] != 0) * 2 + (SESSION_PARAMS['rot_gab_dur'] != 0) * 2
    tot_calc = SESSION_PARAMS['pre_blank'] + SESSION_PARAMS['post_blank'] + \
               (n_stim - 1)*SESSION_PARAMS['inter_blank'] + 2*SESSION_PARAMS['gab_dur'] + \
               2*SESSION_PARAMS['sq_dur'] + 2*SESSION_PARAMS['rot_gab_dur']
    if tot_calc != SESSION_PARAMS['session_dur']:
        print('Session should add up to {} s, but adds up to {} s.'
              .format(SESSION_PARAMS['session_dur'], tot_calc))

    # initialize the stimuli # AMENDED FOR PRODUCTION V2
    stim_order = []
    sq_order = []
    gab_order = []
    rot_gab_order = []
    if SESSION_PARAMS['gab_dur'] != 0:
        gb_1 = init_run_gabors(window, SESSION_PARAMS.copy(), recordOris, surp=1)
        
        # share positions and sizes
        gb_2_session_params = SESSION_PARAMS.copy()
        gb_2_session_params['possize'] = gb_1.stim_params['session_params']['possize']
        gb_2 = init_run_gabors(window, gb_2_session_params, recordOris, surp=2)
        
        stim_order.append('g')
        gab_order = [1, 2]
    if SESSION_PARAMS['rot_gab_dur'] != 0:
        rgb_1 = init_rotate_gabors(window, SESSION_PARAMS.copy(), recordOris, surp=1)
        
        # share positions and sizes from original Gabors. Keeps possize the same
        rgb_2 = init_rotate_gabors(window, gb_2_session_params, recordOris, surp=2)
        
        stim_order.append('rg')
        rot_gab_order = [1, 2]
    if SESSION_PARAMS['sq_dur'] != 0:
        sq_left = init_run_squares(window, 'left', SESSION_PARAMS.copy(), recordPos)
        sq_right = init_run_squares(window, 'right', SESSION_PARAMS.copy(), recordPos)
        stim_order.append('b')
        sq_order = ['l', 'r']

    # initialize display order and times # AMENDED FOR PRODUCTION V2
    SESSION_PARAMS['rng'].shuffle(stim_order) # in place shuffling
    SESSION_PARAMS['rng'].shuffle(sq_order) # in place shuffling
    SESSION_PARAMS['rng'].shuffle(gab_order) # in place shuffling
    SESSION_PARAMS['rng'].shuffle(rot_gab_order) # in place shuffling

    start = SESSION_PARAMS['pre_blank'] # initial blank
    stimuli = []
    for i in stim_order:
        if i == 'g':
            for j in gab_order:
                if j == 1:
                    stimuli.append(gb_1)
                    gb_1.set_display_sequence([(start, start+SESSION_PARAMS['gab_dur'])])
                elif j == 2:
                    stimuli.append(gb_2)
                    gb_2.set_display_sequence([(start, start+SESSION_PARAMS['gab_dur'])])
                # update the new starting point for the next stim
                start += SESSION_PARAMS['gab_dur'] + SESSION_PARAMS['inter_blank'] 
        elif i == 'rg':
            for j in rot_gab_order:
                if j == 1:
                    stimuli.append(rgb_1)
                    rgb_1.set_display_sequence([(start, start+SESSION_PARAMS['rot_gab_dur'])])
                elif j == 2:
                    stimuli.append(rgb_2)
                    rgb_2.set_display_sequence([(start, start+SESSION_PARAMS['rot_gab_dur'])])
                # update the new starting point for the next stim
                start += SESSION_PARAMS['rot_gab_dur'] + SESSION_PARAMS['inter_blank'] 
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
