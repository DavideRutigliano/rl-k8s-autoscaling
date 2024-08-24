import numpy as np

from agent.BaseAgent import BaseAgent


class RandomAgent(BaseAgent):
    def __init__(self, config):
        super().__init__(config)

    def act(self, observation):
        return np.random.choice([0, 1, 2])