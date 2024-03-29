from src.simulation import Simulation, pointSource

sim = Simulation((800, 800), (800, 800))
sim.borderRadius = 50
sim.waveSources.append(pointSource((400, 400), 0.1, 1.6))

sim.run()