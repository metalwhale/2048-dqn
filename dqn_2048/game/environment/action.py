"""
Action
"""

from ...base import Action as BaseAction
from .direction import Direction

class Action(BaseAction):
    """
    Action
    """

    def __init__(self, direction: Direction):
        """
        # Arguments
            direction: Direction. Direction of action.
        """
        self.direction = direction

    def __str__(self):
        return self.direction.__str__()

    @property
    def data(self) -> int:
        """
        # Returns int value of the direction.
        """
        return self.direction.value
