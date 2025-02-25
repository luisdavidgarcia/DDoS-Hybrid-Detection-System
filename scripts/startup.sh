#!/bin/bash

function check_and_build_image {
    IMAGE_NAME=$1
    DOCKERFILE=$2

    if [[ "$(docker images -q $IMAGE_NAME 2> /dev/null)" == "" ]]; then
        echo "Docker image $IMAGE_NAME does not exist. Building it..."
        docker build -t $IMAGE_NAME -f "$DOCKERFILE" .
    else
        echo "Docker image $IMAGE_NAME already exists."
    fi
}

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
STATS_LOG="logs/docker_stats_$TIMESTAMP.csv"

ARCH=$(uname -m)

if [ "$ARCH" = "x86_64" ]; then
    COMPOSE_FILE="docker/docker-compose.intel.yml"
    DL_DOCKERFILE="Dockerfile.dl_base_intel"
    DL_IMAGE_NAME="dl_base_image_intel"
elif [ "$ARCH" = "aarch64" ] || [ "$ARCH" = "arm64" ]; then
    COMPOSE_FILE="docker/docker-compose.arm.yml"
    DL_DOCKERFILE="docker/Dockerfile.dl_base_arm"
    DL_IMAGE_NAME="dl_base_image_arm"
else
    echo "Unsupported architecture: $ARCH"
    exit 1
fi

ML_IMAGE_NAME="ml_base_image"
ML_DOCKERFILE="docker/Dockerfile.ml_base"

check_and_build_image "$ML_IMAGE_NAME" "$ML_DOCKERFILE"
check_and_build_image "$DL_IMAGE_NAME" "$DL_DOCKERFILE"

if [ ! -d "nginx" ]; then
    sh ./scripts/generate_files.sh 
fi

echo "Detected architecture: $ARCH"
echo "Using Docker Compose file: $COMPOSE_FILE"

echo "Starting docker-compose and building containers..."
docker compose -f "$COMPOSE_FILE" up --build -d

echo "Timestamp,Container Name,CPU Usage (%),Memory Usage,Net I/O" > "$STATS_LOG"

function collect_stats {
    docker stats --no-stream --format \
    "{{.Name}},{{.CPUPerc}},{{.MemUsage}},{{.NetIO}}" | \
    while IFS= read -r line; do
        TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
        echo "$TIMESTAMP,$line" >> "$STATS_LOG"
    done
}

SIMULATION_TIME=140 # SECONDS
INTERVAL=5 # SECONDS
ITERATIONS=$((SIMULATION_TIME / INTERVAL))

for i in $(seq 1 $ITERATIONS); do
    collect_stats
    sleep $INTERVAL
done

echo "Stopping docker containers after $SIMULATION_TIME seconds of monitoring..."
docker compose -f "$COMPOSE_FILE" down

echo "Docker container monitoring completed. Stats saved in $STATS_LOG."