import pygame
import numpy as np

from numba import njit, prange
from time import time

@njit()
def updateWaves(waveHeight, waveVelocity, waveWeight, Width, Height):
    for x in prange(1, Width-1):
        for y in prange(1, Height-1):
            for k in prange(3):
                waveVelocity[x][y][k] += ((waveHeight[x+1][y][k] + waveHeight[x-1][y][k] + waveHeight[x][y+1][k] + waveHeight[x][y-1][k]) / 4 - waveHeight[x][y][k]) / waveWeight[x][y][k]
    return waveVelocity

@njit()
def updateDW(waveHeight, frame, cx, cy, size, freq, time):
    for x in prange(cx-size**2, cx+size**2):
        for y in prange(cy-size**2, cy+size**2):
            r = (x - cx)**2 + (y - cy)**2
            fade = np.exp(-r / 2 / size**2) / size
            waveHeight[x, y, 0:3] += fade * np.cos(freq*x) * (np.sin(frame*0.5*freq))

    return waveHeight

class Simulation:
    def __init__(self, screenSize : list | tuple, sceneSize : list | tuple):
        self.screenSize = screenSize
        self.screen = pygame.display.set_mode(screenSize, pygame.WINDOWMAXIMIZED)
        self.surface = pygame.Surface(sceneSize)
        self.weightOverlay = pygame.Surface(sceneSize)
        self.weightOverlay.set_alpha(10)
        self.clock = pygame.time.Clock()

        self.sceneSize = sceneSize
        self.Width = self.sceneSize[0]
        self.Height = self.sceneSize[1]

        self.waveSources = []

        self.waveHeight = np.zeros((self.Width, self.Height, 3), np.float32)
        self.waveVelocity = np.zeros((self.Width, self.Height, 3), np.float32)
        self.waveWeight = np.ones((self.Width, self.Height, 3), np.float32)

        self.frame = 0
        self.borderRadius  = 150
        self.borderCoef = 1 + 0.05*self.borderRadius/200
        self.absRenderWaves = False

    def update(self):
        #WAVE SOURCES:
        for source in self.waveSources:
            source.update(self.waveHeight, self.frame)

        #ALL WAVES:
        self.waveHeight += updateWaves(self.waveHeight, self.waveVelocity, self.waveWeight, self.Width, self.Height)

        #BORDER:
        self.waveHeight[0:self.Width, 0:self.borderRadius] /= self.borderCoef
        self.waveHeight[0:self.Width, self.Height-self.borderRadius:self.Height] /= self.borderCoef
        self.waveHeight[0:self.borderRadius, 0:self.Height] /= self.borderCoef
        self.waveHeight[self.Width-self.borderRadius:self.Width, 0:self.Height] /= self.borderCoef

    def setWeight(self, weightMap):
        self.waveWeight = weightMap
        pygame.surfarray.blit_array(self.weightOverlay, np.clip((self.waveWeight-1)*100000, 0, 255))

    def render(self):
        if self.absRenderWaves:
            pygame.surfarray.blit_array(self.surface, np.clip(np.abs(self.waveHeight)*255, 0, 255))
        else:
            pygame.surfarray.blit_array(self.surface, np.clip(self.waveHeight*255, 0, 255))
        self.screen.blit(pygame.transform.scale(self.surface, self.screenSize), (0, 0))
        self.screen.blit(self.weightOverlay, (0, 0))
        pygame.display.flip()

    def run(self):
        self.running = True
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            self.clock.tick(60)
            self.update()
            self.render()
            self.frame += 1
            print(int(self.clock.get_fps()))

class waveSource:
    def __init__(self, position : list | tuple, frequency : float, amplitude : float):
        self.pos = position
        self.x = self.pos[0]
        self.y = self.pos[1]
        self.freq = frequency
        self.amp = amplitude

class pointSource(waveSource):
    def update(self, waveHeight, frame):
        waveHeight[self.x, self.y, 0:3] = np.sin(frame*self.freq) * self.amp
        return waveHeight

class directedSource(waveSource):
    def __init__(self, position : list | tuple, frequency : float, amplitude : float, size : int):
        super().__init__(position, frequency, amplitude)
        self.size = size

    def update(self, waveHeight, frame):
        return updateDW(waveHeight, frame, self.x, self.y, self.size, self.freq, time())