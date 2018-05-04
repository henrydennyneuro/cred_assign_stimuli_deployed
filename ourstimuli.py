# -*- coding: utf-8 -*-
"""
Created on Tue Apr 24 03:35:50 2018

@author: lyra7
"""

from psychopy import event, logging
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
                 elemarr,
                 fieldSize, # [wid, hei]
                 units='pix',
                 direc=0.0, # only supports a single value. Use speed to flip direction of some elements.
                 speed=0.0, # units are sort of arbitrary for now
                 sizeparams=None, # range from which to sample uniformly [min, max]. Height and width sampled separately from same range.
                 possizes=None, # zipped lists of pos and sizes (each same size as nStims) for A, B, C, D, E
                 sf=None, # if spatial freq is specific in cycles/pix (as elementarray does not use this)
                 cyc=None, # number of cycles visible (for Gabors)
                 newpos=[], # frames at which to reinitialize stimulus positions
                 newori=[0], # frames at which to change stimulus orientations (always include 0)
                 orimus=[0.0], # parameter (mu) to use when setting/changing stimulus orientations in deg
                 orikappa=0, # dispersion for sampling orientations (radians)
                 flipdirec=[], # intervals during which to flip direction [start, end (optional)]S
                 flipfrac=1.0, # fraction of elements that should be flipped (0 to 1)
                 duration=-1, # duration in frames (-1 for no end)
                 initScr=True, # initialize elements on the screen
                 fps=60, # frames per second
                 contrast=1.0,
                 name='',
                 autoLog=None):
    
            #what local vars are defined (these are the init params) for use by __repr__
            self._initParams = __builtins__['dir']()
            self._initParams.remove('self')
            
            self.elemarr = elemarr
            self.nStims = self.elemarr.nElements
            
            super(OurStims, self).__init__(win, units=units, name=name, autoLog=False)#set autoLog at end of init
            
            self.elemarr.setContrs(contrast)
            
            self.elemarr.setFieldSize(fieldSize)
            self.units = units
            self.init_wid = fieldSize[0]
            self.init_hei = fieldSize[1]
            
            self.possizes = possizes
            
            self.sizeparams = sizeparams
            if self.sizeparams is not None:
                self.sizeparams = val2array(sizeparams) #if single value, returns it twice
                self._initSizes(self.nStims)
                
            self.cyc = cyc      
            self.sf = sf
            
            if self.sf is not None and self.units == 'deg':
                self.elemarr.setSfs(self.sf)
            
            self.setDirec(direc)
            self._stimOriginVar()
            if len(newpos) != 0: # get frames from sec
                newpos = [x * float(fps) for x in newpos]
            self.newpos = newpos
            
            self.defaultspeed = speed
            self.speed = np.ones(self.nStims)*speed
            self.flipdirec = flipdirec
            if len(self.flipdirec) != 0: # get frames from sec
                self.flipdirec = [[y * float(fps) for y in x] for x in self.flipdirec]
                self.flipfrac = float(flipfrac)
                self.randel = None
                self._initFlipDirec()
            
            self.newori = [x * float(fps) for x in newori] # get frames from sec
            self.orimus = orimus
            self.orimu = self.orimus[0]
            self.orikappa = orikappa
            self._initOriArrays()
            
            self.duration = duration*float(fps)
            self.initScr = initScr
            
            self.countframes = 0
            self.printed = False # useful for printing things once
            
            self.elemarr.setXYs(self._newStimsXY(self.nStims))
    
            # set autoLog now that params have been initialised
            self.__dict__['autoLog'] = autoLog or autoLog is None and self.win.autoLog
            if self.autoLog:
                logging.exp("Created %s = %s" %(self.name, str(self)))

    def setContrast(self, contrast, operation='', log=None):
        """Usually you can use 'stim.attribute = value' syntax instead,
        but use this method if you need to suppress the log message."""
        self.elemarr.setContrs(contrast, operation, log)
    
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
        self.direc = direc
    
    def setOriParSurp(self, oriparsurp, operation='', log=None):
        """Not used internally, but just to allow new sets of orientations to 
        be initialized based on a new mu, new kappa and set whether the 4th set 
        is a surprise (90 deg shift and E locations and sizes).
        """
        
        self.orimu = oriparsurp[0] # set orientation mu (deg)
        self.orikappa = oriparsurp[1] # set orientation kappa (rad)
        
        # check if surprise set
        if oriparsurp[2] == 0: 
            self.surp = 0
        elif oriparsurp[2] == 1:
            self.surp = 1
        
        # set orientations
        self.setOriParams(operation, log)
        
        
    def setOriKappa(self, ori_kappa, operation='', log=None):
        """Not used internally, but just to allow new sets of orientations to 
        be initialized based on a new mu.
        """
        # update current kappa
        self.orikappa = ori_kappa
        
        # set orientations
        self.setOriParams(operation, log)
    
    def setOriParams(self, operation='', log=None):
        """Not used internally, but just to allow new sets of orientations to 
        be initialized based on parameters using sweeps.
        No need to pass anything as long as self.orimy and self.orikappa are updated.
        """
        if self.orikappa == 0: # no dispersion
            ori_array = np.ones(self.nStims)*self.orimu
        else:
            # takes radians
            ori_array_rad = np.random.vonmises(np.deg2rad(self.orimu), self.orikappa, self.nStims)
            ori_array = np.rad2deg(ori_array_rad)
        
        self.elemarr.setOris(ori_array, operation, log)
    
    def setSizesAll(self, sizes, operation='', log=None):
        """Set new sizes.
        Pass list (same size as nStims)
        """
        
        self.elemarr.setSizes(sizes, operation, log)
        self.adjustSF(sizes)
    
    def adjustSF(self, sizes):
        # update spatial frequency to fit with set nbr of visible cycles
        
        if self.cyc is not None:
            sfs = self.cyc/sizes
            self.elemarr.setSfs(sfs)
        
        # if units are pixels and sf is provided, update spatial frequency 
        # cyc/stim_wid (which is what elementarray expects)
        if self.sf is not None and self.units == 'pix':
            sfs = [self.sf * x for x in sizes]
            self.elemarr.setSfs(sfs)
            
            
    def setSizeParams(self, size_params, operation='', log=None):
        """Allows Sweeps to set new sizes based on parameters (same width and height).
        Pass tuple [mu, std (optional)]
        """
        size_params = val2array(size_params) #if single value, returns it twice
        if size_params.size > 2:
            e = 'Too many parameters: ' + str(size_params.size)
            raise ValueError(e)
        elif size_params[0] == size_params[1]: # originally single value, no range
            sizes = np.ones(self.nStims)*size_params[0]
        elif self.sizeparams.size == 2:
            # sample uniformly from range
            sizes = np.random.uniform(size_params[0], size_params[1], self.nStims)
            # use instead if want to initialize width and height independently
