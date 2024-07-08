#!/bin/bash

# Stop all the containers
echo "Stopping all containers..."
docker stop snort_container
docker stop apache_server_container
docker stop grafana_container

for i in $(seq 1 10); do
    docker stop attacker_container_scary_$i
    docker stop attacker_container_hoic_$i
    docker stop attacker_container_slowloris_$i
done

for i in $(seq 1 18); do
    docker stop normal_traffic_container_$i
done

docker stop ml_model_container
docker stop dl_model_container

# Remove all the containers
echo "Removing all containers..."
docker rm snort_container
docker rm apache_server_container
docker rm grafana_container

for i in $(seq 1 10); do
    docker rm attacker_container_scary_$i
    docker rm attacker_container_hoic_$i
    docker rm attacker_container_slowloris_$i
done

for i in $(seq 1 18); do
    docker rm normal_traffic_container_$i
done

docker rm ml_model_container
docker rm dl_model_container

# Remove the Docker network
echo "Removing Docker network..."
docker network rm ddos_network

echo "Teardown completed successfully."