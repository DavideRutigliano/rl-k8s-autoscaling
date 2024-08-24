#!/bin/bash
minikube start --extra-config=kubelet.housekeeping-interval=10s --kubernetes-version=v1.23.3 --memory 8192 --cpus 4
# minikube addons enable istio-provisioner
# minikube addons enable istio

CPA_VERSION=v1.3.0
HELM_CHART=custom-pod-autoscaler-operator
helm install --set mode=namespaced --namespace=${NAMESPACE} \
${HELM_CHART} https://github.com/jthomperoo/custom-pod-autoscaler-operator/releases/download/${CPA_VERSION}/custom-pod-autoscaler-operator-${CPA_VERSION}.tgz