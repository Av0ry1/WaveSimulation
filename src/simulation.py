import pygame
import numpy as np
from numba import njit, prange

@njit(parallel = True)
def updateWaves(waveHeight, waveVelocity, waveWeight, Width, Height):
    for x in range(1, Width-1):
        for y in range(1, Height-1):
            waveVelocity[x][y] += (((waveHeight[x+1][y] + waveHeight[x-1][y] + waveHeight[x][y+1] + waveHeight[x][y-1]) / 4 - waveHeight[x][y]) / waveWeight[x][y])
    return waveVelocity

class Simulation:
    def __init__(self, screenSize : list | tuple, sceneSize : list | tuple, sources):
        self.screenSize = screenSize
        self.screen = pygame.display.set_mode(screenSize, pygame.FULLSCREEN)
        self.surface = pygame.Surface(sceneSize)
        self.clock = pygame.time.Clock()

        self.sceneSize = sceneSize
        self.Width = self.sceneSize[0]
        self.Height = self.sceneSize[1]

        self.waveSources = sources

        self.waveHeight = np.zeros((self.Width, self.Height), np.float32)
        self.waveVelocity = np.zeros((self.Width, self.Height), np.float32)
        self.waveWeight = np.ones((self.Width, self.Height), np.float32)

        self.frame = 0
        self.borderRadius  = 100
        self.borderCoef = 1 + 0.05*self.borderRadius/200

    def update(self):
        #WAVE SOURCES:
        for source in self.waveSources:
            source.update(self.waveHeight, self.frame)

        #ALL WAVES:
        #self.waveVelocity += ((np.roll(self.waveHeight, 1, 1) + np.roll(self.waveHeight, -1, 1) + np.roll(self.waveHeight, 1, 0) + np.roll(self.waveHeight, -1, 0)) / 4 - self.waveHeight) / self.waveWeight
        #self.waveHeight += self.waveVelocity
        self.waveHeight += updateWaves(self.waveHeight, self.waveVelocity, self.waveWeight, self.Width, self.Height)

        #BORDER:
        self.waveHeight[0:self.Width, 0:self.borderRadius] /= self.borderCoef
        self.waveHeight[0:self.Width, self.Height-self.borderRadius:self.Height] /= self.borderCoef
        self.waveHeight[0:self.borderRadius, 0:self.Height] /= self.borderCoef
        self.waveHeight[self.Width-self.borderRadius:self.Width, 0:self.Height] /= self.borderCoef

    def render(self):
        pygame.surfarray.blit_array(self.surface, np.clip(self.waveHeight*255, 0, 255))
        self.screen.blit(pygame.transform.scale(self.surface, self.screenSize), (0, 0))
        pygame.display.flip()

    def run(self):
        self.running = True
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
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
        self.amplitude = amplitude

class pointSource(waveSource):
    def update(self, waveHeight, frame):
        waveHeight[self.x][self.y] = np.sin(frame*self.freq) * self.amplitude
        return waveHeight

class directedSource(waveSource):
    def update(self, waveHeight, frame):
        pass