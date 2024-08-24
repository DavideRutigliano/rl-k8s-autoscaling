import argparse
import math
import sys
import gym
import numpy as np
import pandas as pd

from agent.RandomAgent import RandomAgent
from agent.HPAAgent import HPAAgent
from agent.DQNAgent import DQNAgent
from agent.PPOAgent import PPOAgent
from agent.RecurrentPPOAgent import RecurrentPPOAgent

from environment.wrappers import ActionIndexWrapper

EPISODES = 100
EPISODE_STEPS = 3000

config = {
    "min_replicas": 1,
    "max_replicas": 100,
    "change_rate": 1,
    "target": 80,
    "max_steps": EPISODE_STEPS,
}

INPUT_DF = pd.read_csv(
    "/home/davide/git/innovation/rl-autoscaling/data/dataset/utilization/utilization_agg_30min.csv"
)


def input_fn(step):
    return INPUT_DF.iloc[step]["OutboundUtilzation (%)"]


def main(args):
    env = gym.make(
        "K8S-AutoScaling-v0", config=config, input_fn=input_fn
    )
    if args.agent == "hpa":
        agent = HPAAgent(config=config)
    elif args.agent == "dqn":
        agent = DQNAgent(
            config=config, model_file="./rl-autoscaling/rl-hpa/model/dqn/best_model.zip"
        )
        env = ActionIndexWrapper(env)
    elif args.agent == "ppo":
        agent = PPOAgent(
            config=config, model_file="./rl-autoscaling/rl-hpa/model/ppo/best_model.zip"
        )
        env = ActionIndexWrapper(env)
    elif args.agent == "rppo":
        agent = RecurrentPPOAgent(
            config=config,
            model_file="./rl-autoscaling/rl-hpa/model/rppo/best_model.zip",
        )
        env = ActionIndexWrapper(env)
    elif args.agent == "random":
        agent = RandomAgent(config=config)
        env = ActionIndexWrapper(env)
    else:
        print(f"Agent {args.agent} not supported")
        sys.exit(1)

    rewards = []
    for episode in range(EPISODES):
        try:
            observation = env.reset()
            for _ in range(EPISODE_STEPS):
                action = agent.act(observation)
                observation, reward, done, info = env.step(action)
                if args.render:
                    env.render()
                if done:
                    print("Episode finished after {} timesteps".format(env.step_idx))
                    env.close()
                    break
            print(
                f"Episode {episode + 1}, average reward {np.mean(env.rewards_history)}"
            )
            print("\n".join(env.get_stats()))
            rewards.append(np.mean(env.rewards_history))
        except KeyboardInterrupt:
            env.close()
            sys.exit(1)
    print(f"Average reward {np.mean(rewards)}")


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--agent", default="dqn")
    parser.add_argument("-r", "--render", default=False, action="store_true")
    return parser


if __name__ == "__main__":
    gym.envs.registration.register(
        id="K8S-AutoScaling-v0",
        entry_point="environment.Environment:Environment",
    )
    parser = get_parser()
    main(parser.parse_args())
