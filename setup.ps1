# Stop script execution if any command fails
$ErrorActionPreference = "Stop"

# Variables for environment name and Python version
$envName = "docker-ddos-testbed"
$pythonVersion = "3.10"

# Create conda environment
Write-Host "Creating the conda environment: $envName with Python $pythonVersion"
conda create --name $envName python=$pythonVersion -y

# Initialize conda
Write-Host "Initializing conda..."
& conda init powershell

# Reload current shell session to recognize conda (or open a new PowerShell session)
Write-Host "Activating the environment: $envName"
conda activate $envName

# Install TensorFlow
Write-Host "Installing TensorFlow..."
conda install -c conda-forge tensorflow -y

# Install scikit-learn and XGBoost
Write-Host "Installing scikit-learn and XGBoost..."
conda install -c conda-forge scikit-learn xgboost -y

# Install additional libraries
Write-Host "Installing additional libraries (numpy, pandas, matplotlib, etc.)..."
conda install -c conda-forge numpy pandas matplotlib imbalanced-learn psutil seaborn jupyter -y

Write-Host "Conda environment '$envName' has been set up with all dependencies."
Write-Host "Activate the environment using: conda activate $envName"