#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module contains definitions of an Iterated Prisoner's Dilemma simulation.
"""

import random
import logging
import sqlite3

import matplotlib.pyplot as plt

import lib.player as p
import lib.tree as tree
from lib.config import STRATEGY_MAP, REVERSE_MAP, IMPLEMENTED

logger = logging.getLogger(__name__)


def evaluation(moveA, moveB):
    if moveA == 'c' and moveB == 'c':
        return 3, 3
    if moveA == 'c' and moveB == 'd':
        return -1, 5
    if moveA == 'd' and moveB == 'c':
        return 5, -1
    if moveA == 'd' and moveB == 'd':
        return 0, 0


def generate_score(A, B, gene_length):
    ASum = 0
    BSum = 0
    for i in range(gene_length):
        moveA = A.move(B, i)
        moveB = B.move(A, i)
        AScore, BScore = evaluation(moveA, moveB)
        ASum += AScore
        BSum += BScore
    return ASum, BSum


class Simulation():
    def __init__(self, pool_size, gene_length, totalrounds, predetermined):
        self.poolsize = pool_size
        self.genesize = gene_length
        self.totalgenetic = 0
        self.totalrounds = totalrounds
        self.players = []
        self.game_hashmap = {}
        self.tree_hashmap = {}
        self.genetic_instance = {}
        self.experimenttitle = ""
        self.geneticpercentage = {}
        self.geneticcount = {}

        self.conn = sqlite3.connect('players.db')
        self._init_db()

        if predetermined:
            self._populate_players()

    def _init_db(self):
        c = self.conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS players
                     (strategy text, size real, bitstring text, id text, original text)''')
        self.conn.commit()

    def _populate_players(self):
        c = self.conn.cursor()
        for strategy in IMPLEMENTED:
            gene_char = STRATEGY_MAP[strategy]
            for _ in range(self.poolsize):
                new = p.Player(strategy, self.genesize)
                self.players.append(new)
                c.execute(
                    "INSERT INTO players VALUES (?, ?, ?, ?, ?)",
                    (strategy, self.genesize, new.strategy_bitstring, new.id, "True")
                )
                self.totalgenetic += self.genesize
                self.genetic_instance[gene_char] = \
                    self.genetic_instance.get(gene_char, 0) + self.genesize
        self.conn.commit()

        for player in self.players:
            self.tree_hashmap[player] = tree.TreeNode(player, player.id)

    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None

    def sim_configuration_1(self, rp):
        self.experimenttitle = (
            "Configuration 1 - Strictly-Growth (SG), "
            "Fixed Growth Rate (FGR) - SGFGR"
        )
        c = self.conn.cursor()
        reprod_rate = rp

        for round_num in range(self.totalrounds):
            self._process_count()
            self._process_percentage()
            self.game_hashmap = {player: 0 for player in self.players}

            # Round-robin scoring
            for left in range(len(self.players) - 1):
                for right in range(left + 1, len(self.players)):
                    playerA = self.players[left]
                    playerB = self.players[right]
                    # Reset move histories for a fresh game
                    playerA.movehistory = []
                    playerB.movehistory = []
                    ARoundSum, BRoundSum = generate_score(playerA, playerB, self.genesize)
                    logger.debug(
                        "Round %d: %s vs %s -> %d, %d",
                        round_num, playerA.strategy_bitstring,
                        playerB.strategy_bitstring, ARoundSum, BRoundSum
                    )
                    self.game_hashmap[playerA] += ARoundSum
                    self.game_hashmap[playerB] += BRoundSum

            # Sort by score descending
            self.game_hashmap = dict(sorted(
                self.game_hashmap.items(), key=lambda item: item[1], reverse=True
            ))

            # Select top performers as mate pool
            n_opp = max(2, int(reprod_rate * len(self.players)))
            matepool = list(self.game_hashmap.keys())[:n_opp]

            # Reproduce
            for _ in range(len(matepool)):
                mates = random.sample(matepool, 2)
                A, B = mates[0], mates[1]
                logger.debug(
                    "Round %d mates: %s x %s",
                    round_num, A.strategy_bitstring, B.strategy_bitstring
                )
                child1, child2 = A.crossover(B)

                for child in (child1, child2):
                    c.execute(
                        "INSERT INTO players VALUES (?, ?, ?, ?, ?)",
                        ("N/A", child.size, child.strategy_bitstring, child.id, "False")
                    )
                    for gene in child.strategy_bitstring:
                        self.genetic_instance[gene] = \
                            self.genetic_instance.get(gene, 0) + 1
                        self.totalgenetic += 1
                    child_node = tree.TreeNode(child, child.id)
                    self.tree_hashmap[child] = child_node
                self.conn.commit()

                child1node = self.tree_hashmap[child1]
                child2node = self.tree_hashmap[child2]
                for parent in (A, B):
                    pnode = self.tree_hashmap[parent]
                    pnode.left = child1node
                    pnode.right = child2node

                self.players.extend([child1, child2])
                self.game_hashmap[child1] = 0
                self.game_hashmap[child2] = 0

            for player, score in self.game_hashmap.items():
                logger.debug("%s: %d", player.strategy_bitstring, score)

            self.print_players()

        self.plot_percentage_count()

    def print_players(self):
        for player in self.players:
            logger.info("%s  %s", player.id, player.strategy_bitstring)

    def traverse_players(self):
        for player in self.players:
            logger.info("--- Traversal ---")
            self.tree_hashmap[player].inorder()

    def _process_percentage(self):
        for gene, count in self.genetic_instance.items():
            pct = count / self.totalgenetic if self.totalgenetic else 0
            self.geneticpercentage.setdefault(gene, []).append(pct)
            logger.debug("%s: %.4f%%", gene, pct)

    def _process_count(self):
        for gene, count in self.genetic_instance.items():
            self.geneticcount.setdefault(gene, []).append(count)
            logger.debug("%s: %d", gene, count)

    def plot_percentage_count(self):
        time = list(range(self.totalrounds))
        fig, (ax1, ax2) = plt.subplots(2)
        fig.suptitle(self.experimenttitle)

        for gene, counts in self.geneticcount.items():
            ax1.plot(time, counts, '-o', label=REVERSE_MAP.get(gene, gene))
        ax1.set(xlabel="Epoch", ylabel="Population")
        ax1.legend()

        for gene, pcts in self.geneticpercentage.items():
            ax2.plot(time, pcts, '-o', label=REVERSE_MAP.get(gene, gene))
        ax2.set(xlabel="Epoch", ylabel="Population Percentage")
        ax2.legend()

        plt.tight_layout()
        plt.show()
