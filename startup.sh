#!/bin/bash

# Function to check if a Docker image exists
function check_and_build_image {
    IMAGE_NAME=$1
    DOCKERFILE=$2

    # Check if the image exists
    if [[ "$(docker images -q $IMAGE_NAME 2> /dev/null)" == "" ]]; then
        echo "Docker image $IMAGE_NAME does not exist. Building it..."
        docker build -t $IMAGE_NAME -f $DOCKERFILE .
    else
        echo "Docker image $IMAGE_NAME already exists."
    fi
}

if [ $# -eq 0 ]; then
    echo "Usage: $0 <scenario_number>"
    exit 1
fi

SCENARIO=$1
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
STATS_LOG="logs/docker_stats_$TIMESTAMP.csv"

# Detect system architecture
ARCH=$(uname -m)

if [ "$SCENARIO" != "1" ] && [ "$SCENARIO" != "2" ]; then
    echo "Invalid scenario. Please select scenario 1 or 2."
    exit 1
fi

# Determine the compose file based on architecture and scenario
if [ "$ARCH" = "x86_64" ]; then
    COMPOSE_FILE="docker-compose.intel.scenario$SCENARIO.yml"
elif [ "$ARCH" = "aarch64" ] || [ "$ARCH" = "arm64" ]; then
    COMPOSE_FILE="docker-compose.arm.scenario$SCENARIO.yml"
else
    echo "Unsupported architecture: $ARCH"
    exit 1
fi

# Check and build images if they don't exist
check_and_build_image "ml_base_image" "Dockerfile.ml_base"
check_and_build_image "dl_base_image" "Dockerfile.dl_base"

echo "Detected architecture: $ARCH"
echo "Using Docker Compose file: $COMPOSE_FILE"

echo "Starting docker-compose and building containers..."
docker-compose -f $COMPOSE_FILE up --build -d

# Create the CSV file with headers
echo "Timestamp,Container Name,CPU Usage (%),Memory Usage,Net I/O" > $STATS_LOG

# Function to collect Docker stats
function collect_stats {
    docker stats --no-stream --format "{{.Name}},{{.CPUPerc}},{{.MemUsage}},{{.NetIO}}" | while IFS= read -r line; do
        # Capture a unique timestamp for each container's stats entry
        TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
        echo "$TIMESTAMP,$line" >> $STATS_LOG
    done
}

SIMULATION_TIME=600  # 10 minutes
INTERVAL=5  # Collect stats every 5 seconds
ITERATIONS=$((SIMULATION_TIME / INTERVAL))

# Loop to collect stats
for i in $(seq 1 $ITERATIONS); do
    collect_stats
    sleep $INTERVAL
done

echo "Stopping docker containers after $SIMULATION_TIME seconds of monitoring..."
docker-compose -f $COMPOSE_FILE down

echo "Docker container monitoring completed. Stats saved in $STATS_LOG."