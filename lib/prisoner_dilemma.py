#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Iterated Prisoner's Dilemma simulation engine.

Provides the Simulation class which manages a population of Player agents,
runs round-robin tournaments, applies genetic crossover to top performers, and
tracks genomic statistics over time. Results are persisted to a SQLite database
and visualised with matplotlib.

Strategies are encoded as single-character genes (see lib/config.py). The
payoff matrix follows the standard formulation:
    - Mutual cooperation:  (3, 3)
    - Mutual defection:    (0, 0)
    - Defect vs cooperate: (5, -1)
    - Cooperate vs defect: (-1, 5)
"""

from __future__ import annotations

import heapq
import logging
import re
import sqlite3
import subprocess
import random
from collections import Counter
from typing import Optional

import matplotlib
matplotlib.use('Agg')  # render to file — avoids macOS main thread requirement
import matplotlib.pyplot as plt

import lib.player as p
import lib.tree as tree
from lib.config import STRATEGY_MAP, REVERSE_MAP, IMPLEMENTED

logger = logging.getLogger(__name__)

# Type aliases
Move = str       # 'c' or 'd'
Gene = str       # single gene character e.g. 'e'
Score = int


def evaluation(moveA: Move, moveB: Move) -> tuple[Score, Score]:
    """Return the payoff tuple (scoreA, scoreB) for a single round.

    Args:
        moveA: Move by player A — 'c' (cooperate) or 'd' (defect).
        moveB: Move by player B — 'c' (cooperate) or 'd' (defect).

    Returns:
        A tuple (scoreA, scoreB) of integer payoffs.
    """
    if moveA == 'c' and moveB == 'c':
        return 3, 3
    if moveA == 'c' and moveB == 'd':
        return -1, 5
    if moveA == 'd' and moveB == 'c':
        return 5, -1
    # moveA == 'd' and moveB == 'd'
    return 0, 0


def generate_score(A: p.Player, B: p.Player, gene_length: int) -> tuple[Score, Score]:
    """Simulate a full game between two players and return their total scores.

    Args:
        A: First Player.
        B: Second Player.
        gene_length: Number of moves to play.

    Returns:
        A tuple (A_total, B_total) of cumulative integer scores.
    """
    a_sum: Score = 0
    b_sum: Score = 0
    for i in range(gene_length):
        moveA = A.move(B, i)
        moveB = B.move(A, i)
        a_score, b_score = evaluation(moveA, moveB)
        a_sum += a_score
        b_sum += b_score
    return a_sum, b_sum


class Simulation:
    """Manages the full lifecycle of an Iterated Prisoner's Dilemma simulation.

    Players compete in round-robin tournaments each epoch. Top scorers form a
    mate pool and reproduce via genetic crossover. Offspring are added to the
    population and all players are persisted to a SQLite database.

    Attributes:
        poolsize: Number of players per strategy in the initial population.
        genesize: Length of each player's gene string (moves per game).
        totalrounds: Number of epochs to simulate.
        players: List of all active Player instances.
        tree_hashmap: Maps each Player to its TreeNode for lineage tracking.
        genetic_instance: Maps gene characters to their total count in the pool.
        geneticpercentage: Per-epoch percentage of each gene in the population.
        geneticcount: Per-epoch raw count of each gene in the population.
    """

    def __init__(
        self,
        pool_size: int,
        gene_length: int,
        total_rounds: int,
        predetermined: bool,
    ) -> None:
        """Initialise the simulation.

        Args:
            pool_size: Number of agents to create per strategy.
            gene_length: Number of moves (and gene characters) per player.
            total_rounds: Number of tournament epochs to run.
            predetermined: If True, populate the initial player pool with all
                           implemented strategies.
        """
        self.pool_size: int = pool_size
        self.gene_size: int = gene_length
        self.total_genetic: int = 0
        self.total_rounds: int = total_rounds
        self.players: list[p.Player] = []
        self.tree_hashmap: dict[p.Player, tree.TreeNode] = {}
        self.genetic_instance: dict[Gene, int] = {}
        self.experiment_title: str = ""
        self.genetic_percentage: dict[Gene, list[float]] = {}
        self.genetic_count: dict[Gene, list[int]] = {}

        self.conn: Optional[sqlite3.Connection] = sqlite3.connect('players.db')
        self._init_db()

        if predetermined:
            self._populate_players()

    def _init_db(self) -> None:
        """Create the players table if it does not already exist."""
        c = self.conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS players
                     (strategy text, size real, bitstring text, id text, original text)''')
        self.conn.commit()

    def _populate_players(self) -> None:
        """Create the initial player pool and persist them to the database."""
        c = self.conn.cursor()
        rows: list[tuple] = []
        for strategy in IMPLEMENTED:
            gene_char = STRATEGY_MAP[strategy]
            for _ in range(self.pool_size):
                new = p.Player(strategy, self.gene_size)
                self.players.append(new)
                rows.append((strategy, self.gene_size, new.strategy_bitstring, new.id, "True"))
                self.total_genetic += self.gene_size
                self.genetic_instance[gene_char] = \
                    self.genetic_instance.get(gene_char, 0) + self.gene_size
        c.executemany("INSERT INTO players VALUES (?, ?, ?, ?, ?)", rows)
        self.conn.commit()

        for player in self.players:
            self.tree_hashmap[player] = tree.TreeNode(player, player.id)

    def close(self) -> None:
        """Close the SQLite database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None

    def sim_configuration_1(self, rp: float, plot: bool = False) -> None:
        """Run the Strictly-Growth, Fixed Growth Rate (SGFGR) simulation.

        Each epoch: players compete in a full round-robin, the top `rp`
        fraction are selected as a mate pool, random pairs reproduce via
        crossover, and offspring are appended to the population. The
        population only grows — no players are eliminated.

        Args:
            rp: Reproduction rate (0–1). Fraction of the population that
                forms the mate pool each epoch.
            plot: If True, save and open a plot after all epochs complete.
        """
        self.experiment_title = (
            "Configuration 1 - Strictly-Growth (SG), "
            "Fixed Growth Rate (FGR) - SGFGR"
        )
        c = self.conn.cursor()

        for round_num in range(self.total_rounds):
            self._record_stats()
            players = self.players
            n = len(players)
            scores: dict[p.Player, Score] = {player: 0 for player in players}

            # Round-robin scoring
            for left in range(n - 1):
                for right in range(left + 1, n):
                    player_a = players[left]
                    player_b = players[right]
                    player_a.move_history = []
                    player_b.move_history = []
                    a_score, b_score = generate_score(player_a, player_b, self.gene_size)
                    logger.debug(
                        "Round %d: %s vs %s -> %d, %d",
                        round_num, player_a.strategy_bitstring,
                        player_b.strategy_bitstring, a_score, b_score
                    )
                    scores[player_a] += a_score
                    scores[player_b] += b_score

            # Pick top performers without a full sort
            n_opp = max(2, int(rp * n))
            matepool: list[p.Player] = heapq.nlargest(n_opp, scores, key=scores.__getitem__)

            # Reproduce and batch-insert offspring
            new_rows: list[tuple] = []
            new_players: list[p.Player] = []
            for _ in range(len(matepool)):
                A, B = random.sample(matepool, 2)
                logger.debug(
                    "Round %d mates: %s x %s",
                    round_num, A.strategy_bitstring, B.strategy_bitstring
                )
                child1, child2 = A.crossover(B)

                for child in (child1, child2):
                    new_rows.append(("N/A", child.size, child.strategy_bitstring, child.id, "False"))
                    gene_counts: Counter[Gene] = Counter(child.strategy_bitstring)
                    for gene, cnt in gene_counts.items():
                        self.genetic_instance[gene] = self.genetic_instance.get(gene, 0) + cnt
                        self.total_genetic += cnt
                    self.tree_hashmap[child] = tree.TreeNode(child, child.id)
                    new_players.append(child)

                child1node = self.tree_hashmap[child1]
                child2node = self.tree_hashmap[child2]
                for parent in (A, B):
                    pnode = self.tree_hashmap[parent]
                    pnode.left = child1node
                    pnode.right = child2node

            c.executemany("INSERT INTO players VALUES (?, ?, ?, ?, ?)", new_rows)
            self.conn.commit()
            self.players.extend(new_players)

            logger.info(
                "Epoch %d/%d complete — population: %d, offspring added: %d",
                round_num + 1, self.total_rounds, len(self.players), len(new_players)
            )
            logger.debug("Round %d complete. Population: %d", round_num, len(self.players))

        self.plot_percentage_count(plot=plot)

    def print_players(self) -> None:
        """Log the ID and gene string of every player at INFO level."""
        for player in self.players:
            logger.info("%s  %s", player.id, player.strategy_bitstring)

    def traverse_players(self) -> None:
        """Log an inorder traversal of the lineage tree for every player."""
        for player in self.players:
            logger.info("--- Traversal ---")
            self.tree_hashmap[player].inorder()

    def _record_stats(self) -> None:
        """Record count and percentage for each gene character for the current epoch."""
        for gene, count in self.genetic_instance.items():
            self.genetic_count.setdefault(gene, []).append(count)
            pct: float = count / self.total_genetic if self.total_genetic else 0.0
            self.genetic_percentage.setdefault(gene, []).append(pct)
            logger.debug("%s: %d (%.4f%%)", gene, count, pct)

    def print_summary(self) -> None:
        """Pretty-print a colour summary of the simulation results to stdout."""
        RESET  = "\033[0m"
        BOLD   = "\033[1m"
        CYAN   = "\033[36m"
        GREEN  = "\033[32m"
        YELLOW = "\033[33m"
        WHITE  = "\033[37m"
        DIM    = "\033[2m"

        BAR_WIDTH = 20
        WIDTH = 60

        def strip(s: str) -> str:
            return re.sub(r'\033\[[0-9;]*m', '', s)

        def box_row(content: str) -> None:
            visible_len = len(strip(content))
            if visible_len > WIDTH:
                ratio = WIDTH / visible_len
                content = content[:int(len(content) * ratio) - 1] + "…"
            padding = WIDTH - len(strip(content))
            print(f"{CYAN}│{RESET}{content}{' ' * padding}{CYAN}│{RESET}")

        total_players: int = len(self.players)
        original: int = sum(1 for pl in self.players if pl.parents is None)
        offspring: int = total_players - original

        gene_totals: dict[Gene, int] = Counter(
            gene for player in self.players for gene in player.strategy_bitstring
        )
        total_genes: int = sum(gene_totals.values())

        final_pcts: dict[Gene, float] = {
            gene: pcts[-1]
            for gene, pcts in self.genetic_percentage.items()
            if pcts
        }
        dominant_gene: Optional[Gene] = max(final_pcts, key=final_pcts.get) if final_pcts else None

        # ── header ──────────────────────────────────────────────
        print()
        print(f"{CYAN}╭{'─' * WIDTH}╮{RESET}")
        title = "SIMULATION SUMMARY"
        pad = (WIDTH - len(title)) // 2
        print(f"{CYAN}│{RESET}{' ' * pad}{BOLD}{WHITE}{title}{RESET}{' ' * (WIDTH - pad - len(title))}{CYAN}│{RESET}")
        print(f"{CYAN}├{'─' * WIDTH}┤{RESET}")

        def meta(label: str, value_str: str) -> None:
            box_row(f"  {BOLD}{label:<13}{RESET} {value_str}")

        max_val = WIDTH - 16
        title_str = self.experiment_title
        if len(title_str) > max_val:
            title_str = title_str[:max_val - 1] + "…"

        meta("Experiment",  f"{YELLOW}{title_str}{RESET}")
        meta("Epochs",      str(self.total_rounds))
        meta("Gene length", str(self.gene_size))
        meta("Population",  f"{total_players} total  {DIM}({original} original, {offspring} offspring){RESET}")

        # ── gene table ───────────────────────────────────────────
        print(f"{CYAN}├{'─' * WIDTH}┤{RESET}")
        box_row(f"  {BOLD}{'Strategy':<10} {'Gene':^4}  {'Count':>6}  {'%':>5}  {'Bar':<{BAR_WIDTH}}{RESET}")
        box_row(f"  {DIM}{'─' * (WIDTH - 2)}{RESET}")

        for gene, count in sorted(gene_totals.items(), key=lambda x: x[1], reverse=True):
            name   = REVERSE_MAP.get(gene, gene)
            pct    = count / total_genes * 100 if total_genes else 0.0
            filled = int(pct / 100 * BAR_WIDTH)
            bar    = f"{GREEN}{'█' * filled}{DIM}{'░' * (BAR_WIDTH - filled)}{RESET}"
            box_row(f"  {name:<10} {gene:^4}  {count:>6}  {pct:>4.1f}%  {bar}")

        # ── dominant ─────────────────────────────────────────────
        if dominant_gene:
            print(f"{CYAN}├{'─' * WIDTH}┤{RESET}")
            dom_name = REVERSE_MAP.get(dominant_gene, dominant_gene)
            dom_pct  = final_pcts[dominant_gene] * 100
            box_row(f"  {BOLD}Dominant:{RESET}  {GREEN}{dom_name}{RESET}  ({dom_pct:.1f}% of gene pool)")

        print(f"{CYAN}╰{'─' * WIDTH}╯{RESET}")
        print()

    def plot_percentage_count(self, plot: bool = False) -> None:
        """Save a two-panel plot of population count and percentage over epochs.

        Args:
            plot: If True, save to PNG and open in Preview. If False, skip.
        """
        if not plot:
            return
        time: list[int] = list(range(self.total_rounds))
        fig, (ax1, ax2) = plt.subplots(2)
        fig.suptitle(self.experiment_title)

        for gene, counts in self.genetic_count.items():
            ax1.plot(time, counts, '-o', label=REVERSE_MAP.get(gene, gene))
        ax1.set(xlabel="Epoch", ylabel="Population")
        ax1.legend()

        for gene, pcts in self.genetic_percentage.items():
            ax2.plot(time, pcts, '-o', label=REVERSE_MAP.get(gene, gene))
        ax2.set(xlabel="Epoch", ylabel="Population Percentage")
        ax2.legend()

        plt.tight_layout()
        plot_path = 'simulation_plot.png'
        plt.savefig(plot_path, dpi=150)
        plt.close()
        logger.info("Plot saved to %s", plot_path)
