import numpy as np

from src.simulation import Simulation, directedSource

sim = Simulation((1600, 900), (1600, 900))
sim.waveSources.append(directedSource((400, 400), 1, 1, 20))

weightMap = np.ones((sim.Width, sim.Height, 3), np.float32)

for x in range(1, sim.Width-1):
    for y in range(1, sim.Height-1):
        for k in range(3):
            if -y*0.6+150 < x-800 < y*0.6-150 and y < 600:
                weightMap[x][y][k] = 1.600

sim.setWeight(weightMap)
sim.accumulate = 1

sim.run()