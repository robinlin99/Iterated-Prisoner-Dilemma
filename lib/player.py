#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Iterated Prisoner's Dilemma player.

Each Player holds a strategy encoded as a fixed-length gene string. Genes are
single characters mapping to one of the implemented strategies (see
lib/config.py). Players can compete move-by-move and reproduce via crossover
with optional point mutation.
"""

from __future__ import annotations

import random
import uuid
import logging
from typing import Optional

from lib.config import STRATEGY_MAP

logger = logging.getLogger(__name__)

# Type alias for a single move character
Move = str  # 'c' or 'd'


class Player:
    """An agent in the Iterated Prisoner's Dilemma.

    The agent's behaviour is fully determined by its strategy_bitstring — a
    sequence of gene characters where each character encodes one of the
    supported strategies for that move index.

    Attributes:
        strategy_bitstring: Gene string encoding the player's strategy.
        size: Length of the gene string (number of moves per game).
        id: Unique UUID string identifying this player.
        movehistory: List of moves made so far in the current game.
        parents: Parent Player instances if this player was bred, else None.
        children: Child Player instances produced by crossover, else None.
    """

    def __init__(
        self,
        strategy: Optional[str],
        size: int,
        is_pure: bool = True,
        genes: Optional[str] = None,
        parents: Optional[list[Player]] = None,
    ) -> None:
        """Initialise a Player.

        Args:
            strategy: Strategy name (e.g. 'TFT') used when is_pure is True.
            size: Gene string length.
            is_pure: If True, build a homogeneous gene string from strategy.
                    If False, use the genes argument directly.
            genes: Pre-built gene string used when is_pure is False.
            parents: Parent players when is_pure is False.
        """
        self.move_history: list[Move] = []
        self.size: int = size
        self.id: str = str(uuid.uuid1())
        if is_pure:
            assert strategy is not None, "strategy must be provided when is_pure=True"
            self.strategy_bitstring: str = STRATEGY_MAP[strategy] * size
            self.parents: Optional[list[Player]] = None
            self.children: Optional[list[Player]] = None
        else:
            assert genes is not None, "genes must be provided when is_pure=False"
            self.strategy_bitstring = genes
            self.parents = parents
            self.children = None

    def crossover(self, mate: Player) -> tuple[Player, Player]:
        """Produce two offspring by crossing gene strings with this player and mate.

        A random left and right cut point are chosen, and the middle segment is
        swapped between the two parents. Each child may also undergo a random
        point mutation.

        Args:
            mate: Another Player of the same size to breed with.

        Returns:
            A tuple (childA, childB) of two new Player instances.
        """
        assert self.size == mate.size
        left = random.randint(0, self.size // 2)
        right = random.randint(self.size // 2, self.size)
        me_left    = self.strategy_bitstring[0:left]
        mate_left  = mate.strategy_bitstring[0:left]
        me_mid     = self.strategy_bitstring[left:right]
        mate_mid   = mate.strategy_bitstring[left:right]
        me_right   = self.strategy_bitstring[right:]
        mate_right = mate.strategy_bitstring[right:]

        childA_bs = _maybe_mutate(me_left + mate_mid + me_right)
        childB_bs = _maybe_mutate(mate_left + me_mid + mate_right)

        childA = Player(None, self.size, False, childA_bs, [self, mate])
        childB = Player(None, self.size, False, childB_bs, [self, mate])
        self.children = [childA, childB]
        mate.children = [childA, childB]
        return childA, childB

    def move(self, opp: Player, move_index: int) -> Move:
        """Return this player's move for the given move index.

        The gene character at move_index determines the strategy used. The move
        is appended to move_history before returning.

        Args:
            opp: The opposing Player (used by reactive strategies like TFT).
            move_index: Zero-based index of the current move in the game.

        Returns:
            'c' for cooperate or 'd' for defect.
        """
        strategy: str = self.strategy_bitstring[move_index]
        prev_index: int = move_index - 1
        m: Move

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
            m = 'c' if move_index == 0 else opp.move_history[prev_index]

        # Tit for Two Tats
        elif strategy == 'f':
            if move_index <= 1:
                m = 'c'
            else:
                opp1 = opp.move_history[prev_index]
                opp2 = opp.move_history[prev_index - 1]
                m = 'd' if (opp1 == 'd' and opp2 == 'd') else 'c'

        # Prober: open with D, C, C then exploit or TFT
        elif strategy == 'g':
            if move_index == 0:
                m = 'd'
            elif move_index in (1, 2):
                m = 'c'
            else:
                if opp.move_history[1] == 'c' and opp.move_history[2] == 'c':
                    m = 'd'
                else:
                    m = opp.move_history[prev_index]

        else:
            logger.warning("Unknown strategy gene '%s', defaulting to cooperate", strategy)
            m = 'c'

        self.move_history.append(m)
        return m


def _maybe_mutate(bitstring: str, rate: float = 0.01) -> str:
    """Randomly replace each gene character with probability `rate`.

    Args:
        bitstring: The gene string to potentially mutate.
        rate: Per-gene mutation probability (default 1%).

    Returns:
        A new gene string with any mutations applied.
    """
    genes: list[str] = list(STRATEGY_MAP.values())
    return ''.join(
        random.choice(genes) if random.random() < rate else ch
        for ch in bitstring
    )
