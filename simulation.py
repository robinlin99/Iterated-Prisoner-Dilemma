#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Entry point for the Iterated Prisoner's Dilemma simulation.

Initialises the simulation, runs it, and prints the resulting player
database to stdout. The database file (players.db) is reset on each run.
"""

import argparse
import os
import logging
from lib import prisoner_dilemma

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)


def run_sim(plot: bool = False) -> None:
    """Create and run a preconfigured simulation, then print a summary.

    Args:
        plot: If True, display an interactive matplotlib plot at the end.
    """
    db_path = 'players.db'
    try:
        os.remove(db_path)
    except FileNotFoundError:
        pass

    sim = prisoner_dilemma.Simulation(4, 20, 7, True)
    try:
        sim.sim_configuration_1(0.33, plot=plot)
    finally:
        sim.close()

    sim.print_summary()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Iterated Prisoner's Dilemma simulation")
    parser.add_argument('--plot', action='store_true', help='Show interactive plot at the end')
    args = parser.parse_args()
    run_sim(plot=args.plot)
