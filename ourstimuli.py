# -*- coding: utf-8 -*-
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
            self._initParams = __builtins__['dir']()
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

        