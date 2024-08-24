import argparse
import math
import sys
import gym
import numpy as np

from stable_baselines3.common.env_checker import check_env
from stable_baselines3.common import monitor

from environment.wrappers import ActionIndexWrapper
from agent.DQNAgent import DQNAgent
from agent.PPOAgent import PPOAgent
from agent.RecurrentPPOAgent import RecurrentPPOAgent


TRAIN_CONFIG = {
    "min_replicas": 1,
    "max_replicas": 100,
    "change_rate": 1,
    "target": 75.0,
    "max_steps": 3000,
    "random_start": True,
}

EVAL_CONFIG = {
    "min_replicas": 1,
    "max_replicas": 100,
    "change_rate": 50,
    "target": 200.0,
    "max_steps": 1500,
}


def train_input_fn(step):
    return 100.0 * math.ceil(1 + np.sin(step * np.pi / 6 + 0.1))


def eval_input_fn(step):
    return (
        330.0
        + 171.10476 * np.sin(step * np.pi / 12 + 3.08)
        + 100.19048 * np.sin(step * np.pi / 6 + 2.08)
        + 31.77143 * np.sin(step * np.pi / 4 + 1.14)
    )


def main(args):
    if args.agent == "dqn":
        Agent = DQNAgent
    elif args.agent == "ppo":
        Agent = PPOAgent
    elif args.agent == "rppo":
        Agent = RecurrentPPOAgent
    else:
        print(f"Agent {args.agent} not supported")
        sys.exit(1)

    train_env = gym.make(
        "K8S-AutoScaling-v0", config=TRAIN_CONFIG, input_fn=train_input_fn
    )
    train_env = ActionIndexWrapper(train_env)
    check_env(train_env)

    eval_env = gym.make(
        "K8S-AutoScaling-v0", config=EVAL_CONFIG, input_fn=eval_input_fn
    )
    eval_env = ActionIndexWrapper(eval_env)
    eval_env = monitor.Monitor(eval_env)
    check_env(eval_env)

    agent = Agent(TRAIN_CONFIG)
    agent.train(train_env, eval_env, timesteps=float(args.steps))


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--agent", default="dqn")
    parser.add_argument("-s", "--steps", default=1e5)
    return parser


if __name__ == "__main__":
    gym.envs.registration.register(
        id="K8S-AutoScaling-v0",
        entry_point="environment.Environment:Environment",
    )
    parser = get_parser()
    main(parser.parse_args())
