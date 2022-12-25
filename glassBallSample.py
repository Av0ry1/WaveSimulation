import numpy as np

from src.simulation import Simulation, directedSource

sim = Simulation((1600, 900), (1600, 900))
sim.waveSources.append(directedSource((400, 300), 1, 1, 20))

weightMap = np.ones((sim.Width, sim.Height, 3), np.float32)

for x in range(1, sim.Width-1):
    for y in range(1, sim.Height-1):
        for k in range(3):
            if (x-800)**2 + (y-450)**2 <= 150**2:
                weightMap[x][y][k] = 1.400 + k*0.05

sim.setWeight(weightMap)
sim.absRenderWaves = True

sim.run()