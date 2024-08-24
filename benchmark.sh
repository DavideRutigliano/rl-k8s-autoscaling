#!/bin/bash

DURATION=120
TARGET="busy-wait"

# CPA-HPA (only run once) - https://github.com/jthomperoo/horizontal-pod-autoscaler
# kubectl delete cpa horizontal-pod-autoscaler-example
# kubectl create -f /home/davide/git/innovation/rl-autoscaling/rl-autoscaling/hpa/manifests/cpa.yaml
# /home/davide/git/innovation/rl-autoscaling/rl-autoscaling/benchmark/start.sh horizontal-pod-autoscaler-example ${DURATION} busy-wait
# kubectl delete cpa horizontal-pod-autoscaler-example

# RL-HPA
kubectl delete cpa rl-pod-autoscaler
kubectl create -f /home/davide/git/innovation/rl-autoscaling/rl-autoscaling/rl-hpa/manifests/cpa.yaml
/home/davide/git/innovation/rl-autoscaling/rl-autoscaling/benchmark/start.sh rl-pod-autoscaler ${DURATION} ${TARGET}
kubectl delete cpa rl-pod-autoscaler