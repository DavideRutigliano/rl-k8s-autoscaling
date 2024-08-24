import argparse
import json
import sys
import logging
import numpy as np

from stable_baselines3 import DQN
from stable_baselines3 import PPO

LOGGER = logging.getLogger(__name__)
MAX_INCREASE = 1
ACTIONS = list(range(-MAX_INCREASE, MAX_INCREASE + 1))


def main(args):
    if args.agent == "dqn":
        agent = DQN.load(f"/app/model/{args.agent}/best_model.zip")
    elif args.agent == "ppo":
        agent = PPO.load(f"/app/model/{args.agent}/best_model.zip")
    spec = json.loads(sys.stdin.read())
    data = json.loads(spec["metrics"][0]["value"])
    observation = np.array(data["observation"])
    action = ACTIONS[agent.predict(observation)[0]]
    evaluation = {"targetReplicas": data["current_replicas"] + action}
    sys.stdout.write(json.dumps(evaluation))
    # LOGGER.info("Current action:\n%s", json.dumps(evaluation))


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--agent", default="dqn")
    return parser


if __name__ == "__main__":
    parser = get_parser()
    main(parser.parse_args())
