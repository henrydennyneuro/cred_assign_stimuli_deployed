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
                 units='deg', # only works for degrees right now :$
                 direc=0.0, # only supports a single value. Use speed to flip direction of some elements.
                 speed=0.0, # units are sort of arbitrary for now
                 newpos=[], # frames at which to reinitialize stimulus positions
                 newori=[0], # frames at which to change stimulus orientations (always include 0)
                 oriparamlist=[[0.0, 0.0]], # parameters to use when changing stimulus orientations [mu, std (optional)]
                 flipspeed=[], # intervals during which to flip speed [start, end (optional)]S
                 flipfrac=0.0, # fraction of elements that should be flipped (0 to 1)
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
            
            super(OurStims, self).__init__(win, units=units, name=name, autoLog=False)#set autoLog at end of init
            
            self.nStims = self.elemarr.nElements
            self.elemarr.contrs = contrast
            self.win = self.elemarr.win # just overriding redundancy to avoid any problems
            self.direc = direc
            self._winVar()
            self._stimOriginVar()
            if len(newpos) != 0: # get frames from sec
                newpos = [x * float(fps) for x in newpos]
            self.newpos = newpos
            
            self.defaultspeed = speed
            self.speed = np.ones(self.nStims)*speed
            if len(flipspeed) != 0: # get frames from sec
                flipspeed = [[y * float(fps) for y in x] for x in flipspeed]
            self._initFlipSpeed(flipspeed)
            self.flipfrac = float(flipfrac)
            if self.flipfrac < 0.0 or self.flipfrac > 1.0:
                raise ValueError('Specify a flipfrac between 0.0 and 1.0.')
            
            self.newori = [x * float(fps) for x in newori]
            self.oriparamlist = oriparamlist
            self._initOriArrays()
            self.elemarr.oris = self.oriarrays[0]
            
            self.duration = duration*float(fps)
            self.initScr = initScr
            
            self.countframes = 0
            self.printed = False # useful for printing things once
            
            self._newStimsXY(self.nStims)
            
            self._update_stims()
    
            # set autoLog now that params have been initialised
            self.__dict__['autoLog'] = autoLog or autoLog is None and self.win.autoLog
            if self.autoLog:
                logging.exp("Created %s = %s" %(self.name, str(self)))

    def setContrast(self, contrast, operation='', log=None):
        """Usually you can use 'stim.attribute = value' syntax instead,
        but use this method if you need to suppress the log message."""
        self.elemarr.setContrs(contrast)
    
    def _check_keys(self):
        for keys in event.getKeys(timeStamped=True):
            if keys[0]in ['escape', 'q']:
                self.escape_pressed = True
                self.win.close()
    
    def _winVar(self):
        """Get variables relevant to the window
        """
        dist = self.win.monitor.getDistance()
        width = self.win.monitor.getWidth()
        
        if self.elemarr.units == 'deg':
            # for a flat screen
            deg_wid = np.rad2deg(np.arctan((0.5*width)/dist)) * 2
            deg_per_pix = deg_wid/self.win.size[0]
            deg_hei = deg_per_pix * self.win.size[1]
            self.init_wid = deg_wid * 2.0 # I don't know why the coords are wrong without multiplication
            self.init_hei = deg_hei * 2.0 # same

        else:
            raise ValueError('Only implemented for deg units so far.')
    
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
        self.buff = (self.init_wid+self.init_hei)/40 # size of initialization area (15 is arbitrary)
        print(self.buff)
        print(self.init_wid)
        print(self.init_hei)
        
        if self.direc%90.0 != 0.0:
            self.ratio = self.dirRad%90.0/basedirRad
            self.leng = self.init_wid*self.ratio + self.init_hei/self.ratio
        
        
    def _initFlipSpeed(self, flipspeed):
        self.flipstart = list()
        self.flipend = list()
        
        for i in flipspeed:
            i = val2array(i)
            if i.size > 2:
                raise ValueError('Too many parameters.')
            else:
                self.flipstart.append(i[0])
            if i.size == 1: # assume last end possible
                if i == len(flipspeed) - 1:
                    self.flipend.append(-1)
                else:
                    self.flipend.append(flipspeed[i+1][0] - 1)
            else:
                self.flipend.append(i[1])
        
    def _newStimsXY(self, newStims):
        # for first initialization, initialize gaussians on screen

        if self.initScr:
            coords_wid = np.random.uniform(-self.init_wid/2, self.init_wid/2, newStims)[:, np.newaxis]
            coords_hei = np.random.uniform(-self.init_hei/2, self.init_hei/2, newStims)[:, np.newaxis]
            coords = np.concatenate((coords_wid, coords_hei), axis=1)
            self.initScr = False
            return coords
        
        # subsequent initializations from L around window (or I if mult of 90)
        else:            
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
    
    def _update_stims(self):
        """
        The user shouldn't call this - it gets done within draw()
        """
    
        """Find out of bound stims, update positions, get new positions
        """
        self.countframes += 1
        self._check_keys()
        
        if self.countframes == self.duration:
            self.win.close()
        
        # get new positions for all stimuli if needed
        if self.countframes in self.newpos:
            self.initScr = True
            self.elemarr.setXYs(self._newStimsXY(self.nStims))
        
        dead = np.zeros(self.nStims, dtype=bool)
    
        #stims that have exited the field
        dead = dead+(np.abs(self.elemarr.xys[:,0]) > (self.init_wid/2 + self.buff))
        dead = dead+(np.abs(self.elemarr.xys[:,1]) > (self.init_hei/2 + self.buff))
        
        ##update XY based on speed and dir
        new_xs = self.elemarr.xys[:,0] + self.speed*np.cos(self.dirRad)
        new_ys = self.elemarr.xys[:,1] + self.speed*np.sin(self.dirRad)# 0 radians=East!
        
        all_coords = np.array([new_xs, new_ys]).transpose()
        
        #update any dead stims
        if sum(dead):
            all_coords[dead,:] = self._newStimsXY(sum(dead))
        
        self.elemarr.setXYs(all_coords)
        
        # change orientation if needed
        if self.countframes in self.newori:
            self.elemarr.oris = self.oriarrays[self.newori.index(self.countframes)]
        
        # flip speed (i.e., direction) if needed
        self.randel = None
        if self.countframes in self.flipstart:
            self.randel = np.random.rand(self.nStims) < self.flipfrac
            self.speed[self.randel] = - self.speed[self.randel]
        elif self.countframes in self.flipend:
            self.speed[self.randel] = self.defaultspeed
    
    def _initOriArrays(self):
        """
        Initialize the list of arrays of orientations.
        """
        if len(self.newori) != len(self.oriparamlist):
            raise ValueError('Length of newori must match length of oriparamList.')
        
        self.oriarrays = list()
        for i in self.oriparamlist:
            i = val2array(i)
            if i.size > 2:
                raise ValueError('Too many parameters.')
            elif i.size == 1: # assume no standard deviation
                self.oriarrays.append(np.ones(self.nStims)*i[0])
            elif i.size == 2:
                self.oriarrays.append(np.random.normal(i[0], i[1], self.nStims))
    
    def draw(self, win=None):
        """Draw the stimulus in its relevant window. You must call
        this method after every MyWin.flip() if you want the
        stimulus to appear on that frame and then update the screen
        again.
        """
        
        if win is None:
            win=self.win
        self._selectWindow(win)
    
        self._update_stims()
        
        self.elemarr.draw()