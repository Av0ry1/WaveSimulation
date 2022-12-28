import pygame
import numpy as np

from numba import njit, prange

@njit()
def update_waves(waveHeight, waveVelocity, waveWeight, Width, Height):
    for x in prange(1, Width-1):
        for y in prange(1, Height-1):
            for k in prange(3):
                waveVelocity[x][y][k] += ((waveHeight[x+1][y][k] + waveHeight[x-1][y][k] + waveHeight[x][y+1][k] + waveHeight[x][y-1][k]) / 4 - waveHeight[x][y][k]) / waveWeight[x][y][k]
    return waveVelocity

@njit()
def update_dw(waveHeight, frame, cx, cy, size, freq):
    for x in prange(cx-size**2, cx+size**2):
        for y in prange(cy-size**2, cy+size**2):
            r = (x - cx)**2 + (y - cy)**2
            fade = np.exp(-r / 2 / size**2) / size
            waveHeight[x, y, 0:3] += fade * np.cos(freq*x) * (np.sin(frame*0.5*freq))

    return waveHeight

@njit()
def border(waveHeight, waveVelocity, Width, Height, borderRadius):
    for x in prange(1, Width-1):
        for y in prange(1, Height-1):
            if x < borderRadius or Width-x < borderRadius or y < borderRadius or Height-y < borderRadius:
                for k in prange(3):
                    if waveVelocity[x][y][k] < 0 and waveHeight[x][y][k] < 0 or waveVelocity[x][y][k] > 0 and waveVelocity[x][y][k] > 0:
                        waveHeight[x][y][k] -= waveHeight[x][y][k]/min(x, Width-x, y, Height-y)**1.2

class Simulation:
    def __init__(self, screenSize : list | tuple, sceneSize : list | tuple):
        self.screenSize = screenSize
        self.screen = pygame.display.set_mode(screenSize, pygame.WINDOWMAXIMIZED)
        self.surface = pygame.Surface(sceneSize)
        self.weightOverlay = pygame.Surface(sceneSize)
        self.weightOverlay = pygame.transform.scale(self.weightOverlay, self.screenSize)
        self.weightOverlay.set_alpha(10)
        self.clock = pygame.time.Clock()

        self.sceneSize = sceneSize
        self.Width = sceneSize[0]
        self.Height = sceneSize[1]

        self.waveSources = []

        self.waveHeight = np.zeros((self.Width, self.Height, 3), np.float32)
        self.waveVelocity = np.zeros((self.Width, self.Height, 3), np.float32)
        self.waveWeight = np.ones((self.Width, self.Height, 3), np.float32)
        self.accumulatedLight = np.zeros((self.Width, self.Height, 3), np.float32)

        self.borderRadius  = 100
        self.accumulate = False

        self.frame = 0

    def setWeight(self, weightMap):
        self.waveWeight = weightMap

        for x in range(1, self.Width-1):
            for y in range(1, self.Height-1):
                for k in range(3):
                    self.waveWeight[x][y][k] = self.waveWeight[x][y][k] + (k*0.065 if self.waveWeight[x][y][k] != 1 else 0)

        pygame.surfarray.blit_array(self.weightOverlay, np.clip((self.waveWeight-1)*100000, 0, 255))
        self.weightOverlay = pygame.transform.scale(self.weightOverlay, self.screenSize)

    def update(self):
        #WAVE SOURCES:
        for source in self.waveSources:
            source.update(self.waveHeight, self.frame)

        #ALL WAVES:
        self.waveHeight += update_waves(self.waveHeight, self.waveVelocity, self.waveWeight, self.Width, self.Height)

        #BORDER:
        border(self.waveHeight, self.waveVelocity, self.Width, self.Height, self.borderRadius)

    def render(self):
        if self.accumulate:
            self.accumulatedLight = (self.accumulatedLight * 299 + np.abs(self.waveHeight)) / 300

            pygame.surfarray.blit_array(self.surface, np.clip(self.accumulatedLight*255, 0, 255))
        else:
            pygame.surfarray.blit_array(self.surface, np.clip(self.waveHeight*255, 0, 255))

        self.screen.blit(pygame.transform.scale(self.surface, self.screenSize), (0, 0))
        self.screen.blit(self.weightOverlay, (0, 0))
        pygame.display.flip()
        #print(int(self.clock.get_fps()))

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
        return update_dw(waveHeight, frame, self.x, self.y, self.size, self.freq)

class rectSource:
    def __init__(self, start_position : list | tuple, end_position : list | tuple,frequency : float, amplitude : float):
        self.pos = [start_position, end_position]
        self.x1 = self.pos[0][0]
        self.x2 = self.pos[1][0]
        self.y1 = self.pos[0][1]
        self.y2 = self.pos[1][1]
        self.freq = frequency
        self.amp = amplitude

    def update(self, waveHeight, frame):
        waveHeight[self.x1:self.x2, self.y1:self.y2, 0:3] = np.sin(frame*self.freq) * self.amp
        return waveHeight