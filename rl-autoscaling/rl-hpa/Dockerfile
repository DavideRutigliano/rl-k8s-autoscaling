FROM custompodautoscaler/python:latest

WORKDIR /app

# Copy CPA config
COPY config.yaml /

# Copy RL Agent config
COPY ./.env /app
COPY ./model /app/model

# Copy python scripts
COPY ./get_metrics.py /app
COPY ./predict.py /app

# Setup environment
COPY ./requirements.txt /tmp
RUN pip install -r /tmp/requirements.txt && \
    rm /tmp/requirements.txt
