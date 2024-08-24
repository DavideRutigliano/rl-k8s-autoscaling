import argparse
import os
import re
import glob
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import seaborn as sns


def parse_cpa_logs(cpa_logs_file, scenario, scaling_method):
    cpa_df = []
    with open(cpa_logs_file, "r") as cpa_logs:
        for line in cpa_logs.readlines():
            pattern = re.compile(".*; replicas [0-9]+")
            match = pattern.search(line)
            if match:
                _, n_replicas = line.split(";")
                cpa_df.append({"replicas": int(n_replicas.replace("replicas", ""))})
    cpa_df = pd.DataFrame(cpa_df)
    cpa_df["scenario"] = scenario
    cpa_df["scaling_method"] = scaling_method
    return cpa_df


def parse_response_times(hey_logs_file, stage, scenario, scaling_method):
    hey_df = pd.read_csv(hey_logs_file)
    hey_df["stage"] = stage
    hey_df["scenario"] = scenario
    hey_df["scaling_method"] = scaling_method
    return hey_df[["stage", "scenario", "scaling_method", "response-time"]]


def parse_pod_utilization(pod_util_file, stage, scenario, scaling_method):
    util_df = pd.read_csv(pod_util_file)
    util_df["stage"] = stage
    util_df["scenario"] = scenario
    util_df["scaling_method"] = scaling_method
    util_df["value"] = util_df["value"].astype("float")
    return util_df[["stage", "scenario", "scaling_method", "value"]]


def main(path):
    response_times_df = pd.DataFrame()
    pod_util_df = pd.DataFrame()
    replicas_df = pd.DataFrame()
    for log_dir in glob.glob(os.path.join(path, "*", "scenario-*")):
        if len(glob.glob(os.path.join(log_dir, "stage-*"))) < 8:
            continue
        names = log_dir.split(os.path.sep)
        scenario = int(names[-1].split("-")[-1])
        scaling_method = names[-2]
        scenario_replicas = parse_cpa_logs(
            os.path.join(log_dir, "cpa-events.log"), scenario, scaling_method
        )
        replicas_df = pd.concat([replicas_df, scenario_replicas])
        for stage_dir in glob.glob(os.path.join(log_dir, "stage-*")):
            names = log_dir.split(os.path.sep)
            stage = int(stage_dir[-1].split("-")[-1])
            try:
                stage_resp_time = parse_response_times(
                    os.path.join(stage_dir, "hey-info.csv"),
                    stage,
                    scenario,
                    scaling_method,
                )
                response_times_df = pd.concat([response_times_df, stage_resp_time])
            except:
                pass
            try:
                stage_pod_util = parse_pod_utilization(
                    os.path.join(stage_dir, "pod_util.csv"),
                    stage,
                    scenario,
                    scaling_method,
                )
                pod_util_df = pd.concat([pod_util_df, stage_pod_util])
            except:
                pass

    response_times_df.groupby(["scenario", "stage", "scaling_method"]).agg(
        {"response-time": "mean"}  # lambda x: np.percentile(x, 95)
    )
    # response_times_df['response-time'] = np.cumsum(response_times_df['response-time'])
    sns.catplot(
        data=response_times_df,
        x="stage",
        y="response-time",
        col="scenario",
        hue="scaling_method",
        kind="box",
    )
    # sns.relplot(
    #     data=response_times_df.reset_index(),
    #     x='index', y='response-time',
    #     col='scenario',
    #     hue='scaling_method',
    #     kind='line'
    # )
    plt.savefig(os.path.join(path, "response_time.png"))
    response_times_df.to_csv(os.path.join(path, "response_time.csv"))

    sns.relplot(
        data=pod_util_df.reset_index(),
        x="index",
        y="value",
        col="scenario",
        hue="scaling_method",
        kind="line",
    )
    plt.savefig(os.path.join(path, "utilization.png"))
    pod_util_df.reset_index().to_csv(os.path.join(path, "utilization.csv"))

    sns.relplot(
        data=replicas_df.reset_index(),
        x="index",
        y="replicas",
        col="scenario",
        hue="scaling_method",
        kind="line",
    )
    plt.savefig(os.path.join(path, "replicas.png"))
    replicas_df.reset_index().to_csv(os.path.join(path, "replicas.csv"))


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--path", required=True)
    return parser


if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()
    main(args.path)
