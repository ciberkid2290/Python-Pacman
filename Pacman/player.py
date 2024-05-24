import pygame
from pygame.locals import *
from vector import Vector
from constants import *
from entity import Entity
from sprites import PacmanSprites

pacspeed = 80
#Pacman class
class Pacman(Entity):
    def __init__(self, node, level = 0):
        Entity.__init__(self, node)
        self.name = PACMAN
        #self.position = Vector(200, 400)
        self.directions = {STOP:Vector(), UP:Vector(0, -1), DOWN:Vector(0, 1), LEFT:Vector(-1, 0), RIGHT:Vector(1, 0)}
        self.direction = STOP
        if level == 0:
            pacspeed = 80
        elif level >= 1 and level <= 3:
            pacspeed = 90
        elif level > 3 and level <= 19:
            pacspeed = 100
        else:
            pacspeed = 90
        self.setSpeed(pacspeed)
        self.radius = 10
        self.collideRadius = 5
        self.color = YELLOW
        self.setBetweenNodes(LEFT)
        self.node = node
        self.target = node
        self.direction = LEFT
        self.visible = True
        self.alive = True
        self.sprites = PacmanSprites(self)
        print("pacman speed: ",self.speed)
        self.reset()
        
    def setPosition(self):
        self.position = self.node.position.copy()
        
    def update(self, dt):
        self.sprites.update(dt)
        self.position += self.directions[self.direction] * self.speed * dt
        direction = self.getValidKey()
        if self.overshotTarget():
            self.node = self.target
            
            #check if target is a portal
            if self.node.neighbors[PORTAL] is not None:
                self.node = self.node.neighbors[PORTAL]
            
            if self.node.neighbors[TUNNEL] is not None:
                self.die()
            
            self.target = self.getNewTarget(direction)
            if self.target is not self.node:
                self.direction = direction
            else:
                self.target = self.getNewTarget(self.direction) 
            if self.target is self.node:
                self.direction = STOP
            self.setPosition()
        else:
            if self.oppositeDirection(direction):
                self.reverseDirection()
    
    def reset(self):
        Entity.reset(self)
        self.direction = LEFT
        self.setSpeed(self.speed)
        self.setBetweenNodes(LEFT)
        self.alive = True
        self.speed = pacspeed
        self.image = self.sprites.getStartImage()
        self.sprites.reset()
    
    def die(self):
        self.alive = False
        self.direction = STOP
        
    def getValidKey(self):
        key_pressed = pygame.key.get_pressed()
        if key_pressed[K_UP]:
            return UP
        if key_pressed[K_DOWN]:
            return DOWN
        if key_pressed[K_LEFT]:
            return LEFT
        if key_pressed[K_RIGHT]:
            return RIGHT
        else:
            return STOP
     
        
    
    def eatPellets(self, pelletList):
        for pellet in pelletList:
            if self.collideCheck(pellet):
                self.setSpeed(pacspeed)
                return pellet
            self.setSpeed(pacspeed)
        return None
    
    def collideGhost(self, ghost):
        return self.collideCheck(ghost)
    
    def collideCheck(self, other):
        d = self.position - other.position
        dSquared = d.magnitudeSquared()
        rSquared = (self.collideRadius + other.collideRadius)**2
        if dSquared <= rSquared:
            return True
        return False
    
    