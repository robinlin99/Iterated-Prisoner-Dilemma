#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
import lib.player as player
from lib.prisoner_dilemma import generate_score, evaluation


class TestPlayer(unittest.TestCase):
    def setUp(self):
        self.gene_size = 20
        self.A = player.Player('Cu', self.gene_size)
        self.B = player.Player('Du', self.gene_size)
        self.E = player.Player('TFT', self.gene_size)
        # Opponent with known move history for TFT testing
        self.F = player.Player('Cu', self.gene_size)
        self.F.move_history = ['d'] * self.gene_size

    def test_always_cooperate(self):
        for i in range(self.gene_size):
            self.assertEqual(self.A.move(self.B, i), 'c')

    def test_always_defect(self):
        b = player.Player('Du', self.gene_size)
        for i in range(self.gene_size):
            self.assertEqual(b.move(self.A, i), 'd')

    def test_tft_first_move_cooperates(self):
        e = player.Player('TFT', self.gene_size)
        self.assertEqual(e.move(self.F, 0), 'c')

    def test_tft_copies_opponent(self):
        e = player.Player('TFT', self.gene_size)
        e.move(self.F, 0)  # first move
        for i in range(1, self.gene_size):
            result = e.move(self.F, i)
            self.assertEqual(result, self.F.move_history[i - 1])

    def test_tftt_cooperates_first_two(self):
        f = player.Player('TFTT', self.gene_size)
        opp = player.Player('Du', self.gene_size)
        opp.move_history = ['d'] * self.gene_size
        self.assertEqual(f.move(opp, 0), 'c')
        self.assertEqual(f.move(opp, 1), 'c')

    def test_tftt_defects_after_two_defections(self):
        f = player.Player('TFTT', self.gene_size)
        opp = player.Player('Du', self.gene_size)
        opp.move_history = ['d', 'd', 'd'] + ['d'] * (self.gene_size - 3)
        f.move_history = ['c', 'c']  # simulate first two moves already done
        result = f.move(opp, 2)
        self.assertEqual(result, 'd')

    def test_prober_opens_d_c_c(self):
        g = player.Player('Prober', self.gene_size)
        opp = player.Player('Cu', self.gene_size)
        opp.move_history = ['c'] * self.gene_size
        self.assertEqual(g.move(opp, 0), 'd')
        self.assertEqual(g.move(opp, 1), 'c')
        self.assertEqual(g.move(opp, 2), 'c')

    def test_prober_exploits_passive_opponent(self):
        """Prober should defect from move 3 onward if opponent didn't retaliate."""
        g = player.Player('Prober', self.gene_size)
        opp = player.Player('Cu', self.gene_size)
        opp.move_history = ['c'] * self.gene_size
        g.move(opp, 0)
        g.move(opp, 1)
        g.move(opp, 2)
        self.assertEqual(g.move(opp, 3), 'd')

    def test_prober_tft_when_retaliated(self):
        """Prober falls back to TFT if opponent defected in moves 1 or 2."""
        g = player.Player('Prober', self.gene_size)
        opp = player.Player('Du', self.gene_size)
        opp.move_history = ['d', 'd', 'd'] + ['c'] * (self.gene_size - 3)
        g.move(opp, 0)
        g.move(opp, 1)
        g.move(opp, 2)
        self.assertEqual(g.move(opp, 3), opp.move_history[2])

    def test_move_history_appended_every_move(self):
        """Every strategy should append to move_history on every call."""
        strategies = ['Cu', 'Du', 'Random', 'Cp', 'TFT', 'TFTT', 'Prober']
        n = 10
        for strat in strategies:
            pl = player.Player(strat, n)
            opp = player.Player('Cu', n)
            opp.move_history = ['c'] * n
            for i in range(n):
                pl.move(opp, i)
            self.assertEqual(
                len(pl.move_history), n,
                f"{strat} move_history length mismatch"
            )

    def test_crossover_produces_children(self):
        a = player.Player('Cu', self.gene_size)
        b = player.Player('Du', self.gene_size)
        c1, c2 = a.crossover(b)
        self.assertEqual(len(c1.strategy_bitstring), self.gene_size)
        self.assertEqual(len(c2.strategy_bitstring), self.gene_size)
        self.assertIn(c1, a.children)
        self.assertIn(c1, b.children)


class TestEvaluation(unittest.TestCase):
    def test_mutual_cooperate(self):
        self.assertEqual(evaluation('c', 'c'), (3, 3))

    def test_mutual_defect(self):
        self.assertEqual(evaluation('d', 'd'), (0, 0))

    def test_exploit(self):
        self.assertEqual(evaluation('d', 'c'), (5, -1))
        self.assertEqual(evaluation('c', 'd'), (-1, 5))


class TestGenerateScore(unittest.TestCase):
    def test_cu_vs_du(self):
        """Cu always cooperates, Du always defects — Du should dominate."""
        a = player.Player('Cu', 10)
        b = player.Player('Du', 10)
        a_score, b_score = generate_score(a, b, 10)
        self.assertGreater(b_score, a_score)

    def test_cu_vs_cu(self):
        """Two cooperators should score equally."""
        a = player.Player('Cu', 10)
        b = player.Player('Cu', 10)
        a_score, b_score = generate_score(a, b, 10)
        self.assertEqual(a_score, b_score)


if __name__ == '__main__':
    unittest.main()
