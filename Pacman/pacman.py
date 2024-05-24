import pygame
from pygame.locals import *
from constants import *
from player import Pacman
from Nodes import nodeGroup
from pellets import pelletGroup
from ghosts import ghostGroup
from fruit import Fruit
from pauser import Pause
from text import TextGroup
import numpy as np
from sprites import LifeSprites, MazeSprites
from mazedata import MazeData

# Game controller class
class GameController:
    def __init__(self):
        self.screen = pygame.display.set_mode(SCREENSIZE, 0, 32)
        pygame.display.set_caption("Pacman")
        self.background = None
        self.background_norm = None
        self.background_flash = None
        self.clock = pygame.time.Clock()
        self.fruit = None
        self.level = 0
        self.pause = Pause(True)
        self.lives = 5
        self.score = 0
        self.hasSpawnedLife = False
        self.livesGained = 0
        self.textGroup = TextGroup()
        self.lifesprites = LifeSprites(self.lives-1)
        self.count = 0
        self.flashBG = False
        self.flashTime = 0.2
        self.flashTimer = 0
        self.fruitCaptured = []
        self.mazedata = MazeData()
    
    def restartGame(self):
        self.lives = 5
        self.level = 0
        self.pause.paused = True
        self.fruit = None
        self.startGame()
        self.fruitCaptured = []
        self.score = 0
        self.textGroup.updateScore(self.score)
        self.textGroup.updateLevel(self.level)
        self.textGroup.showText(READYTXT)
        self.lifesprites.resetLives(self.lives-1)
        
    def resetLevel(self):
        self.pause.paused = True
        self.pacman.reset()
        self.ghosts.reset()
        self.fruit = None
        self.textGroup.showText(READYTXT)
        
    def setBackground(self):
        self.background_norm = pygame.surface.Surface(SCREENSIZE).convert()
        self.background_norm.fill(BLACK)
        self.background_flash = pygame.surface.Surface(SCREENSIZE).convert()
        self.background_flash.fill(BLACK)
        self.background_norm = self.mazesprites.constructBackground(self.background_norm, self.level%5)
        self.background_flash = self.mazesprites.constructBackground(self.background_flash, 5)
        self.flashBG = False
        self.background = self.background_norm
        
    def startGame(self):
        self.mazedata.loadMaze(self.level)
        self.mazesprites = MazeSprites(self.mazedata.obj.name+".txt", self.mazedata.obj.name+"_rotation.txt")
        self.setBackground()
        self.nodes = nodeGroup(self.mazedata.obj.name+".txt")
        self.mazedata.obj.setPortalPairs(self.nodes)
        self.mazedata.obj.connectHomeNodes(self.nodes)
        self.pacman = Pacman(self.nodes.getNodeFromTiles(*self.mazedata.obj.pacmanStart))
        self.pellets = pelletGroup(self.mazedata.obj.name + ".txt")
        self.ghosts = ghostGroup(self.nodes.getStartTempNode(), self.pacman)
        self.ghosts.pinky.setStartNode(self.nodes.getNodeFromTiles(*self.mazedata.obj.addOffset(2, 3)))
        self.ghosts.inky.setStartNode(self.nodes.getNodeFromTiles(*self.mazedata.obj.addOffset(0, 3)))
        self.ghosts.clyde.setStartNode(self.nodes.getNodeFromTiles(*self.mazedata.obj.addOffset(4, 3)))
        self.ghosts.setSpawnNode(self.nodes.getNodeFromTiles(*self.mazedata.obj.addOffset(2, 3)))
        self.ghosts.blinky.setStartNode(self.nodes.getNodeFromTiles(*self.mazedata.obj.addOffset(2, 0)))
        
        #list of denied movements
        self.nodes.denyHomeAccess(self.pacman)
        self.nodes.denyHomeAccessList(self.ghosts)
        self.ghosts.inky.startNode.denyAccess(RIGHT, self.ghosts.inky)
        self.ghosts.clyde.startNode.denyAccess(LEFT, self.ghosts.clyde)
        self.mazedata.obj.denyGhostsAccess(self.ghosts, self.nodes)
        
    def update(self):
        dt = self.clock.tick(30) / 1000 # 30 fps
        self.pellets.update(dt)
        if not self.pause.paused:
            self.ghosts.update(dt)
            if self.fruit is not None:
                self.fruit.update(dt)
            self.checkPelletEvents()
            self.checkGhostEvents()
            self.checkFruitEvents()
            self.checkScoreEvents()
            
        if self.pacman.alive:
            if not self.pause.paused:
                self.pacman.update(dt)
        else:
            self.pacman.update(dt)
        
        if self.flashBG:
            self.flashTimer += dt
            if self.flashTimer >= self.flashTime:
                self.flashTimer = 0
                if self.background == self.background_norm:
                    self.background = self.background_flash
                else:
                    self.background = self.background_norm
        
        afterPauseMethod = self.pause.update(dt)
        if afterPauseMethod is not None:
            afterPauseMethod()
        self.checkEvents()
        self.render()
        self.textGroup.update(dt)
    
    def updateScore(self, points):
        self.score += points
        self.textGroup.updateScore(self.score)
    
    def checkEvents(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                exit()
            elif event.type == KEYDOWN:
                if event.key == K_SPACE:
                    if self.pacman.alive:
                        self.pause.setPause(playerPaused = True)
                        if not self.pause.paused:
                            self.textGroup.hideText()
                            self.showEntities()
                        else:
                            self.textGroup.showText(PAUSETXT)
                            self.hideEntities()
    def nextLevel(self):
        self.showEntities()
        self.level += 1
        self.pause.paused = True
        self.startGame()
        self.textGroup.updateLevel(self.level)
    
    def checkGhostEvents(self):
        for ghost in self.ghosts:
            if self.pacman.collideGhost(ghost):
                if ghost.mode.current is FRIGHT:
                    self.pacman.visible = False
                    ghost.visible = False
                    self.updateScore(ghost.points)
                    self.textGroup.addText(str(ghost.points), PEACH, ghost.position.x, ghost.position.y, 8, time = 1)
                    self.ghosts.updatePoints()
                    self.pause.setPause(pauseTime = 1, func = self.showEntities)
                    ghost.startSpawn()
                    self.nodes.allowHomeAccess(ghost)
                elif ghost.mode.current is not SPAWN:
                    self.lives -= 1
                    self.lifesprites.removeImage()
                    self.pacman.die()
                    self.ghosts.hide()
                    if self.lives <= 0:
                        self.textGroup.showText(GAMEOVERTXT)
                        self.pause.setPause(pauseTime = 3, func = self.restartGame)
                    else:
                        self.pause.setPause(pauseTime = 3, func = self.resetLevel)         
      
    def checkFruitEvents(self):
        if self.pellets.numEaten == 50 or self.pellets.numEaten == 140:
            if self.fruit is None:
                self.fruit = Fruit(self.nodes.getNodeFromTiles(9, 20))
        if self.fruit is not None:
            if self.pacman.collideCheck(self.fruit):
                self.updateScore(self.fruit.points)
                self.textGroup.addText(str(self.fruit.points), PEACH, self.fruit.position.x, self.fruit.position.y, 8, time = 2)
                fruitCaptured = False
                for fruit in self.fruitCaptured:
                    if fruit.get_offset() == self.fruit.image.get_offset():
                        fruitCaptured = True
                        break
                if not fruitCaptured:
                    self.fruitCaptured.append(self.fruit.image)
                self.fruit = None
            elif self.fruit.destroy:
                self.fruit = None
    
    def checkPelletEvents(self):
        pellet = self.pacman.eatPellets(self.pellets.pelletList)
        if pellet:
            self.pellets.numEaten += 1
            self.updateScore(pellet.points)
            if self.pellets.numEaten == 30:
                self.ghosts.inky.startNode.allowAccess(RIGHT, self.ghosts.inky)
            
            if self.pellets.numEaten == 70:
                self.ghosts.clyde.startNode.allowAccess(LEFT, self.ghosts.clyde)
            self.pellets.pelletList.remove(pellet)
            if pellet.name == POWERPELLET:
                self.ghosts.startFright()
                
            if self.pellets.isEmpty():
                self.flashBG = True
                self.ghosts.hide()
                self.pause.setPause(pauseTime = 3, func = self.nextLevel)
                
    def checkScoreEvents(self):
        if self.score >= 10000 and self.count < 1:
            self.count += 1
            self.lives += 1
            self.lifesprites.addImage()
        
        if self.score // 30000 > self.livesGained:
            self.lives += 1
            self.lifesprites.addImage()
            self.livesGained += 1
            
    
    def showEntities(self):
        self.pacman.visible = True
        self.ghosts.show()
    
    def hideEntities(self):
        self.pacman.visible = False
        self.ghosts.hide()
    
    def render(self):
        self.screen.blit(self.background, (0, 0))
        self.pellets.render(self.screen)
        if self.fruit is not None:
            self.fruit.render(self.screen)
        self.pacman.render(self.screen)
        self.ghosts.render(self.screen)
        self.textGroup.render(self.screen)
        
        for i in range(len(self.lifesprites.images)):
            x = self.lifesprites.images[i].get_width() * i
            y = SCREENHEIGHT - self.lifesprites.images[i].get_height()
            self.screen.blit(self.lifesprites.images[i], (x, y))
            
        for i in range(len(self.fruitCaptured)):
            x = SCREENWIDTH - self.fruitCaptured[i].get_width() * (i+1)
            y = SCREENHEIGHT - self.fruitCaptured[i].get_height()
            self.screen.blit(self.fruitCaptured[i], (x, y))
        pygame.display.update()
        

if __name__ == '__main__':
    game = GameController()
    game.startGame()
    while True:
        game.update()