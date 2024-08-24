class BaseAgent:
    def __init__(self, config):
        self.config = config  # kwargs.get("config", {})
        self.max_replicas = self.config.get("max_replicas", 1)
        self.min_replicas = self.config.get("min_replicas", 1)

    def act(self, observation):
        pass
