import unittest
import prisonerdilemma
import os
import sqlite3



class TestGame(unittest.TestCase):
    def test_sim(self):
       os.system("rm players.db")
       sim = prisonerdilemma.Simulation(4,20,7,True)
       sim.sim_configuration_1(0.33)
    # sim.print_players()
       sim.traverse_players()
       def database_print():
        # Create a SQL connection to our SQLite database
        con = sqlite3.connect("players.db")
        cur = con.cursor()
        # The result of a "cursor.execute" can be iterated over by row
        for row in cur.execute('SELECT * FROM players;'):
            print(row)
        # Be sure to close the connection
        con.close()
    #    database_print()


if __name__ == '__main__':
    unittest.main()