#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module contains definitions of an Iterated Prisoner's Dilemma player.
"""

import random
import uuid
import logging

from lib.config import STRATEGY_MAP

logger = logging.getLogger(__name__)


class Player():
    def __init__(self, strategy, size, isPure=True, genes=None, parents=None):
        self.movehistory = []
        self.size = size
        self.id = str(uuid.uuid1())
        if isPure:
            self.strategy_bitstring = STRATEGY_MAP[strategy] * size
            self.parents = None
            self.children = None
        else:
            self.strategy_bitstring = genes
            self.children = None
            self.parents = parents

    def crossover(self, mate):
        assert self.size == mate.size
        left = random.randint(0, self.size // 2)
        right = random.randint(self.size // 2, self.size)
        me_left   = self.strategy_bitstring[0:left]
        mate_left = mate.strategy_bitstring[0:left]
        me_mid    = self.strategy_bitstring[left:right]
        mate_mid  = mate.strategy_bitstring[left:right]
        me_right   = self.strategy_bitstring[right:]
        mate_right = mate.strategy_bitstring[right:]

        # Optionally introduce a point mutation in each child
        childA_bs = _maybe_mutate(me_left + mate_mid + me_right)
        childB_bs = _maybe_mutate(mate_left + me_mid + mate_right)

        childA = Player(None, self.size, False, childA_bs, [self, mate])
        childB = Player(None, self.size, False, childB_bs, [self, mate])
        self.children = [childA, childB]
        mate.children = [childA, childB]
        return childA, childB

    def move(self, opp, moveindex):
        strategy = self.strategy_bitstring[moveindex]
        previndex = moveindex - 1

        # Always cooperate
        if strategy == 'a':
            m = 'c'

        # Always defect
        elif strategy == 'b':
            m = 'd'

        # Random
        elif strategy == 'c':
            m = 'c' if random.random() > 0.5 else 'd'

        # Cooperate with probability 0.7
        elif strategy == 'd':
            m = 'c' if random.random() < 0.7 else 'd'

        # Tit for Tat
        elif strategy == 'e':
            m = 'c' if moveindex == 0 else opp.movehistory[previndex]

        # Tit for Two Tats
        elif strategy == 'f':
            if moveindex <= 1:
                m = 'c'
            else:
                opp1 = opp.movehistory[previndex]
                opp2 = opp.movehistory[previndex - 1]
                m = 'd' if (opp1 == 'd' and opp2 == 'd') else 'c'

        # Prober: open with D, C, C then exploit or TFT
        elif strategy == 'g':
            if moveindex == 0:
                m = 'd'
            elif moveindex == 1:
                m = 'c'
            elif moveindex == 2:
                m = 'c'
            else:
                if opp.movehistory[1] == 'c' and opp.movehistory[2] == 'c':
                    m = 'd'
                else:
                    m = opp.movehistory[previndex]

        else:
            logger.warning("Unknown strategy gene '%s', defaulting to cooperate", strategy)
            m = 'c'

        self.movehistory.append(m)
        return m


def _maybe_mutate(bitstring: str, rate: float = 0.01) -> str:
    """Randomly flip each gene with probability `rate`."""
    genes = list(STRATEGY_MAP.values())
    return ''.join(
        random.choice(genes) if random.random() < rate else ch
        for ch in bitstring
    )
