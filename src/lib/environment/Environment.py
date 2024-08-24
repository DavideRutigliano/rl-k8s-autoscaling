import collections
import sys
import math
import numpy as np

import gym
from gym import spaces


class Environment(gym.Env):
    def __init__(self, config, input_fn, *args, **kwargs):
        self.input_fn = input_fn

        self.config = config

        self.min_replicas = self.config.get("min_replicas")
        self.max_replicas = self.config.get("max_replicas")
        self.target = self.config.get("target")

        self.change_rate = self.config.get("change_rate", 1)
        self.max_steps = self.config.get("max_steps")
        self.random_start = self.config.get("random_start", False)

        self.max_increase = 1  # 5
        self.actions = list(range(-self.max_increase, self.max_increase + 1))
        self.action_space = spaces.Discrete(
            n=len(self.actions),
        )

        self.observation_size = 3
        self.observation_space = spaces.Box(
            low=0.0, high=sys.float_info.max, shape=(self.observation_size,)
        )

        self.max_history = 600
        self.window_size = (self.max_history, self.max_history)
        self.window = None

        super().__init__(*args, **kwargs)

        self.reset()

    def reset(self):
        self.step_idx = 0
        self.queue_size = 0.0
        self.load = 0.0
        if self.random_start:
            self.replicas = self.min_replicas
        else:
            self.step_idx = np.random.randint(0, self.max_steps // 2)
            self.replicas = np.random.randint(self.min_replicas, self.max_replicas)
        self.input = self._next_input()
        self.total_capacity = self.replicas * self.target
        self.actions_history = []
        self.rewards_history = []
        self.replicas_history = collections.deque(maxlen=self.max_history)
        self.load_history = collections.deque(maxlen=self.max_history)
        self.input_history = collections.deque(maxlen=self.max_history)
        self.queue_history = collections.deque(maxlen=self.max_history)
        return self._get_observation()  # , {}

    def step(self, action):
        self._step()
        self._do_action(action)
        observation = self._get_observation()
        reward = self._get_reward()
        self._update_observations(action, reward)
        done = self.step_idx >= self.max_steps if self.max_steps else False
        return observation, reward, done, {}

    def _next_input(self):
        return self.input_fn(self.step_idx)

    def _step(self):
        self.step_idx += 1
        if self.step_idx % self.change_rate == 0:
            self.input = self._next_input()
        self.total_capacity = self.replicas * self.target
        total_items = self.input + self.queue_size
        self.load = min(total_items, self.total_capacity)
        self.queue_size = total_items - self.load

    def _do_action(self, action):
        self.penalty = 0.0
        new_replicas = self.replicas + action
        if new_replicas > self.replicas:
            self.penalty += 1.0
        self.replicas = max(self.min_replicas, min(new_replicas, self.max_replicas))
        if not (self.max_replicas >= new_replicas >= self.min_replicas):
            self.penalty += 100.0

    def __normalize_replicas(self):
        return (self.replicas - self.min_replicas) / (
            self.max_replicas - self.min_replicas
        )

    def __normalize_load(self):
        return math.ceil(float(self.load) / float(self.total_capacity) * 100) / 100

    def _get_observation(self):
        observation = np.zeros((self.observation_size,), dtype=np.float32)
        observation[0] = self.__normalize_replicas()
        observation[1] = self.__normalize_load()
        observation[2] = self.input
        # observation[3] = 1 - (self.step_idx / self.max_steps)
        # observation[2] = self.queue_size
        # observation[4] = self.total_capacity
        return observation

    def _get_reward(self):
        num_instances_normalized = self.__normalize_replicas()
        normalized_load = self.__normalize_load()
        total_reward = (-1 * (1 - normalized_load)) * num_instances_normalized
        total_reward -= self.queue_size / (1 + self.queue_size)
        total_reward -= self.penalty
        return total_reward

    def _update_observations(self, action, reward):
        self.replicas_history.append(self.replicas)
        self.load_history.append(self.load)
        self.input_history.append(self.input)
        self.queue_history.append(self.queue_size)
        self.actions_history.append(action)
        self.rewards_history.append(reward)

    def render(self, mode="human"):
        if len(self.rewards_history) == 0:
            # skip rendering without at least one step
            return

        from environment.rendering import PygletWindow

        stats = self.get_stats()
        if self.window is None:
            self.window = PygletWindow(
                self.window_size[0] + 20, self.window_size[1] + 20 + 20 * len(stats)
            )

        self.window.reset()

        offset = 10

        # self.window.rectangle(
        #     offset,
        #     self.window_size[1],
        #     self.window_size[0],
        #     self.window_size[1]
        # )

        max_input_axis = max(max(self.input_history), max(self.queue_history))
        max_replica_axis = max(self.replicas_history)

        # self.window.text(str(max_input_axis), 1, 1, font_size=5)
        # self.window.text(str(max_replica_axis), self.window_size[0] + 5, 1, font_size=5)

        input_scale_factor = float(self.window_size[1] - 20) / float(
            max_input_axis + 1e-6
        )
        replica_scale_factor = float(self.window_size[1] - 20) / float(
            max_replica_axis + 1e-6
        )

        self.draw_data(input_scale_factor, replica_scale_factor, offset)

        stats_offset = self.window_size[1] + 15
        for txt in stats:
            self.window.text(txt, offset, stats_offset, font_size=8)
            stats_offset += 20

        self.window.update()

    def draw_data(self, input_scale_factor, replica_scale_factor, x_offset):
        from environment.rendering import RED, GREEN, BLACK

        prev_queue_size = 0
        prev_input = 0
        prev_replicas = 0
        y_offset = self.window_size[1] + 5
        for input, replicas, queue_size in zip(
            self.input_history, self.replicas_history, self.queue_history
        ):
            x_offset += 1

            # self.window.line(
            #     x_offset - 1,
            #     y_offset - math.ceil(input_scale_factor * float(prev_queue_size)) - 2,
            #     x_offset,
            #     y_offset - math.ceil(input_scale_factor * float(queue_size)) - 2,
            #     color=RED
            # )

            self.window.line(
                x_offset - 1,
                y_offset - math.ceil(input_scale_factor * float(self.target)) - 2,
                x_offset,
                y_offset - math.ceil(input_scale_factor * float(self.target)) - 2,
                color=BLACK,
            )

            self.window.line(
                x_offset - 1,
                y_offset - math.ceil(input_scale_factor * float(prev_input)) - 1,
                x_offset,
                y_offset - math.ceil(input_scale_factor * float(input)) - 1,
                color=GREEN,
            )

            self.window.line(
                x_offset - 1,
                y_offset - replica_scale_factor * prev_replicas - 1,
                x_offset,
                y_offset - replica_scale_factor * replicas - 1,
                color=RED,
            )

            prev_queue_size = queue_size
            prev_input = input
            prev_replicas = replicas

    def get_stats(self):
        return [
            "step              = %d" % self.step_idx,
            "replicas          = %d" % self.replicas,
            "avg reward        = %.5f" % (np.mean(self.rewards_history)),
            "avg replicas      = %.3f" % (np.mean(self.replicas_history)),
            "avg input         = %.3f" % (np.mean(self.input_history)),
            "avg load          = %.3f" % (np.mean(self.load_history)),
            "avg queue size    = %.3f" % (np.mean(self.queue_history)),
        ]

    def close(self):
        if self.window:
            self.window.close()
            self.window = None
