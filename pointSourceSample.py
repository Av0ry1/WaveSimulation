from src.simulation import Simulation, pointSource

sim = Simulation((1600, 900), (1600, 900))
sim.waveSources.append(pointSource((800, 450), 0.2, 1))

sim.run()