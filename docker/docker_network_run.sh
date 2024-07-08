#!/bin/bash

NUM_ATTACKER_NODES=10
NUM_REGULAR_NODES=18

echo "Running Snort container..."
docker run --net ddos_network --name snort_container -d snort_image

echo "Running Apache server container..."
docker run --net ddos_network --name apache_server_container -d -p 80:80 -p 443:443 apache_server_image

echo "Running Grafana container..."
docker run --net ddos_network --name grafana_container -d -p 3000:3000 grafana/grafana

echo "Running attacker containers..."
for i in $(seq 1 $NUM_ATTACKER_NODES); do
    docker run --net ddos_network --name attacker_container_scary_$i -d attacker_image python3 scary_attack.py
    docker run --net ddos_network --name attacker_container_hoic_$i -d attacker_image python3 hoic_attack.py
    docker run --net ddos_network --name attacker_container_slowloris_$i -d attacker_image python3 slowloris_attack.py
done

echo "Running normal traffic containers..."
for i in $(seq 1 $NUM_REGULAR_NODES); do
    docker run --net ddos_network --name normal_traffic_container_$i -d normal_traffic_image
done

echo "Running traditional ML model container..."
docker run --net ddos_network --name ml_model_container -d ml_model_image

echo "Running deep learning model container..."
docker run --net ddos_network --name dl_model_container -d dl_model_image

echo "All containers are running."