import pygame
from pygame.locals import *
from vector import Vector
from constants import *
from entity import Entity
from modes import modeController
from sprites import GhostSprites

ghostspeed = 75

class Ghost(Entity):
    def __init__(self, node, pacman=None, blinky = None, level = 0):
        Entity.__init__(self, node)
        self.name = GHOST
        self.points = 200
        self.timer = 0
        self.time = 0
        self.mood = 0
        self.node = node
        self.goal = Vector()
        self.directionMethod = self.goalDirection
        self.pacman = pacman
        self.mode = modeController(self)
        self.blinky = blinky
        self.homeNode = node
        if level == 0:
            ghostspeed = 75
        elif level >= 1 and level <= 3:
            ghostspeed = 85
        elif level > 3 and level <= 19:
            ghostspeed = 95
        else:
            ghostspeed = 95
        self.setSpeed(ghostspeed)
        self.scatterCount = 0
        self.chaseCount = 0
        print("ghost speed: ",self.speed)
    
    def reset(self):
        Entity.reset(self)
        self.mood = 0
        self.timer = 0
        self.time = 0
        self.scatterCount = 0
        self.chaseCount = 0
        self.points = 200
        self.mode = modeController(self)
        self.directionMethod = self.goalDirection
    
    def update(self, dt):
        self.sprites.update(dt)
        self.mode.update(dt)
        if self.chaseCount <= 3:
            self.reverseUpdate(dt)
        if self.mode.current is SCATTER:
            self.scatter()
        elif self.mode.current is CHASE:
            self.chase()
        Entity.update(self, dt)   
        
    
    def scatter(self):
        self.goal = Vector(TILEWIDTH*NCOLS, 0)
        
    
    def chase(self):
        self.goal = self.pacman.position
    
    def startFright(self):
        self.mode.setFrightMode()
        if self.mode.current == FRIGHT:
            self.reverseDirection()
            self.setSpeed(ghostspeed / 2)
            self.directionMethod = self.randomDirection
            
    def normalMode(self):   
        self.setSpeed(ghostspeed)
        self.directionMethod = self.goalDirection
        self.homeNode.denyAccess(DOWN, self)
    
    def spawn(self):
        self.goal = self.spawnNode.position
        
    
    def setSpawnNode(self, node):
        self.spawnNode = node
        
    def startSpawn(self):
        self.mode.setspawnMode()
        if self.mode.current == SPAWN:
            self.setSpeed(ghostspeed * 2)
            self.directionMethod = self.goalDirection
            self.spawn()
            
    def reverseTimer(self):
        if self.mood == 0: # 0 = scatter, 1 = chase
            self.time = 20
        elif self.mood == 1:
            if self.scatterCount < 2:
                self.time = 7
            elif self.scatterCount < 3:
                self.time = 5
            else:
                self.time = 1/60
        self.timer = 0

    def reverseUpdate(self, dt):
        self.timer += dt
        if self.timer >= self.time:
            if self.mood == 0:
                print("Scatter")
                self.scatterCount += 1
                self.mood = 1
                self.reverseDirection()
                self.reverseTimer()
            elif self.mood == 1:
                print("Chase")
                self.chaseCount += 1
                self.mood = 0   
                self.reverseDirection()
                self.reverseTimer()
        
    
    
# Blinky Class
class Blinky(Ghost):
    def __init__(self, node, pacman=None, blinky=None):
        Ghost.__init__(self, node, pacman, blinky)
        self.name = BLINKY
        self.color = RED
        self.sprites = GhostSprites(self)
        
# Pinky Class
class Pinky(Ghost):
    def __init__(self, node, pacman=None, blinky=None):
        Ghost.__init__(self, node, pacman, blinky)
        self.name = PINKY
        self.color = PINK
        self.sprites = GhostSprites(self)
        
    def scatter(self):
        self.goal = Vector()
        
    def chase(self):
        self.goal = self.pacman.position + self.pacman.directions[self.pacman.direction] * TILEWIDTH * 4
        

# Inky Class
class Inky(Ghost):
    def __init__(self, node, pacman=None, blinky=None):
        Ghost.__init__(self, node, pacman, blinky)
        self.name = INKY
        self.color = TEAL
        self.sprites = GhostSprites(self)
        
    def scatter(self):
        self.goal = Vector(TILEWIDTH*NCOLS, TILEHEIGHT*NROWS)
        
    def chase(self):
        vec1 = self.pacman.position + self.pacman.directions[self.pacman.direction] * TILEWIDTH * 2
        vec2 = (vec1 - self.blinky.position) * 2
        self.goal = self.blinky.position + vec2
        
        
# Clyde Class
class Clyde(Ghost):
    def __init__(self, node, pacman=None, blinky=None):
        Ghost.__init__(self, node, pacman, blinky)
        self.name = CLYDE
        self.color = ORANGE
        self.sprites = GhostSprites(self)

    def scatter(self):
        self.goal = Vector(0, TILEHEIGHT*NROWS)
        
    def chase(self):
        d = self.pacman.position - self.position
        ds = d.magnitudeSquared()
        if ds <= (TILEWIDTH*8)**2:
            self.scatter()
        else:
            self.goal = self.pacman.position
            

# Group class
class ghostGroup(object):
    def __init__(self, node, pacman):
        self.blinky = Blinky(node, pacman)
        self.pinky = Pinky(node, pacman)
        self.inky = Inky(node, pacman, self.blinky)
        self.clyde = Clyde(node, pacman)
        self.ghosts = [self.blinky, self.pinky, self.inky, self.clyde]
    
    def __iter__(self):
        return iter(self.ghosts)
    
    def update(self, dt):
        for ghost in self:
            ghost.update(dt)
    
    def startFright(self):
        for ghost in self:
            ghost.startFright()
        self.resetPoints()
    
    def setSpawnNode(self, node):
        for ghost in self:
            ghost.setSpawnNode(node)
    
    def updatePoints(self):
        for ghost in self:
            ghost.points *=2
            
    def resetPoints(self):
        for ghost in self:
            ghost.points = 200

    def reset(self):
        for ghost in self:
            ghost.reset()
    
    def hide(self):
        for ghost in self:
            ghost.visible = False
    
    def show(self):
        for ghost in self:
            ghost.visible = True
    
    def render(self, screen):
        for ghost in self:
            ghost.render(screen)
        