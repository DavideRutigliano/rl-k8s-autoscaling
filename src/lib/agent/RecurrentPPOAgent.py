import os
from sb3_contrib import RecurrentPPO
from stable_baselines3.common.callbacks import EvalCallback

from agent.BaseAgent import BaseAgent


class RecurrentPPOAgent(BaseAgent):
    def __init__(self, config, model_file=None):
        super().__init__(config)
        self.model = None
        self.model_file = model_file

    def _build_model(self, env=None):
        if self.model_file:
            self.model = RecurrentPPO.load(self.model_file, env)
        else:
            self.model = RecurrentPPO("MlpLstmPolicy", env, verbose=1)

    def train(self, train_env, eval_env=None, timesteps=500000):
        args = dict(total_timesteps=timesteps)
        if not self.model:
            self._build_model(train_env)
        if eval_env:
            eval_callback = EvalCallback(
                eval_env,
                best_model_save_path="./rl-autoscaling/rl-hpa/model/rppo",
                log_path="./rl-autoscaling/rl-hpa/model/rppo",
                eval_freq=1000,
                deterministic=True,
                render=False,
            )
            args.update(dict(callback=eval_callback))
        self.model.learn(**args)

    def act(self, observation):
        if not self.model:
            self._build_model()
        action, _ = self.model.predict(observation)
        return action