#            size_w = np.random.uniform(size_params[0], size_params[1], self.nStims)
#            size_h = np.random.uniform(size_params[0], size_params[1], self.nStims)
#            sizes = zip(size_w, size_h)
        
        self.elemarr.setSizes(sizes, operation, log)
        self.adjustSF(sizes)
            
                
    def setPosAll(self, pos, operation='', log=None):
        """Set new positions.
        Pass list (same size as nStims)
        """
        
        self.elemarr.setXYs(pos, operation, log)
    
    def setPosSizesAll(self, combo, operation='', log=None):
        """Allows Sweeps to set which pos/size combo to use where
        0, 1, 2, 3 = A, B, C, D.
        4 is set manually below
        """
        pos = self.possizes[combo][0]
        sizes = self.possizes[combo][1]
        
        self.elemarr.setXYs(pos, operation, log)
        self.elemarr.setSizes(sizes, operation, log)
        self.adjustSF(sizes)
        
        # if it's the D (3rd set) of a surprise round, switch orientation mu
        # and switch positions to E
        # note: this is done here because the sweep visits the highest level param last
        if self.surp == 1 and combo == 3:
            pos = self.possizes[4][0]
            size = self.possizes[4][1]
            self.elemarr.setXYs(pos, operation, log)
            self.elemarr.setSizes(size, operation, log)
            self.adjustSF(size)
            self.orimu = (self.orimu + 90)%360
            self.countsets = 0
        
        # resample orientations each time new positions and sizes are set
        self.setOriParams(operation, log)
    
    def _check_keys(self):
        for keys in event.getKeys(timeStamped=True):
            if keys[0]in ['escape', 'q']:
                self.escape_pressed = True
                self.win.close()
    
    def _stimOriginVar(self):
        """Get variables relevant to determining where to initialize stimuli
        """
        self.dirRad = self.direc*np.pi/180.0
        
        # set values to calculate new stim origins
        quad = int(self.direc/90.0)%4
        if quad == 0:
            self.buffsign = np.array([1, 1])
        elif quad == 1:
            self.buffsign = np.array([-1, 1])
        elif quad == 2:
            self.buffsign = np.array([-1, -1])
        elif quad == 3:
            self.buffsign = np.array([1, -1])
        basedirRad = np.arctan(1.0*self.init_hei/self.init_wid)
        self.buff = (self.init_wid+self.init_hei)/20 # size of initialization area (15 is arbitrary)
        
        if self.direc%90.0 != 0.0:
            self.ratio = self.dirRad%(np.pi/2)/basedirRad
            self.leng = self.init_wid*self.ratio + self.init_hei/self.ratio
        
        
    def _initFlipDirec(self):      
        self.flipstart = list()
        self.flipend = list()
        
        for i, flip in enumerate(self.flipdirec):
            flip = val2array(flip) #if single value, returns it twice
            if flip.size > 2:
                raise ValueError('Too many parameters.')
            else:
                self.flipstart.append(flip[0])
            if flip[0] == flip[1]: # assume last end possible if same value (originally single value)
                if i == len(self.flipdirec) - 1:
                    self.flipend.append(-1)
                else:
                    self.flipend.append(self.flipdirec[i+1][0] - 1)
            else:
                self.flipend.append(flip[1])
        
    def _newStimsXY(self, newStims):
        
        # initialize on screen (e.g., for first initialization)
        if self.initScr:
            if self.speed[0] == 0.0: # initialize on screen
                coords_wid = np.random.uniform(-self.init_wid/2, self.init_wid/2, newStims)[:, np.newaxis]
                coords_hei = np.random.uniform(-self.init_hei/2, self.init_hei/2, newStims)[:, np.newaxis]
                self.coords = np.concatenate((coords_wid, coords_hei), axis=1)
                return self.coords
        
            else: # initialize on screen and in buffer areas
                if self.direc%180.0 == 0.0: # I stim origin case:
                    coords_wid = np.random.uniform(-self.init_wid/2-self.buff, self.init_wid/2+self.buff, newStims)[:, np.newaxis]
                    coords_hei = np.random.uniform(-self.init_hei/2, self.init_hei/2, newStims)[:, np.newaxis]
                elif self.direc%90.0 == 0.0:
                    coords_wid = np.random.uniform(-self.init_wid/2, self.init_wid/2, newStims)[:, np.newaxis]
                    coords_hei = np.random.uniform(-self.init_hei/2-self.buff, self.init_hei/2+self.buff, newStims)[:, np.newaxis]
                else:
                    coords_wid = np.random.uniform(-self.init_wid/2-self.buff, self.init_wid/2+self.buff, newStims)[:, np.newaxis]
                    coords_hei = np.random.uniform(-self.init_hei/2-self.buff, self.init_hei/2+self.buff, newStims)[:, np.newaxis]
                self.coords = np.concatenate((coords_wid, coords_hei), axis=1)
                self.initScr = False
                return self.coords
        
        # subsequent initializations from L around window (or I if mult of 90)
        elif self.speed[0] != 0.0:            
            # iniialize for buffer area
            coords_buff = np.random.uniform(-self.buff, 0, newStims)[:, np.newaxis]
            
            if self.direc%180.0 == 0.0: # I stim origin case
                coords_hei = np.random.uniform(-self.init_hei/2, self.init_hei/2, newStims)[:, np.newaxis]
                coords = np.concatenate((self.buffsign[0]*(coords_buff - self.init_wid/2), coords_hei), axis=1)
            elif self.direc%90.0 == 0.0: # flat I stim origin case
                coords_wid = np.random.uniform(-self.init_wid/2, self.init_wid/2, newStims)[:, np.newaxis]
                coords = np.concatenate((coords_wid, self.buffsign[1]*(coords_buff - self.init_hei/2)), axis=1)
            else:
                coords_main = np.random.uniform(-self.buff, self.leng, newStims)[:, np.newaxis]
                coords = np.concatenate((coords_main, coords_buff), axis=1)
                for i, val in enumerate(coords):
                    if val[0] > self.init_wid*self.ratio: # samples in the height area
                        new_main = val[0] - self.init_wid*self.ratio # for val over wid -> hei
                        coords[i][0] = (val[1] - self.init_wid/2)*self.buffsign[0] 
                        coords[i][1] = new_main*self.ratio - self.init_hei/2
                    elif val[0] < 0.1: # samples in the corner area
                        coords[i][0] = (val[0] - self.init_wid/2)*self.buffsign[0]
                        coords[i][1] = (val[1] - self.init_hei/2)*self.buffsign[1]
                    else: # samples in the width area
                        coords[i][0] = val[0]*self.ratio - self.init_wid/2
                        coords[i][1] = (val[1] - self.init_hei/2)*self.buffsign[1]
            return coords
        
        else:
            raise ValueError('Stimuli have no speed, but are not set to initialize on screen.')
    
    def _update_stim_mov(self):
        """
        The user shouldn't call this - it gets done within draw()
        """
    
        """Find out of bound stims, update positions, get new positions
        """
        self.countframes += 1
        self._check_keys()
        
        if self.countframes == self.duration:
            self.win.close()
        
        dead = np.zeros(self.nStims, dtype=bool)
    
        # stims that have exited the field
        dead = dead+(np.abs(self.coords[:,0]) > (self.init_wid/2 + self.buff))
        dead = dead+(np.abs(self.coords[:,1]) > (self.init_hei/2 + self.buff))

        # if there is speed flipping, update stimulus speeds to be flipped
        if len(self.flipdirec) != 0:
            dead = self._update_stim_speed(dead)
        
        ##update XY based on speed and dir
        new_xs = self.coords[:,0] + self.speed*np.cos(self.dirRad)
        new_ys = self.coords[:,1] + self.speed*np.sin(self.dirRad)# 0 radians=East!
        
        self.coords = np.array([new_xs, new_ys]).transpose()
        
        #update any dead stims
        if dead.any():
            self.coords[dead,:] = self._newStimsXY(sum(dead))
        
        self.elemarr.setXYs(self.coords)

    def _update_stim_speed(self, dead):        
        # flip speed (i.e., direction) if needed
        if self.countframes in self.flipstart:
            self.randel = np.where(np.random.rand(self.nStims) < self.flipfrac)[0]
            self.speed[self.randel] = -self.defaultspeed
            if self.randel.size == 0: # in case no elements are selected
                self.randel = None
        elif self.countframes in self.flipend:
            if self.randel.size is not None:
                self.speed[self.randel] = self.defaultspeed
            self.randel = None
        
        # revive and flip direction on flipped stimuli out of bounds
        if self.randel is not None and dead[self.randel].any():
            self.speed[self.randel[np.where(dead[self.randel])[0]]] = self.defaultspeed
            dead[self.randel]=False
        
        return dead
    
    def _update_stim_ori(self):
        # change orientations
        self.elemarr.oris = self.oriarrays[self.newori.index(self.countframes)]
    
    def _update_stim_pos(self):
        # get new positions
        self.initScr = True
        self.elemarr.setXYs(self._newStimsXY(self.nStims))
    
    def _initOriArrays(self):
        """
        Initialize the list of arrays of orientations and set first orientations.
        """
        if len(self.newori) != len(self.orimus):
            raise ValueError('Length of newori must match length of oriparamList.')
        
        self.oriarrays = list()
        for i in self.orimus:
            if self.orikappa == 0.0: # no dispersion
                self.oriarrays.append(np.ones(self.nStims)*i)
            else:
                neworisrad = np.random.vonmises(np.deg2rad(i), self.orikappa, self.nStims)
                self.oriarrays.append(np.rad2deg(neworisrad))
        
        self.elemarr.oris = self.oriarrays[0]
        
    def _initSizes(self, nStims):
        """
        Initialize the sizes uniformly from range (height and width same).
        """
          
        if self.sizeparams.size > 2:
            raise ValueError('Too many parameters.')
        elif self.sizeparams[0] == self.sizeparams[1]: # assume last end possible if same value (originally single value)
            sizes = np.ones(nStims)*self.sizeparams[0]
        else:
            # sample uniformly from range
            sizes = np.random.uniform(self.sizeparams[0], self.sizeparams[1], nStims)
            # use instead if want to initialize width and height independently
#            size_w = np.random.uniform(self.sizeparams[0], self.sizeparams[1], nStims)
#            size_h = np.random.uniform(self.sizeparams[0], self.sizeparams[1], nStims)
#            sizes = zip(size_w, size_h)
        
        self.elemarr.sizes = sizes
    
    def draw(self, win=None):
        """Draw the stimulus in its relevant window. You must call
        this method after every MyWin.flip() if you want the
        stimulus to appear on that frame and then update the screen
        again.
        """
        
        # update if new positions (newpos)
        if len(self.newpos) > 0 and self.countframes in self.newpos:
            self._update_stim_pos()
        
        # update if new orientations (newori)
        if len(self.newori) > 1 and self.countframes in self.newori[1:]:
            self._update_stim_ori()
        
        self.elemarr.draw()
        
        # check for end
#        self._check_keys()
#        if self.countframes == self.duration:
#            self.win.close()
        
        # count frames
        self.countframes += 1
        
        # update based on speed
        if self.speed[0] != 0.0:
            self._update_stim_mov()

        