from constants import *

class mainMode(object):
    def __init__(self):
        self.timer = 0
        self.scatterCount = 0
        self.chaseCount = 0
        self.scatter()
    
    def update(self, dt):
        self.timer += dt
        if self.timer >= self.time:
            if self.mode is SCATTER:
                self.chase()
            elif self.mode is CHASE:
                self.scatter()
    
    def scatter(self):
        self.scatterCount += 1
        self.mode = SCATTER
        if self.scatterCount < 2:
            self.time = 7
        elif self.scatterCount < 3:
            self.time = 5
        else:
            self.time = 1/60
        self.timer = 0
        
    def chase(self):
        self.chaseCount += 1
        self.mode = CHASE
        if self.chaseCount <= 2:
            self.time = 20
        else:
            self.time = 2000
        self.timer = 0
    
    
class modeController(object):
    def __init__(self, entity):
        self.timer = 0
        self.time = None
        self.mainmode = mainMode()
        self.current = self.mainmode.mode
        self.entity = entity
    
    def update(self, dt):
        self.mainmode.update(dt)
        if self.current is FRIGHT:
            self.timer += dt
            if (self.time - self.timer) < 3:
                self.entity.flashMode() 
            if self.timer >= self.time:
                self.time = None
                self.entity.normalMode()
                self.current = self.mainmode.mode
        elif self.current in [SCATTER, CHASE]:
            self.current = self.mainmode.mode
        
        if self.current is SPAWN:
            if self.entity.node == self.entity.spawnNode:
                self.entity.normalMode()
                self.current = self.mainmode.mode
    
    def setspawnMode(self):
        if self.current is FRIGHT:
            self.current = SPAWN
        
    def setFrightMode(self):
        if self.current in [SCATTER, CHASE]:
            self.timer = 0
            self.time = 7
            self.current = FRIGHT
        elif self.current is FRIGHT:
            self.timer = 0
        