#!/bin/bash

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
STATS_LOG="logs/docker_stats_$TIMESTAMP.log"

# Detect system architecture
ARCH=$(uname -m)
if [ "$ARCH" = "x86_64" ]; then
    COMPOSE_FILE="docker-compose.intel.yml"
elif [ "$ARCH" = "aarch64" ] || [ "$ARCH" = "arm64" ]; then
    COMPOSE_FILE="docker-compose.arm.yml"
else
    echo "Unsupported architecture: $ARCH"
    exit 1
fi

echo "Detected architecture: $ARCH"
echo "Using Docker Compose file: $COMPOSE_FILE"

echo "Starting docker-compose and building containers..."
docker-compose -f $COMPOSE_FILE up --build -d

echo "Monitoring Docker containers..." > $STATS_LOG

function collect_stats {
    echo "Collecting stats at $(date)..." >> $STATS_LOG
    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}" >> $STATS_LOG
}

SIMULATION_TIME=120  # 10 minutes
INTERVAL=5  # Collect stats every 5 seconds
ITERATIONS=$((SIMULATION_TIME / INTERVAL))

for i in $(seq 1 $ITERATIONS); do
    collect_stats
    sleep $INTERVAL
done

echo "Stopping docker containers after $SIMULATION_TIME seconds of monitoring..."
docker-compose -f $COMPOSE_FILE down

echo "Docker container monitoring completed. Logs saved in $STATS_LOG."