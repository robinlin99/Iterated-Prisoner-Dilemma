#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sqlite3
import logging

from lib import prisoner_dilemma

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)


def print_database(filename: str) -> None:
    conn = sqlite3.connect(filename)
    cur = conn.cursor()
    for row in cur.execute('SELECT * FROM players;'):
        logger.info(row)
    conn.close()


def run_sim() -> None:
    db_path = 'players.db'
    try:
        os.remove(db_path)
    except FileNotFoundError:
        pass

    sim = prisoner_dilemma.Simulation(4, 20, 7, True)
    try:
        sim.sim_configuration_1(0.33)
        sim.print_players()
        sim.traverse_players()
    finally:
        sim.close()

    print_database(db_path)


if __name__ == '__main__':
    run_sim()
