#!/usr/bin/env python2

'''This stimulus class defines a field of dots with an update rule that
determines how they change on every call to the .draw() method.'''

# Part of the PsychoPy library
# Copyright (C) 2015 Jonathan Peirce
# Distributed under the terms of the GNU General Public License (GPL).

# Ensure setting pyglet.options['debug_gl'] to False is done prior to any
# other calls to pyglet or pyglet submodules, otherwise it may not get picked
# up by the pyglet GL engine and have no effect.
# Shaders will work but require OpenGL2.0 drivers AND PyOpenGL3.0+
import pyglet
pyglet.options['debug_gl'] = False
import ctypes
GL = pyglet.gl

import psychopy  # so we can get the __path__
from psychopy import logging

# tools must only be imported *after* event or MovieStim breaks on win32
# (JWP has no idea why!)
from psychopy.tools.attributetools import attributeSetter, setAttribute
from psychopy.tools.arraytools import val2array
from psychopy.tools.monitorunittools import cm2pix, deg2pix
from psychopy.visual.basevisual import BaseVisualStim, ColorMixin, ContainerMixin

import numpy
from numpy import pi


class MovStim(BaseVisualStim, ColorMixin, ContainerMixin):
    """
    This stimulus class allows stimuli to be moved about.
    """
    def __init__(self,
                 win,
                 stim,
                 units='',
                 nDots=1,
                 speed=0.5,
                 rgb=None,
                 color=(1.0, 1.0, 1.0),
                 colorSpace='rgb',
                 opacity=1.0,
                 contrast=1.0,
                 depth=0,
                 initScr=True,
                 name=None,
                 autoLog=None):

        #what local vars are defined (these are the init params) for use by __repr__
        self._initParams = __builtins__['dir']()
        self._initParams.remove('self')

        super(MovStim, self).__init__(win, units=units, name=name, autoLog=False)#set autoLog at end of init

        self.nDots = nDots
        self.speed = speed
        self.stim = stim
        self.pos = self.stim.pos
        self.dir = self.stim.ori
        self.size = self.stim.size
        self.dirRad = self.dir*pi/180
        self.initScr = initScr
        self.opacity = float(opacity)
        self.contrast = float(contrast)

        self.useShaders=True
        self.colorSpace=colorSpace
        if rgb!=None:
            logging.warning("Use of rgb arguments to stimuli are deprecated. Please use color and colorSpace args instead")
            self.setColor(rgb, colorSpace='rgb', log=False)
        else:
            self.setColor(color, log=False)

        self.depth=depth

        #initialise the dots themselves - give them all random dir and then
        #fix the first n in the array to have the direction specifieds

        self._verticesBase = self._dotsXY = self._newDotsXY(self.nDots) #initialise a random array of X,Y

        self._update_dotsXY()

        # set autoLog now that params have been initialised
        self.__dict__['autoLog'] = autoLog or autoLog is None and self.win.autoLog
        if self.autoLog:
            logging.exp("Created %s = %s" %(self.name, str(self)))


    @attributeSetter
    def stim(self, stim):
        """*None* or a visual stimulus object
        This can be any object that has a ``.draw()`` method and a
        ``.setPos([x,y])`` method (e.g. a GratingStim, TextStim...)!!
        DotStim assumes that the stim uses pixels as units.
        ``None`` defaults to dots.

        See `ElementArrayStim` for a faster implementation of this idea.
        """
        self.__dict__['stim'] = stim


    @attributeSetter
    def size(self, size):
        """Float specified in pixels (overridden if `element` is specified).
        :ref:`operations <attrib-operations>` are supported."""
        self.__dict__['size'] = self.stim.size
        
    @attributeSetter
    def dir(self, dir):
        """float (degrees). Direction of dots
        """
        self.__dict__['dir'] = self.stim.ori
        self.dirRad = self.dir*pi/180

    @attributeSetter
    def pos(self, pos):
        """Specifying the location of the centre of the stimulus using a :ref:`x,y-pair <attrib-xy>`.
        See e.g. :class:`.ShapeStim` for more documentation/examples on how to set position.

        """
        # Isn't there a way to use BaseVisualStim.pos.__doc__ as docstring here?
        self.__dict__['pos'] = self.stim.pos  # using BaseVisualStim. we'll store this as both

    @attributeSetter
    def speed(self, speed):
        """float. speed of the dots (in *units*/frame).
        """
        self.__dict__['speed'] = speed

    def draw(self, win=None):
        """Draw the stimulus in its relevant window. You must call
        this method after every MyWin.flip() if you want the
        stimulus to appear on that frame and then update the screen
        again.
        """
        if win is None:
            win=self.win
        self._selectWindow(win)

        self._update_dotsXY()

        GL.glPushMatrix()#push before drawing, pop after

        #draw the dots
        if self.stim is None:
            win.setScale('pix')
            GL.glPointSize(self.stim.size)

            #load Null textures into multitexteureARB - they modulate with glColor
            GL.glActiveTexture(GL.GL_TEXTURE0)
            GL.glEnable(GL.GL_TEXTURE_2D)
            GL.glBindTexture(GL.GL_TEXTURE_2D, 0)
            GL.glActiveTexture(GL.GL_TEXTURE1)
            GL.glEnable(GL.GL_TEXTURE_2D)
            GL.glBindTexture(GL.GL_TEXTURE_2D, 0)

            GL.glVertexPointer(2, GL.GL_DOUBLE, 0, self.verticesPix.ctypes.data_as(ctypes.POINTER(ctypes.c_double)))
            desiredRGB = self._getDesiredRGB(self.rgb, self.colorSpace, self.contrast)

            GL.glColor4f(desiredRGB[0], desiredRGB[1], desiredRGB[2], self.opacity)
            GL.glEnableClientState(GL.GL_VERTEX_ARRAY)
            GL.glDrawArrays(GL.GL_POINTS, 0, self.nDots)
            GL.glDisableClientState(GL.GL_VERTEX_ARRAY)
        else:
            #we don't want to do the screen scaling twice so for each dot subtract the screen centre
            initialDepth=self.stim.depth
            for pointN in range(0,self.nDots):
                self.stim.setPos(self.verticesPix[pointN,:])
                self.stim.draw()
            self.stim.setDepth(initialDepth)#reset depth before going to next frame
        GL.glPopMatrix()

    def _newDotsXY(self, nDots):
        # get window dimensions (pixels)
        win_wid = self.win.size[0]
        win_hei = self.win.size[1]
        
        # for first initialization, initialize gaussians on screen
        if self.initScr:
            coords = numpy.random.uniform(-0.1, 0.1, [nDots,2]) #NOT SURE WHY NOT -0.5 to 0.5 (added /5 lower)
            self.initScr = False
            return coords
        
        else:
            # For a rectangular window, the base direction is tan(wid/hei)
            base_dir = numpy.arctan(win_wid/win_hei)
            
            # width of area in which to initialize dots
            buff = numpy.min((win_wid, win_hei))/6
            
            # sample a window-relative coordinate
            leng = win_wid + win_hei
            coord_main = numpy.random.uniform(-buff, leng, nDots)[:, numpy.newaxis]
            # sample coordinate from buffer zone
            coord_buff = numpy.random.uniform(-buff, 0, nDots)[:, numpy.newaxis]
            
            coords = numpy.concatenate((coord_main, coord_buff), axis=1)
            for i, val in enumerate(coords):
                if val[0] > win_wid:
                    new_main = val[0] - win_wid # switch wid and hei
                    coords[i] = (numpy.array([val[1]/win_wid, new_main/win_hei]) - 0.5)/5 # also scaling and shifting
                else:
                    coords[i] = (numpy.array([val[0]/win_wid, val[1]/win_hei]) -0.5)/5 # just scaling and shifting
            
            # rotate based on actual direction
            rot_rad = self.dirRad - base_dir
            rot_cos = numpy.cos(rot_rad)
            rot_sin = numpy.sin(rot_rad)
            rot_mat = numpy.array([[rot_cos, -rot_sin], [rot_sin, rot_cos]])
            
            rot_coords = numpy.matmul(coords, numpy.transpose(rot_mat))
        
        return rot_coords

    def _update_dotsXY(self):
        """
        The user shouldn't call this - its gets done within draw()
        """

        """Find out of bound dots, update positions, get new positions
        """

        dead = numpy.zeros(self.nDots, dtype=bool)

        ##update XY based on speed and dir
        self._verticesBase[:,0] += self.speed*numpy.cos(self.dirRad)
        self._verticesBase[:,1] += self.speed*numpy.sin(self.dirRad)# 0 radians=East!

        #dots that have exited the field
        quad = int(self.dir/90)
        if quad == 0 or 1:
            dead = dead+(numpy.array(self._verticesBase[:,0])>0.1) # replaced 0.5 all here...
        else:
            dead = dead+(numpy.array(self._verticesBase[:,0])<0.1)
        if quad == 0 or 3:
            dead = dead+(numpy.array(self._verticesBase[:,1])>0.1)
        else:
            dead = dead+(numpy.array(self._verticesBase[:,0])<0.1)
            
        #update any dead dots
        if sum(dead):
            self._verticesBase[dead,:] = self._newDotsXY(sum(dead))

        #update the pixel XY coordinates in pixels (using _BaseVisual class)
        self._updateVertices()
