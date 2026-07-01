#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Binary tree data structure used to track player lineage across simulation rounds.

Each TreeNode wraps a Player and stores left/right child references pointing to
offspring produced by crossover. Traversals are implemented iteratively to
avoid hitting Python's recursion limit on deep lineage trees.
"""

from __future__ import annotations
from typing import Generator


class TreeNode:
    """A node in the player lineage tree.

    Attributes:
        player: The Player instance stored at this node.
        id: The player's UUID string.
        left: Left child node (first offspring), or None.
        right: Right child node (second offspring), or None.
    """

    def __init__(self, player, playerid: str) -> None:
        """Initialise a TreeNode.

        Args:
            player: The Player instance to store.
            playerid: The player's UUID string.
        """
        self.player = player
        self.id = playerid
        self.left: TreeNode | None = None
        self.right: TreeNode | None = None

    def __repr__(self) -> str:
        return f"TreeNode(id={self.id!r}, gene={self.player.strategy_bitstring!r})"

    # ── traversals ───────────────────────────────────────────────────────────

    def inorder(self) -> list[TreeNode]:
        """Return nodes in inorder (left → node → right) using an iterative approach.

        Iterative traversal avoids recursion-limit issues on deep lineage trees.
        """
        result: list[TreeNode] = []
        stack: list[TreeNode] = []
        current: TreeNode | None = self

        while current is not None or stack:
            while current is not None:
                stack.append(current)
                current = current.left
            current = stack.pop()
            result.append(current)
            current = current.right

        return result

    def preorder(self) -> list[TreeNode]:
        """Return nodes in preorder (node → left → right) using an iterative approach."""
        if self is None:
            return []
        result: list[TreeNode] = []
        stack: list[TreeNode] = [self]

        while stack:
            node = stack.pop()
            result.append(node)
            # Push right first so left is processed first
            if node.right is not None:
                stack.append(node.right)
            if node.left is not None:
                stack.append(node.left)

        return result

    def postorder(self) -> list[TreeNode]:
        """Return nodes in postorder (left → right → node) using an iterative approach."""
        result: list[TreeNode] = []
        stack: list[TreeNode] = [self]

        while stack:
            node = stack.pop()
            result.append(node)
            if node.left is not None:
                stack.append(node.left)
            if node.right is not None:
                stack.append(node.right)

        # Reverse gives left → right → node order
        result.reverse()
        return result

    def ancestors(self) -> Generator[TreeNode, None, None]:
        """Yield all nodes in this subtree via preorder traversal (generator form)."""
        stack: list[TreeNode] = [self]
        while stack:
            node = stack.pop()
            yield node
            if node.right is not None:
                stack.append(node.right)
            if node.left is not None:
                stack.append(node.left)

    def depth(self) -> int:
        """Return the maximum depth of this subtree."""
        stack: list[tuple[TreeNode, int]] = [(self, 1)]
        max_depth = 0

        while stack:
            node, d = stack.pop()
            max_depth = max(max_depth, d)
            if node.left is not None:
                stack.append((node.left, d + 1))
            if node.right is not None:
                stack.append((node.right, d + 1))

        return max_depth
