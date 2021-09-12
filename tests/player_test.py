#!/usr/bin/env python3

import unittest
import lib.player as player


class TestPlayer(unittest.TestCase):
    def test_moves(self):
        genesize = 20
        A = player.Player('Cu', genesize, True, None, None)
        B = player.Player('Du', genesize, True, None, None)
        C = player.Player('Random', genesize, True, None, None)
        D = player.Player('Cp', genesize, True, None, None)
        E = player.Player('TFT', genesize, True, None, None)
        F = player.Player('Cu', genesize, True, None, None)
        F.movehistory = ["d", "e", "d", "e", "d", "e", "d", "e",
                         "d", "e", "d", "e", "d", "e", "d", "e", "d", "e", "d", "e"]
        for i in range(0, genesize):
            moveA = A.move(B, i)
            moveB = B.move(A, i)
            moveE = E.move(F, i)
            self.assertEqual(moveA, "c")
            self.assertEqual(moveB, "d")
            if i == 0:
                self.assertEqual(moveE, "c")
            else:
                self.assertEqual(moveE, F.movehistory[i-1])


if __name__ == '__main__':
    unittest.main()
