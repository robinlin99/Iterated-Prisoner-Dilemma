#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Shared constants for the Prisoner's Dilemma simulation.
"""

# Maps strategy names to gene characters
STRATEGY_MAP = {
    'Cu':     'a',
    'Du':     'b',
    'Random': 'c',
    'Cp':     'd',
    'TFT':    'e',
    'TFTT':   'f',
    'Prober': 'g',
}

# Reverse lookup: gene character -> strategy name
REVERSE_MAP = {v: k for k, v in STRATEGY_MAP.items()}

# Strategies included in the simulation
IMPLEMENTED = list(STRATEGY_MAP.keys())
