#!/usr/bin/env python3

import os
import sqlite3
from lib import prisoner_dilemma


def print_database(filename: str) -> None:
    con = sqlite3.connect(filename)
    cur = con.cursor()
    for row in cur.execute('SELECT * FROM players;'):
        print(row)
    con.close()


def run_sim() -> None:
    os.system("rm players.db")
    sim = prisoner_dilemma.Simulation(4, 20, 7, True)
    sim.sim_configuration_1(0.33)
    sim.print_players()
    sim.traverse_players()
    print_database("players.db")


if __name__ == '__main__':
    run_sim()
