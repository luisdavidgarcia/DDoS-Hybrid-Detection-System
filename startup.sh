#!/bin/bash

# Start docker-compose and build containers in detached mode
echo "Starting docker-compose and building containers..."
docker-compose up --build -d

# Define the log file where you want to store the stats
STATS_LOG="logs/docker_stats.log"
echo "Monitoring Docker containers..." > $STATS_LOG

# Function to collect stats and append to the log file with timestamp
function collect_stats {
    echo "Collecting stats at $(date)..." >> $STATS_LOG
    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}" >> $STATS_LOG
}

# Set simulation time in seconds and interval for stats collection in seconds
SIMULATION_TIME=180  # 3 minutes
INTERVAL=5  # Collect stats every 5 seconds

# Calculate the number of iterations needed
ITERATIONS=$((SIMULATION_TIME / INTERVAL))

# Run the monitor for the calculated time, collecting stats at each interval
for i in $(seq 1 $ITERATIONS); do
    collect_stats
    sleep $INTERVAL
done

# Stop docker-compose containers after simulation time
echo "Stopping docker containers after $SIMULATION_TIME seconds of monitoring..."
docker-compose down

# Summary report
echo "Docker container monitoring completed. Logs saved in $STATS_LOG."