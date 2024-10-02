# Function to check if a Docker image exists
function Check-AndBuildImage {
    param (
        [string]$imageName,
        [string]$dockerfile
    )

    # Check if the image exists
    if (-not (docker images -q $imageName)) {
        Write-Host "Docker image $imageName does not exist. Building it..."
        docker build -t $imageName -f $dockerfile .
    } else {
        Write-Host "Docker image $imageName already exists."
    }
}

# Check if the scenario number was provided
if ($args.Count -eq 0) {
    Write-Host "Usage: .\script.ps1 <scenario_number>"
    exit 1
}

# Assign the scenario argument
$scenario = $args[0]
$timestamp = (Get-Date -Format "yyyyMMdd_HHmmss")
$statsLog = "logs/docker_stats_$timestamp.csv"

# Detect system architecture
$arch = (Get-CimInstance -ClassName Win32_Processor).Architecture

if ($scenario -ne "1" -and $scenario -ne "2") {
    Write-Host "Invalid scenario. Please select scenario 1 or 2."
    exit 1
}

# Determine the compose file based on architecture and scenario
if ($arch -eq 9) {  # Architecture code 9 means x64
    $composeFile = "docker-compose.intel.scenario$scenario.yml"
    $mlDockerfile = "Dockerfile.ml_base"
    $dlDockerfile = "Dockerfile.dl_base_intel"
} elseif ($arch -eq 12) {  # Architecture code 12 means ARM64
    $composeFile = "docker-compose.arm.scenario$scenario.yml"
    $mlDockerfile = "Dockerfile.ml_base"
    $dlDockerfile = "Dockerfile.dl_base"
} else {
    Write-Host "Unsupported architecture: $arch"
    exit 1
}

# Check and build images if they don't exist
Check-AndBuildImage "ml_base_image" $mlDockerfile
Check-AndBuildImage "dl_base_image" $dlDockerfile

Write-Host "Detected architecture: $arch"
Write-Host "Using Docker Compose file: $composeFile"

# Start Docker Compose and build containers
Write-Host "Starting docker-compose and building containers..."
docker-compose -f $composeFile up --build -d

# Create the CSV file with headers
"Timestamp,Container Name,CPU Usage (%),Memory Usage,Net I/O" | Out-File -FilePath $statsLog -Encoding UTF8

# Function to collect Docker stats
function Collect-Stats {
    docker stats --no-stream --format "{{.Name}},{{.CPUPerc}},{{.MemUsage}},{{.NetIO}}" | ForEach-Object {
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        "$timestamp,$_"
    } | Out-File -Append -FilePath $statsLog -Encoding UTF8
}

$simulationTime = 600  # 10 minutes
$interval = 5  # Collect stats every 5 seconds
$iterations = $simulationTime / $interval

# Loop to collect stats
for ($i = 1; $i -le $iterations; $i++) {
    Collect-Stats
    Start-Sleep -Seconds $interval
}

Write-Host "Stopping docker containers after $simulationTime seconds of monitoring..."
docker-compose -f $composeFile down

Write-Host "Docker container monitoring completed. Stats saved in $statsLog."