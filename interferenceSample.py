import numpy as np

from src.simulation import Simulation, rectSource

freq = 0.1

k = 1

sim = Simulation((800, 800), (800*k, 800*k))
sim.borderRadius = 100*k
sim.waveSources.append(rectSource((102*k, 300*k), (103*k, 500*k), freq, -1))

weightMap = np.ones((sim.Width, sim.Height, 3), np.float32)

weightMap[103*k:134*k, 0*k:799*k] = 10000000
weightMap[103*k:134*k, 350*k:370*k] = 1
weightMap[103*k:134*k, 430*k:450*k] = 1

sim.setWeight(weightMap)
sim.accumulate = 1

sim.run()