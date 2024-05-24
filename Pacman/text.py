import pygame
from vector import Vector
from constants import *


pygame.font.init()

class Text(object):
    def __init__(self, text, color, x, y, size, time = None, id = None, visible = True):
        self.id = id
        self.text = text
        self.color = color
        self.size = size
        self.visible = visible
        self.position = Vector(x, y)
        self.timer = 0
        self.lifespan = time
        self.label = None
        self.destroy = False
        self.setupFont("PressStart2P-Regular.ttf")
        self.createLabel()
        
    def setupFont(self, fontpath):
        self.font = pygame.font.Font(fontpath, self.size)
        
    def createLabel(self):
        self.label = self.font.render(self.text, 1, self.color)
    
    def setText(self, newtext):
        self.text = str(newtext)
        self.createLabel()
    
    def update(self, dt):
        if self.lifespan is not None:
            self.timer += dt
            if self.timer >= self.lifespan:
                self.timer = 0
                self.lifespan = None
                self.destroy = True
                
    def render(self, screen):
        if self.visible:
            x, y = self.position.asTuple()
            screen.blit(self.label, (x, y))
        

class TextGroup(object):
    def __init__(self):
        self.nextid = 10
        self.alltext = {}
        self.setupText()
        self.showText(READYTXT)

    def addText(self, text, color, x, y, size, time = None, id = None):
        # Increment the next id to make sure each entry has a unique id
        self.nextid += 1
        # Make a new Text object with the new id, and store it in the alltext dictionary
        self.alltext[self.nextid] = Text(text, color, x, y, size, time = time, id = id)
        # Return the newly assigned id
        return self.nextid

    def removeText(self, id):
        self.alltext.pop(id)
        
    def setupText(self):
        # Set the font size for the text
        fontSize = TILEHEIGHT
        
        # Create and add Text objects for the score, level, and various status messages
        self.alltext[SCORETXT] = Text("0".zfill(8), WHITE, 0, TILEHEIGHT, fontSize)  # Score text, initially set to 0
        self.alltext[LEVELTXT] = Text(str(1).zfill(3), WHITE, 23*TILEWIDTH, TILEHEIGHT, fontSize)  # Level text, initially set to 1
        self.alltext[READYTXT] = Text("READY!", YELLOW, 11.25 * TILEWIDTH, 20 * TILEHEIGHT, fontSize, visible=False)  # Ready text, initially hidden
        self.alltext[PAUSETXT] = Text("PAUSED!", TEAL, 10.625 * TILEHEIGHT, 20 * TILEHEIGHT, fontSize, visible = False)  # Paused text, initially hidden
        self.alltext[GAMEOVERTXT] = Text("GAME OVER", RED, 10 * TILEHEIGHT, 20 * TILEHEIGHT, fontSize, visible = False)  # Game over text, initially hidden
        
        # Add score and level labels to the TextGroup
        self.addText("SCORE", WHITE, 0, 0, fontSize)  # Score label
        self.addText("LEVEL", WHITE, 23*TILEWIDTH, 0, fontSize)  # Level label

    def update(self, dt):
        for tkey in list(self.alltext.keys()):
            self.alltext[tkey].update(dt)
            if self.alltext[tkey].destroy:
                self.removeText(tkey)
    def showText(self, id):
        self.hideText()
        self.alltext[id].visible = True
    
    def hideText(self):
        self.alltext[READYTXT].visible = False
        self.alltext[PAUSETXT].visible = False
        self.alltext[GAMEOVERTXT].visible = False
    
    def updateScore(self, score):
        self.updateText(SCORETXT, str(score).zfill(8))
    
    def updateLevel(self, level):
        self.updateText(LEVELTXT, str(level + 1).zfill(3))
        
    def updateText(self, id, value):
        if id in self.alltext.keys():
            self.alltext[id].setText(value)
    
    def render(self, screen):
        for tkey in list(self.alltext.keys()):
            self.alltext[tkey].render(screen)