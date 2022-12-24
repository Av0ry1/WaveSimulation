from src.simulation import Simulation, pointSource

src = [pointSource((800, 450), 0.2, 1)]
sim = Simulation((1600, 900), (1600, 900), src)
sim.run()