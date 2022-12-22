import math

import pygame
import numpy as np

from numba import njit

W, H = 800, 800
RES = (W, H)

@njit()
def update(waveHeight, waveVelocity):
    for x in range(1, W-1):
        for y in range(1, H-1):
            waveVelocity[x][y] += (waveHeight[x+1][y] + waveHeight[x-1][y] + waveHeight[x][y+1] + waveHeight[x][y-1]) / 4 - waveHeight[x][y]

    return waveVelocity

def main():
    pygame.init()

    screen = pygame.display.set_mode(RES)
    surface = pygame.Surface(RES)
    clock = pygame.time.Clock()

    frame = 0

    waveVelocity = np.zeros((W, H), np.float32)
    waveHeight = np.zeros((W, H), np.float32)
    waveWeight = np.zeros((W, H), np.float32).fill(1)

    for _ in iter(int, 1):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        clock.tick(100)

        waveHeight[1:W-1][1:H-1] += update(waveHeight, waveVelocity)[1:W-1][1:H-1]

        waveHeight[W//2][H//2] = math.sin(frame*0.3)
        waveVelocity[W//2][H//2] = 0

        renderArray = (waveHeight).copy()*255

        pygame.surfarray.blit_array(surface, np.clip(np.dstack([renderArray for i in range(3)]), 0, 1000))

        screen.blit(surface, (0, 0))
        pygame.display.flip()

        frame += 1
        print(int(clock.get_fps()))

if __name__=='__main__':
    main()