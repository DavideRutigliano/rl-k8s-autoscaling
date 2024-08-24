import argparse
from datetime import datetime, timedelta
import os
import pandas as pd

from prometheus_api_client.prometheus_connect import PrometheusConnect

DURATION = 120


def main(path, duration=DURATION):
    client = PrometheusConnect(url="http://192.168.58.2:30000", disable_ssl=True)
    metrics = client.custom_query_range(
        'sum(rate(container_cpu_usage_seconds_total{container="busy-wait"}[1m])) / '
        'avg(kube_pod_container_resource_limits{resource="cpu",unit="core", container="busy-wait"})',
        start_time=datetime.now() - timedelta(seconds=int(duration)),
        end_time=datetime.now(),
        step='1s'
    )
    metrics_df = pd.DataFrame([{'ts': value[0], 'value': value[1]} for value in metrics[0]['values']])
    metrics_df.to_csv(os.path.join(path, 'pod_util.csv'))


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-p", "--path",
        required=True
    )
    parser.add_argument(
        "-d", "--duration",
        default=DURATION
    )
    return parser


if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()
    main(args.path, args.duration)