"""
Quality
"""

from __future__ import annotations

from datetime import datetime
from os import makedirs, path
from typing import List, Tuple

from numpy import array, argmax, ndarray
from keras.layers import Dense
from keras.models import Sequential
from keras.optimizers import SGD

from ...base import Quality as BaseQuality
from ..environment.state import State
from ..environment.direction import Direction
from ..environment.action import Action
from .experience import Experience

class Quality(BaseQuality):
    """
    Quality
    """

    def __init__(self, gamma: float, input_size: int, output_size: int, learning_rate: float):
        """
        # Arguments
            gamma: float. Gamma.
            input_size: int. Input size of the model.
            output_size: int. Output size of the model.
            learning_rate: float. Learning rate of the optimizer.
        """
        super().__init__(gamma)
        self.output_size = output_size
        self.__model = self.__create_model(input_size, output_size)
        self.__model.compile(SGD(learning_rate), loss="mse")
        self.__learning_model = None

    def learn(self, batch: List[Experience]):
        state_list: List[State] = [experience.state for experience in batch]
        state_data = array([state.data for state in state_list])
        action_data = self.__model.predict(state_data)
        for i, experience in enumerate(batch):
            action: Action = experience.action
            action_data[i][action.data] = experience.value
        self.__model.fit(state_data, action_data, verbose=0)

    def copied(self, training_quality: Quality):
        self.__model.set_weights(training_quality.weights)

    def save(self, dir_path: str):
        makedirs(dir_path, exist_ok=True)
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.__model.save_weights(path.join(dir_path, f"{now}.hdf5"))

    @property
    def weights(self) -> List[ndarray]:
        """
        # Returns the weights of the model.
        """
        return self.__model.get_weights()

    def _select_action(self, state: State) -> Tuple[Action, float]:
        values = self.__model.predict(array([state.data]))[0]
        max_index = argmax(values)
        return (Action(Direction(max_index)), values[max_index])

    @staticmethod
    def __create_model(input_size: int, output_size: int) -> Sequential:
        """
        # Arguments
            input_size: int. Input size.
            output_size: int. Output size.
        # Returns the model.
        """
        model = Sequential()
        model.add(Dense(64, activation="relu", input_shape=(input_size,)))
        model.add(Dense(32, activation="relu"))
        model.add(Dense(output_size))
        return model
