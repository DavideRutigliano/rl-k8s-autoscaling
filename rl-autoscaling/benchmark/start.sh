#!/bin/bash

CPA_NAME=$1
DURATION=$2
TARGET=$3

HOST=""
SERVICE_TIME="/${TARGET}/175"

LOGS_DIR=logs
STAGE_DIR=""
SCENARIO_DIR=""
SCENARIOS=(REQUEST_RATE_S1 REQUEST_RATE_S2 REQUEST_RATE_S3 REQUEST_RATE_S4)

# Scenario 1
REQUEST_RATE_S1=(2 2 4 6 8 6 4 2 2)

# Scenario 2
REQUEST_RATE_S2=(2 2 8 8 8 2 2 2 2)

# Scenario 3
REQUEST_RATE_S3=(2 2 8 8 2 2 2 2 2)

# Scenario 4
REQUEST_RATE_S4=(2 2 8 2 8 2 8 2 2)

function create_dir(){
    mkdir -p "${1}"
}

function info(){
    printf "Starting scenario ${1}...\n"
}

function reset() {
    kubectl delete po ${CPA_NAME}
    kubectl scale deploy ${TARGET} --replicas=1
    sleep 10;
}

# function save_logs(){

#     for value in {1..12}
#     do
#         (kubectl get pods -o json) > "${SCENARIO_DIR}/${STAGE_DIR}/pods-request-${value}.log"
#         (kubectl top pods) >> "${SCENARIO_DIR}/${STAGE_DIR}/pods-usage-${value}.log"
#         sleep 10;
#     done

# }

function start_experiment(){
    S_AUX=1
    HOST=$(minikube service ${TARGET} --url)
    for scenario in "${SCENARIOS[@]}"
    do
        reset
        eval SCENARIO_NAME=\( \${${scenario}[@]} \)
        INC=1
        SCENARIO_DIR="scenario-${S_AUX}"
        info ${S_AUX}
        for REQ_RATE in "${SCENARIO_NAME[@]}"
        do
            STAGE_DIR="stage-${INC}"
            echo "Stage ${INC}: hey workers ${REQ_RATE}, duration ${DURATION} seconds..."
            create_dir "results/${CPA_NAME}/${SCENARIO_DIR}/${STAGE_DIR}"
            # save_logs &
            (hey -disable-keepalive -z ${DURATION}s -c ${REQ_RATE} -q 1 -o csv -m GET -T “application/x-www-form-urlencoded” ${HOST}${SERVICE_TIME}) > "results/${CPA_NAME}/${SCENARIO_DIR}/${STAGE_DIR}/hey-info.csv"
            (python3 /home/davide/git/innovation/rl-autoscaling/rl-autoscaling/benchmark/tools/get_metrics.py -p "results/${CPA_NAME}/${SCENARIO_DIR}/${STAGE_DIR}" -d ${DURATION})
            INC=$((INC+1))
        done
        (kubectl logs ${CPA_NAME}) > "results/${CPA_NAME}/${SCENARIO_DIR}/cpa-events.log"
        printf "Scenario ${S_AUX} finished. The logs were saved.\n"
        S_AUX=$((S_AUX+1))
    done
    echo "Experiment finished."
}

start_experiment