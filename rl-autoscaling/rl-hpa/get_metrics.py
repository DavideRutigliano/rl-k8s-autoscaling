import math
import logging
import json
import sys

LOGGER = logging.getLogger(__name__)
ENV_FILE = "/app/.env"


def build_observation(spec, env):
    metrics = spec["kubernetesMetrics"][0]
    curr_replicas = int(metrics["current_replicas"])

    total_metric_value = sum(
        [
            pod_info["Value"]
            for pod_info in metrics["resource"]["pod_metrics_info"].values()
        ]
    )
    metric_value = total_metric_value / curr_replicas

    queue_size = env["queue_size"]
    total_capacity = curr_replicas * env["target"]
    total_items = metric_value + queue_size
    load = min(total_items, total_capacity)
    env["queue_size"] = total_items - load

    return env, {
        "curr_replicas": curr_replicas,
        "load": load,
        "metric_value": metric_value,
        "total_capacity": total_capacity,
    }


def main():
    with open(ENV_FILE, "r") as env_file:
        env = json.load(env_file)
    spec = json.loads(sys.stdin.read())
    env, obs = build_observation(spec, env)
    norm_replicas = (obs["curr_replicas"] - env["min_replicas"]) / (
        env["max_replicas"] - env["min_replicas"]
    )
    norm_load = math.ceil(float(obs["load"]) / float(obs["total_capacity"]) * 100) / 100
    sys.stdout.write(
        json.dumps(
            {
                "current_replicas": obs["curr_replicas"],
                "observation": [norm_replicas, norm_load, obs["metric_value"], 1],
            }
        )
    )
    with open(ENV_FILE, "w") as env_file:
        json.dump(env, env_file)
    # LOGGER.info("Current state:\n%s", json.dumps({
    #     "current_replicas": obs['curr_replicas'],
    #     "observation": [norm_replicas, norm_load, obs['metric_value']]
    # }))


if __name__ == "__main__":
    main()
