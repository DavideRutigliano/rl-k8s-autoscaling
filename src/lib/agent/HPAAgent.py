import math

from agent.BaseAgent import BaseAgent


class HPAAgent(BaseAgent):
    def __init__(self, config):
        self.target = config.get('target')
        super().__init__(config)

    def _unnormalize_replicas(self, replicas):
        return replicas * (self.max_replicas - self.min_replicas) + self.min_replicas

    def act(self, observation):
        current_replicas = self._unnormalize_replicas(observation[0])
        current_input = observation[2]
        desired_replicas = math.ceil(
            current_replicas * (current_input / self.target)
        )
        return desired_replicas - current_replicas