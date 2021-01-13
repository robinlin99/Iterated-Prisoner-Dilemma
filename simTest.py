import unittest
import prisonerdilemma


class TestGame(unittest.TestCase):
    def test_sim(self):
       sim = prisonerdilemma.Simulation(4,20,7)
       sim.sim_configuration_1(0.33)
       sim.print_players()

if __name__ == '__main__':
    unittest.main()