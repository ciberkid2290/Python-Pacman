import pygame
from vector import Vector
from constants import *
import numpy as np

class pellet(object):
    def __init__(self, row, column):
        self.name = PELLET
        self.position = Vector(column*TILEWIDTH, row*TILEHEIGHT)
        self.color = WHITE
        self.radius = int(2 * TILEWIDTH / 16)
        self.collideRadius = int(2 * TILEWIDTH / 16)
        self.points = 10
        self.visible = True
        
    def render(self, screen):
        if self.visible:
            adjust = Vector(TILEWIDTH, TILEHEIGHT) / 2
            p = self.position + adjust
            pygame.draw.circle(screen, self.color, p.asInt(), self.radius)
            
class powerPellet(pellet):
    def __init__(self, row, column):
        pellet.__init__(self, row, column)
        self.name = POWERPELLET
        self.radius = int(8 * TILEWIDTH / 16)
        self.points = 50
        self.flashTime = 0.2
        self.timer = 0
    
    def update(self, dt):
        self.timer += dt
        if self.timer > self.flashTime:
            self.visible = not self.visible
            self.timer = 0
            
class pelletGroup(object):
    def __init__(self, pelletfile):
        self.pelletList = []
        self.powerPellets = []
        self.createPelletList(pelletfile)
        self.numEaten = 0
        
    def update(self, dt):
        for powerpellet in self.powerPellets:
            powerpellet.update(dt)
    
    def createPelletList(self, pelletfile):
        data = self.readPelletFile(pelletfile)
        for row in range(data.shape[0]):
            for col in range(data.shape[1]):
                if data[row][col] in ['.', '+']:
                    self.pelletList.append(pellet(row, col))
                elif data[row][col] in ['P', 'p']:
                    pp = powerPellet(row, col)
                    self.pelletList.append(pp)
                    self.powerPellets.append(pp)
    
    def readPelletFile(self, textfile):
        return np.loadtxt(textfile, dtype='<U1')
    
    def isEmpty(self):
        if len(self.pelletList) == 0:
            return True
        return False
    
    def render(self, screen):
        for pellet in self.pelletList:
            pellet.render(screen)  