"""
State
"""

from __future__ import annotations

import copy
import random
from typing import List

from ...base import State as BaseState
from .direction import Direction

class State(BaseState):
    """
    Represents the board contains tiles.
    """

    _EMPTY: int = 0

    def __init__(self, size: int, unit: int):
        """
        # Arguments
            size: Int. The size of the board.
            unit: Int. Unit value for tile, other valid values are powers of this unit value.
        """
        self.size = size
        self.unit = unit
        # Initialize a `size` x `size` board filled with empty values
        self._board = [row[:] for row in [[self._EMPTY] * self.size] * self.size]

    def __eq__(self, other: State):
        return self._board == other._board

    def __str__(self):
        return "\n".join(["".join([f"{tile:4}" for tile in row]) for row in self._board])

    def seeded(self) -> int:
        """
        Randomly seeds a new tile in an empty spot on the board with unit value.
        # Returns the value of the new tile if it is successfully seeded,
            otherwise returns empty value if the board has no spot for seeding new tile.
        # Examples
            0   2   0   0           0   2   0   0
            0   0   0   0      ⇒    0   0   0   0
            0   0   0   0           0   0   0   2 ← new tile
            0   0   2   0           0   0   2   0
        """
        flattened_board = [tile for row in self._board for tile in row]
        empty_indices = [index for index, tile in enumerate(flattened_board) if tile == self._EMPTY]
        if len(empty_indices) == 0:
            return self._EMPTY
        index = random.choice(empty_indices)
        self._board[index // self.size][index % self.size] = self.unit
        return self.unit

    def collapsed(self, direction: Direction) -> State:
        """
        Collapse the entire board in a given direction
        # Arguments
            direction: Direction. Collapsing direction.
        # Returns a flag indicates whether the board is changed after collapsing or not.
        # Examples
            0   0   0   4                                   0   0   2   4
            0   0   0   0       direction:  UP         ⇒    0   0   0   2
            0   0   0   2                                   0   0   0   0
            0   0   2   0                                   0   0   0   0
        """
        old_state = self.clone()
        for i in range(self.size):
            collapsed_array = self._collapse(self._peel(direction, i), self._EMPTY)
            self._paved(direction, i, collapsed_array)
        return self != old_state

    def is_collapsible(self) -> bool:
        """
        # Returns a flag indicates whether the board is collapsible or not.
        """
        for i in range(self.size):
            row = self._board[i]
            column = [r[i] for r in self._board]
            for j in range(self.size):
                if (row[j] == self._EMPTY or column[j] == self._EMPTY
                        or j < self.size and (row[j] == row[j + 1] or column[j] == column[j + 1])):
                    return True
        return False

    def clone(self) -> State:
        """
        # Returns new cloned `State`.
        """
        return copy.deepcopy(self)

    def _peel(self, direction: Direction, index: int) -> List[int]:
        """
        Peel off an array from the board by a given direction and index.
        # Arguments
            direction: Direction. Peeling direction.
            index: int. Index of row or column.
        # Returns the array peeled off from the board.
        # Examples
            0   2   4   0       direction:  RIGHT
            0   0   0   0       index: 0               ⇒    0   4   2   0
            0   0   2   0
            0   0   0   0
        """
        if direction in (Direction.LEFT, Direction.RIGHT):
            array = self._board[index]
        else:
            array = [row[index] for row in self._board]
        if direction in (Direction.RIGHT, Direction.DOWN):
            array = list(reversed(array))
        return array

    def _paved(self, direction: Direction, index: int, array: List[int]):
        """
        Copy entire array elements into specific row or column.
        # Arguments
            direction: Direction. Paving direction.
            index: int. Index of row or column.
            array: List[int]. Array to be copied.
        # Examples
            0   2   0   0       direction:  UP                  0   2   4   0
            0   0   0   0       index: 3                   ⇒    0   0   0   0
            0   0   0   0       array:  4   0   2   0           0   0   2   0
            0   0   2   0                                       0   0   0   0
                                                                        ↑
                                                                        paved column
        """
        array = array[:self.size]
        if direction in (Direction.RIGHT, Direction.DOWN):
            array = reversed(array)
        for i, tile in enumerate(array):
            if direction in (Direction.LEFT, Direction.RIGHT):
                self._board[index][i] = tile
            else:
                self._board[i][index] = tile

    @staticmethod
    def _collapse(array: List[int], empty_element: int) -> List[int]:
        """
        Slide entire elements of an array as far as possible to the left side.
        If two elements of the same number collide while moving, they will merge into an element
            with the total value of the two elements that collided.
        The resulting element cannot merge with another element again in the same move.
        # Arguments
            array: List[int]. Original array.
            empty_element: int. Value of empty element.
        # Returns a collapsed array
        # Examples
            1. No elements merged
                0   2   0   0      ⇒    2   0   0   0
            2. One element merged
                0   2   2   4      ⇒    4   4   0   0
                                        ↑
                                        2+2
            3. Two elements merged
                2   2   2   2      ⇒    4   4   0   0
                                        ↑   ↑
                                        2+2 2+2
        """
        collapsed_array = []
        is_merging = False
        for element in array:
            if element == empty_element:
                continue
            last_element = None if not collapsed_array else collapsed_array[-1]
            if element == last_element and not is_merging:
                collapsed_array[-1] += element
                is_merging = True
            else:
                collapsed_array.append(element)
                is_merging = False
        collapsed_array += [empty_element] * (len(array) - len(collapsed_array))
        return collapsed_array